"""CLI entry points for orchestrate command."""

from .workflow import _orchestrate_auto_impl, extract_task_id_from_file


async def orchestrate_auto_command(
    task_file: str | None,
    resume_from: int = 1,
    task_id: str | None = None,
    resume_alias: str | None = None,
    single_mode: bool = False,
    writer_key: str | None = None,
    fresh_writer: bool = False,
    fresh_judges: bool = False,
    resume_prompt: str | None = None,
) -> None:
    """Fully autonomous orchestration - runs entire workflow.

    Args:
        task_file: Path to task file (can be None if resuming from phase > 1)
        resume_from: Phase number to resume from (1-10)
        task_id: Optional task ID (if not provided, extracted from task_file)
        resume_alias: Original alias used (e.g., "peer-review") to handle special cases
        single_mode: Run in single-writer mode
        writer_key: The writer to use in single-writer mode
        fresh_writer: Clear winner's session and start fresh (for dead sessions)
        fresh_judges: Start fresh judge sessions instead of resuming
        resume_prompt: Additional context/instructions to prepend when resuming
    """
    from ...core.master_log import master_log_context

    if task_id is None:
        if not task_file:
            raise ValueError("Task ID or task file must be provided")
        task_id = extract_task_id_from_file(task_file)

    with master_log_context(task_id):
        await _orchestrate_auto_impl(
            task_file=task_file,
            resume_from=resume_from,
            task_id=task_id,
            resume_alias=resume_alias,
            single_mode=single_mode,
            writer_key=writer_key,
            fresh_writer=fresh_writer,
            fresh_judges=fresh_judges,
            resume_prompt=resume_prompt,
        )
