"""Single writer execution."""

from datetime import datetime
from pathlib import Path

from ..automation.stream import format_stream_message
from ..core.agent import run_agent
from ..core.agent_logger import agent_logging_context
from ..core.git import commit_and_push, create_worktree, has_uncommitted_changes, has_unpushed_commits, push_only
from ..core.output import console, print_error, print_info, print_success, print_warning
from ..core.parsers.registry import get_parser
from ..core.session import load_session, save_session
from ..core.single_layout import SingleAgentLayout
from ..core.user_config import get_writer_config
from ..models.types import WriterInfo


class InterruptFollowUp(Exception):
    """Raised when user provides follow-up after Ctrl+C interrupt."""

    def __init__(self, message: str, writer_info: WriterInfo):
        self.message = message
        self.writer_info = writer_info
        super().__init__(message)


async def run_single_writer(writer_info: WriterInfo, prompt: str, resume: bool) -> bool:
    """Run a single writer agent.

    Returns True if completed normally, False if interrupted and user wants to exit.
    Raises InterruptFollowUp if user provided follow-up text.
    """
    from ..core.user_config import load_config as load_user_config

    config = load_user_config()
    cli_name = config.cli_tools.get(writer_info.model, "cursor-agent")
    parser = get_parser(cli_name)

    layout = SingleAgentLayout
    layout.initialize(writer_info.label)
    layout.start()

    session_id = writer_info.session_id if resume else None

    stream = run_agent(writer_info.worktree, writer_info.model, prompt, session_id=session_id, resume=resume)

    final_line_count = 0

    try:
        async with agent_logging_context(
            agent_type="writer",
            agent_name=writer_info.name,
            task_id=writer_info.task_id,
            session_key=writer_info.key.upper(),
            session_task_key=writer_info.task_id,
            metadata=f"{writer_info.label} ({writer_info.model}) - {writer_info.task_id} - {datetime.now()}",
        ) as logger:
            async for line in stream:
                logger.write_line(line)

                msg = parser.parse(line)
                if msg:
                    if msg.type == "system" and msg.subtype == "init":
                        msg.resumed = resume
                    if msg.session_id and not writer_info.session_id:
                        writer_info.session_id = msg.session_id
                        save_session(
                            writer_info.key.upper(),
                            writer_info.task_id,
                            msg.session_id,
                            f"Writer {writer_info.name} ({writer_info.model})",
                        )

                    formatted = format_stream_message(msg, writer_info.label, writer_info.color)
                    if formatted:
                        if formatted.startswith("[thinking]"):
                            thinking_text = formatted.replace("[thinking]", "").replace("[/thinking]", "")
                            layout.update_thinking(thinking_text)
                        elif msg.type == "assistant" and msg.content:
                            layout.add_assistant_message(msg.content, writer_info.label, writer_info.color)
                        else:
                            layout.add_output(formatted)

            if logger.line_count < 10:
                raise RuntimeError(
                    f"{writer_info.label} completed suspiciously quickly ({logger.line_count} lines). Check {logger.log_file} for errors."
                )

            final_line_count = logger.line_count

    except KeyboardInterrupt:
        layout.close()
        console.print()
        console.print(f"[yellow]⏸️  {writer_info.label} interrupted[/yellow]")

        # Session should already be saved from the stream
        if writer_info.session_id:
            console.print(f"[dim]Session saved: {writer_info.session_id}[/dim]")

        console.print()
        console.print("[cyan]Enter follow-up message (or press Enter to exit):[/cyan]")

        try:
            follow_up = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            follow_up = ""

        if follow_up:
            raise InterruptFollowUp(follow_up, writer_info)
        else:
            console.print("[yellow]Exiting. Resume later with:[/yellow]")
            console.print("  cube auto <task> --resume-from 2")
            return False

    # Calculate status and mark complete
    status = f"{final_line_count} events"

    try:
        import subprocess

        result = subprocess.run(
            ["git", "diff", "--stat", "HEAD"], cwd=writer_info.worktree, capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout:
            lines = result.stdout.strip().split("\n")
            if lines:
                files_changed = len([line for line in lines if "|" in line])
                if files_changed > 0:
                    status = f"{files_changed} file{'s' if files_changed != 1 else ''} changed"
    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
        pass

    layout.mark_complete(status)
    return True


async def launch_single_writer(
    task_id: str,
    prompt_file: Path,
    writer_key: str | None = None,
    resume_mode: bool = False,
    resume_prompt: str | None = None,
) -> None:
    """Launch a single writer for a task.

    Args:
        resume_prompt: If provided when resume_mode=True, use this as the prompt instead of the file.
    """

    if not prompt_file.exists() and not resume_mode:
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")

    if not writer_key:
        from ..core.user_config import get_default_writer

        writer_key = get_default_writer()

    wconfig = get_writer_config(writer_key)

    layout = SingleAgentLayout
    layout.initialize(f"Writer: {wconfig.label}")

    from ..core.writer_metadata import WriterMetadata, save_writer_metadata

    # Use resume_prompt if provided when resuming, otherwise read from file
    if resume_mode and resume_prompt:
        prompt = resume_prompt
        print_info(f"Resuming with additional context: {resume_prompt[:50]}...")
    else:
        prompt = prompt_file.read_text()

    worktree = create_worktree(task_id, wconfig.name)
    branch = f"writer-{wconfig.name}/{task_id}"

    save_writer_metadata(
        wconfig.name,
        task_id,
        WriterMetadata(
            name=wconfig.name, model=wconfig.model, label=wconfig.label, color=wconfig.color, key=wconfig.key
        ),
    )

    session_id = None
    if resume_mode:
        session_id = load_session(wconfig.key.upper(), task_id)
        if not session_id:
            raise RuntimeError(f"No session found for writer {wconfig.name}")

    writer_info = WriterInfo(
        key=wconfig.key,
        name=wconfig.name,
        model=wconfig.model,
        color=wconfig.color,
        label=wconfig.label,
        task_id=task_id,
        worktree=worktree,
        branch=branch,
        session_id=session_id,
    )

    if resume_mode:
        print_info(f"Resuming Single Writer for Task: {task_id}")
        console.print(f"  [{writer_info.color}]{writer_info.label}[/{writer_info.color}]: {writer_info.session_id}")
    else:
        print_info(f"Launching Single Writer for Task: {task_id}")

    print_info(f"Prompt: {prompt_file}")

    from ..core.user_config import load_config

    config = load_config()
    cli_name = config.cli_tools.get(writer_info.model, "cursor-agent")
    status = "↩️ Resuming" if resume_mode else "✨ New"
    console.print(f"[dim]{status} {writer_info.label}: {writer_info.model} (CLI: {cli_name})...")

    current_prompt = prompt
    is_resuming = resume_mode

    while True:
        try:
            completed = await run_single_writer(writer_info, current_prompt, is_resuming)
            if completed:
                print_success("Writer completed successfully")
            break
        except InterruptFollowUp as interrupt:
            # User provided follow-up, resume with it
            console.print()
            console.print(f"[cyan]↩️  Resuming {writer_info.label} with follow-up...[/cyan]")
            console.print()
            current_prompt = interrupt.message
            is_resuming = True
            # Re-initialize layout for the resume
            layout.initialize(f"Writer: {wconfig.label}")
            continue
        except Exception as e:
            print_error(f"Writer {writer_info.label} failed: {e}")
            raise

    layout.close()

    console.print()

    console.print("📤 Ensuring all changes are committed and pushed...")

    if has_uncommitted_changes(writer_info.worktree):
        print_info(f"{writer_info.label}: Committing uncommitted changes...")
        message = f"{writer_info.label} ({writer_info.model}) - Task: {task_id}\n\nAuto-commit of remaining changes at end of session."
        if commit_and_push(writer_info.worktree, writer_info.branch, message):
            print_success(f"{writer_info.label}: Changes committed and pushed")
        else:
            print_warning(f"{writer_info.label}: Failed to commit/push")
    else:
        print_success(f"{writer_info.label}: All changes already committed")

        if has_unpushed_commits(writer_info.worktree, writer_info.branch):
            print_info(f"{writer_info.label}: Pushing unpushed commits...")
            if push_only(writer_info.worktree, writer_info.branch):
                print_success(f"{writer_info.label}: Pushed to origin")
            else:
                print_warning(f"{writer_info.label}: Failed to push")

    console.print()
    print_success("All changes committed and pushed!")
    console.print()
    console.print("Next step: Peer Review")
