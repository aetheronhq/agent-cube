"""Main workflow orchestration for Agent Cube."""

import json
from pathlib import Path

import typer

from ...core.config import PROJECT_ROOT
from ...core.output import console, print_error, print_info
from ...core.state import get_progress, load_state, validate_resume
from .executor import execute_workflow
from .handlers import register_phases
from .phases_registry import WorkflowContext

register_phases()


def extract_task_id_from_file(task_file: str) -> str:
    """Extract task ID from filename."""
    name = Path(task_file).stem

    if not name:
        raise ValueError(f"Cannot extract task ID from: {task_file}")

    prefixes = ["writer-prompt-", "task-", "synthesis-", "panel-prompt-", "peer-review-", "minor-fixes-", "feedback-"]
    task_id = name
    for prefix in prefixes:
        if task_id.startswith(prefix):
            task_id = task_id[len(prefix) :]
            break

    if not task_id or task_id.startswith("-") or task_id.endswith("-"):
        raise ValueError(f"Invalid task ID extracted: '{task_id}' from {task_file}")

    return task_id


async def _orchestrate_auto_impl(
    task_file: str,
    resume_from: int,
    task_id: str,
    resume_alias: str | None = None,
    single_mode: bool = False,
    writer_key: str | None = None,
    fresh_writer: bool = False,
) -> None:
    """Internal implementation of orchestrate_auto_command."""
    from ...core.state_backfill import backfill_state_from_artifacts

    prompts_dir = PROJECT_ROOT / ".prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)

    existing_state = load_state(task_id)

    # Check if resuming single mode from state
    if existing_state and existing_state.mode == "single":
        single_mode = True
        writer_key = existing_state.writer_key
        print_info(f"Resuming in single-writer mode with [bold cyan]{writer_key}[/bold cyan]")

    # Set default writer for single mode
    if single_mode and not writer_key:
        from ...core.user_config import get_default_writer

        writer_key = get_default_writer()

    if not existing_state and resume_from > 1:
        console.print("[dim]Backfilling state from existing artifacts...[/dim]")
        existing_state = backfill_state_from_artifacts(task_id)
        console.print(f"[dim]Detected: {get_progress(task_id)}[/dim]")

    if existing_state:
        console.print(f"[dim]Progress: {get_progress(task_id)}[/dim]")

    if resume_from > 1:
        valid, msg = validate_resume(task_id, resume_from)
        if not valid:
            print_error(msg)
            raise typer.Exit(1)
        console.print(f"[yellow]Resuming from Phase {resume_from}[/yellow]")

    console.print()

    ctx = WorkflowContext(
        task_id=task_id,
        task_file=task_file,
        prompts_dir=prompts_dir,
        resume_from=resume_from,
        writer_key=writer_key,  # None = dual mode, set = single mode
        resume_alias=resume_alias,
        fresh_writer=fresh_writer,
    )

    # If resuming from phase 6+, load the aggregated result
    if resume_from >= 6:
        if single_mode and writer_key:
            # Single mode: reconstruct result from state
            ctx.result = {"winner": writer_key, "all_approved": False}
        else:
            ctx.result = _load_aggregated_result(task_id, prompts_dir)

    await execute_workflow(ctx)


def _load_aggregated_result(task_id: str, prompts_dir: Path) -> dict:
    """Load aggregated decision result from file."""
    result_file = prompts_dir / "decisions" / f"{task_id}-aggregated.json"
    if result_file.exists():
        try:
            with open(result_file) as f:
                result = json.load(f)
            if "next_action" not in result:
                raise RuntimeError("Aggregated decision missing 'next_action'. Re-run Phase 5.")
            return result
        except json.JSONDecodeError:
            raise RuntimeError(f"Corrupt aggregated decision file: {result_file}. Re-run Phase 5.")
    else:
        raise RuntimeError("No aggregated decision found. Run Phase 5 first.")
