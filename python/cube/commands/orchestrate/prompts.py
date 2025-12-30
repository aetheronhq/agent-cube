"""Prompt generation for Agent Cube workflow."""

import asyncio
from pathlib import Path

from ...core.output import print_success, print_info, console
from ...core.config import PROJECT_ROOT
from ...core.agent import run_agent
from ...core.parsers.registry import get_parser
from ...core.user_config import get_prompter_model
from ...automation.stream import format_stream_message


def generate_orchestrator_prompt(task_file: str, task_content: str) -> str:
    """Generate orchestrator meta-prompt."""
    prompt = f"""# Agent Cube Orchestrator

You are an autonomous orchestrator for the Agent Cube parallel LLM coding workflow. Your goal is to complete the entire workflow from task spec to merged PR.

## Task to Orchestrate

**Task File:** `{task_file}`

```markdown
{task_content}
```

## Your Capabilities

You can execute cube CLI commands by running them in your terminal. Available commands:

- `cube-py writers <task-id> <writer-prompt-file>` - Launch dual writers
- `cube-py panel <task-id> <panel-prompt-file> initial` - Launch initial review panel (3 new judges)
- `cube-py peer-review <task-id> <peer-review-prompt-file>` - Resume original 3 judges for peer review
- `cube-py feedback <writer> <task-id> <feedback-file>` - Send feedback to writer
- `cube-py status` - Check active agent sessions
- `cube-py sessions` - List all session IDs

## Workflow Phases

### Phase 1: Dual Writer Launch
1. Generate a comprehensive writer prompt in `.prompts/writer-prompt-${{task-id}}.md`
   - **Always create .prompts folder** at workspace root if it doesn't exist
   - Store all prompts in `.prompts/` for organization and reuse
2. Run: `cube writers <task-id> .prompts/writer-prompt-${{task-id}}.md`
3. Wait for completion (watch terminal output)
4. Read writer outputs from their worktrees

### Phase 2: Initial Review Panel
1. Analyze both writer outputs
2. Compare against task requirements and planning docs
3. Generate panel prompt in `.prompts/panel-prompt-${{task-id}}.md`
4. Run: `cube panel <task-id> .prompts/panel-prompt-${{task-id}}.md`
5. Wait for 3 judges to complete

### Phase 3: Synthesis (if needed)
1. If both writers have valuable contributions, merge best parts
2. Generate synthesis instructions in `.prompts/synthesis-${{task-id}}.md`
3. Resume winning writer: `cube feedback <winner> <task-id> .prompts/synthesis-${{task-id}}.md`

### Phase 4: Peer Review (Winner Only)

**CRITICAL:** Peer review is for the WINNING writer only, not both!

1. **Identify the winning writer** from panel votes (e.g., Writer B won)

2. Generate peer review prompt in `.prompts/peer-review-${{task-id}}.md`:

```markdown
# Peer Review: [Winner Name] Implementation

**Winner:** Writer B (Codex)  
**Branch:** writer-codex/${{task-id}}  
**Location:** ~/.cube/worktrees/PROJECT/writer-codex-${{task-id}}/

## Your Task

Review Writer B's UPDATED implementation to verify:
1. Your concerns from initial panel were addressed
2. Synthesis changes are correct (if any)
3. Code is ready to merge

## How to Review

Use read_file to read files from the worktree:
~/.cube/worktrees/PROJECT/writer-codex-${{task-id}}/apps/api/src/lib/crud/register.ts

Or use git commands:
git diff main...writer-codex/${{task-id}}
git show writer-codex/${{task-id}}:apps/api/src/lib/crud/register.ts

**DO NOT review Writer A** - they did not win the panel vote.
```

3. Run: `cube peer-review <task-id> .prompts/peer-review-${{task-id}}.md`

4. Original 3 judges review ONLY the winning writer's code

### Prompt Organization

**Always use .prompts/ folder:**
- `.prompts/writer-prompt-<task-id>.md` - Initial writer instructions
- `.prompts/panel-prompt-<task-id>.md` - Judge panel review
- `.prompts/synthesis-<task-id>.md` - Synthesis feedback (if needed)
- `.prompts/peer-review-<task-id>.md` - Final peer review

This keeps all prompts organized and reusable.

### Phase 5: PR Creation
1. If approved, create PR using winning writer's branch
2. Write comprehensive PR description
3. Reference task file and review decisions

## Important Rules

1. **Generate prompts dynamically** - Don't use hardcoded prompts
2. **Read actual outputs** - Don't assume, read the actual files
3. **Explain your reasoning** - Before each command, explain why
4. **Handle failures gracefully** - If something fails, diagnose and retry
5. **Be thorough** - Don't skip steps; this is production code

## Available Context

- **Project root**: Current workspace
- **Task file**: `{task_file}`
- **Worktrees**: `~/.cube/worktrees/{{project-name}}/`

## Your First Step

Start by:
1. Reading relevant planning docs for this task
2. Understanding the acceptance criteria
3. Generating the writer prompt
4. Launching the dual writers

Begin orchestration now!"""

    return prompt


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

    parser = get_parser("cursor-agent")
    layout = SingleAgentLayout.initialize("Prompter")
    layout.start()

    stream = run_agent(PROJECT_ROOT, get_prompter_model(), prompt, session_id=None, resume=False)

    async for line in stream:
        msg = parser.parse(line)
        if msg:
            formatted = format_stream_message(msg, "Prompter", "cyan")
            if formatted:
                if formatted.startswith("[thinking]"):
                    thinking_text = formatted.replace("[thinking]", "").replace("[/thinking]", "")
                    layout.add_thinking(thinking_text)
                elif msg.type == "assistant" and msg.content:
                    layout.add_assistant_message(msg.content, "Prompter", "cyan")
                else:
                    layout.add_output(formatted)

        if writer_prompt_path.exists():
            layout.close()
            print_success(f"Created: {writer_prompt_path}")
            break

    if not writer_prompt_path.exists():
        raise RuntimeError("Failed to generate writer prompt")

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

    parser = get_parser("cursor-agent")
    layout = SingleAgentLayout.initialize("Prompter")
    layout.start()

    stream = run_agent(PROJECT_ROOT, get_prompter_model(), prompt, session_id=None, resume=False)

    async for line in stream:
        msg = parser.parse(line)
        if msg:
            formatted = format_stream_message(msg, "Prompter", "cyan")
            if formatted:
                if formatted.startswith("[thinking]"):
                    thinking_text = formatted.replace("[thinking]", "").replace("[/thinking]", "")
                    layout.add_thinking(thinking_text)
                elif msg.type == "assistant" and msg.content:
                    layout.add_assistant_message(msg.content, "Prompter", "cyan")
                else:
                    layout.add_output(formatted)

        if panel_prompt_path.exists():
            layout.close()
            print_success(f"Created: {panel_prompt_path}")
            break

    if not panel_prompt_path.exists():
        raise RuntimeError("Failed to generate panel prompt")

    return panel_prompt_path


