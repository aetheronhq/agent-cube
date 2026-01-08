"""Feedback command."""

import asyncio
from pathlib import Path

import typer

from ..core.agent import check_cursor_agent, run_agent
from ..core.config import PROJECT_ROOT, get_worktree_path, resolve_path
from ..core.output import console, print_error, print_info
from ..core.session import load_session
from ..core.user_config import get_writer_aliases, resolve_writer_alias


async def send_feedback_async(
    task_id: str,
    feedback_file: Path,
    session_id: str,
    worktree: Path,
    writer_name: str,
    writer_model: str,
    writer_label: str,
    writer_key: str,
    writer_color: str = "green",
) -> None:
    """Send feedback to a writer asynchronously."""
    from ..automation.stream import format_stream_message
    from ..core.agent_logger import agent_logging_context
    from ..core.parsers.registry import get_parser
    from ..core.single_layout import SingleAgentLayout
    from ..core.user_config import load_config

    if not worktree.exists():
        raise RuntimeError(f"Worktree not found: {worktree}")

    config = load_config()
    cli_name = config.cli_tools.get(writer_model, "cursor-agent")
    parser = get_parser(cli_name)

    feedback_message = feedback_file.read_text()

    stream = run_agent(worktree, writer_model, feedback_message, session_id=session_id, resume=True)

    layout = SingleAgentLayout
    layout.initialize(writer_label)
    layout.start()

    async with agent_logging_context(
        agent_type="feedback",
        agent_name=writer_name,
        task_id=task_id,
        session_key=writer_key.upper(),
        session_task_key=task_id,
        metadata=f"Feedback {writer_label} ({writer_model}) - {task_id}",
    ) as logger:
        async for line in stream:
            logger.write_line(line)  # Log every line

            msg = parser.parse(line)
            if msg:
                formatted = format_stream_message(msg, writer_label, writer_color)
                if formatted:
                    if formatted.startswith("[thinking]"):
                        thinking_text = formatted.replace("[thinking]", "").replace("[/thinking]", "")
                        layout.add_thinking(thinking_text)
                    elif msg.type == "assistant" and msg.content:
                        layout.add_assistant_message(msg.content, writer_label, writer_color)
                    else:
                        layout.add_output(formatted)

    layout.close()


def feedback_command(writer: str, task_id: str, feedback_file: str) -> None:
    """Send feedback to a writer (resumes their session)."""
    from ..core.config import WORKTREE_BASE
    from ..core.writer_metadata import load_writer_metadata

    # Try to resolve from config first
    wconfig = None
    wconfig = None
    try:
        wconfig = resolve_writer_alias(writer)
        writer_name = wconfig.name
        writer_model = wconfig.model
        writer_label = wconfig.label
        writer_key = wconfig.key.upper()
        writer_color = wconfig.color
    except KeyError:
        # Try metadata fallback for orphaned writers
        metadata = load_writer_metadata(writer.lower(), task_id)
        if metadata:
            writer_name = metadata.name
            writer_model = metadata.model
            writer_label = metadata.label
            writer_key = metadata.key.upper()
            writer_color = metadata.color
        else:
            print_error(f"Invalid writer: {writer} (choices: {', '.join(get_writer_aliases())})")
            print_info(f"Not in config and no metadata at .prompts/writers/{writer.lower()}-{task_id}.json")
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

    session_id = load_session(writer_key, task_id)

    if not session_id:
        print_error(f"Session ID not found for {writer_label}")
        print_info("Run 'cube sessions' to see available sessions")
        raise typer.Exit(1)

    project_name = Path(PROJECT_ROOT).name
    if wconfig:
        worktree = get_worktree_path(project_name, writer_name, task_id)
    else:
        worktree = WORKTREE_BASE / project_name / f"writer-{writer.lower()}-{task_id}"

    if not worktree.exists():
        print_error(f"Worktree not found: {worktree}")
        raise typer.Exit(1)

    print_info(f"Sending feedback to {writer_label} for task: {task_id}")
    console.print()
    console.print("[yellow]📋 Resuming session:[/yellow]")
    console.print(f"  Session ID: [cyan]{session_id}[/cyan]")
    console.print(f"  Feedback: {feedback_file}")
    console.print()

    try:
        asyncio.run(
            send_feedback_async(
                task_id=task_id,
                feedback_file=feedback_path,
                session_id=session_id,
                worktree=worktree,
                writer_name=writer_name,
                writer_model=writer_model,
                writer_label=writer_label,
                writer_key=writer_key,
                writer_color=writer_color,
            )
        )
    except RuntimeError as e:
        print_error(str(e))
        raise typer.Exit(1)


# Backwards compatibility
feedback = feedback_command
