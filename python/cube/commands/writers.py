"""Writers command."""

import asyncio
from pathlib import Path
import typer

from ..core.agent import check_cursor_agent
from ..core.output import print_error, print_info, console
from ..core.config import PROJECT_ROOT
from ..automation.dual_writers import launch_dual_writers

def writers_command(
    task_id: str,
    prompt_file_or_message: str,
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
    
    if resume:
        from .resume import resume_command
        console.print("[yellow]Resuming both writers with message...[/yellow]")
        console.print()
        resume_command("writer-a", task_id, prompt_file_or_message)
        console.print()
        resume_command("writer-b", task_id, prompt_file_or_message)
    else:
        prompt_path = PROJECT_ROOT / prompt_file_or_message
        
        if not prompt_path.exists():
            print_error(f"Prompt file not found: {prompt_file_or_message}")
            raise typer.Exit(1)
        
        asyncio.run(launch_dual_writers(task_id, prompt_path, resume_mode=False))

