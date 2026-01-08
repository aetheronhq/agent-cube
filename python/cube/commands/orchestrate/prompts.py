"""Prompt generation for Agent Cube workflow."""

import asyncio
from pathlib import Path
from typing import Any

from ...core.agent_runner import run_agent_with_layout
from ...core.config import PROJECT_ROOT
from ...core.output import console, print_info, print_success
from ...core.session import get_prompter_session, save_prompter_session
from ...core.user_config import get_prompter_model


async def generate_writer_prompt(task_id: str, task_content: str, prompts_dir: Path) -> Path:
    """Phase 1: Generate writer prompt using orchestrator agent."""
    from ...core.single_layout import SingleAgentLayout

    writer_prompt_path = prompts_dir / f"writer-prompt-{task_id}.md"

    if writer_prompt_path.exists():
        print_info(f"Writer prompt already exists: {writer_prompt_path}")
        return writer_prompt_path

    prompt = f"""# Task: Generate Writer Prompt

Generate a comprehensive writer prompt for the Agent Cube dual-writer workflow.

## Source Task

{task_content}

## Your Output

Create a detailed writer prompt and save to: `.prompts/writer-prompt-{task_id}.md`

Include: context, requirements, steps, constraints, anti-patterns, success criteria.

**Critical Instructions for Writers:**
1. **First step**: Merge latest main to avoid conflicts later:
   - `git fetch origin main`
   - `git merge origin/main --no-edit` (non-interactive merge)
   - If conflicts: Use read_file/write_file to fix them programmatically (no interactive editors!)
   - Verify clean with `git status` before proceeding
2. **Last step**: Commit and push when complete!"""

    layout = SingleAgentLayout.initialize("Prompter")
    layout.start()

    # Resume prompter session if exists, otherwise capture new session ID
    session_id, should_resume = get_prompter_session(task_id)
    captured_session_id: str | None = None

    def capture_session(sid: str) -> None:
        nonlocal captured_session_id
        captured_session_id = sid

    try:
        await run_agent_with_layout(
            cwd=PROJECT_ROOT,
            model=get_prompter_model(),
            prompt=prompt,
            layout=layout,
            label="Prompter",
            color="cyan",
            stop_when_exists=writer_prompt_path,
            session_id=session_id,
            resume=should_resume,
            capture_session_callback=capture_session if not should_resume else None,
        )
    finally:
        layout.close()

    # Save session ID if we captured a new one
    if captured_session_id and not should_resume:
        save_prompter_session(task_id, captured_session_id)

    if not writer_prompt_path.exists():
        raise RuntimeError("Failed to generate writer prompt")

    print_success(f"Created: {writer_prompt_path}")
    return writer_prompt_path


async def generate_panel_prompt(task_id: str, prompts_dir: Path) -> Path:
    """Phase 3: Generate panel prompt."""
    from ...core.single_layout import SingleAgentLayout

    panel_prompt_path = prompts_dir / f"panel-prompt-{task_id}.md"

    if panel_prompt_path.exists():
        print_info(f"Panel prompt already exists: {panel_prompt_path}")
        return panel_prompt_path

    prompt = f"""Generate a panel review prompt for task: {task_id}

Review both writer implementations and create: `.prompts/panel-prompt-{task_id}.md`

Include evaluation criteria, scoring rubric, and decision JSON format."""

    layout = SingleAgentLayout.initialize("Prompter")
    layout.start()

    # Resume prompter session if exists, otherwise capture new session ID
    session_id, should_resume = get_prompter_session(task_id)
    captured_session_id: str | None = None

    def capture_session(sid: str) -> None:
        nonlocal captured_session_id
        captured_session_id = sid

    try:
        await run_agent_with_layout(
            cwd=PROJECT_ROOT,
            model=get_prompter_model(),
            prompt=prompt,
            layout=layout,
            label="Prompter",
            color="cyan",
            stop_when_exists=panel_prompt_path,
            session_id=session_id,
            resume=should_resume,
            capture_session_callback=capture_session if not should_resume else None,
        )
    finally:
        layout.close()

    # Save session ID if we captured a new one
    if captured_session_id and not should_resume:
        save_prompter_session(task_id, captured_session_id)

    if not panel_prompt_path.exists():
        raise RuntimeError("Failed to generate panel prompt")

    print_success(f"Created: {panel_prompt_path}")
    return panel_prompt_path


