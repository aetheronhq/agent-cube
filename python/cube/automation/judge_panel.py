"""Parallel judge panel execution."""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import List

from ..core.adapters.registry import get_adapter
from ..core.config import PROJECT_ROOT, WORKTREE_BASE, get_project_root, get_worktree_path
from ..core.dynamic_layout import DynamicLayout
from ..core.git import branch_exists, fetch_branches, get_commit_hash, sync_worktree
from ..core.output import console, print_error, print_info, print_success
from ..core.parsers.registry import get_parser
from ..core.session import load_session, save_session
from ..core.user_config import get_judge_configs, get_writer_by_key, load_config
from ..models.types import JudgeInfo
from .stream import format_stream_message


async def _prefetch_worktrees(task_id: str, winner: str = None) -> None:
    """Fetch and sync writer worktrees to latest remote commits before judge review."""
    project_name = Path(PROJECT_ROOT).name

    if winner and winner.startswith("LOCAL:"):
        # PR review - create/sync worktree for the PR branch
        branch_name = winner.replace("LOCAL:", "")
        print_info(f"Syncing worktree for PR branch: {branch_name}")

        worktree = WORKTREE_BASE / project_name / task_id
        commit = sync_worktree(worktree, branch_name)
        if not commit:
            raise RuntimeError(f"Failed to sync worktree for branch {branch_name}. Check branch exists on origin.")
        console.print(f"  ✅ {branch_name}: {commit}")
        console.print()
        return

    config = load_config()

    if winner:
        winner_cfg = get_writer_by_key(winner)
        writers = [(winner_cfg.name, f"writer-{winner_cfg.name}/{task_id}")]
    else:
        writers = [
            (cfg.name, f"writer-{cfg.name}/{task_id}") for cfg in (config.writers[k] for k in config.writer_order)
        ]

    print_info("Fetching latest commits from writer branches...")

    for writer_name, branch in writers:
        worktree = WORKTREE_BASE / project_name / f"writer-{writer_name}-{task_id}"
        commit = sync_worktree(worktree, branch)
        console.print(f"  {'✅' if commit else '⚠️ '} {branch}: {commit or 'sync failed'}")

    console.print()


def _get_cli_review_worktrees(task_id: str, winner: str = None) -> dict:
    """Get worktree paths for CLI review adapters."""
    if winner and winner.startswith("LOCAL:"):
        branch_name = winner.replace("LOCAL:", "")
        project_name = Path(get_project_root()).name
        # PR reviews use a dedicated worktree synced to the PR branch
        return {f"PR ({branch_name})": WORKTREE_BASE / project_name / task_id}

    project_name = Path(get_project_root()).name

    if winner:
        winner_cfg = get_writer_by_key(winner)
        winner_path = get_worktree_path(project_name, winner_cfg.name, task_id)
        if not winner_path.exists():
            raise FileNotFoundError(
                f"Winner worktree does not exist: {winner_path}\n"
                f"  If you want to review a different branch, use: cube peer-review <task-id> --local"
            )
        return {winner_cfg.label: winner_path}

    config = load_config()
    writers = {
        w.label: get_worktree_path(project_name, w.name, task_id)
        for w in (config.writers[k] for k in config.writer_order)
    }
    return writers


