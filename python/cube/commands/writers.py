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
        from .resume import resume_async
        from ..core.session import load_session
        from ..core.config import get_worktree_path, WORKTREE_BASE
        from pathlib import Path
        
        console.print("[yellow]Resuming both writers with message...[/yellow]")
        console.print()
        
        async def resume_both():
            project_name = Path(PROJECT_ROOT).name
            
            session_a = load_session("WRITER_A", task_id)
            session_b = load_session("WRITER_B", task_id)
            
            worktree_a = WORKTREE_BASE / project_name / f"writer-sonnet-{task_id}"
            worktree_b = WORKTREE_BASE / project_name / f"writer-codex-{task_id}"
            
            await asyncio.gather(
                resume_async("writer-sonnet", task_id, prompt_file_or_message, session_a, worktree_a, "sonnet-4.5-thinking"),
                resume_async("writer-codex", task_id, prompt_file_or_message, session_b, worktree_b, "gpt-5-codex-high")
            )
        
        asyncio.run(resume_both())
    else:
        prompt_path = PROJECT_ROOT / prompt_file_or_message
        
        if not prompt_path.exists():
            print_error(f"Prompt file not found: {prompt_file_or_message}")
            raise typer.Exit(1)
        
        asyncio.run(launch_dual_writers(task_id, prompt_path, resume_mode=False))