async def generate_dual_feedback(
    task_id: str, prompts_dir: Path, winner_only: bool = False, winner_key: str | None = None
):
    """Generate feedback prompts.

    When winner_only=True, only generate/send feedback for the winning writer.
    """
    from ...core.dynamic_layout import DynamicLayout
    from ...core.single_layout import SingleAgentLayout
    from ...core.user_config import get_writer_config, load_config

    config = load_config()

    prompt_base = """## Available Information

**Judge Decisions (JSON):**
- `.prompts/decisions/judge_1-{task_id}-decision.json`
- `.prompts/decisions/judge_2-{task_id}-decision.json`
- `.prompts/decisions/judge_3-{task_id}-decision.json`

Read these to see what issues judges found for Writer {writer_label}.

**Writer {writer_label}'s Work:**
Branch: `writer-{writer_slug}/{task_id}`
Location: `~/.cube/worktrees/PROJECT/writer-{writer_slug}-{task_id}/`

## Your Task

Create a targeted feedback prompt for Writer {writer_label} that tells them to:
1. **First**: Merge latest main (`git fetch origin main && git merge origin/main --no-edit`) and fix any conflicts programmatically using read_file/write_file (no interactive editors!)
2. Lists specific issues judges found
3. Provides concrete fix suggestions
4. References specific files/lines
5. Keeps their good work, fixes problems
6. Commit and push when complete

Save to: `.prompts/feedback-{writer_slug}-{task_id}.md`"""

    entries = []
    for writer_key in config.writer_order:
        wconfig = get_writer_config(writer_key)

        prompt_intro = (
            "Both writers need changes based on judge reviews."
            if not winner_only
            else "Judges requested fixes for this writer."
        )

        prompt = f"""Generate a feedback prompt for {wconfig.label}.

Task: {task_id}
{prompt_intro}

{prompt_base.format(
    task_id=task_id,
    writer_label=wconfig.label,
    writer_slug=wconfig.name,
)}"""

        entries.append(
            {
                "key": writer_key,
                "cfg": wconfig,
                "path": prompts_dir / f"feedback-{wconfig.name}-{task_id}.md",
                "prompt": prompt,
                "box_id": f"prompter_{writer_key}",
                "label": f"Prompter {wconfig.label}",
                "color": wconfig.color,
            }
        )

    if winner_only:
        if winner_key not in config.writer_order:
            raise ValueError(f"winner_key '{winner_key}' not found in configured writers: {config.writer_order}")
        entries = [entry for entry in entries if entry["key"] == winner_key]

    # Resume prompter session if exists, otherwise capture new session ID
    session_id, should_resume = get_prompter_session(task_id)
    captured_session_id: str | None = None

    def capture_session(sid: str) -> None:
        nonlocal captured_session_id
        if not captured_session_id:  # Only capture first one
            captured_session_id = sid

    if len(entries) == 1:
        entry = entries[0]
        layout = SingleAgentLayout.initialize(entry["label"])
        layout.start()
        try:
            await run_agent_with_layout(
                cwd=PROJECT_ROOT,
                model=get_prompter_model(),
                prompt=entry["prompt"],
                layout=layout,
                label=entry["label"],
                color=entry["color"],
                stop_when_exists=entry["path"],
                session_id=session_id,
                resume=should_resume,
                capture_session_callback=capture_session if not should_resume else None,
            )
            if not entry["path"].exists():  # type: ignore[attr-defined]
                raise RuntimeError(f"Failed to generate feedback at {entry['path']}")
        finally:
            layout.close()

        # Save session ID if we captured a new one
        if captured_session_id and not should_resume:
            save_prompter_session(task_id, captured_session_id)

        print_success(f"Created: {entry['path']}")
        from ...core.config import WORKTREE_BASE
        from ...core.session import load_session
        from ..feedback import send_feedback_async

        session = load_session(entry["key"].upper(), task_id)  # type: ignore[attr-defined]
        if not session:
            raise RuntimeError("No session found for winner. Cannot send feedback.")

        project_name = Path(PROJECT_ROOT).name
        cfg: Any = entry["cfg"]
        worktree = WORKTREE_BASE / project_name / f"writer-{cfg.name}-{task_id}"
        await send_feedback_async(
            task_id=task_id,
            feedback_file=entry["path"],
            session_id=session,
            worktree=worktree,
            writer_name=cfg.name,
            writer_model=cfg.model,
            writer_label=cfg.label,
            writer_key=cfg.key,
            writer_color=cfg.color,
        )
        return

    console.print("Generating feedback for all writers in parallel...")
    console.print()

    boxes = {entry["box_id"]: entry["label"] for entry in entries}
    DynamicLayout.initialize(boxes, lines_per_box=2, task_name=task_id)
    layout = DynamicLayout
    layout.start()

    async def generate_entry(entry, is_first: bool):
        await run_agent_with_layout(
            cwd=PROJECT_ROOT,
            model=get_prompter_model(),
            prompt=entry["prompt"],
            layout=layout,
            label=entry["label"],
            color=entry["color"],
            box_id=entry["box_id"],
            stop_when_exists=entry["path"],
            session_id=session_id,
            resume=should_resume,
            capture_session_callback=capture_session if (is_first and not should_resume) else None,
        )

    await asyncio.gather(*(generate_entry(entry, i == 0) for i, entry in enumerate(entries)))

    layout.close()

    # Save session ID if we captured a new one
    if captured_session_id and not should_resume:
        save_prompter_session(task_id, captured_session_id)

    for entry in entries:
        if not entry["path"].exists():  # type: ignore[attr-defined]
            raise RuntimeError(f"{entry['label']} failed to generate feedback at {entry['path']}")
        print_success(f"Created: {entry['path']}")

    console.print()
    print_info("Sending feedback to writers...")
    from ...core.config import WORKTREE_BASE
    from ...core.output import print_warning
    from ...core.session import load_session
    from ..feedback import send_feedback_async

    # Send feedback to each writer that has a session
    tasks = []
    any_session_found = False
    for entry in entries:
        session = load_session(entry["key"].upper(), task_id)  # type: ignore[attr-defined]
        if session:
            any_session_found = True
            project_name = Path(PROJECT_ROOT).name
            wcfg: Any = entry["cfg"]
            worktree = WORKTREE_BASE / project_name / f"writer-{wcfg.name}-{task_id}"
            tasks.append(
                send_feedback_async(
                    task_id=task_id,
                    feedback_file=entry["path"],
                    session_id=session,
                    worktree=worktree,
                    writer_name=wcfg.name,
                    writer_model=wcfg.model,
                    writer_label=wcfg.label,
                    writer_key=wcfg.key,
                    writer_color=wcfg.color,
                )
            )
        else:
            cfg_label = entry["cfg"].label  # type: ignore[attr-defined]
            print_warning(f"No session found for {cfg_label}. Feedback generated at {entry['path']} but not sent.")

    if not any_session_found:
        print_warning("No sessions found for any writer. Feedback files generated but not sent.")
        print_info("Writers will need to manually read and address feedback:")
        for entry in entries:
            console.print(f"  {entry['cfg'].label}: {entry['path']}")  # type: ignore[attr-defined]
        return

    if tasks:
        await asyncio.gather(*tasks)
