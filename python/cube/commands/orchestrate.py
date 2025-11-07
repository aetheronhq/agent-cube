"""Orchestrate command."""

import asyncio
import subprocess
from pathlib import Path
import typer

from ..core.output import print_error, print_success, print_warning, print_info, console
from ..core.config import PROJECT_ROOT
from ..core.agent import run_agent
from ..core.parsers.registry import get_parser
from ..automation.stream import format_stream_message
from ..automation.dual_writers import launch_dual_writers
from ..automation.judge_panel import launch_judge_panel
from .decide import decide_command

__all__ = ['orchestrate_prompt_command', 'orchestrate_auto_command']

def extract_task_id_from_file(task_file: str) -> str:
    """Extract task ID from filename."""
    name = Path(task_file).stem
    
    if name.startswith("writer-prompt-"):
        return name.replace("writer-prompt-", "")
    elif name.startswith("task-"):
        return name.replace("task-", "")
    
    parts = name.split("-")
    if len(parts) > 0 and parts[0].isdigit():
        return name
    
    return name

def orchestrate_prompt_command(
    task_file: str,
    copy: bool = False
) -> None:
    """Generate orchestrator prompt for autonomous workflow execution."""
    
    task_path = PROJECT_ROOT / task_file
    
    if not task_path.exists():
        print_error(f"Task file not found: {task_file}")
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

def generate_orchestrator_prompt(task_file: str, task_content: str) -> str:
    """Generate orchestrator meta-prompt."""
    return f"""# Agent Cube Orchestrator

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

async def orchestrate_auto_command(task_file: str) -> None:
    """Fully autonomous orchestration - runs entire workflow."""
    
    task_path = PROJECT_ROOT / task_file
    
    if not task_path.exists():
        raise FileNotFoundError(f"Task file not found: {task_file}")
    
    task_id = extract_task_id_from_file(task_file)
    
    console.print(f"[bold cyan]🤖 Agent Cube Autonomous Orchestration[/bold cyan]")
    console.print(f"Task: {task_id}")
    console.print()
    
    task_content = task_path.read_text()
    
    orchestrator_prompt = f"""# Task: Generate Writer Prompt

Your ONLY job is to generate a comprehensive writer prompt for the Agent Cube dual-writer workflow.

## Source Task

{task_content}

## Your Output

Create a detailed writer prompt in markdown that includes:

1. **Context** - What this task builds on
2. **Requirements** - Specific acceptance criteria
3. **Implementation steps** - Ordered checklist
4. **Architecture constraints** - From planning docs
5. **Anti-patterns** - What to avoid
6. **Success criteria** - How to verify
7. **Final steps** - MUST include commit and push instructions

## Output Format

Write the prompt as markdown and save it to:

`.prompts/writer-prompt-{task_id}.md`

**Critical:** Tell writers to commit and push their changes at the end!

Begin now!"""
    
    console.print("[yellow]Phase 1: Orchestrator generates writer prompt[/yellow]")
    console.print()
    
    prompts_dir = PROJECT_ROOT / ".prompts"
    prompts_dir.mkdir(exist_ok=True)
    
    writer_prompt_path = prompts_dir / f"writer-prompt-{task_id}.md"
    
    parser = get_parser("cursor-agent")
    
    stream = run_agent(
        PROJECT_ROOT,
        "sonnet-4.5-thinking",
        orchestrator_prompt,
        session_id=None,
        resume=False
    )
    
    console.print("[cyan]🤖 Orchestrator (Sonnet 4.5):[/cyan]")
    
    async for line in stream:
        msg = parser.parse(line)
        if msg:
            formatted = format_stream_message(msg, "Orchestrator", "cyan")
            if formatted:
                console.print(formatted)
        
        if writer_prompt_path.exists():
            console.print()
            print_success(f"Writer prompt created: {writer_prompt_path}")
            console.print()
            break
    
    if not writer_prompt_path.exists():
        raise RuntimeError("Orchestrator didn't create writer prompt")
    
    console.print("[yellow]Phase 2: Launching dual writers[/yellow]")
    console.print()
    
    await launch_dual_writers(task_id, writer_prompt_path, resume_mode=False)
    
    panel_prompt_path = prompts_dir / f"panel-prompt-{task_id}.md"
    
    if panel_prompt_path.exists():
        console.print()
        console.print("[yellow]Phase 3: Launching judge panel[/yellow]")
        console.print()
        
        await launch_judge_panel(task_id, panel_prompt_path, "panel", resume_mode=False)
        
        console.print()
        console.print("[yellow]Phase 4: Aggregating decisions[/yellow]")
        console.print()
        
        decide_command(task_id)
    else:
        console.print()
        print_warning("Panel prompt not found - manual intervention needed")
        console.print(f"Next: Create {panel_prompt_path}")
        console.print(f"Then: cube panel {task_id} .prompts/panel-prompt-{task_id}.md")
