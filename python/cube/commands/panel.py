"""Panel command."""

import asyncio

import typer

from ..automation.judge_panel import launch_judge_panel
from ..core.agent import check_cursor_agent
from ..core.config import PROJECT_ROOT, resolve_path
from ..core.output import console, print_error, print_info
from ..core.state import update_phase


def panel_command(task_id: str, panel_prompt_file: str, resume: bool = False) -> None:
    """Launch 3-judge panel for solution review."""

    if not check_cursor_agent():
        print_error("cursor-agent CLI is not installed")
        print_info("Install cursor-agent:")
        print_info("  npm install -g @cursor/cli")
        console.print()
        print_info("After installation, authenticate with:")
        print_info("  cursor-agent login")
        raise typer.Exit(1)

    try:
        prompt_path = resolve_path(panel_prompt_file)
    except FileNotFoundError:
        temp_path = PROJECT_ROOT / ".prompts" / f"temp-panel-{task_id}.md"
        temp_path.parent.mkdir(exist_ok=True)
        temp_path.write_text(panel_prompt_file)
        prompt_path = temp_path

    try:
        asyncio.run(launch_judge_panel(task_id, prompt_path, "panel", resume))
        update_phase(task_id, 4, panel_complete=True)
    except RuntimeError as e:
        print_error(str(e))
        raise typer.Exit(1)
