"""Peer review command."""

import asyncio
import json
from pathlib import Path
from typing import Optional

import typer

from ..automation.judge_panel import launch_judge_panel
from ..core.agent import check_cursor_agent
from ..core.config import PROJECT_ROOT, resolve_path
from ..core.output import console, print_error, print_info, print_success, print_warning
from ..core.state import update_phase
from ..github.reviews import ReviewComment


def _load_repo_context() -> str:
    """Load repo context for review (planning docs, README, CONTRIBUTING)."""
    context_parts = []
    project_root = Path(PROJECT_ROOT)

    planning_dir = project_root / "planning"
    if planning_dir.exists():
        for doc in sorted(planning_dir.glob("*.md"))[:5]:
            try:
                content = doc.read_text()[:2000]
                context_parts.append(f"## {doc.name}\n{content}")
            except (OSError, IOError):
                pass

    readme = project_root / "README.md"
    if readme.exists():
        try:
            context_parts.append(f"## README.md\n{readme.read_text()[:2000]}")
        except (OSError, IOError):
            pass

    return "\n\n---\n\n".join(context_parts) if context_parts else ""


def _get_winner_from_aggregated(task_id: str) -> Optional[str]:
    """Get winner from aggregated decision file."""
    aggregated_path = PROJECT_ROOT / ".prompts" / "decisions" / f"{task_id}-aggregated.json"
    if not aggregated_path.exists():
        return None

    try:
        data = json.loads(aggregated_path.read_text())
        winner = data.get("winner")
        if not winner:
            return None

        from ..core.decision_parser import normalize_winner

        return normalize_winner(winner)
    except (json.JSONDecodeError, KeyError):
        return None


