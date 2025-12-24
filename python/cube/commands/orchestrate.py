"""Orchestrate command - entry points only."""

import subprocess
from pathlib import Path

import typer

from ..core.config import resolve_path
from ..core.output import console, print_error, print_success, print_warning
from .orchestrate import run_decide_peer_review
from .orchestrate.prompts import generate_orchestrator_prompt
from .orchestrate.workflow import _orchestrate_auto_impl

__all__ = [
    "orchestrate_prompt_command",
    "orchestrate_auto_command",
    "extract_task_id_from_file",
    "run_decide_peer_review",
]


def extract_task_id_from_file(task_file: str) -> str:
    """Extract task ID from filename."""
    name = Path(task_file).stem

    if not name:
        raise ValueError(f"Cannot extract task ID from: {task_file}")

    prefixes = ["writer-prompt-", "task-", "synthesis-", "panel-prompt-", "peer-review-", "minor-fixes-", "feedback-"]
    task_id = name
    for prefix in prefixes:
        if task_id.startswith(prefix):
            task_id = task_id[len(prefix):]
            break

    if not task_id:
        parts = name.split("-")
        if len(parts) > 0 and parts[0].isdigit():
            task_id = name
        else:
            task_id = name

    if not task_id or task_id.startswith("-") or task_id.endswith("-"):
        raise ValueError(f"Invalid task ID extracted: '{task_id}' from {task_file}")

    return task_id


def orchestrate_prompt_command(task_file: str, copy: bool = False) -> None:
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
            subprocess.run(["pbcopy"], input=prompt.encode(), check=True)
            print_success("Orchestrator prompt copied to clipboard!")
        except FileNotFoundError:
            try:
                subprocess.run(["xclip", "-selection", "clipboard"], input=prompt.encode(), check=True)
                print_success("Orchestrator prompt copied to clipboard!")
            except FileNotFoundError:
                print_warning("No clipboard utility found. Printing to stdout instead.")
                console.print(prompt)
        except Exception:
            print_warning("Failed to copy to clipboard. Printing to stdout instead.")
            console.print(prompt)
    else:
        console.print(prompt)


async def orchestrate_auto_command(task_file: str, resume_from: int = 1, task_id: str | None = None, resume_alias: str | None = None) -> None:
    """Fully autonomous orchestration - runs entire workflow."""
    from ..core.master_log import master_log_context

    if task_id is None:
        task_id = extract_task_id_from_file(task_file)

    with master_log_context(task_id):
        await _orchestrate_auto_impl(task_file, resume_from, task_id, resume_alias)