async def run_judge(judge_info: JudgeInfo, prompt: str, resume: bool, layout, winner: str = None) -> int:
    """Run a single judge agent and return line count."""
    config = load_config()

    # Determine CLI tool based on judge type or model mapping
    is_cli_review = judge_info.adapter_config and judge_info.adapter_config.get("type") == "cli-review"
    cli_name = "cli-review" if is_cli_review else config.cli_tools.get(judge_info.model, "cursor-agent")

    adapter = get_adapter(cli_name, judge_info.adapter_config)

    if is_cli_review:
        adapter.set_task_id(judge_info.task_id)  # type: ignore[attr-defined]
        adapter.set_writer_worktrees(_get_cli_review_worktrees(judge_info.task_id, winner))  # type: ignore[attr-defined]

    parser = get_parser(cli_name)
    from ..core.agent_logger import agent_logging_context

    session_id = judge_info.session_id if resume else None

    console.print(f"[dim]{judge_info.label}: Starting with model {judge_info.model} (CLI: {cli_name})...[/dim]")

    run_dir = WORKTREE_BASE.parent if cli_name == "gemini" else PROJECT_ROOT

    judge_specific_prompt = prompt.replace("{{judge_key}}", judge_info.key).replace("{judge_key}", judge_info.key)

    stream = adapter.run(run_dir, judge_info.model, judge_specific_prompt, session_id=session_id, resume=resume)

    # Use generic logging context
    async with agent_logging_context(
        agent_type="judge",
        agent_name=judge_info.key,
        task_id=judge_info.task_id,
        suffix=judge_info.review_type,
        session_key=judge_info.key.upper(),
        session_task_key=f"{judge_info.task_id}_{judge_info.review_type}",
        metadata=f"{judge_info.label} ({judge_info.key}) - {judge_info.task_id} - {judge_info.review_type} - {datetime.now()}",
    ) as logger:
        async for line in stream:  # type: ignore[attr-defined]
            logger.write_line(line)

            msg = parser.parse(line)
            if msg:
                if msg.session_id and not judge_info.session_id:
                    judge_info.session_id = msg.session_id
                    # Save session immediately when captured
                    save_session(
                        judge_info.key.upper(),
                        f"{judge_info.task_id}_{judge_info.review_type}",
                        msg.session_id,
                        f"{judge_info.label} ({judge_info.model})",
                    )

                formatted = format_stream_message(msg, judge_info.label, judge_info.color)
                if formatted:
                    if formatted.startswith("[thinking]"):
                        # Thinking message -> thinking box (buffered)
                        thinking_text = formatted.replace("[thinking]", "").replace("[/thinking]", "")
                        layout.add_thinking(judge_info.key, thinking_text)
                    elif msg.type == "assistant" and msg.content:
                        # Assistant message -> buffered per agent, no emoji logic
                        layout.add_assistant_message(judge_info.key, msg.content, judge_info.label, judge_info.color)
                    else:
                        # Tool calls, errors, etc -> immediate
                        layout.add_output(formatted)

        layout.flush_buffers()

        if logger.line_count < 10:
            raise RuntimeError(
                f"{judge_info.label} completed suspiciously quickly ({logger.line_count} lines). Check {logger.log_file}"
            )

        final_line_count = logger.line_count

    status = _parse_decision_status(judge_info)
    layout.mark_complete(judge_info.key, status)
    # Only show ✅ for approved, otherwise just show status
    icon = "✅" if "APPROVED" in status or "Ready to merge" in status else ""
    console.print(f"[{judge_info.color}][{judge_info.label}][/{judge_info.color}] {icon} {status}".strip())
    return final_line_count


def _parse_decision_status(judge_info: JudgeInfo) -> str:
    """Parse decision file and return status string."""
    from ..core.decision_parser import get_decision_file_path, parse_single_decision_file

    decision_type = "peer-review" if judge_info.review_type == "peer-review" else "decision"
    decision_file = get_decision_file_path(judge_info.key, judge_info.task_id, review_type=decision_type)

    data = parse_single_decision_file(decision_file)
    if data is None:
        return "Review complete"

    decision = data.get("decision", "")
    winner = data.get("winner", "")
    remaining_issues = data.get("remaining_issues", [])
    blocker_issues = data.get("blocker_issues", [])
    inline_comments = data.get("inline_comments", [])

    scores = data.get("scores", {})

    config = load_config()
    writer_scores = []
    for writer_key in config.writer_order:
        raw_score = scores.get(writer_key, {}).get("total_weighted") or scores.get(writer_key, {}).get("total")
        try:
            score = float(raw_score) if raw_score is not None else None
        except (ValueError, TypeError):
            score = None
        writer_scores.append((writer_key, score))

    if judge_info.review_type == "peer-review":
        # Count both remaining_issues and inline_comments for accurate issue count
        all_issues = remaining_issues + inline_comments
        return _format_peer_review_status(decision, all_issues)

    score_text = " / ".join([f"{s:.0f}" for _, s in writer_scores if s is not None])

    return _format_panel_status(decision, winner, score_text, blocker_issues)


