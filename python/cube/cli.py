"""Main CLI entry point for cube-py."""

import sys
from typing import Optional

import typer
from typing_extensions import Annotated

from .commands.clean import clean_command
from .commands.decide import decide_command
from .commands.feedback import feedback_command
from .commands.install import install_command
from .commands.logs import logs_command
from .commands.orchestrate import extract_task_id_from_file, orchestrate_auto_command, orchestrate_prompt_command
from .commands.panel import panel_command
from .commands.peer_review import peer_review_command
from .commands.resume import resume_command
from .commands.run import run_command
from .commands.sessions import sessions_command
from .commands.status import status_command
from .commands.ui import ui_command
from .commands.version import version_command
from .commands.writers import writers_command
from .core.output import console, print_success
from .core.phases import format_phase_aliases, resolve_phase_identifier
from .core.updater import auto_update

PHASE_ALIAS_SUMMARY = format_phase_aliases()


def _print_error(e: Exception):
    """Print error message safely, escaping markup and falling back to plain text."""
    msg = str(e)
    try:
        from rich.console import Console
        from rich.markup import escape

        escaped_msg = escape(msg)
        Console(stderr=True).print(f"\n[bold red]❌ Error:[/bold red] {escaped_msg}\n")
    except Exception:
        print(f"\n❌ Error: {msg}\n", file=sys.stderr)


def _parse_resume_option(value: Optional[str]) -> tuple[Optional[int], Optional[str]]:
    """Convert --resume-from input into a phase number and original alias if provided."""
    if value is None:
        return None, None
    try:
        phase = resolve_phase_identifier(value)
        # Return both the phase number and the original alias (normalized)
        normalized = value.strip().lower().replace("_", "-").replace(" ", "-")
        return phase, normalized if not normalized.isdigit() else None
    except ValueError as exc:
        raise typer.BadParameter(str(exc), param_hint="--resume-from") from exc


def _resolve_resume_from(
    task_id: str, resume_flag: bool, resume_from_value: Optional[str]
) -> tuple[int, Optional[str]]:
    """Determine final phase number to resume from. Returns (phase, original_alias)."""
    from .commands.orchestrate.phases_registry import get_max_phase

    parsed_phase, original_alias = _parse_resume_option(resume_from_value)

    if resume_flag and parsed_phase is None:
        from .core.state import load_state

        state = load_state(task_id)
        if state:
            current = state.current_phase
            path = getattr(state, "path", None) or "DUAL"

            max_phase = get_max_phase(path) if path in ("SINGLE", "MERGE", "FEEDBACK", "SYNTHESIS") else 10

            if current >= max_phase:
                if path == "FEEDBACK":
                    parsed_phase = 6
                    console.print(f"[cyan]Auto-resuming from Phase {parsed_phase} (FEEDBACK path loop)[/cyan]")
                else:
                    print_success(f"Task {task_id} complete!")
                    parsed_phase = max_phase
            else:
                parsed_phase = current + 1
                console.print(f"[cyan]Auto-resuming from Phase {parsed_phase}[/cyan]")
        else:
            parsed_phase = 1
    elif parsed_phase is None:
        parsed_phase = 1

    return parsed_phase, original_alias


app = typer.Typer(
    name="cube-py",
    help="Agent Cube CLI - Parallel LLM Coding Workflow Orchestrator",
    add_completion=False,
    pretty_exceptions_show_locals=False,
    pretty_exceptions_short=True,
)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context, version: Annotated[bool, typer.Option("--version", "-v", help="Show version")] = False):
    """Agent Cube CLI - Parallel LLM Coding Workflow Orchestrator."""
    auto_update()

    if version:
        version_command()
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())


@app.command(name="writers")
def writers(
    task_id: Annotated[Optional[str], typer.Argument(help="Task ID (optional if CUBE_TASK_ID set)")] = None,
    prompt_file: Annotated[Optional[str], typer.Argument(help="Prompt file or message (optional if --resume)")] = None,
    resume: Annotated[bool, typer.Option("--resume", help="Resume existing writer sessions")] = False,
):
    """Launch dual writers for a task."""
    from .core.config import resolve_task_id, set_current_task_id

    resolved_task_id = resolve_task_id(task_id)
    if not resolved_task_id:
        from .core.output import print_error

        print_error("No task ID provided and CUBE_TASK_ID not set")
        print_error("Usage: cube writers <task-id> <prompt-file>")
        print_error("   or: export CUBE_TASK_ID=my-task && cube writers <prompt-file>")
        raise typer.Exit(1)

    if not prompt_file and not resume:
        from .core.output import print_error

        print_error("Prompt file/message is required unless using --resume")
        raise typer.Exit(1)

    set_current_task_id(resolved_task_id)

    try:
        writers_command(resolved_task_id, prompt_file or "", resume)
    except Exception as e:
        _print_error(e)
        sys.exit(1)


