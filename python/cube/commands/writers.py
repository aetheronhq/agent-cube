"""Writers command."""

import asyncio
from pathlib import Path
import typer

from ..core.agent import check_cursor_agent
from ..core.output import print_error, print_info
from ..core.config import PROJECT_ROOT
from ..automation.dual_writers import launch_dual_writers

def writers_command(
    task_id: str,
    prompt_file: str,
    resume: bool = False
) -> None:
    """Launch dual writers for a task."""
    
    if not check_cursor_agent():
        print_error("cursor-agent CLI is not installed")
        print()
        print("Install cursor-agent:")
        print("  npm install -g @cursor/cli")
        print()
        print("Or add to your PATH if already installed:")
        print('  export PATH="$HOME/.local/bin:$PATH"')
        print()
        print("After installation, authenticate with:")
        print("  cursor-agent login")
        print()
        raise typer.Exit(1)
    
    prompt_path = PROJECT_ROOT / prompt_file
    
    if not prompt_path.exists():
        print_error(f"Prompt file not found: {prompt_file}")
        raise typer.Exit(1)
    
    try:
        asyncio.run(launch_dual_writers(task_id, prompt_path, resume))
    except Exception as e:
        print_error(f"Failed to launch writers: {e}")
        raise typer.Exit(1)

