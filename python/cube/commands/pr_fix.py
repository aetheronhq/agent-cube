"""Fix PR review comments command."""

import subprocess
from pathlib import Path
from typing import Optional

from ..core.config import PROJECT_ROOT, get_worktree_path
from ..core.output import console, print_error, print_info, print_success, print_warning
from ..github.comments import CommentThread, PRComment, fetch_all_comments, fetch_comment_threads
from ..github.pulls import check_gh_installed, fetch_failed_ci_logs, fetch_pr
from ..github.responder import reply_and_resolve


def _sync_pr_worktree(pr_number: int, branch: str, cwd: Optional[str] = None) -> Optional[Path]:
    """Create or sync a worktree for fixing PR comments."""
    try:
        # Fetch the branch first
        result = subprocess.run(
            ["git", "fetch", "origin", branch],
            cwd=cwd or PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            print_warning(f"Failed to fetch branch: {result.stderr}")

        # Check if there's already a worktree for this branch
        result = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            cwd=cwd or PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            lines = result.stdout.split("\n")
            current_worktree = None
            for line in lines:
                if line.startswith("worktree "):
                    current_worktree = line.replace("worktree ", "")
                elif line.startswith("branch ") and current_worktree:
                    worktree_branch = line.replace("branch refs/heads/", "")
                    if worktree_branch == branch:
                        worktree_path = Path(current_worktree)
                        if not worktree_path.exists():
                            print_warning(f"Stale worktree entry (directory missing): {worktree_path}")
                            subprocess.run(
                                ["git", "worktree", "remove", "--force", str(worktree_path)],
                                cwd=cwd or PROJECT_ROOT,
                                capture_output=True,
                                timeout=10,
                            )
                            break
                        print_info(f"Using existing worktree: {worktree_path}")
                        subprocess.run(
                            ["git", "pull", "--ff-only"],
                            cwd=worktree_path,
                            capture_output=True,
                            timeout=30,
                        )
                        return worktree_path

        # No existing worktree - create a new one tracking the branch
        project_name = Path(PROJECT_ROOT).name
        worktree_path = get_worktree_path(project_name, "pr-fix", str(pr_number))

        if not worktree_path.exists():
            worktree_path.parent.mkdir(parents=True, exist_ok=True)
            # Create local tracking branch, then add worktree on it
            subprocess.run(
                ["git", "branch", "--track", branch, f"origin/{branch}"],
                cwd=cwd or PROJECT_ROOT,
                capture_output=True,
                timeout=10,
            )
            result = subprocess.run(
                ["git", "worktree", "add", str(worktree_path), branch],
                cwd=cwd or PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                print_error(f"Failed to create worktree: {result.stderr}")
                return None
            # Fast-forward to latest remote
            subprocess.run(
                ["git", "reset", "--hard", f"origin/{branch}"],
                cwd=worktree_path,
                capture_output=True,
                timeout=30,
            )
        else:
            # Worktree exists - make sure we're on the branch, not detached
            subprocess.run(
                ["git", "checkout", branch],
                cwd=worktree_path,
                capture_output=True,
                timeout=10,
            )
            result = subprocess.run(
                ["git", "reset", "--hard", f"origin/{branch}"],
                cwd=worktree_path,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                print_error(f"Reset failed: {result.stderr}")
                return None

        return worktree_path
    except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
        print_error(f"Git operation failed: {e}")
        return None


def _build_fix_prompt(
    comments: list[PRComment], pr_number: int, pr_title: str, ci_logs: list[dict] | None = None
) -> str:
    """Build a prompt for the writer agent to fix the comments."""
    prompt = f"""# Fix PR Review Comments

You are fixing review comments on PR #{pr_number}: {pr_title}

## Comments to Address

"""
    for i, comment in enumerate(comments, 1):
        path_info = f"{comment.path}:{comment.line}" if comment.path else "(general)"
        prompt += f"""### Comment {i}: {path_info}
**Author:** {comment.author}
**Comment:**
{comment.body}

"""

    if ci_logs:
        prompt += "## Failed CI/Build Logs\n\n"
        prompt += "The following CI checks are failing and MUST be fixed:\n\n"
        for ci in ci_logs:
            prompt += f"### {ci['name']} ({ci['status']})\n```\n{ci['log']}\n```\n\n"

    prompt += """## Instructions

1. Read each comment carefully
2. Make the requested changes in the appropriate files
3. If a comment contains a `suggestion` block, apply that exact change
4. For questions, add code comments or make clarifying changes as appropriate
5. **If you disagree** with a comment or believe the reviewer lacks context:
   - Still address the comment appropriately (add clarifying code comment, or explain in commit)
   - You can reply inline explaining your reasoning
   - If a change would be incorrect/harmful, explain why rather than blindly applying it
6. **Before committing**: Run the repo's verification command to ensure your fixes don't break anything:
   - Check `Taskfile.yml` for `verify`, `check`, or `ci` task
   - Or `package.json` for `verify`, `check`, or `ci` script
   - Or `Makefile` for `verify`, `check`, or `ci` target
   - Fix any errors before proceeding
7. Commit your changes with a message referencing the PR

**Important:** Focus only on the changes requested in the comments above. Do not refactor or change unrelated code.
"""
    return prompt


def _build_commit_message(comments: list[PRComment], pr_number: int) -> str:
    """Build a detailed commit message for the fix."""
    summaries = []
    for comment in comments[:5]:
        body_preview = comment.body[:40].replace("\n", " ").strip()
        if len(comment.body) > 40:
            body_preview += "..."
        path_info = comment.path or "general"
        summaries.append(f"- {path_info}: {body_preview}")

    msg = f"fix: address PR #{pr_number} review comments\n\n"
    msg += "Addressed feedback:\n"
    msg += "\n".join(summaries)
    if len(comments) > 5:
        msg += f"\n... and {len(comments) - 5} more"
    msg += "\n\nAutomated fixes via cube auto --fix-comments"
    return msg


def _run_fix_agent(
    worktree: Path, prompt: str, pr_number: int, comments: Optional[list[PRComment]] = None
) -> Optional[str]:
    """Run a writer agent to fix the comments and return the commit SHA."""
    from ..automation.stream import format_stream_message
    from ..core.agent import run_agent, run_async
    from ..core.output import console
    from ..core.parsers.registry import get_parser
    from ..core.session import load_session, save_session
    from ..core.single_layout import SingleAgentLayout
    from ..core.user_config import get_default_writer, get_writer_config, load_config

    writer_key = get_default_writer()
    wconfig = get_writer_config(writer_key)
    config = load_config()
    cli_name = config.cli_tools.get(wconfig.model, "cursor-agent")
    parser = get_parser(cli_name)

    # Check for existing session to resume
    session_key = f"PR_FIX_{pr_number}"
    existing_session = load_session("FIXER", session_key)
    resume = existing_session is not None

    if resume and existing_session:
        console.print(f"[dim]Resuming {wconfig.label} (session: {existing_session[:8]}...)[/dim]")
    else:
        console.print(f"[dim]Running {wconfig.label} to fix comments...[/dim]")

    # Record HEAD before agent runs (to detect if agent committed)
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=worktree,
        capture_output=True,
        text=True,
        timeout=10,
    )
    head_before = result.stdout.strip() if result.returncode == 0 else None

    layout = SingleAgentLayout
    layout.initialize(wconfig.label)
    layout.start()

    # Track session ID from stream
    captured_session_id: Optional[str] = None

    async def run_fix():
        nonlocal captured_session_id
        stream = run_agent(worktree, wconfig.model, prompt, session_id=existing_session, resume=resume)
        line_count = 0
        async for line in stream:
            line_count += 1
            msg = parser.parse(line)
            if msg:
                # Capture session ID if present
                if msg.session_id and not captured_session_id:
                    captured_session_id = msg.session_id
                    save_session("FIXER", session_key, msg.session_id, f"PR #{pr_number} fixer")

                formatted = format_stream_message(msg, wconfig.label, wconfig.color)
                if formatted:
                    if formatted.startswith("[thinking]"):
                        thinking_text = formatted.replace("[thinking]", "").replace("[/thinking]", "")
                        layout.update_thinking(thinking_text)
                    elif msg.type == "assistant" and msg.content:
                        layout.add_assistant_message(msg.content, wconfig.label, wconfig.color)
                    else:
                        layout.add_output(formatted)
        return line_count

    try:
        line_count = run_async(run_fix())
        layout.close()
        if line_count < 5:
            print_warning("Agent completed very quickly - may not have made changes")
    except KeyboardInterrupt:
        layout.close()
        print_warning("Agent interrupted by user")
        return None
    except Exception as e:
        layout.close()
        print_error(f"Agent failed: {e}")
        return None

    # Check if agent already committed (HEAD changed)
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=worktree,
        capture_output=True,
        text=True,
        timeout=10,
    )
    head_after = result.stdout.strip() if result.returncode == 0 else None
    agent_committed = head_before and head_after and head_before != head_after

    if agent_committed:
        # Agent already committed - just get the SHA and push
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=worktree,
            capture_output=True,
            text=True,
            timeout=10,
        )
        commit_sha = result.stdout.strip() if result.returncode == 0 else None
        print_info(f"Agent committed changes: {commit_sha}")
    else:
        # Check for uncommitted changes
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=worktree,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if not result.stdout.strip():
            print_warning("No changes detected after agent run")
            return None

        # Commit the changes ourselves
        subprocess.run(["git", "add", "-A"], cwd=worktree, capture_output=True, timeout=30)
        commit_msg = (
            _build_commit_message(comments or [], pr_number)
            if comments
            else f"fix: address PR #{pr_number} review comments"
        )
        result = subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=worktree,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            print_warning(f"Commit failed: {result.stderr}")
            return None

        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=worktree,
            capture_output=True,
            text=True,
            timeout=10,
        )
        commit_sha = result.stdout.strip() if result.returncode == 0 else None

    # Push the changes — resolve branch name explicitly to avoid detached HEAD issues
    branch_result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=worktree,
        capture_output=True,
        text=True,
        timeout=10,
    )
    branch_name = branch_result.stdout.strip() if branch_result.returncode == 0 else ""
    if not branch_name or branch_name == "HEAD":
        # Detached HEAD — find the branch from the reflog
        branch_result = subprocess.run(
            ["git", "log", "--format=%D", "-1"],
            cwd=worktree,
            capture_output=True,
            text=True,
            timeout=10,
        )
        for ref in (branch_result.stdout.strip() or "").split(", "):
            ref = ref.strip()
            if ref.startswith("origin/") and not ref.startswith("origin/HEAD"):
                branch_name = ref.replace("origin/", "")
                break

    if branch_name and branch_name != "HEAD":
        push_ref = f"HEAD:{branch_name}"
    else:
        push_ref = "HEAD"

    result = subprocess.run(
        ["git", "push", "origin", push_ref],
        cwd=worktree,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        print_error(f"Push failed: {result.stderr}")
        return None

    return commit_sha


def _get_pr_for_task(task_id: str, cwd: Optional[str] = None) -> Optional[int]:
    """Find the open PR for a task by checking writer branch patterns."""
    from ..core.user_config import load_config

    effective_cwd = cwd or str(PROJECT_ROOT)
    config = load_config()

    # Check writer branches: writer-opus/<task_id>, writer-codex/<task_id>, etc.
    for writer_key in config.writer_order:
        writer = config.writers[writer_key]
        branch = f"writer-{writer.name}/{task_id}"
        pr = _find_open_pr_for_branch(branch, effective_cwd)
        if pr is not None:
            print_info(f"Found PR #{pr} for branch {branch}")
            return pr

    return None


def _get_current_pr_number(cwd: Optional[str] = None) -> Optional[int]:
    """Detect the most recent open PR for the current branch or any worktree branch.

    Uses `gh pr list --head <branch>` to find the most recent open PR for a
    specific branch, rather than `gh pr view` which can return stale/wrong PRs.
    """
    import subprocess

    effective_cwd = cwd or str(PROJECT_ROOT)

    # Collect all branch names: workspace + worktrees
    branches = []

    # Current workspace branch
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=effective_cwd,
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode == 0:
        branch = result.stdout.strip()
        if branch and branch != "HEAD":
            branches.append(branch)

    # Worktree branches
    result = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        cwd=effective_cwd,
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode == 0:
        for line in result.stdout.split("\n"):
            if line.startswith("branch refs/heads/"):
                branch = line.replace("branch refs/heads/", "")
                if branch not in branches:
                    branches.append(branch)

    # Find the most recent open PR for any of these branches
    for branch in branches:
        pr = _find_open_pr_for_branch(branch, effective_cwd)
        if pr is not None:
            return pr

    return None


def _find_open_pr_for_branch(branch: str, cwd: str) -> Optional[int]:
    """Find the most recent open PR for a specific branch."""
    import json
    import subprocess

    try:
        result = subprocess.run(
            ["gh", "pr", "list", "--head", branch, "--state", "open", "--json", "number", "--limit", "1"],
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=15,
        )
        if result.returncode == 0:
            prs = json.loads(result.stdout)
            if prs:
                return prs[0].get("number")
    except (subprocess.TimeoutExpired, Exception):
        pass
    return None


def _filter_threads_by_author(
    threads: list[CommentThread],
    from_author: Optional[str],
) -> list[CommentThread]:
    """Filter threads to only those with comments from specified author."""
    if not from_author:
        return threads

    filtered = []
    for thread in threads:
        has_author = any(c.author.lower() == from_author.lower() for c in thread.comments)
        if has_author:
            filtered.append(thread)

    return filtered


def _filter_threads_skip_bots(
    threads: list[CommentThread],
    skip_bots: list[str],
) -> list[CommentThread]:
    """Filter out threads where all comments are from bots to skip."""
    if not skip_bots:
        return threads

    filtered = []
    for thread in threads:
        non_skipped = [
            c
            for c in thread.comments
            if c.author.lower() not in [b.lower() for b in skip_bots]
            and not (c.author.endswith("[bot]") and "agent-cube" in c.author.lower())
        ]
        if non_skipped:
            filtered.append(thread)

    return filtered


def fix_pr_comments(
    pr_number: Optional[int] = None,
    dry_run: bool = False,
    from_author: Optional[str] = None,
    skip_bots: Optional[list[str]] = None,
    task_id: Optional[str] = None,
) -> None:
    """Fix review comments on a PR.

    Args:
        pr_number: PR number (auto-detected if not provided)
        dry_run: Show plan without making changes
        from_author: Only process comments from this author
        skip_bots: List of bot usernames to skip
        task_id: Task ID to find the PR by writer branch pattern
    """
    if not check_gh_installed():
        print_error("gh CLI not installed or not authenticated")
        console.print("Install: https://cli.github.com/")
        console.print("Auth: gh auth login")
        return

    cwd = str(PROJECT_ROOT)

    if pr_number is None:
        pr_number = _get_pr_for_task(task_id, cwd) if task_id else _get_current_pr_number(cwd)
        if pr_number is None:
            if task_id:
                print_error(f"No open PR found for task '{task_id}'. Use --pr to specify.")
            else:
                print_error("Could not detect PR number. Use --pr to specify or pass a task file.")
            return

    print_info(f"Fetching comments from PR #{pr_number}...")

    threads = fetch_comment_threads(pr_number, cwd)
    all_comments = fetch_all_comments(pr_number, cwd)

    console.print(f"[dim]Found {len(threads)} threads, {len(all_comments)} total comments[/dim]")

    active_threads = [t for t in threads if not t.is_resolved and not t.is_outdated]
    console.print(f"[dim]Active (unresolved, not outdated): {len(active_threads)} threads[/dim]")

    if from_author:
        active_threads = _filter_threads_by_author(active_threads, from_author)
        console.print(f"[dim]After filtering by author '{from_author}': {len(active_threads)} threads[/dim]")

    default_skip_bots = ["agent-cube"]
    bots_to_skip = skip_bots if skip_bots is not None else default_skip_bots
    if bots_to_skip:
        active_threads = _filter_threads_skip_bots(active_threads, bots_to_skip)
        console.print(f"[dim]After filtering bots: {len(active_threads)} threads[/dim]")

    thread_comments = []
    for thread in active_threads:
        if thread.comments:
            thread_comments.append(thread.comments[0])

    issue_comments = [c for c in all_comments if c.path is None and not c.is_bot]
    if from_author:
        issue_comments = [c for c in issue_comments if c.author.lower() == from_author.lower()]
    if bots_to_skip:
        issue_comments = [c for c in issue_comments if c.author.lower() not in [b.lower() for b in bots_to_skip]]

    all_to_process = thread_comments + issue_comments
    console.print(
        f"[dim]Processing: {len(thread_comments)} thread comments + {len(issue_comments)} issue comments[/dim]"
    )

    print_info(f"Fetching PR #{pr_number} details...")
    try:
        pr = fetch_pr(pr_number, cwd=cwd)
    except RuntimeError as e:
        print_error(f"Failed to fetch PR: {e}")
        return

    print_info("Fetching CI/build logs...")
    ci_logs = fetch_failed_ci_logs(pr_number, cwd=cwd)
    if ci_logs:
        console.print(f"[dim]Found {len(ci_logs)} failed CI check(s): {', '.join(c['name'] for c in ci_logs)}[/dim]")
    else:
        console.print("[dim]No failed CI checks[/dim]")

    if not all_to_process and not ci_logs:
        print_success("No active comments and CI is passing!")
        return

    if all_to_process:
        console.print()
        console.print(
            f"[bold]Processing {len(all_to_process)} comments from {len(active_threads)} active threads[/bold]"
        )
        for comment in all_to_process:
            path_info = f"{comment.path}:{comment.line}" if comment.path else "(top-level)"
            body_preview = comment.body[:80].replace("\n", " ")
            if len(comment.body) > 80:
                body_preview += "..."
            console.print(f"  {path_info}: {body_preview}")

    if dry_run:
        console.print()
        print_warning("Dry run - no changes made")
        return

    print_info(f"Setting up worktree for branch: {pr.head_branch}")
    worktree = _sync_pr_worktree(pr_number, pr.head_branch, cwd=cwd)
    if not worktree:
        print_error("Failed to create/sync worktree for fixes")
        return

    console.print(f"[dim]Worktree ready at: {worktree}[/dim]")

    work_items = []
    if all_to_process:
        work_items.append(f"{len(all_to_process)} comments")
    if ci_logs:
        work_items.append(f"{len(ci_logs)} failed CI checks")
    console.print()
    print_info(f"Running writer agent to fix {', '.join(work_items)}...")

    fix_prompt = _build_fix_prompt(all_to_process, pr_number, pr.title, ci_logs=ci_logs)
    commit_sha = _run_fix_agent(worktree, fix_prompt, pr_number, comments=all_to_process)

    if not commit_sha:
        print_warning("No fixes were committed - agent may not have made changes")
        return

    print_success(f"Fixes committed: {commit_sha}")

    console.print()
    print_info("Replying to comments and resolving threads...")

    success_count = 0
    for comment in all_to_process:
        path_info = f"{comment.path}:{comment.line}" if comment.path else "(top-level)"

        if comment.id:
            success = reply_and_resolve(
                pr_number=pr_number,
                comment=comment,
                commit_sha=commit_sha,
                cwd=cwd,
            )

            if success:
                success_count += 1
                console.print(f"  [green]Replied and resolved: {path_info}[/green]")
            else:
                console.print(f"  [yellow]Replied but could not resolve: {path_info}[/yellow]")

    console.print()
    print_success(f"Addressed {success_count}/{len(all_to_process)} comments (commit: {commit_sha})")


def list_pr_comments(
    pr_number: Optional[int] = None,
    from_author: Optional[str] = None,
    show_resolved: bool = False,
) -> None:
    """List comments on a PR.

    Args:
        pr_number: PR number (auto-detected if not provided)
        from_author: Only show comments from this author
        show_resolved: Include resolved threads
    """
    cwd = str(PROJECT_ROOT)

    if pr_number is None:
        pr_number = _get_current_pr_number(cwd)
        if pr_number is None:
            print_error("Could not detect PR number. Use --pr to specify.")
            return

    print_info(f"Fetching comments from PR #{pr_number}...")

    threads = fetch_comment_threads(pr_number, cwd)

    if not show_resolved:
        threads = [t for t in threads if not t.is_resolved]

    if from_author:
        threads = _filter_threads_by_author(threads, from_author)

    if not threads:
        print_info("No comments found matching criteria")
        return

    console.print()
    console.print(f"[bold]PR #{pr_number} Comments ({len(threads)} threads)[/bold]")
    console.print()

    for thread in threads:
        if thread.comments:
            comment = thread.comments[0]
            path_info = f"{comment.path}:{comment.line}" if comment.path else "(top-level)"
            body_preview = comment.body[:100].replace("\n", " ")
            if len(comment.body) > 100:
                body_preview += "..."
            console.print(f"  {path_info}")
            console.print(f"    [dim]{comment.author}:[/dim] {body_preview}")
