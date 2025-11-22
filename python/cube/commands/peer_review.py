"""Peer review command."""

import asyncio
from pathlib import Path
import typer

from ..core.agent import check_cursor_agent
from ..core.output import print_error, print_info, console
from ..core.config import PROJECT_ROOT, resolve_path
from ..automation.judge_panel import launch_judge_panel
from ..core.state import update_phase

def peer_review_command(
    task_id: str,
    peer_review_prompt_file: str,
    fresh: bool = False
) -> None:
    """Resume original judges from initial panel for peer review."""
    
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
    
    try:
        if fresh:
            print_info("Launching fresh judge panel for peer review")
            asyncio.run(launch_judge_panel(task_id, prompt_path, "peer-review", resume_mode=False))
        else:
            print_info("Resuming original judge panel for peer review")
            from ..core.session import session_exists
            from ..core.user_config import get_judge_configs
            
            judge_configs = get_judge_configs()
            missing_sessions = []
            
            for jconfig in judge_configs:
                if not session_exists(f"JUDGE_{jconfig.number}", f"{task_id}_panel"):
                    missing_sessions.append(jconfig.number)
            
            if missing_sessions:
                print_error(f"Could not find panel session IDs for task: {task_id}")
                print()
                print("Make sure you've run the panel first:")
                print(f"  cube panel {task_id} <panel-prompt.md>")
                print()
                print("Session files expected:")
                for num in missing_sessions:
                    print(f"  .agent-sessions/JUDGE_{num}_{task_id}_panel_SESSION_ID.txt")
                print()
                print("Or use --fresh to launch new judges instead")
                raise typer.Exit(1)
            
            asyncio.run(launch_judge_panel(task_id, prompt_path, "peer-review", resume_mode=True))
        
        update_phase(task_id, 7, peer_review_complete=True)
    except RuntimeError as e:
        print_error(str(e))
        raise typer.Exit(1)