def _run_pr_review(
    pr_number: int, dry_run: bool = False, include_cli: bool = False, skip_agents: bool = False, fresh: bool = False
) -> None:
    """Run peer review on a GitHub PR with full judge panel."""
    from ..core.session import load_session
    from ..github.pulls import check_gh_installed, fetch_pr
    from ..github.reviews import Review, post_review

    if not check_gh_installed():
        print_error("gh CLI not installed or not authenticated")
        console.print("Install: https://cli.github.com/")
        console.print("Auth:    gh auth login")
        raise typer.Exit(1)

    print_info(f"Fetching PR #{pr_number}...")
    try:
        pr = fetch_pr(pr_number, cwd=str(PROJECT_ROOT))
    except RuntimeError as e:
        print_error(str(e))
        raise typer.Exit(1)

    print_info(f"PR: {pr.title}")
    print_info(f"Branch: {pr.head_branch} → {pr.base_branch}")

    if not pr.diff.strip():
        print_warning("PR has no diff - nothing to review")
        raise typer.Exit(0)

    task_id = f"pr-{pr_number}"
    prompts_dir = PROJECT_ROOT / ".prompts"
    prompts_dir.mkdir(exist_ok=True)

    # Load repo context (planning docs, README, etc.)
    repo_context = _load_repo_context()

    from ..automation.prompts import build_pr_review_prompt

    prompt_path = prompts_dir / f"peer-review-{task_id}.md"
    prompt_path.write_text(
        build_pr_review_prompt(
            pr_number=pr_number,
            title=pr.title,
            body=pr.body or "",
            head_branch=pr.head_branch,
            head_sha=pr.head_sha,
            base_branch=pr.base_branch,
            diff=pr.diff,
            task_id=task_id,
            repo_context=repo_context,
        )
    )

    if skip_agents:
        print_info(f"Skipping agents, using existing decisions for PR #{pr_number}...")
    else:
        # Get judges, optionally excluding cli-review types (like CodeRabbit)
        from ..core.user_config import get_judge_configs

        all_judges = get_judge_configs()
        if include_cli:
            judges_to_run = all_judges
        else:
            judges_to_run = [j for j in all_judges if j.type != "cli-review"]

        # Check for existing sessions to resume (unless --fresh)
        resume_mode = False
        if not fresh:
            sessions_found = []
            for jconfig in judges_to_run:
                if jconfig.type == "cli-review":
                    continue
                if load_session(jconfig.key.upper(), f"{task_id}_peer-review"):
                    sessions_found.append(jconfig.label)

            if sessions_found:
                resume_mode = True
                print_info(f"Resuming {len(sessions_found)} judge session(s) for PR #{pr_number}...")
                for label in sessions_found:
                    console.print(f"  [dim]→ {label}[/dim]")
            else:
                print_info(f"Starting fresh judge panel ({len(judges_to_run)} judges) for PR #{pr_number}...")
        else:
            print_info(f"Starting fresh judge panel ({len(judges_to_run)} judges) for PR #{pr_number}...")

        excluded = len(all_judges) - len(judges_to_run)
        if excluded:
            print_info(f"Excluding {excluded} cli-review judge(s)")

        try:
            asyncio.run(
                launch_judge_panel(
                    task_id,
                    prompt_path,
                    "peer-review",
                    resume_mode=resume_mode,
                    winner=f"LOCAL:{pr.head_branch}",
                    judges_to_run=judges_to_run,
                )
            )
        except RuntimeError as e:
            # Some judges may have failed but others succeeded - continue with partial results
            print_warning(f"Partial panel failure: {e}")
            print_info("Continuing with available judge decisions...")

    # Aggregate decisions and post to GitHub
    from ..core.decision_parser import get_peer_review_status
    from ..core.user_config import get_judge_config, get_judge_configs

    status = get_peer_review_status(task_id, project_root=PROJECT_ROOT)

    total = status["decisions_found"]
    approvals = status["approvals"]

    if total == 0:
        print_error("No judge decisions found - cannot post review")
        raise typer.Exit(1)

    # Always COMMENT - never auto-approve, that's for humans
    decision = "COMMENT"
    if status["approved"]:
        summary = f"✅ All {approvals}/{total} judges approved this PR."
    elif approvals > 0:
        summary = f"⚠️ {approvals}/{total} judges approved. Some requested changes."
    else:
        summary = f"❌ {total} judge(s) requested changes."

    # Collect issues and inline comments from all decisions
    from ..core.decision_parser import get_decision_file_path

    all_issues: list[tuple[str, str]] = []
    all_comments: list[tuple[str, ReviewComment]] = []  # (judge_label, comment)

    # Use get_decision_file_path which checks worktrees and copies to PROJECT_ROOT
    for jconfig in get_judge_configs():
        decision_path = get_decision_file_path(jconfig.key, task_id, review_type="peer-review")
        console.print(f"[dim]Looking for {jconfig.key}: {decision_path} (exists: {decision_path.exists()})[/dim]")
        if not decision_path.exists():
            print_warning(f"Decision file not found for {jconfig.label}: {decision_path}")
            continue
        try:
            data = json.loads(decision_path.read_text())
            judge_key = data.get("judge", jconfig.key)
            judge_cfg = get_judge_config(judge_key)
            judge_label = judge_cfg.label if judge_cfg else judge_key

            # Collect text issues
            issues = data.get("blocker_issues", []) + data.get("remaining_issues", [])
            for issue in issues:
                all_issues.append((judge_label, issue))

            # Collect inline comments
            for c in data.get("inline_comments", []):
                if "path" in c and "line" in c and "body" in c:
                    try:
                        line_num = int(c["line"])
                        if line_num <= 0:
                            continue
                    except (ValueError, TypeError):
                        continue
                    all_comments.append(
                        (
                            judge_label,
                            ReviewComment(
                                path=c["path"],
                                line=line_num,
                                body=c["body"],
                                severity=c.get("severity", "warning"),
                            ),
                        )
                    )
        except (json.JSONDecodeError, OSError):
            pass

    # Fetch existing comments for AI deduplication
    from ..github.reviews import fetch_existing_comments

    print_info("Fetching existing comments from PR...")
    existing_comments = fetch_existing_comments(pr_number, cwd=str(PROJECT_ROOT))
    console.print(f"[dim]Found {len(existing_comments)} existing comments[/dim]")

    # Use AI deduper to intelligently combine/skip comments
    from ..automation.comment_deduper import run_dedupe_agent

    dedupe_result = asyncio.run(
        run_dedupe_agent(
            new_comments=all_comments,
            existing_comments=existing_comments,
            pr_diff=pr.diff,
            pr_number=pr_number,
        )
    )

    comments_to_post = dedupe_result.comments_to_post

    if dedupe_result.skipped:
        console.print(f"[dim]Skipping {len(dedupe_result.skipped)} comment(s) (duplicates/low-value)[/dim]")
    if dedupe_result.merged:
        console.print(f"[dim]Merged {len(dedupe_result.merged)} comment group(s)[/dim]")

    # Build summary with issues
    if all_issues:
        summary += "\n\n**Issues found:**\n" + "\n".join(f"- [{j}] {issue}" for j, issue in all_issues[:10])

    summary += "\n\n---\n🤖 Agent Cube Peer Review"

    # Display results
    console.print()
    console.print(f"[bold]Decision:[/bold] {decision}")
    console.print(f"[bold]Summary:[/bold] {summary[:200]}...")
    console.print()

    if comments_to_post:
        severity_order = {"critical": 0, "warning": 1, "nitpick": 2}
        sorted_comments = sorted(comments_to_post, key=lambda c: severity_order.get(c.severity, 99))

        console.print(f"[bold]Comments to post ({len(sorted_comments)}):[/bold]")
        console.print()
        severity_colors = {"critical": "red", "warning": "yellow", "nitpick": "dim"}
        for c in sorted_comments:
            color = severity_colors.get(c.severity, "white")
            console.print(f"[{color}]{c.severity.upper():8}[/{color}] {c.path}:{c.line}")
            body_first_line = c.body.split("\n")[0]
            console.print(f"  {body_first_line}")
            console.print()
    elif all_issues:
        console.print(f"[bold]Issues ({len(all_issues)}):[/bold]")
        for judge_name, issue in all_issues[:10]:
            console.print(f"  [cyan][{judge_name}][/cyan] {issue}")
        if len(all_issues) > 10:
            console.print(f"  [dim]... and {len(all_issues) - 10} more[/dim]")
    else:
        console.print("[dim]No issues found[/dim]")

    # Post review
    if dry_run:
        print_warning("Dry run - review NOT posted to GitHub")
        if comments_to_post:
            console.print(f"[dim]Would post {len(comments_to_post)} new comment(s)[/dim]")
    else:
        print_info("Posting review to GitHub...")
        try:
            review = Review(decision=decision, summary=summary, comments=comments_to_post)
            post_review(pr_number, review, cwd=str(PROJECT_ROOT))
            print_success(f"Review posted to PR #{pr_number} ({len(comments_to_post)} new comments)")
        except RuntimeError as e:
            print_error(f"Failed to post review: {e}")
            raise typer.Exit(1)


