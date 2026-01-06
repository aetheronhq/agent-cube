"""Peer review command."""

import asyncio
import json
from typing import Optional

import typer

from ..automation.judge_panel import launch_judge_panel
from ..core.agent import check_cursor_agent
from ..core.config import PROJECT_ROOT, resolve_path
from ..core.output import console, print_error, print_info, print_success, print_warning
from ..core.state import update_phase


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

    prompt_path = prompts_dir / f"peer-review-{task_id}.md"
    prompt_path.write_text(f"""# Peer Review: PR #{pr_number}

## PR: {pr.title}

{pr.body or "(No description)"}

## Branch
- Head: {pr.head_branch} ({pr.head_sha})
- Base: {pr.base_branch}

## Diff
```diff
{pr.diff}
```

## Your Task

Review this PR and create your decision file at:
`.prompts/decisions/{{judge_key}}-{task_id}-peer-review.json`

Focus on:
1. Security issues
2. Performance concerns
3. Code quality
4. Missing tests
5. Documentation

If the code is good, APPROVE it. If issues need fixing, REQUEST_CHANGES.
""")

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

    # Collect issues from all decisions (check both field names)
    all_issues = []
    decisions_dir = PROJECT_ROOT / ".prompts" / "decisions"
    for f in decisions_dir.glob(f"*-{task_id}-peer-review.json"):
        try:
            data = json.loads(f.read_text())
            judge_key = data.get("judge", f.stem.split("-")[0])
            from ..core.user_config import get_judge_config

            judge_cfg = get_judge_config(judge_key)
            judge_label = judge_cfg.label if judge_cfg else judge_key
            issues = data.get("blocker_issues", []) + data.get("remaining_issues", [])
            for issue in issues:
                all_issues.append((judge_label, issue))
        except (json.JSONDecodeError, OSError):
            pass

    if all_issues:
        summary += "\n\n**Issues found:**\n" + "\n".join(f"- [{j}] {issue}" for j, issue in all_issues[:10])

    summary += "\n\n---\n🤖 Agent Cube Peer Review"

    console.print()
    console.print(f"[bold]Decision:[/bold] {decision}")
    console.print(f"[bold]Summary:[/bold] {summary[:200]}...")
    console.print()

    if all_issues:
        console.print(f"[bold]Issues ({len(all_issues)}):[/bold]")
        for judge_name, issue in all_issues[:10]:
            console.print(f"  [cyan][{judge_name}][/cyan] {issue}")
        if len(all_issues) > 10:
            console.print(f"  [dim]... and {len(all_issues) - 10} more[/dim]")
    else:
        console.print("[dim]No blocking issues found[/dim]")

    if dry_run:
        print_warning("Dry run - review NOT posted to GitHub")
    else:
        print_info("Posting review to GitHub...")
        try:
            review = Review(decision=decision, summary=summary, comments=[])
            post_review(pr_number, review, cwd=str(PROJECT_ROOT))
            print_success(f"Review posted to PR #{pr_number}")
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
