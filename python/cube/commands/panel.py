"""Panel command."""

import asyncio
from pathlib import Path
import typer

from ..core.agent import check_cursor_agent
from ..core.output import print_error, console
from ..core.config import PROJECT_ROOT
from ..automation.judge_panel import launch_judge_panel

def panel_command(
    task_id: str,
    panel_prompt_file: str,
    resume: bool = False
) -> None:
    """Launch 3-judge panel for solution review."""
    
    if not check_cursor_agent():
        print_error("cursor-agent CLI is not installed")
        print()
        print("Install cursor-agent:")
        print("  npm install -g @cursor/cli")
        print()
        print("After installation, authenticate with:")
        print("  cursor-agent login")
        print()
        raise typer.Exit(1)
    
    prompt_path = PROJECT_ROOT / panel_prompt_file
    
    if not prompt_path.exists():
        temp_path = PROJECT_ROOT / ".prompts" / f"temp-panel-{task_id}.md"
        temp_path.parent.mkdir(exist_ok=True)
        temp_path.write_text(panel_prompt_file)
        prompt_path = temp_path
    
    asyncio.run(launch_judge_panel(task_id, prompt_path, "panel", resume))

