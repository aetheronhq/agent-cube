"""Feedback command."""

import asyncio
from pathlib import Path
import typer

from ..core.agent import check_cursor_agent, run_agent
from ..core.session import load_session
from ..core.output import print_error, print_info, console
from ..core.config import PROJECT_ROOT, MODELS, get_worktree_path, WRITER_LETTERS
from ..automation.stream import parse_and_format_stream

async def send_feedback_async(
    writer: str,
    task_id: str,
    feedback_file: Path,
    session_id: str,
    worktree: Path
) -> None:
    """Send feedback to a writer asynchronously."""
    feedback_message = feedback_file.read_text()
    model = MODELS[writer]
    
    stream = run_agent(
        worktree,
        model,
        feedback_message,
        session_id=session_id,
        resume=True
    )
    
    writer_label = f"Writer {WRITER_LETTERS[writer]}"
    color = "green" if writer == "sonnet" else "blue"
    
    parsed_stream = parse_and_format_stream(stream, writer_label, color)
    
    async for formatted, _ in parsed_stream:
        if formatted:
            console.print(formatted)

def feedback_command(
    writer: str,
    task_id: str,
    feedback_file: str
) -> None:
    """Send feedback to a writer (resumes their session)."""
    
    if writer not in ["sonnet", "codex"]:
        print_error(f"Invalid writer: {writer} (must be 'sonnet' or 'codex')")
        raise typer.Exit(1)
    
    if not check_cursor_agent():
        print_error("cursor-agent CLI is not installed")
        raise typer.Exit(1)
    
    feedback_path = PROJECT_ROOT / feedback_file
    if not feedback_path.exists():
        print_error(f"Feedback file not found: {feedback_file}")
        raise typer.Exit(1)
    
    writer_letter = WRITER_LETTERS[writer]
    session_id = load_session(f"WRITER_{writer_letter}", task_id)
    
    if not session_id:
        print_error(f"Session ID not found for writer-{writer}")
        print_info("Run 'cube-py sessions' to see available sessions")
        raise typer.Exit(1)
    
    project_name = Path(PROJECT_ROOT).name
    worktree = get_worktree_path(project_name, writer, task_id)
    
    if not worktree.exists():
        print_error(f"Worktree not found: {worktree}")
        raise typer.Exit(1)
    
    print_info(f"Sending feedback to writer-{writer} for task: {task_id}")
    print_info(f"Session ID: {session_id}")
    print_info(f"Feedback file: {feedback_file}")
    
    try:
        asyncio.run(send_feedback_async(writer, task_id, feedback_path, session_id, worktree))
    except Exception as e:
        print_error(f"Failed to send feedback: {e}")
        raise typer.Exit(1)

