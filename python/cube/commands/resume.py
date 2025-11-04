"""Resume command."""

import asyncio
from pathlib import Path
import typer

from ..core.agent import check_cursor_agent, run_agent
from ..core.session import load_session
from ..core.output import print_error, print_info, console
from ..core.config import PROJECT_ROOT, MODELS, get_worktree_path, WRITER_LETTERS
from ..automation.stream import parse_and_format_stream

async def resume_async(
    target: str,
    task_id: str,
    message: str,
    session_id: str,
    worktree: Path,
    model: str
) -> None:
    """Resume a session asynchronously."""
    stream = run_agent(
        worktree,
        model,
        message,
        session_id=session_id,
        resume=True
    )
    
    color = "green" if "sonnet" in target else "blue"
    
    parsed_stream = parse_and_format_stream(stream, target, color)
    
    async for formatted, _ in parsed_stream:
        if formatted:
            console.print(formatted)

def resume_command(
    target: str,
    task_id: str,
    message: str
) -> None:
    """Resume a writer or judge session with a message."""
    
    if not check_cursor_agent():
        print_error("cursor-agent CLI is not installed")
        raise typer.Exit(1)
    
    writer_name = None
    writer_letter = None
    model = None
    
    if target in ["writer-sonnet", "sonnet", "a", "A"]:
        writer_name = "sonnet"
        writer_letter = "A"
        model = MODELS["sonnet"]
    elif target in ["writer-codex", "codex", "b", "B"]:
        writer_name = "codex"
        writer_letter = "B"
        model = MODELS["codex"]
    else:
        print_error(f"Invalid target: {target} (must be writer-sonnet or writer-codex)")
        raise typer.Exit(1)
    
    session_id = load_session(f"WRITER_{writer_letter}", task_id)
    
    if not session_id:
        print_error(f"Session ID not found for {target}")
        print_info("Run 'cube-py sessions' to see available sessions")
        raise typer.Exit(1)
    
    project_name = Path(PROJECT_ROOT).name
    worktree = get_worktree_path(project_name, writer_name, task_id)
    
    if not worktree.exists():
        print_error(f"Worktree not found: {worktree}")
        raise typer.Exit(1)
    
    print_info(f"Resuming {target} for task: {task_id}")
    print_info(f"Session ID: {session_id}")
    print_info(f"Message: {message}")
    
    try:
        asyncio.run(resume_async(target, task_id, message, session_id, worktree, model))
    except Exception as e:
        print_error(f"Failed to resume: {e}")
        raise typer.Exit(1)