def _format_peer_review_status(decision: str, remaining_issues: list) -> str:
    """Format status for peer review decisions."""
    if decision == "APPROVED":
        return "✓ APPROVED → Ready to merge"
    if decision == "REQUEST_CHANGES":
        count = len(remaining_issues)
        return f"⚠ REQUEST_CHANGES → {count} issue{'s' if count != 1 else ''}"
    if decision == "REJECTED":
        return "✗ REJECTED → Major issues"
    return f"Review complete → {decision}"


def _format_panel_status(decision: str, winner: str, score_text: str, blocker_issues: list) -> str:
    """Format status for panel decisions."""
    winner_text = _get_winner_text(winner)
    score_display = f" ({score_text})" if score_text else ""

    # If there are blockers, that overrides APPROVED status
    if blocker_issues:
        count = len(blocker_issues)
        return f"⚠ {count} blocker{'s' if count != 1 else ''} → {winner_text}{score_display}"

    if decision == "APPROVED":
        return f"✓ APPROVED → {winner_text}{score_display}"
    if decision == "REQUEST_CHANGES":
        return f"⚠ REQUEST_CHANGES → {winner_text}{score_display}"
    if decision == "REJECTED":
        return f"✗ REJECTED → {winner_text}{score_display}"
    return f"{winner_text}{score_display}"


def _get_winner_text(winner: str) -> str:
    """Get human-readable winner text."""
    if winner == "TIE":
        return "TIE"

    try:
        wconfig = get_writer_by_key(winner)
        return f"{wconfig.label} wins"
    except KeyError:
        return f"Winner: {winner}"