@app.command(name="panel")
def panel(
    task_id: Annotated[Optional[str], typer.Argument(help="Task ID (optional if CUBE_TASK_ID set)")] = None,
    panel_prompt_file: Annotated[Optional[str], typer.Argument(help="Path to the panel prompt file")] = None,
    resume: Annotated[bool, typer.Option("--resume", help="Resume existing judge sessions")] = False,
):
    """Launch 3-judge panel for solution review."""
    from .core.config import resolve_task_id, set_current_task_id

    resolved_task_id = resolve_task_id(task_id)
    if not resolved_task_id:
        from .core.output import print_error

        print_error("No task ID provided and CUBE_TASK_ID not set")
        raise typer.Exit(1)

    if not panel_prompt_file:
        from .core.output import print_error

        print_error("Panel prompt file is required")
        raise typer.Exit(1)

    set_current_task_id(resolved_task_id)

    try:
        panel_command(resolved_task_id, panel_prompt_file, resume)
    except Exception as e:
        _print_error(e)
        sys.exit(1)


@app.command(name="feedback")
def feedback(
    writer: Annotated[str, typer.Argument(help="Writer to send feedback to (sonnet|codex)")],
    task_id: Annotated[Optional[str], typer.Argument(help="Task ID (optional if CUBE_TASK_ID set)")] = None,
    feedback_file: Annotated[Optional[str], typer.Argument(help="Path to the feedback file")] = None,
):
    """Send feedback to a writer (resumes their session)."""
    from .core.config import resolve_task_id, set_current_task_id

    resolved_task_id = resolve_task_id(task_id)
    if not resolved_task_id:
        from .core.output import print_error

        print_error("No task ID provided and CUBE_TASK_ID not set")
        raise typer.Exit(1)

    if not feedback_file:
        from .core.output import print_error

        print_error("Feedback file is required")
        raise typer.Exit(1)

    set_current_task_id(resolved_task_id)
    feedback_command(writer, resolved_task_id, feedback_file)


@app.command(name="resume")
def resume(
    target: Annotated[str, typer.Argument(help="Target to resume (writer alias or judge key)")],
    task_id: Annotated[Optional[str], typer.Argument(help="Task ID (optional if CUBE_TASK_ID set)")] = None,
    message: Annotated[Optional[str], typer.Argument(help="Message to send (optional, defaults to 'continue')")] = None,
):
    """Resume a writer or judge session with a message."""
    from .core.config import resolve_task_id, set_current_task_id
    from .core.output import print_error, print_warning

    # Detect if task_id looks like a message (user forgot to include task_id)
    if task_id and (" " in task_id or len(task_id) > 50):
        print_error(f"'{task_id[:40]}...' looks like a message, not a task ID")
        print_warning("Usage: cube resume <target> <task-id> [message]")
        print_warning("Example: cube resume writer-a my-task-id 'your message here'")
        print_warning("Or set CUBE_TASK_ID: export CUBE_TASK_ID=my-task-id && cube resume writer-a 'message'")
        raise typer.Exit(1)

    resolved_task_id = resolve_task_id(task_id)
    if not resolved_task_id:
        print_error("No task ID provided and CUBE_TASK_ID not set")
        raise typer.Exit(1)

    set_current_task_id(resolved_task_id)
    resume_command(target, resolved_task_id, message)


