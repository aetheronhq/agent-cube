"""Peer review command."""

import asyncio
import json
from typing import Optional

import typer

from ..automation.judge_panel import launch_judge_panel
from ..core.agent import check_cursor_agent
from ..core.config import PROJECT_ROOT, resolve_path
from ..core.output import console, print_error, print_info, print_warning
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


def peer_review_command(
    task_id: str, peer_review_prompt_file: str, fresh: bool = False, judge: Optional[str] = None, local: bool = False
) -> None:
    """Resume original judges from initial panel for peer review.

    Args:
        task_id: Task ID
        peer_review_prompt_file: Path to prompt file
        fresh: Launch new judges instead of resuming
        judge: Run only this specific judge (e.g., "judge_4")
        local: Review current git branch instead of cube-managed worktree
    """
    import subprocess

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