async def launch_judge_panel(
    task_id: str,
    prompt_file: Path,
    review_type: str = "initial",
    resume_mode: bool = False,
    winner: str = None,
    single_judge: str = None,
    run_all_judges: bool = False,
    judges_to_run: list = None,
) -> None:
    """Launch judge panel in parallel.

    Args:
        single_judge: If provided, only run this specific judge (e.g., "judge_4")
        run_all_judges: If True, run ALL judges regardless of review_type filtering
        judges_to_run: If provided, only run these specific JudgeConfig instances
    """

    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")

    await _prefetch_worktrees(task_id, winner)

    all_judges = get_judge_configs()

    # Filter judges based on parameters
    if judges_to_run is not None:
        # Use the explicitly provided list
        judge_configs = judges_to_run
    elif single_judge:
        judge_configs = [j for j in all_judges if j.key == single_judge]
        if not judge_configs:
            raise ValueError(f"Judge not found: {single_judge}. Available: {[j.key for j in all_judges]}")
    elif run_all_judges:
        # Explicit override: run ALL judges regardless of review_type
        judge_configs = all_judges
    elif review_type == "panel":
        # Panel review: exclude peer_review_only judges (they only do peer review)
        judge_configs = [j for j in all_judges if not j.peer_review_only]
    elif review_type == "peer-review":
        # Peer review: by default run only peer_review_only judges (e.g. CodeRabbit)
        # The handler may override this with judges_to_run for judges that haven't approved
        peer_only = [j for j in all_judges if j.peer_review_only]
        judge_configs = peer_only if peer_only else all_judges
    else:
        judge_configs = all_judges

    boxes = {j.key: j.label for j in judge_configs}
    DynamicLayout.initialize(boxes, lines_per_box=2)
    panel_layout = DynamicLayout

    base_prompt = prompt_file.read_text()
    project_name = Path(PROJECT_ROOT).name

    judge_assignments = """# YOUR JUDGE KEY

You are **Judge {judge_key}** in this panel.

When creating your decision file, use judge key {judge_key}.

---

"""

    if review_type == "peer-review":
        from .prompts import build_peer_review_prompt

        is_pr_review = winner and winner.startswith("LOCAL:")
        review_instructions = build_peer_review_prompt(
            task_id=task_id,
            worktree_base=WORKTREE_BASE,
            project_name=project_name,
            is_pr_review=is_pr_review,
        )
    else:
        config = load_config()

        from .prompts import build_review_checklist

        review_instructions_parts = [
            """# Code Review Locations

Review each writer's implementation in their worktree:
"""
        ]

        review_instructions_parts.append(f"""
---

{build_review_checklist()}

### Panel-Specific: Questions for `blocker_issues`
Include significant questions that block approval:
- "Why was auth changed from X to Y? This contradicts docs/architecture.md"
- "Is the change to [component] intentional? Not mentioned in task"

---
""")

        for writer_key in config.writer_order:
            wconfig = config.writers[writer_key]
            review_instructions_parts.append(f"""
## {wconfig.label} Implementation

**Branch:** `writer-{wconfig.name}/{task_id}`
**Location:** `{WORKTREE_BASE}/{project_name}/writer-{wconfig.name}-{task_id}/`

Review commits since main:
```bash
cd {WORKTREE_BASE}/{project_name}/writer-{wconfig.name}-{task_id}/
git log --oneline main..HEAD
git diff main...HEAD --stat
```""")

        scores_template = {}
        for writer_key in config.writer_order:
            scores_template[writer_key] = {
                "planning_alignment": "0-10 (matches docs/planning/architecture)",
                "scope_adherence": "0-10 (no undocumented changes)",
                "kiss_compliance": "0-10 (simple, elegant, minimal - no over-engineering)",
                "architecture": "0-10 (clean structure, good abstractions)",
                "type_safety": "0-10",
                "tests": "0-10",
                "production_ready": "0-10",
                "total_weighted": "0-10",
            }
        import json

        scores_json = json.dumps(scores_template, indent=4)

        winner_options = " | ".join([f'"{k}"' for k in config.writer_order] + ['"TIE"'])

        review_instructions_parts.append(f"""
---

# REQUIRED: Panel Decision File

**You MUST create this JSON file at the end of your review:**

**File:** `{PROJECT_ROOT}/.prompts/decisions/{{{{judge_key}}}}-{task_id}-decision.json`

⚠️ **Use this EXACT absolute path. Do NOT write to a worktree.**

**Format:**
```json
{{
  "judge": "{{judge_key}}",
  "task_id": "{task_id}",
  "timestamp": "{{current-iso-timestamp}}",
  "decision": "APPROVED" | "REQUEST_CHANGES" | "REJECTED",
  "winner": {winner_options},
  "scores": {scores_json},
  "blocker_issues": [
    "Description of blocking issues that must be fixed"
  ],
  "recommendation": "Brief explanation of why winner was chosen"
}}
```

**⚠️ EXACT SPELLING REQUIRED for decision field:**
- Use EXACT strings: `"APPROVED"`, `"REQUEST_CHANGES"`, or `"REJECTED"`
- NOT "Approved", "approve", "APPROVE" - use exactly `"APPROVED"`

---
""")
        review_instructions = "".join(review_instructions_parts)

        # Replace single curly braces from json.dumps with double to not conflict with f-string
        # Logic removed as we use .replace() for substitution, not .format()
        pass

    prompt = judge_assignments + review_instructions + base_prompt

    # Substitute placeholders for peer-review prompts
    if review_type == "peer-review" and winner:
        if winner.startswith("LOCAL:"):
            branch_name = winner.replace("LOCAL:", "")
            prompt = prompt.replace("{winner}", f"Local branch ({branch_name})")
            prompt = prompt.replace("{branch}", branch_name)
        else:
            winner_cfg = get_writer_by_key(winner)
            prompt = prompt.replace("{winner}", winner_cfg.name)

    # Don't re-filter - already filtered correctly above based on review_type and single_judge

    judges: List[JudgeInfo] = []
    for jconfig in judge_configs:
        session_id = None

        # CLI review tools and peer_review_only judges don't have resumable sessions
        needs_resume = resume_mode and jconfig.type != "cli-review" and not jconfig.peer_review_only

        if needs_resume:
            # Session suffix must match what's used in save_session (line 118)
            session_id = load_session(jconfig.key.upper(), f"{task_id}_{review_type}")

            if not session_id:
                raise RuntimeError(f"No session found for {jconfig.label}")

        judges.append(
            JudgeInfo(
                key=jconfig.key,
                model=jconfig.model,
                color=jconfig.color,
                label=jconfig.label,
                task_id=task_id,
                review_type=review_type,
                session_id=session_id,
                adapter_config={"type": jconfig.type, "cmd": jconfig.cmd, "name": jconfig.label}
                if jconfig.type == "cli-review"
                else None,
            )
        )

    if resume_mode:
        print_info(f"Resuming Judge Panel for Task: {task_id}")
        console.print()
        console.print("[yellow]📋 Found existing judge sessions to resume:[/yellow]")
        for judge in judges:
            if judge.session_id:
                console.print(f"  [{judge.color}]{judge.label}[/{judge.color}] ({judge.model}): {judge.session_id}")
            else:
                console.print(
                    f"  [{judge.color}]{judge.label}[/{judge.color}] ({judge.model}): [red]No session found[/red]"
                )
        console.print()
    else:
        print_info(f"Launching Judge Panel for Task: {task_id}")

    print_info(f"Prompt: {prompt_file}")
    print_info(f"Review Type: {review_type}")
    console.print()

    print_info("Fetching latest changes from writer branches...")
    fetch_branches()

    config = load_config()

    for writer_key in config.writer_order:
        writer_cfg = config.writers[writer_key]
        branch = f"writer-{writer_cfg.name}/{task_id}"
        if branch_exists(branch):
            commit = get_commit_hash(branch)
            console.print(f"  📍 {branch}: {commit}")
    console.print()

    console.print("━" * 60)
    if review_type == "peer-review" and winner:
        console.print("[bold yellow]⚖️  JUDGES: Peer review winning implementation[/bold yellow]")
        console.print()
        if winner.startswith("LOCAL:"):
            branch_name = winner.replace("LOCAL:", "")
            console.print(f"PR branch: [green]{branch_name}[/green]")
            console.print(f"Worktree: [green]~/.cube/worktrees/{project_name}/{task_id}/[/green]")
        else:
            winner_cfg = get_writer_by_key(winner)
            console.print(
                f"{winner_cfg.label}: [green]~/.cube/worktrees/{project_name}/writer-{winner_cfg.name}-{task_id}/[/green]"
            )
    else:
        console.print("[bold yellow]⚖️  JUDGES: Review all writer implementations[/bold yellow]")
        console.print()
        for writer_key in config.writer_order:
            writer_cfg = config.writers[writer_key]
            console.print(
                f"{writer_cfg.label}: [green]~/.cube/worktrees/{project_name}/writer-{writer_cfg.name}-{task_id}/[/green]"
            )
    console.print()
    console.print("Use your native tools (read_file, git commands, etc.)")
    console.print("━" * 60)
    console.print()

    for judge in judges:
        cli_name = config.cli_tools.get(judge.model, "cursor-agent")
        adapter = get_adapter(cli_name)
        if not adapter.check_installed():
            print_error(f"{cli_name} not installed (needed for {judge.model})")
            console.print()
            console.print(adapter.get_install_instructions())
            raise RuntimeError(f"{cli_name} not installed")

    for judge in judges:
        console.print(f"🚀 Starting {judge.label} with {judge.model}...")
    console.print()
    console.print(f"⏳ Waiting for all {len(judges)} judges to complete...")
    console.print()

    # Start layout AFTER printing startup messages
    panel_layout.start()

    results = await asyncio.gather(
        *(run_judge(judge, prompt, resume_mode, panel_layout, winner=winner) for judge in judges),
        return_exceptions=True,
    )

    DynamicLayout.close()

    errors = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            errors.append((judges[i].label, result))

    console.print()

    if errors:
        print_error("Some judges failed:")
        for label, error in errors:
            console.print(f"  {label}: {error}")
        console.print()
        failed_names = ", ".join(label for label, _ in errors)
        print_info("To retry failed judges, run the same command again (without --fresh)")
        print_info("To retry a specific judge: cube resume <judge-key> <task-id>")
        raise RuntimeError(f"Judge panel incomplete: {len(errors)} judge(s) failed ({failed_names}).")

    console.print("✅ All judges completed successfully")
    console.print()
    print_success("Judge panel complete!")
