"""Feedback command."""

import asyncio
from pathlib import Path
import typer

from ..core.agent import check_cursor_agent, run_agent
from ..core.session import load_session
from ..core.output import print_error, print_info, console
from ..core.config import PROJECT_ROOT, get_worktree_path, WRITER_LETTERS, resolve_path
from ..core.user_config import resolve_writer_alias, get_writer_aliases
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
    
    if not worktree.exists():
        raise RuntimeError(f"Worktree not found: {worktree}")
    
    wconfig = resolve_writer_alias(writer)
    writer_slug = wconfig.name
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
    
    writer_label = wconfig.label
    color = wconfig.color
    
    layout = SingleAgentLayout(title=writer_label)
    layout.start()
    
    async for line in stream:
        msg = parser.parse(line)
        if msg:
            formatted = format_stream_message(msg, writer_label, color)
            if formatted:
                if formatted.startswith("[thinking]"):
                    thinking_text = formatted.replace("[thinking]", "").replace("[/thinking]", "")
                    layout.add_thinking(thinking_text)
                else:
                    layout.add_output(formatted)
    
    layout.close()

def feedback_command(
    writer: str,
    task_id: str,
    feedback_file: str
) -> None:
    """Send feedback to a writer (resumes their session)."""
    
    try:
        wconfig = resolve_writer_alias(writer)
    except KeyError:
        print_error(f"Invalid writer: {writer} (choices: {', '.join(get_writer_aliases())})")
        raise typer.Exit(1)
    
    writer_slug = wconfig.name
    
    if not check_cursor_agent():
        print_error("cursor-agent CLI is not installed")
        raise typer.Exit(1)
    
    try:
        feedback_path = resolve_path(feedback_file)
    except FileNotFoundError:
        temp_path = PROJECT_ROOT / ".prompts" / f"temp-feedback-{task_id}.md"
        temp_path.parent.mkdir(exist_ok=True)
        temp_path.write_text(feedback_file)
        feedback_path = temp_path
    
    writer_letter = WRITER_LETTERS[writer_slug]
    session_id = load_session(f"WRITER_{writer_letter}", task_id)
    
    if not session_id:
        print_error(f"Session ID not found for writer-{writer}")
        print_info("Run 'cube-py sessions' to see available sessions")
        raise typer.Exit(1)
    
    project_name = Path(PROJECT_ROOT).name
    worktree = get_worktree_path(project_name, writer_slug, task_id)
    
    if not worktree.exists():
        print_error(f"Worktree not found: {worktree}")
        raise typer.Exit(1)
    
    print_info(f"Sending feedback to {wconfig.label} for task: {task_id}")
    console.print()
    console.print("[yellow]📋 Resuming session:[/yellow]")
    console.print(f"  Session ID: [cyan]{session_id}[/cyan]")
    console.print(f"  Feedback: {feedback_file}")
    console.print()
    
    try:
    asyncio.run(send_feedback_async(writer_slug, task_id, feedback_path, session_id, worktree))
    except RuntimeError as e:
        print_error(str(e))
        raise typer.Exit(1)