@app.command(name="peer-review")
def peer_review(
    task_id_or_prompt: Annotated[Optional[str], typer.Argument(help="Task ID or prompt message")] = None,
    peer_review_prompt_file: Annotated[
        Optional[str], typer.Argument(help="Path to prompt file or prompt message")
    ] = None,
    fresh: Annotated[bool, typer.Option("--fresh", help="Launch new judges instead of resuming")] = False,
    judge: Annotated[Optional[str], typer.Option("--judge", "-j", help="Run only this judge (e.g., judge_4)")] = None,
):
    """Resume judge panel for peer review of winner's implementation."""
    from pathlib import Path

    from .core.config import resolve_task_id, set_current_task_id

    env_task_id = resolve_task_id(None)
    resolved_task_id: str | None = None
    prompt_arg: str | None = None

    if env_task_id:
        resolved_task_id = env_task_id
        prompt_arg = task_id_or_prompt if task_id_or_prompt else peer_review_prompt_file
    elif task_id_or_prompt and peer_review_prompt_file:
        resolved_task_id = task_id_or_prompt
        prompt_arg = peer_review_prompt_file
    elif task_id_or_prompt and (Path(task_id_or_prompt).exists() or " " in task_id_or_prompt):
        resolved_task_id = env_task_id or resolve_task_id(None)
        prompt_arg = task_id_or_prompt
    else:
        resolved_task_id = task_id_or_prompt
        prompt_arg = peer_review_prompt_file

    if not resolved_task_id:
        from .core.output import print_error

        print_error("No task ID provided and CUBE_TASK_ID not set")
        print_error("Usage: cube peer-review <task-id> <prompt-file-or-message>")
        print_error("   or: export CUBE_TASK_ID=my-task && cube peer-review <prompt-file-or-message>")
        raise typer.Exit(1)

    if not prompt_arg:
        from .core.output import print_error

        print_error("Peer review prompt file or message is required")
        raise typer.Exit(1)

    set_current_task_id(resolved_task_id)
    peer_review_command(resolved_task_id, prompt_arg, fresh, judge)


@app.command(name="status")
def status(task_id: Annotated[Optional[str], typer.Argument(help="Task ID (optional if CUBE_TASK_ID set)")] = None):
    """Check workflow status and progress."""
    from .core.config import resolve_task_id

    resolved_task_id = resolve_task_id(task_id)
    status_command(resolved_task_id)


@app.command(name="sessions")
def sessions():
    """List all active sessions."""
    sessions_command()


@app.command(name="orchestrate")
def orchestrate(
    subcommand: Annotated[str, typer.Argument(help="Subcommand (prompt|auto)")],
    task_file: Annotated[str, typer.Argument(help="Path to the task file")],
    copy: Annotated[bool, typer.Option("--copy", help="Copy to clipboard (prompt only)")] = False,
    resume_from: Annotated[
        Optional[str], typer.Option("--resume-from", help=f"Resume from phase number or alias ({PHASE_ALIAS_SUMMARY})")
    ] = None,
    resume: Annotated[bool, typer.Option("--resume", help="Auto-resume from last checkpoint")] = False,
    reset: Annotated[bool, typer.Option("--reset", help="Clear state and start fresh")] = False,
    single: Annotated[bool, typer.Option("--single", help="Run with single writer instead of dual")] = False,
    writer: Annotated[
        Optional[str], typer.Option("--writer", "-w", help="Specific writer for single mode (opus, codex, a, b)")
    ] = None,
):
    """Generate orchestrator prompt or run autonomous orchestration."""
    if subcommand == "prompt":
        orchestrate_prompt_command(task_file, copy)
    elif subcommand == "auto":
        from .core.output import print_error, print_info
        from .core.user_config import get_default_writer, is_single_mode_default, resolve_writer_alias

        task_id = extract_task_id_from_file(task_file)

        if reset:
            from .core.state import clear_state

            clear_state(task_id)
            from .core.output import print_success

            print_success(f"Cleared state for {task_id}")

        # Determine mode (single or dual)
        single_mode = single or writer is not None or is_single_mode_default()
        writer_key = None
        if single_mode:
            try:
                # If --writer is specified, use it. Otherwise, use config default.
                writer_to_resolve = writer if writer else get_default_writer()
                writer_config = resolve_writer_alias(writer_to_resolve)
                writer_key = writer_config.key
                print_info(f"Running in single-writer mode with [bold cyan]{writer_config.name}[/bold cyan]")
            except KeyError as e:
                print_error(str(e))
                raise typer.Exit(1) from e
        else:
            print_info("Running in dual-writer mode")

        resolved_resume_from, resume_alias = _resolve_resume_from(task_id, resume, resume_from)

        try:
            import asyncio

            asyncio.run(
                orchestrate_auto_command(
                    task_file,
                    resolved_resume_from,
                    resume_alias=resume_alias,
                    single_mode=single_mode,
                    writer_key=writer_key,
                )
            )
        except Exception as e:
            from .core.output import console_err

            console_err.print(f"\n[bold red]❌ Error:[/bold red] {e}\n")
            sys.exit(1)
    else:
        typer.echo(f"Unknown subcommand: {subcommand}")
        typer.echo("Usage: cube orchestrate prompt|auto <task-file> [--copy] [--resume] [--resume-from N] [--reset]")
        raise typer.Exit(1)


