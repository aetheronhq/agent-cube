"""Writers command."""

import asyncio
from pathlib import Path
import typer

from ..core.agent import check_cursor_agent
from ..core.output import print_error, print_info, console
from ..core.config import PROJECT_ROOT, resolve_path
from ..automation.dual_writers import launch_dual_writers
from ..core.state import update_phase

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
        if not prompt_file_or_message:
            prompt_file_or_message = "Resume from where you left off. Complete any remaining tasks and push your changes."
        
        prompt_path = PROJECT_ROOT / ".prompts" / f"resume-message-{task_id}.md"
        prompt_path.parent.mkdir(exist_ok=True)
        prompt_path.write_text(prompt_file_or_message)
        
        console.print("[yellow]Resuming both writers with message...[/yellow]")
        console.print()
        
        try:
            asyncio.run(launch_dual_writers(task_id, prompt_path, resume_mode=True))
            update_phase(task_id, 2, writers_complete=True)
        except RuntimeError as e:
            print_error(str(e))
            raise typer.Exit(1)
    else:
        try:
            prompt_path = resolve_path(prompt_file_or_message)
        except FileNotFoundError as e:
            print_error(str(e))
            raise typer.Exit(1)
        
        try:
            asyncio.run(launch_dual_writers(task_id, prompt_path, resume_mode=False))
            update_phase(task_id, 2, writers_complete=True)
        except RuntimeError as e:
            print_error(str(e))
            raise typer.Exit(1)