def peer_review_command(
    task_id: str,
    peer_review_prompt_file: str,
    fresh: bool = False,
    judge: Optional[str] = None,
    local: bool = False,
    pr: Optional[int] = None,
    dry_run: bool = False,
    include_cli: bool = False,
    skip_agents: bool = False,
) -> None:
    """Resume original judges from initial panel for peer review.

    Args:
        task_id: Task ID
        peer_review_prompt_file: Path to prompt file
        fresh: Launch new judges instead of resuming
        judge: Run only this specific judge (e.g., "judge_4")
        local: Review current git branch instead of cube-managed worktree
        pr: GitHub PR number to review (runs full panel and posts review)
        dry_run: Show review but don't post to GitHub (only with --pr)
        skip_agents: Skip running agents, use existing decision files
    """
    import subprocess

    # Handle --pr mode separately
    if pr is not None:
        _run_pr_review(pr, dry_run=dry_run, include_cli=include_cli, skip_agents=skip_agents, fresh=fresh)
        return

    if not check_cursor_agent():
        print_error("cursor-agent CLI is not installed")
        raise typer.Exit(1)

    try:
        prompt_path = resolve_path(peer_review_prompt_file)
    except FileNotFoundError:
        temp_path = PROJECT_ROOT / ".prompts" / f"temp-peer-review-{task_id}.md"
        temp_path.parent.mkdir(exist_ok=True)
        temp_path.write_text(peer_review_prompt_file)
        prompt_path = temp_path

    # Use current branch if --local, otherwise auto-detect winner
    winner: Optional[str] = None
    if local:
        result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, cwd=PROJECT_ROOT)
        current_branch = result.stdout.strip()
        if not current_branch:
            print_error("Could not determine current git branch")
            raise typer.Exit(1)
        winner = f"LOCAL:{current_branch}"
        print_info(f"Reviewing local branch: {current_branch}")
    else:
        winner = _get_winner_from_aggregated(task_id) or ""
        if winner:
            print_info(f"Winner from panel: Writer {winner}")
        else:
            print_warning("No aggregated decision found - will review both writers")

    try:
        if judge:
            # Run single judge
            print_info(f"Running single judge: {judge}")
            asyncio.run(
                launch_judge_panel(
                    task_id, prompt_path, "peer-review", resume_mode=not fresh, winner=winner, single_judge=judge
                )
            )
        elif fresh:
            print_info("Launching fresh judge panel for peer review")
            # For local branches, run ALL judges (not just peer_review_only)
            asyncio.run(
                launch_judge_panel(
                    task_id, prompt_path, "peer-review", resume_mode=False, winner=winner, run_all_judges=local
                )
            )
        else:
            print_info("Resuming original judge panel for peer review")
            from ..core.session import session_exists
            from ..core.user_config import get_judge_configs

            judge_configs = get_judge_configs()
            missing_sessions = []

            for jconfig in judge_configs:
                if not session_exists(f"JUDGE_{jconfig.key}", f"{task_id}_panel"):
                    missing_sessions.append(jconfig.key)

            if missing_sessions:
                print_error(f"Could not find panel session IDs for task: {task_id}")
                console.print()
                console.print("Make sure you've run the panel first:")
                console.print(f"  cube panel {task_id} <panel-prompt.md>")
                console.print()
                console.print("Session files expected:")
                for num in missing_sessions:
                    console.print(f"  .agent-sessions/JUDGE_{num}_{task_id}_panel_SESSION_ID.txt")
                console.print()
                console.print("Or use --fresh to launch new judges instead")
                raise typer.Exit(1)

            asyncio.run(launch_judge_panel(task_id, prompt_path, "peer-review", resume_mode=True, winner=winner))

        update_phase(task_id, 7, peer_review_complete=True)
    except RuntimeError as e:
        print_error(str(e))
        raise typer.Exit(1)
