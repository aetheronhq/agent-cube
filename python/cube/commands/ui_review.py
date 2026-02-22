"""UI review command."""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer

from ..core.agent import run_async
from ..core.config import PROJECT_ROOT
from ..core.output import console, print_error, print_info, print_success, print_warning

UI_FILE_EXTENSIONS = {".tsx", ".jsx", ".css", ".scss", ".sass", ".less", ".html", ".svg"}
UI_CONFIG_FILENAMES = {
    "tailwind.config.js",
    "tailwind.config.ts",
    "postcss.config.js",
    "postcss.config.ts",
}


def _read_files(file_paths: list[str]) -> str:
    """Read and concatenate file contents with filename headers."""
    parts = []
    for path_str in file_paths:
        path = Path(path_str)
        if not path.exists():
            print_warning(f"File not found: {path_str}")
            continue
        try:
            content = path.read_text()
            parts.append(f"### {path.name}\n\n```\n{content}\n```")
        except (OSError, IOError) as e:
            print_warning(f"Could not read {path_str}: {e}")
    return "\n\n".join(parts)


def _filter_ui_diff(diff: str) -> str:
    """Filter a PR diff to only include UI-relevant file sections."""
    lines = diff.split("\n")
    result: list[str] = []
    include = False

    for line in lines:
        if line.startswith("diff --git"):
            include = False
            # Extract the b/ path from "diff --git a/path b/path"
            parts = line.split(" ")
            if len(parts) >= 4:
                filepath = parts[-1].lstrip("b/")
                suffix = Path(filepath).suffix
                filename = Path(filepath).name
                if suffix in UI_FILE_EXTENSIONS or filename in UI_CONFIG_FILENAMES:
                    include = True
        if include:
            result.append(line)

    return "\n".join(result)


def _fetch_pr_ui_diff(pr_number: int) -> tuple[str, str]:
    """Fetch a PR and return (title, filtered_ui_diff).

    Raises RuntimeError if gh CLI is missing or no UI files are changed.
    """
    from ..github.pulls import check_gh_installed, fetch_pr

    if not check_gh_installed():
        raise RuntimeError("gh CLI not installed or not authenticated. Run: gh auth login")

    pr = fetch_pr(pr_number, cwd=str(PROJECT_ROOT))
    ui_diff = _filter_ui_diff(pr.diff)

    if not ui_diff.strip():
        raise RuntimeError(
            f"No UI-related file changes found in PR #{pr_number}. "
            f"Checked extensions: {', '.join(sorted(UI_FILE_EXTENSIONS))}"
        )

    return pr.title, ui_diff


def _collect_findings(task_id: str) -> dict:
    """Collect and merge P0/P1/P2 findings from all judge decision files."""
    from ..core.decision_parser import get_decision_file_path
    from ..core.user_config import get_judge_configs

    all_p0: list[dict] = []
    all_p1: list[dict] = []
    all_p2: list[dict] = []
    all_quick_wins: list[str] = []
    summaries: list[str] = []

    for jconfig in get_judge_configs():
        decision_path = get_decision_file_path(jconfig.key, task_id, review_type="ui-review")
        if not decision_path.exists():
            print_warning(f"No decision file for {jconfig.label}: {decision_path}")
            continue
        try:
            data = json.loads(decision_path.read_text())
        except (json.JSONDecodeError, OSError):
            print_warning(f"Could not parse decision file for {jconfig.label}")
            continue

        label = jconfig.label
        for finding in data.get("P0", []):
            all_p0.append({**finding, "_judge": label})
        for finding in data.get("P1", []):
            all_p1.append({**finding, "_judge": label})
        for finding in data.get("P2", []):
            all_p2.append({**finding, "_judge": label})

        all_quick_wins.extend(data.get("quick_wins", []))

        if data.get("summary"):
            summaries.append(f"[{label}] {data['summary']}")

    # Deduplicate quick wins while preserving order
    seen: set[str] = set()
    unique_wins: list[str] = []
    for win in all_quick_wins:
        if win not in seen:
            seen.add(win)
            unique_wins.append(win)

    return {
        "P0": all_p0,
        "P1": all_p1,
        "P2": all_p2,
        "quick_wins": unique_wins,
        "summaries": summaries,
    }


def _strip_markup(text: str) -> str:
    """Remove Rich markup tags for plain-text output."""
    return re.sub(r"\[/?[^\]]+\]", "", text)


