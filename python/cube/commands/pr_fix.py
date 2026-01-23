"""Fix PR review comments command."""

import subprocess
from pathlib import Path
from typing import Optional

from ..core.config import PROJECT_ROOT, get_worktree_path
from ..core.output import console, print_error, print_info, print_success, print_warning
from ..github.comments import CommentThread, PRComment, fetch_all_comments, fetch_comment_threads
from ..github.pulls import check_gh_installed, fetch_pr
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
                        # Found existing worktree for this branch - use it
                        worktree_path = Path(current_worktree)
                        print_info(f"Using existing worktree: {worktree_path}")
                        # Pull latest changes
                        subprocess.run(
                            ["git", "pull", "--ff-only"],
                            cwd=worktree_path,
                            capture_output=True,
                            timeout=30,
                        )
                        return worktree_path

        # No existing worktree - create a new one
        project_name = Path(PROJECT_ROOT).name
        worktree_path = get_worktree_path(project_name, "pr-fix", str(pr_number))

        if not worktree_path.exists():
            worktree_path.parent.mkdir(parents=True, exist_ok=True)
            result = subprocess.run(
                ["git", "worktree", "add", str(worktree_path), f"origin/{branch}"],
                cwd=cwd or PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                print_error(f"Failed to create worktree: {result.stderr}")
                return None
        else:
            # Worktree exists but on different branch - reset it
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


def _build_fix_prompt(comments: list[PRComment], pr_number: int, pr_title: str) -> str:
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

    prompt += """## Instructions

1. Read each comment carefully
2. Make the requested changes in the appropriate files
3. If a comment contains a `suggestion` block, apply that exact change
4. For questions, add code comments or make clarifying changes as appropriate
5. Run any relevant tests to ensure your fixes don't break anything
6. Commit your changes with a message referencing the PR

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
    from ..core.single_layout import SingleAgentLayout
    from ..core.user_config import get_default_writer, get_writer_config, load_config

    writer_key = get_default_writer()
    wconfig = get_writer_config(writer_key)
    config = load_config()
    cli_name = config.cli_tools.get(wconfig.model, "cursor-agent")
    parser = get_parser(cli_name)

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

    async def run_fix():
        stream = run_agent(worktree, wconfig.model, prompt, session_id=None, resume=False)
        line_count = 0
        async for line in stream:
            line_count += 1
            msg = parser.parse(line)
            if msg:
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

    # Push the changes
    result = subprocess.run(
        ["git", "push", "origin", "HEAD"],
        cwd=worktree,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        print_error(f"Push failed: {result.stderr}")
        return None

    return commit_sha


def _get_current_pr_number(cwd: Optional[str] = None) -> Optional[int]:
    """Try to detect PR number from current branch."""
    import subprocess

    result = subprocess.run(
        ["gh", "pr", "view", "--json", "number"],
        capture_output=True,
        text=True,
        cwd=cwd,
        timeout=30,
    )

    if result.returncode != 0:
        return None

    try:
        import json

        data = json.loads(result.stdout)
        return data.get("number")
    except Exception:
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
) -> None:
    """Fix review comments on a PR.

    Args:
        pr_number: PR number (auto-detected if not provided)
        dry_run: Show plan without making changes
        from_author: Only process comments from this author
        skip_bots: List of bot usernames to skip
    """
    if not check_gh_installed():
        print_error("gh CLI not installed or not authenticated")
        console.print("Install: https://cli.github.com/")
        console.print("Auth: gh auth login")
        return

    cwd = str(PROJECT_ROOT)

    if pr_number is None:
        pr_number = _get_current_pr_number(cwd)
        if pr_number is None:
            print_error("Could not detect PR number. Use --pr to specify.")
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

    if not all_to_process:
        print_success("No active comments to address!")
        return

    console.print()
    console.print(f"[bold]Processing {len(all_to_process)} comments from {len(active_threads)} active threads[/bold]")

    # Show brief summary of each comment
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

    print_info(f"Fetching PR #{pr_number} details...")
    try:
        pr = fetch_pr(pr_number, cwd=cwd)
    except RuntimeError as e:
        print_error(f"Failed to fetch PR: {e}")
        return

    print_info(f"Setting up worktree for branch: {pr.head_branch}")
    worktree = _sync_pr_worktree(pr_number, pr.head_branch, cwd=cwd)
    if not worktree:
        print_error("Failed to create/sync worktree for fixes")
        return

    console.print(f"[dim]Worktree ready at: {worktree}[/dim]")

    console.print()
    print_info(f"Running writer agent to fix {len(all_to_process)} comments...")

    fix_prompt = _build_fix_prompt(all_to_process, pr_number, pr.title)
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