@app.command(name="install")
def install():
    """Install cube-py CLI to your PATH."""
    install_command()


@app.command(name="version")
def version_cmd():
    """Show version information."""
    version_command()


@app.command(name="run")
def run(
    model: Annotated[str, typer.Argument(help="Model to use (gemini-2.5-pro, sonnet-4.5-thinking, etc.)")],
    prompt: Annotated[str, typer.Argument(help="Prompt text")],
    directory: Annotated[str, typer.Option("--directory", "-d", help="Directory to run in")] = ".",
):
    """Run a single agent with specified model."""
    try:
        run_command(model, prompt, directory)
    except Exception as e:
        _print_error(e)
        sys.exit(1)


@app.command(name="decide")
def decide(
    task_id: Annotated[Optional[str], typer.Argument(help="Task ID (optional if CUBE_TASK_ID set)")] = None,
    panel: Annotated[bool, typer.Option("--panel", help="Check panel decisions")] = False,
    peer: Annotated[bool, typer.Option("--peer", help="Check peer review decisions")] = False,
):
    """Aggregate judge decisions and determine the winner.

    Read decision JSON files from all three judges, aggregate their votes
    using majority rule, and display the result. Auto-detects the latest
    review type unless --panel or --peer is specified.

    Args:
        task_id: The task identifier to find decisions for
        panel: If True, only check initial panel decisions
        peer: If True, only check peer review decisions

    Raises:
        typer.Exit: If no task ID provided or decisions missing
    """
    from .core.config import resolve_task_id, set_current_task_id

    resolved_task_id = resolve_task_id(task_id)
    if not resolved_task_id:
        from .core.output import print_error

        print_error("No task ID provided and CUBE_TASK_ID not set")
        raise typer.Exit(1)

    set_current_task_id(resolved_task_id)

    review_type = "auto"
    if panel:
        review_type = "panel"
    elif peer:
        review_type = "peer-review"

    try:
        decide_command(resolved_task_id, review_type)
    except Exception as e:
        _print_error(e)
        sys.exit(1)


@app.command(name="logs")
def logs(
    task_id: Annotated[Optional[str], typer.Argument(help="Task ID to view logs for")] = None,
    agent: Annotated[Optional[str], typer.Argument(help="Specific agent (writer-a, judge-1, etc.)")] = None,
    tail: Annotated[int, typer.Option("--tail", "-n", help="Number of lines to show")] = 50,
):
    """View agent log files."""
    logs_command(task_id, agent, tail)


@app.command(name="ui")
def ui(port: Annotated[int, typer.Option("--port", help="Port to run UI server on", show_default=True)] = 3030):
    """Launch AgentCube web UI."""
    ui_command(port)


@app.command(name="clean")
def clean(
    task_id: Annotated[Optional[str], typer.Argument(help="Task ID to clean")] = None,
    old: Annotated[bool, typer.Option("--old", help="Clean sessions older than 7 days")] = False,
    all_tasks: Annotated[bool, typer.Option("--all", help="Clean all completed tasks")] = False,
    full: Annotated[bool, typer.Option("--full", help="Full reset: + worktrees, branches, decisions, logs")] = False,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview without deleting")] = False,
):
    """Clean up completed or stale sessions."""
    clean_command(task_id, old, all_tasks, full, dry_run)


