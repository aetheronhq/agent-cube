"""Peer review command."""

import asyncio
from pathlib import Path
import typer

from ..core.agent import check_cursor_agent
from ..core.output import print_error, print_info, console
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
        temp_path = PROJECT_ROOT / ".prompts" / f"temp-peer-review-{task_id}.md"
        temp_path.parent.mkdir(exist_ok=True)
        temp_path.write_text(peer_review_prompt_file)
        prompt_path = temp_path
    
    if fresh:
        print_info("Launching fresh judge panel for peer review")
        asyncio.run(launch_judge_panel(task_id, prompt_path, "peer-review", resume_mode=False))
    else:
        print_info("Resuming original judge panel for peer review")
        from ..core.session import session_exists
        
        for judge_num in [1, 2, 3]:
            if not session_exists(f"JUDGE_{judge_num}", f"{task_id}_panel"):
                print_error(f"Could not find panel session IDs for task: {task_id}")
                print()
                print("Make sure you've run the panel first:")
                print(f"  cube panel {task_id} <panel-prompt.md>")
                print()
                print("Session files expected:")
                print(f"  .agent-sessions/JUDGE_1_{task_id}_panel_SESSION_ID.txt")
                print(f"  .agent-sessions/JUDGE_2_{task_id}_panel_SESSION_ID.txt")
                print(f"  .agent-sessions/JUDGE_3_{task_id}_panel_SESSION_ID.txt")
                print()
                print("Or use --fresh to launch new judges instead")
                raise typer.Exit(1)
        
        asyncio.run(launch_judge_panel(task_id, prompt_path, "peer-review", resume_mode=True))

