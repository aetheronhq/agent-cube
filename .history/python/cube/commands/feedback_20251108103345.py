"""Feedback command."""

import asyncio
from pathlib import Path
import typer

from ..core.agent import check_cursor_agent, run_agent
from ..core.session import load_session
from ..core.output import print_error, print_info, console
from ..core.config import PROJECT_ROOT, MODELS, get_worktree_path, WRITER_LETTERS
async def send_feedback_async(
    writer: str,
    task_id: str,
    feedback_file: Path,
    session_id: str,
    worktree: Path
) -> None:
    """Send feedback to a writer asynchronously."""
    from ..automation.stream import format_stream_message
    from ..core.user_config import load_config, get_writer_config
    from ..core.parsers.registry import get_parser
    from ..core.single_layout import SingleAgentLayout
    
    wconfig = get_writer_config(f"writer_{'a' if writer == 'sonnet' else 'b'}")
    model = wconfig.model
    
    config = load_config()
    cli_name = config.cli_tools.get(model, "cursor-agent")
    parser = get_parser(cli_name)
    
    feedback_message = feedback_file.read_text()
    
    stream = run_agent(
        worktree,
        model,
        feedback_message,
        session_id=session_id,
        resume=True
    )
    
    writer_label = f"Writer {WRITER_LETTERS[writer]}"
    color = "green" if writer == "sonnet" else "blue"
    
    async for line in stream:
        msg = parser.parse(line)
        if msg:
            formatted = format_stream_message(msg, writer_label, color)
            if formatted and not formatted.startswith("[thinking]"):
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
    console.print()
    console.print("[yellow]📋 Resuming session:[/yellow]")
    console.print(f"  Session ID: [cyan]{session_id}[/cyan]")
    console.print(f"  Feedback: {feedback_file}")
    console.print()
    
    asyncio.run(send_feedback_async(writer, task_id, feedback_path, session_id, worktree))

