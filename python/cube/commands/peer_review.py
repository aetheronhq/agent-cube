"""Peer review command."""

import asyncio
from pathlib import Path
import typer

from ..core.agent import check_cursor_agent
from ..core.output import print_error, print_info
from ..core.config import PROJECT_ROOT
from ..automation.judge_panel import launch_judge_panel

def peer_review_command(
    task_id: str,
    peer_review_prompt_file: str,
    fresh: bool = False
) -> None:
    """Resume original 3 judges from initial panel for peer review."""
    
    if not check_cursor_agent():
        print_error("cursor-agent CLI is not installed")
        raise typer.Exit(1)
    
    prompt_path = PROJECT_ROOT / peer_review_prompt_file
    
    if not prompt_path.exists():
        print_error(f"Peer review prompt file not found: {peer_review_prompt_file}")
        raise typer.Exit(1)
    
    if fresh:
        print_info("Launching fresh judge panel for peer review")
        try:
            asyncio.run(launch_judge_panel(task_id, prompt_path, "peer-review", resume_mode=False))
        except Exception as e:
            print_error(f"Failed to launch peer review: {e}")
            raise typer.Exit(1)
    else:
        print_info("Resuming original judge panel for peer review")
        try:
            asyncio.run(launch_judge_panel(task_id, prompt_path, "peer-review", resume_mode=True))
        except Exception as e:
            print_error(f"Failed to resume peer review: {e}")
            print()
            print("Make sure you've run the initial panel first:")
            print(f"  cube-py panel {task_id} <panel-prompt.md> initial")
            print()
            print("Or use --fresh to launch new judges instead")
            raise typer.Exit(1)

