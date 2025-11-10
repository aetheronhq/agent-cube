"""Main CLI entry point for cube-py."""

import typer
from typing_extensions import Annotated
from typing import Optional
import sys

from .core.updater import auto_update
from .core.config import VERSION
from .commands.version import version_command
from .commands.status import status_command
from .commands.sessions import sessions_command
from .commands.install import install_command
from .commands.writers import writers_command
from .commands.panel import panel_command
from .commands.feedback import feedback_command
from .commands.resume import resume_command
from .commands.peer_review import peer_review_command
from .commands.orchestrate import orchestrate_prompt_command, orchestrate_auto_command
from .commands.run import run_command
from .commands.decide import decide_command
from .commands.logs import logs_command

app = typer.Typer(
    name="cube-py",
    help="Agent Cube CLI - Parallel LLM Coding Workflow Orchestrator",
    add_completion=False
)

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Annotated[bool, typer.Option("--version", "-v", help="Show version")] = False
):
    """Agent Cube CLI - Parallel LLM Coding Workflow Orchestrator."""
    auto_update()
    
    if version:
        version_command()
        raise typer.Exit()
    
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())

@app.command(name="writers")
def writers(
    task_id: Annotated[str, typer.Argument(help="Task ID for the writers")],
    prompt_file: Annotated[Optional[str], typer.Argument(help="Prompt file or message (optional if --resume)")] = None,
    resume: Annotated[bool, typer.Option("--resume", help="Resume existing writer sessions")] = False
):
    """Launch dual writers for a task."""
    if not prompt_file and not resume:
        from .core.output import print_error
        print_error("Prompt file/message is required unless using --resume")
        raise typer.Exit(1)
    
    try:
        writers_command(task_id, prompt_file or "", resume)
    except Exception as e:
        from .core.output import console_err
        console_err.print(f"\n[bold red]❌ Error:[/bold red] {e}\n")
        sys.exit(1)

@app.command(name="panel")
def panel(
    task_id: Annotated[str, typer.Argument(help="Task ID for the panel")],
    panel_prompt_file: Annotated[str, typer.Argument(help="Path to the panel prompt file")],
    resume: Annotated[bool, typer.Option("--resume", help="Resume existing judge sessions")] = False
):
    """Launch 3-judge panel for solution review."""
    try:
        panel_command(task_id, panel_prompt_file, resume)
    except Exception as e:
        from .core.output import console_err
        console_err.print(f"\n[bold red]❌ Error:[/bold red] {e}\n")
        sys.exit(1)

@app.command(name="feedback")
def feedback(
    writer: Annotated[str, typer.Argument(help="Writer to send feedback to (sonnet|codex)")],
    task_id: Annotated[str, typer.Argument(help="Task ID")],
    feedback_file: Annotated[str, typer.Argument(help="Path to the feedback file")]
):
    """Send feedback to a writer (resumes their session)."""
    feedback_command(writer, task_id, feedback_file)

@app.command(name="resume")
def resume(
    target: Annotated[str, typer.Argument(help="Target to resume (writer-sonnet|writer-codex)")],
    task_id: Annotated[str, typer.Argument(help="Task ID")],
    message: Annotated[Optional[str], typer.Argument(help="Message to send (optional, defaults to 'continue')")] = None
):
    """Resume a writer or judge session with a message."""
    resume_command(target, task_id, message)

@app.command(name="peer-review")
def peer_review(
    task_id: Annotated[str, typer.Argument(help="Task ID")],
    peer_review_prompt_file: Annotated[str, typer.Argument(help="Path to the peer review prompt file")],
    fresh: Annotated[bool, typer.Option("--fresh", help="Launch new judges instead of resuming")] = False
):
    """Resume original 3 judges from initial panel for peer review."""
    peer_review_command(task_id, peer_review_prompt_file, fresh)

@app.command(name="status")
def status(
    task_id: Annotated[str, typer.Argument(help="Task ID to check status for")]
):
    """Show task status (branches, sessions, worktrees)."""
    status_command(task_id)

@app.command(name="sessions")
def sessions():
    """List all active sessions."""
    sessions_command()

@app.command(name="orchestrate")
def orchestrate(
    subcommand: Annotated[str, typer.Argument(help="Subcommand (prompt|auto)")],
    task_file: Annotated[str, typer.Argument(help="Path to the task file")],
    copy: Annotated[bool, typer.Option("--copy", help="Copy to clipboard (prompt only)")] = False,
    resume_from: Annotated[int, typer.Option("--resume-from", help="Resume from phase number (1-10)")] = 1
):
    """Generate orchestrator prompt or run autonomous orchestration."""
    if subcommand == "prompt":
        orchestrate_prompt_command(task_file, copy)
    elif subcommand == "auto":
        try:
            import asyncio
            asyncio.run(orchestrate_auto_command(task_file, resume_from))
        except Exception as e:
            from .core.output import console_err
            console_err.print(f"\n[bold red]❌ Error:[/bold red] {e}\n")
            sys.exit(1)
    else:
        typer.echo(f"Unknown subcommand: {subcommand}")
        typer.echo("Usage: cube orchestrate prompt|auto <task-file> [--copy] [--resume-from N]")
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
    directory: Annotated[str, typer.Option("--directory", "-d", help="Directory to run in")] = "."
):
    """Run a single agent with specified model."""
    try:
        run_command(model, prompt, directory)
    except Exception as e:
        from .core.output import console_err
        console_err.print(f"\n[bold red]❌ Error:[/bold red] {e}\n")
        sys.exit(1)

@app.command(name="decide")
def decide(
    task_id: Annotated[str, typer.Argument(help="Task ID to aggregate decisions for")]
):
    """Aggregate judge decisions and determine next action."""
    try:
        decide_command(task_id)
    except Exception as e:
        from .core.output import console_err
        console_err.print(f"\n[bold red]❌ Error:[/bold red] {e}\n")
        sys.exit(1)

@app.command(name="logs")
def logs(
    task_id: Annotated[Optional[str], typer.Argument(help="Task ID to view logs for")] = None,
    agent: Annotated[Optional[str], typer.Argument(help="Specific agent (writer-a, judge-1, etc.)")] = None,
    tail: Annotated[int, typer.Option("--tail", "-n", help="Number of lines to show")] = 50
):
    """View agent log files."""
    logs_command(task_id, agent, tail)

if __name__ == "__main__":
    app()

