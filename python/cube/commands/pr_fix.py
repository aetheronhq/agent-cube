"""Fix PR review comments command."""

from typing import Optional

from ..core.config import PROJECT_ROOT
from ..core.output import console, print_error, print_info, print_success, print_warning
from ..github.categorizer import CategorizedComment, categorize_comments, filter_actionable
from ..github.comments import CommentThread, fetch_all_comments, fetch_comment_threads
from ..github.responder import (
    format_fix_reply,
    reply_to_comment,
    resolve_thread,
)


def _get_current_pr_number(cwd: Optional[str] = None) -> Optional[int]:
    """Try to detect PR number from current branch."""
    import subprocess

    result = subprocess.run(
        ["gh", "pr", "view", "--json", "number"],
        capture_output=True,
        text=True,
        cwd=cwd,
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
    auto_resolve: bool = False,
    include_questions: bool = True,
    include_suggestions: bool = False,
    verbose: bool = False,
) -> None:
    """Fix review comments on a PR.

    Args:
        pr_number: PR number (auto-detected if not provided)
        dry_run: Show plan without making changes
        from_author: Only process comments from this author
        skip_bots: List of bot usernames to skip
        auto_resolve: Automatically resolve threads after fixing
        include_questions: Include questions in actionable items
        include_suggestions: Include suggestions in actionable items
        verbose: Show all comments including skipped ones
    """
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

    if not active_threads:
        print_success("No active comments to address!")
        return

    thread_comments = []
    for thread in active_threads:
        if thread.comments:
            thread_comments.append(thread.comments[0])

    print_info("Categorizing comments...")
    categorized = categorize_comments(thread_comments)

    actionable = filter_actionable(
        categorized,
        include_questions=include_questions,
        include_suggestions=include_suggestions,
    )

    console.print()
    console.print("[bold]Summary:[/bold]")
    console.print(f"  Total threads: {len(threads)}")
    console.print(f"  Active threads: {len(active_threads)}")
    console.print(f"  Actionable: {len(actionable)}")

    skipped = [c for c in categorized if c.category == "SKIP"]
    console.print(f"  Skipped: {len(skipped)}")

    if verbose:
        _display_categorized_comments(categorized, show_all=True)
    else:
        _display_categorized_comments(actionable, show_all=False)

    if dry_run:
        console.print()
        print_warning("Dry run - no changes made")
        if actionable:
            console.print()
            console.print("[bold]Would process:[/bold]")
            for cat in actionable:
                path_info = f"{cat.comment.path}:{cat.comment.line}" if cat.comment.path else "(top-level)"
                console.print(f"  - [{cat.category}] {path_info}: {cat.fix_plan or 'Review needed'}")
        return

    if not actionable:
        print_success("No actionable comments - nothing to fix!")
        return

    console.print()
    print_info(f"Processing {len(actionable)} actionable comments...")

    success_count = 0
    for cat in actionable:
        comment = cat.comment
        path_info = f"{comment.path}:{comment.line}" if comment.path else "(top-level)"

        if cat.fix_plan:
            console.print(f"[dim]Processing {path_info}...[/dim]")

            reply_body = format_fix_reply(
                f"Acknowledged. {cat.fix_plan}",
                include_signature=True,
            )

            if comment.id:
                success = reply_to_comment(
                    pr_number,
                    comment.id,
                    reply_body,
                    cwd=cwd,
                )

                if success:
                    success_count += 1
                    console.print(f"  [green]Replied to {path_info}[/green]")

                    if auto_resolve and comment.thread_id:
                        if resolve_thread(comment.thread_id, cwd=cwd):
                            console.print("  [green]Resolved thread[/green]")
                else:
                    console.print(f"  [red]Failed to reply to {path_info}[/red]")
        else:
            console.print(f"[dim]Skipping {path_info} - no fix plan generated[/dim]")

    console.print()
    if success_count > 0:
        print_success(f"Processed {success_count}/{len(actionable)} comments")
    else:
        print_warning("No comments were processed")


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