@app.command(name="auto")
def auto(
    task_file: Annotated[Optional[str], typer.Argument(help="Path to the task file (optional if --resume)")] = None,
    resume_from: Annotated[
        Optional[str], typer.Option("--resume-from", help=f"Resume from phase number or alias ({PHASE_ALIAS_SUMMARY})")
    ] = None,
    resume: Annotated[bool, typer.Option("--resume", help="Auto-resume from last checkpoint")] = False,
    reset: Annotated[bool, typer.Option("--reset", help="Clear state and start fresh")] = False,
    single: Annotated[bool, typer.Option("--single", help="Run with single writer instead of dual")] = False,
    writer: Annotated[
        Optional[str], typer.Option("--writer", "-w", help="Specific writer for single mode (opus, codex, a, b)")
    ] = None,
):
    """Shortcut for: cube orchestrate auto <task-file>

    If --resume is passed without a task file, resumes the last task from this terminal.
    """
    from .core.config import get_current_task_id, set_current_task_id
    from .core.output import print_error, print_info
    from .core.user_config import get_default_writer, is_single_mode_default, resolve_writer_alias

    # Determine mode (single or dual) - but don't print yet if resuming (saved state may override)
    single_mode = single or writer is not None or is_single_mode_default()
    writer_key = None
    if single_mode:
        try:
            writer_to_resolve = writer if writer else get_default_writer()
            writer_config = resolve_writer_alias(writer_to_resolve)
            writer_key = writer_config.key
            if not resume and not resume_from:
                print_info(f"Running in single-writer mode with [bold cyan]{writer_config.name}[/bold cyan]")
        except KeyError as e:
            print_error(str(e))
            raise typer.Exit(1) from e
    elif not resume and not resume_from:
        print_info("Running in dual-writer mode")

    # If no task file provided, try to get from saved state
    if not task_file:
        if not resume and not resume_from:
            print_error("Task file required. Use --resume to continue last task, or provide a task.md path.")
            raise typer.Exit(1)

        saved_task_id = get_current_task_id()
        if not saved_task_id:
            print_error("No saved task ID. Please provide a task file path.")
            raise typer.Exit(1)

        task_id = saved_task_id
        print_info(f"Resuming task: {task_id}")

        # Try to find the task file
        from pathlib import Path

        possible_paths = [
            Path(f".prompts/{task_id}.md"),
            Path(f".prompts/task-{task_id}.md"),
            Path(f"{task_id}.md"),
        ]
        task_file = next((str(p) for p in possible_paths if p.exists()), None)
        force_skip_phase_1 = False
        if not task_file:
            # No task file found - must resume from phase > 1
            force_skip_phase_1 = not resume_from
            task_file = f".prompts/{task_id}.md"
    else:
        # Extract task_id from filename (works even if file doesn't exist)
        task_id = extract_task_id_from_file(task_file)

        # Only require file to exist if not resuming from later phase
        from pathlib import Path

        task_path = Path(task_file)
        if task_path.exists():
            force_skip_phase_1 = False
        elif resume or resume_from:
            # Resuming - file not needed, just the task_id
            force_skip_phase_1 = True
        else:
            # Not resuming and file doesn't exist - error
            print_error(f"Task file not found: {task_file}")
            raise typer.Exit(1)

    set_current_task_id(task_id)

    if reset:
        from .core.state import clear_state

        clear_state(task_id)
        from .core.output import print_success

        print_success(f"Cleared state for {task_id}")

    resolved_resume_from, resume_alias = _resolve_resume_from(task_id, resume, resume_from)
    if force_skip_phase_1 and resolved_resume_from < 2:
        resolved_resume_from = 2  # Skip Phase 1 which requires task file

    try:
        import asyncio

        asyncio.run(
            orchestrate_auto_command(
                task_file,
                resolved_resume_from,
                task_id=task_id,
                resume_alias=resume_alias,
                single_mode=single_mode,
                writer_key=writer_key,
            )
        )
    except Exception as e:
        _print_error(e)
        sys.exit(1)


@app.command(name="continue")
def continue_task(
    task_id: Annotated[Optional[str], typer.Argument(help="Task ID (optional if CUBE_TASK_ID set)")] = None,
):
    """Continue autonomous workflow from where it left off."""
    from .core.config import resolve_task_id, set_current_task_id
    from .core.output import print_error
    from .core.state import load_state

    resolved_task_id = resolve_task_id(task_id)
    if not resolved_task_id:
        print_error("No task ID provided and CUBE_TASK_ID not set")
        raise typer.Exit(1)

    set_current_task_id(resolved_task_id)

    state = load_state(resolved_task_id)
    if not state:
        print_error(f"No state found for {resolved_task_id}")
        console.print("Start with: cube auto <task-file>")
        raise typer.Exit(1)

    next_phase = state.current_phase + 1 if state.current_phase < 10 else state.current_phase

    console.print(f"[cyan]Continuing {resolved_task_id} from Phase {next_phase}[/cyan]")
    console.print()

    try:
        import asyncio

        asyncio.run(orchestrate_auto_command(f"**/{resolved_task_id}.md", next_phase))
    except Exception as e:
        _print_error(e)
        sys.exit(1)


if __name__ == "__main__":
    app()
