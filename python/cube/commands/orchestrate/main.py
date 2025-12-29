"""CLI entry points for orchestrate command."""

import subprocess
from pathlib import Path
import typer

from ...core.output import print_error, print_success, print_warning, console
from ...core.config import PROJECT_ROOT, resolve_path

from .prompts import generate_orchestrator_prompt
from .workflow import extract_task_id_from_file, _orchestrate_auto_impl


def orchestrate_prompt_command(
    task_file: str,
    copy: bool = False
) -> None:
    """Generate orchestrator prompt for autonomous workflow execution."""

    try:
        task_path = resolve_path(task_file)
    except FileNotFoundError as e:
        print_error(str(e))
        raise typer.Exit(1)

    task_content = task_path.read_text()

    prompt = generate_orchestrator_prompt(task_file, task_content)

    if copy:
        try:
            subprocess.run(
                ["pbcopy"],
                input=prompt.encode(),
                check=True
            )
            print_success("Orchestrator prompt copied to clipboard!")
        except FileNotFoundError:
            try:
                subprocess.run(
                    ["xclip", "-selection", "clipboard"],
                    input=prompt.encode(),
                    check=True
                )
                print_success("Orchestrator prompt copied to clipboard!")
            except FileNotFoundError:
                print_warning("No clipboard utility found. Printing to stdout instead.")
                console.print(prompt)
        except Exception:
            print_warning("Failed to copy to clipboard. Printing to stdout instead.")
            console.print(prompt)
    else:
        console.print(prompt)


async def orchestrate_auto_command(task_file: str | None, resume_from: int = 1, task_id: str | None = None, resume_alias: str | None = None) -> None:
    """Fully autonomous orchestration - runs entire workflow.

    Args:
        task_file: Path to task file (can be None if resuming from phase > 1)
        resume_from: Phase number to resume from (1-10)
        task_id: Optional task ID (if not provided, extracted from task_file)
        resume_alias: Original alias used (e.g., "peer-review") to handle special cases
    """
    from ...core.master_log import master_log_context

    if task_id is None:
        task_id = extract_task_id_from_file(task_file)

    with master_log_context(task_id):
        await _orchestrate_auto_impl(task_file, resume_from, task_id, resume_alias)
