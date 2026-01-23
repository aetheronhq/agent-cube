"""Fix PR review comments command."""

import subprocess
from pathlib import Path
from typing import Optional

from ..core.config import PROJECT_ROOT, get_worktree_path
from ..core.output import console, print_error, print_info, print_success, print_warning
from ..github.categorizer import CategorizedComment, categorize_comments
from ..github.comments import CommentThread, fetch_all_comments, fetch_comment_threads
from ..github.pulls import check_gh_installed, fetch_pr
from ..github.responder import reply_and_resolve


def _sync_pr_worktree(pr_number: int, branch: str, cwd: Optional[str] = None) -> Optional[Path]:
    """Create or sync a worktree for fixing PR comments."""
    project_name = Path(PROJECT_ROOT).name
    worktree_path = get_worktree_path(project_name, "pr-fix", str(pr_number))

    try:
        result = subprocess.run(
            ["git", "fetch", "origin", branch],
            cwd=cwd or PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            print_warning(f"Failed to fetch branch: {result.stderr}")

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
            result = subprocess.run(
                ["git", "checkout", "-B", branch, f"origin/{branch}"],
                cwd=worktree_path,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                print_error(f"Checkout failed: {result.stderr}")
                return None

        return worktree_path
    except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
        print_error(f"Git operation failed: {e}")
        return None


def _build_fix_prompt(comments: list[CategorizedComment], pr_number: int, pr_title: str) -> str:
    """Build a prompt for the writer agent to fix the comments."""
    prompt = f"""# Fix PR Review Comments

You are fixing review comments on PR #{pr_number}: {pr_title}

## Comments to Address

"""
    for i, cat in enumerate(comments, 1):
        comment = cat.comment
        path_info = f"{comment.path}:{comment.line}" if comment.path else "(general)"
        prompt += f"""### Comment {i}: {path_info}
**Author:** {comment.author}
**Category:** {cat.category}
**Comment:**
{comment.body}

**Fix Plan:** {cat.fix_plan or "Address the feedback appropriately"}

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


def _build_commit_message(comments: list[CategorizedComment], pr_number: int) -> str:
    """Build a detailed commit message for the fix."""
    summaries = []
    for cat in comments[:5]:
        body_preview = cat.comment.body[:40].replace("\n", " ").strip()
        if len(cat.comment.body) > 40:
            body_preview += "..."
        path_info = cat.comment.path or "general"
        summaries.append(f"- {path_info}: {body_preview}")

    msg = f"fix: address PR #{pr_number} review comments\n\n"
    msg += "Addressed feedback:\n"
    msg += "\n".join(summaries)
    if len(comments) > 5:
        msg += f"\n... and {len(comments) - 5} more"
    msg += "\n\nAutomated fixes via cube auto --fix-comments"
    return msg


def _run_fix_agent(
    worktree: Path, prompt: str, pr_number: int, comments: Optional[list[CategorizedComment]] = None
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

    layout = SingleAgentLayout
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


def _display_categorized_comments(
    categorized: list[CategorizedComment],
    show_all: bool = False,
) -> None:
    """Display categorized comments in a formatted way."""
    if not categorized:
        console.print("[dim]No comments to display[/dim]")
        return

    category_colors = {
        "ACTIONABLE": "red",
        "QUESTION": "yellow",
        "SUGGESTION": "cyan",
        "RESOLVED": "green",
        "SKIP": "dim",
    }

    for cat in categorized:
        if not show_all and cat.category == "SKIP":
            continue

        color = category_colors.get(cat.category, "white")
        path_info = f"{cat.comment.path}:{cat.comment.line}" if cat.comment.path else "(top-level)"

        console.print(f"\n[{color}][{cat.category}][/{color}] {path_info}")
        console.print(f"  [dim]Author:[/dim] {cat.comment.author}")
        console.print(f"  [dim]Confidence:[/dim] {cat.confidence:.0%}")

        body_preview = cat.comment.body[:200].replace("\n", " ")
        if len(cat.comment.body) > 200:
            body_preview += "..."
        console.print(f"  [dim]Comment:[/dim] {body_preview}")

        if cat.fix_plan:
            console.print(f"  [bold]Fix plan:[/bold] {cat.fix_plan}")


def fix_pr_comments(
    pr_number: Optional[int] = None,
    dry_run: bool = False,
    from_author: Optional[str] = None,
    skip_bots: Optional[list[str]] = None,
    verbose: bool = False,
) -> None:
    """Fix review comments on a PR.

    Args:
        pr_number: PR number (auto-detected if not provided)
        dry_run: Show plan without making changes
        from_author: Only process comments from this author
        skip_bots: List of bot usernames to skip
        verbose: Show all comments including skipped ones
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

    # Categorize for display purposes but process ALL comments
    categorized = categorize_comments(all_to_process)

    console.print()
    console.print(f"[bold]Processing {len(all_to_process)} comments from {len(active_threads)} active threads[/bold]")

    if verbose:
        _display_categorized_comments(categorized, show_all=True)
    else:
        # Show brief summary of each comment
        for cat in categorized:
            path_info = f"{cat.comment.path}:{cat.comment.line}" if cat.comment.path else "(top-level)"
            body_preview = cat.comment.body[:80].replace("\n", " ")
            if len(cat.comment.body) > 80:
                body_preview += "..."
            console.print(f"  [{cat.category}] {path_info}: {body_preview}")

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
    print_info(f"Running writer agent to fix {len(categorized)} comments...")

    fix_prompt = _build_fix_prompt(categorized, pr_number, pr.title)
    commit_sha = _run_fix_agent(worktree, fix_prompt, pr_number, comments=categorized)

    if not commit_sha:
        print_warning("No fixes were committed - agent may not have made changes")
        return

    print_success(f"Fixes committed: {commit_sha}")

    console.print()
    print_info("Replying to comments and resolving threads...")

    success_count = 0
    for cat in categorized:
        comment = cat.comment
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
    print_success(f"Addressed {success_count}/{len(categorized)} comments (commit: {commit_sha})")


def list_pr_comments(
    pr_number: Optional[int] = None,
    from_author: Optional[str] = None,
    show_resolved: bool = False,
) -> None:
    """List comments on a PR with their categories.

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

    thread_comments = []
    for thread in threads:
        if thread.comments:
            thread_comments.append(thread.comments[0])

    categorized = categorize_comments(thread_comments)

    console.print()
    console.print(f"[bold]PR #{pr_number} Comments ({len(categorized)} threads)[/bold]")
    console.print()

    _display_categorized_comments(categorized, show_all=True)
