"""Feedback command."""

import asyncio
from pathlib import Path
import typer

from ..core.agent import check_cursor_agent, run_agent
from ..core.session import load_session
from ..core.output import print_error, print_info, console
from ..core.config import PROJECT_ROOT, get_worktree_path, resolve_path
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
    from ..core.agent_logger import agent_logging_context
    
    if not worktree.exists():
        raise RuntimeError(f"Worktree not found: {worktree}")
    
    wconfig = resolve_writer_alias(writer)
    
    config = load_config()
    cli_name = config.cli_tools.get(wconfig.model, "cursor-agent")
    parser = get_parser(cli_name)
    
    feedback_message = feedback_file.read_text()
    
    stream = run_agent(
        worktree,
        wconfig.model,
        feedback_message,
        session_id=session_id,
        resume=True
    )
    
    layout = SingleAgentLayout(title=wconfig.label)
    layout.start()
    
    async with agent_logging_context(
        agent_type="feedback",
        agent_name=wconfig.name,
        task_id=task_id,
        session_key=wconfig.key.upper(),
        session_task_key=task_id,
        metadata=f"Feedback {wconfig.label} ({wconfig.model}) - {task_id}"
    ) as logger:
        async for line in stream:
            logger.write_line(line)  # Log every line
            
            msg = parser.parse(line)
            if msg:
                formatted = format_stream_message(msg, wconfig.label, wconfig.color)
                if formatted:
                    if formatted.startswith("[thinking]"):
                        thinking_text = formatted.replace("[thinking]", "").replace("[/thinking]", "")
                        layout.add_thinking(thinking_text)
                    elif msg.type == "assistant" and msg.content:
                        layout.add_assistant_message("agent", msg.content, wconfig.label, wconfig.color)
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
    
    session_id = load_session(wconfig.key.upper(), task_id)
    
    if not session_id:
        print_error(f"Session ID not found for {wconfig.label}")
        print_info("Run 'cube-py sessions' to see available sessions")
        raise typer.Exit(1)
    
    project_name = Path(PROJECT_ROOT).name
    worktree = get_worktree_path(project_name, wconfig.name, task_id)
    
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
        asyncio.run(send_feedback_async(wconfig.name, task_id, feedback_path, session_id, worktree))
    except RuntimeError as e:
        print_error(str(e))
        raise typer.Exit(1)

# Backwards compatibility
feedback = feedback_command