async def generate_dual_feedback(
    task_id: str,
    prompts_dir: Path,
    winner_only: bool = False,
    winner_key: str | None = None
):
    """Generate feedback prompts.
    
    When winner_only=True, only generate/send feedback for the winning writer.
    """
    from ...core.dynamic_layout import DynamicLayout
    from ...core.single_layout import SingleAgentLayout
    from ...core.user_config import load_config, get_writer_config

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
            if not winner_only else
            "Judges requested fixes for this writer."
        )

        prompt = f"""Generate a feedback prompt for {wconfig.label}.

Task: {task_id}
{prompt_intro}

{prompt_base.format(
    task_id=task_id, 
    writer_label=wconfig.label, 
    writer_slug=wconfig.name, 
)}"""

        entries.append({
            "key": writer_key,
            "cfg": wconfig,
            "path": prompts_dir / f"feedback-{wconfig.name}-{task_id}.md",
            "prompt": prompt,
            "box_id": f"prompter_{writer_key}",
            "label": f"Prompter {wconfig.label}",
            "color": wconfig.color
        })

    if winner_only:
        if winner_key not in config.writer_order:
            raise ValueError(f"winner_key '{winner_key}' not found in configured writers: {config.writer_order}")
        entries = [entry for entry in entries if entry["key"] == winner_key]

    parser = get_parser("cursor-agent")
    
    if len(entries) == 1:
        entry = entries[0]
        layout = SingleAgentLayout.initialize(entry["label"])
        layout.start()
        try:
            stream = run_agent(PROJECT_ROOT, get_prompter_model(), entry["prompt"], session_id=None, resume=False)
            async for line in stream:
                msg = parser.parse(line)
                if msg:
                    formatted = format_stream_message(msg, entry["label"], entry["color"])
                    if formatted:
                        if formatted.startswith("[thinking]"):
                            thinking_text = formatted.replace("[thinking]", "").replace("[/thinking]", "")
                            layout.add_thinking(thinking_text)
                        elif msg.type == "assistant" and msg.content:
                            layout.add_assistant_message(msg.content, entry["label"], entry["color"])
                        else:
                            layout.add_output(formatted)
                if entry["path"].exists():  # type: ignore[attr-defined]
                    break
            if not entry["path"].exists():  # type: ignore[attr-defined]
                raise RuntimeError(f"Failed to generate feedback at {entry['path']}")
        finally:
            layout.close()

        print_success(f"Created: {entry['path']}")
        from ...core.session import load_session
        from ...core.config import WORKTREE_BASE
        from ..feedback import send_feedback_async

        session = load_session(entry['key'].upper(), task_id)  # type: ignore[attr-defined]
        if not session:
            raise RuntimeError("No session found for winner. Cannot send feedback.")

        project_name = Path(PROJECT_ROOT).name
        worktree = WORKTREE_BASE / project_name / f"writer-{entry['cfg'].name}-{task_id}"  # type: ignore[attr-defined]
        await send_feedback_async(entry["cfg"].name, task_id, entry["path"], session, worktree)  # type: ignore[attr-defined]
        return

    console.print("Generating feedback for all writers in parallel...")
    console.print()

    boxes = {entry["box_id"]: entry["label"] for entry in entries}
    DynamicLayout.initialize(boxes, lines_per_box=2)
    layout = DynamicLayout
    layout.start()

    parser = get_parser("cursor-agent")

    async def generate_entry(entry):
        stream = run_agent(PROJECT_ROOT, get_prompter_model(), entry["prompt"], session_id=None, resume=False)
        async for line in stream:
            msg = parser.parse(line)
            if msg:
                formatted = format_stream_message(msg, entry["label"], entry["color"])
                if formatted:
                    if formatted.startswith("[thinking]"):
                        thinking_text = formatted.replace("[thinking]", "").replace("[/thinking]", "")
                        layout.add_thinking(entry["box_id"], thinking_text)
                    elif msg.type == "assistant" and msg.content:
                        layout.add_assistant_message(entry["box_id"], msg.content, entry["label"], entry["color"])
                    else:
                        layout.add_output(formatted)
            if entry["path"].exists():
                return

    await asyncio.gather(*(generate_entry(entry) for entry in entries))

    layout.close()

    for entry in entries:
        if not entry["path"].exists():  # type: ignore[attr-defined]
            raise RuntimeError(f"{entry['label']} failed to generate feedback at {entry['path']}")
        print_success(f"Created: {entry['path']}")

    console.print()
    print_info("Sending feedback to writers...")
    from ..feedback import send_feedback_async
    from ...core.session import load_session
    from ...core.config import WORKTREE_BASE
    from ...core.output import print_warning

    # Send feedback to each writer that has a session
    tasks = []
    any_session_found = False
    for entry in entries:
        session = load_session(entry['key'].upper(), task_id)  # type: ignore[attr-defined]
        if session:
            any_session_found = True
            project_name = Path(PROJECT_ROOT).name
            worktree = WORKTREE_BASE / project_name / f"writer-{entry['cfg'].name}-{task_id}"  # type: ignore[attr-defined]
            tasks.append(send_feedback_async(entry['cfg'].name, task_id, entry['path'], session, worktree))  # type: ignore[attr-defined]
        else:
            print_warning(f"No session found for {entry['cfg'].label}. Feedback generated at {entry['path']} but not sent.")  # type: ignore[attr-defined]
            
    if not any_session_found:
        print_warning("No sessions found for any writer. Feedback files generated but not sent.")
        print_info("Writers will need to manually read and address feedback:")
        for entry in entries:
            console.print(f"  {entry['cfg'].label}: {entry['path']}")  # type: ignore[attr-defined]
        return

    if tasks:
        await asyncio.gather(*tasks)