def _display_findings(findings: dict, output_path: Optional[Path] = None) -> None:
    """Print merged findings to the terminal and optionally save to a file."""
    lines: list[str] = []

    def emit(text: str = "") -> None:
        lines.append(text)
        console.print(text)

    emit()
    emit("[bold cyan]UI Review Report[/bold cyan]")
    emit()

    if findings["summaries"]:
        emit("[bold]Overall Assessment[/bold]")
        for s in findings["summaries"]:
            emit(f"  {s}")
        emit()

    if findings["P0"]:
        emit(f"[bold red]P0 — Blockers ({len(findings['P0'])})[/bold red]")
        for i, f in enumerate(findings["P0"], 1):
            judge_tag = f"[dim][{f.get('_judge', '?')}][/dim]"
            emit(f"  [red]{i}.[/red] {f.get('problem', '')} {judge_tag}")
            if f.get("evidence"):
                emit(f"     Evidence:  {f['evidence']}")
            if f.get("diagnosis"):
                emit(f"     Diagnosis: {f['diagnosis']}")
            if f.get("principle"):
                emit(f"     Principle: {f['principle']}")
            if f.get("fix"):
                emit(f"     Fix:       {f['fix']}")
            if f.get("acceptance"):
                emit(f"     Verify:    {f['acceptance']}")
            emit()

    if findings["P1"]:
        emit(f"[bold yellow]P1 — Important ({len(findings['P1'])})[/bold yellow]")
        for i, f in enumerate(findings["P1"], 1):
            judge_tag = f"[dim][{f.get('_judge', '?')}][/dim]"
            emit(f"  [yellow]{i}.[/yellow] {f.get('problem', '')} {judge_tag}")
            if f.get("principle"):
                emit(f"     Principle: {f['principle']}")
            if f.get("fix"):
                emit(f"     Fix:    {f['fix']}")
            if f.get("acceptance"):
                emit(f"     Verify: {f['acceptance']}")
            emit()

    if findings["P2"]:
        emit(f"[bold dim]P2 — Polish ({len(findings['P2'])})[/bold dim]")
        for i, f in enumerate(findings["P2"], 1):
            judge_tag = f"[dim][{f.get('_judge', '?')}][/dim]"
            emit(f"  {i}. {f.get('problem', '')} {judge_tag}")
            if f.get("fix"):
                emit(f"     Fix: {f['fix']}")
        emit()

    if findings["quick_wins"]:
        emit("[bold green]Quick Wins[/bold green]")
        for i, win in enumerate(findings["quick_wins"][:5], 1):
            emit(f"  {i}. {win}")
        emit()

    if not any([findings["P0"], findings["P1"], findings["P2"]]):
        emit("[dim]No findings collected.[/dim]")
        emit()

    if output_path:
        clean = "\n".join(_strip_markup(line) for line in lines)
        output_path.write_text(clean)
        print_success(f"Report saved to {output_path}")


def ui_review_command(
    files: list[str],
    description: Optional[str],
    context: str,
    pr: Optional[int],
    output: Optional[str],
    fresh: bool,
) -> None:
    """Run a UI review through the judge panel.

    Args:
        files: Paths to UI files to review (multiple allowed).
        description: Free-text description of the UI to review.
        context: One-liner providing platform, user type, and primary task.
        pr: GitHub PR number — review only UI-related file changes.
        output: Optional path to save the report as a Markdown file.
        fresh: Start fresh judge sessions (skip any cached sessions).
    """
    from ..automation.judge_panel import launch_judge_panel
    from ..automation.ui_review_prompts import build_ui_review_prompt
    from ..core.user_config import get_judge_configs

    # --- Input validation ---
    if not files and not description and pr is None:
        print_error("Provide at least one of: --file, --description, --pr")
        raise typer.Exit(1)

    if pr is not None and (files or description):
        print_error("--pr cannot be combined with --file or --description")
        raise typer.Exit(1)

    # --- Build input content ---
    if pr is not None:
        print_info(f"Fetching UI diff for PR #{pr}...")
        try:
            pr_title, ui_diff = _fetch_pr_ui_diff(pr)
        except RuntimeError as e:
            print_error(str(e))
            raise typer.Exit(1)
        input_content = f"PR: {pr_title}\n\n{ui_diff}"
        input_type = "pr_diff"
        task_id = f"ui-review-pr-{pr}"
        console.print(f"[dim]UI diff extracted from PR #{pr}[/dim]")
    elif files:
        input_content = _read_files(files)
        if not input_content:
            print_error("No readable files provided")
            raise typer.Exit(1)
        input_type = "file"
        task_id = f"ui-review-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    else:
        input_content = description or ""
        input_type = "description"
        task_id = f"ui-review-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    # --- Save prompt file ---
    prompt_content = build_ui_review_prompt(
        task_id=task_id,
        input_content=input_content,
        input_type=input_type,
        context=context,
    )
    prompts_dir = PROJECT_ROOT / ".prompts"
    prompts_dir.mkdir(exist_ok=True)
    prompt_path = prompts_dir / f"{task_id}.md"
    prompt_path.write_text(prompt_content)

    # --- Print header ---
    console.print()
    console.print("[bold cyan]UI Review[/bold cyan]")
    if pr is not None:
        console.print(f"[bold]PR:[/bold] #{pr}")
    else:
        for f in files:
            console.print(f"[bold]File:[/bold] {f}")
        if description:
            console.print(f"[bold]Description:[/bold] {description[:80]}...")
    if context:
        console.print(f"[bold]Context:[/bold] {context}")
    console.print(f"[bold]Task ID:[/bold] {task_id}")
    console.print()

    judges = get_judge_configs()
    if not judges:
        print_error("No judges configured. Check cube.yaml or ~/.cube/config.yaml")
        raise typer.Exit(1)

    print_info(f"Starting UI review with {len(judges)} judge(s)...")

    # --- Run judge panel ---
    try:
        run_async(
            launch_judge_panel(
                task_id,
                prompt_path,
                "ui-review",
                resume_mode=not fresh,
                winner=None,
            )
        )
    except RuntimeError as e:
        print_warning(f"Judge panel error: {e}")
        print_info("Collecting available findings...")

    # --- Collect and display findings ---
    findings = _collect_findings(task_id)
    output_path = Path(output) if output else None
    _display_findings(findings, output_path)

    total = len(findings["P0"]) + len(findings["P1"]) + len(findings["P2"])
    if total > 0:
        print_success(
            f"UI review complete: {len(findings['P0'])} P0, "
            f"{len(findings['P1'])} P1, {len(findings['P2'])} P2"
        )
    else:
        print_warning("No findings collected from judges")
