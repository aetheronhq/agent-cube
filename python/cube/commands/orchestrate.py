"""Orchestrate command."""

import asyncio
import subprocess
from pathlib import Path
import typer

from ..core.output import print_error, print_success, print_warning, print_info, console
from ..core.config import PROJECT_ROOT, resolve_path
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
    
    if not name:
        raise ValueError(f"Cannot extract task ID from: {task_file}")
    
    if name.startswith("writer-prompt-"):
        task_id = name.replace("writer-prompt-", "")
    elif name.startswith("task-"):
        task_id = name.replace("task-", "")
    else:
        parts = name.split("-")
        if len(parts) > 0 and parts[0].isdigit():
            task_id = name
        else:
            task_id = name
    
    if not task_id or task_id.startswith("-") or task_id.endswith("-"):
        raise ValueError(f"Invalid task ID extracted: '{task_id}' from {task_file}")
    
    return task_id

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

async def orchestrate_auto_command(task_file: str, resume_from: int = 1, task_id: str = None) -> None:
    """Fully autonomous orchestration - runs entire workflow.
    
    Args:
        task_file: Path to task file (can be None if resuming from phase > 1)
        resume_from: Phase number to resume from (1-10)
        task_id: Optional task ID (if not provided, extracted from task_file)
    """
    from ..core.state import validate_resume, update_phase, load_state, get_progress
    
    # Get task_id - either provided directly or from file
    if task_id is None:
        task_id = extract_task_id_from_file(task_file)
    
    prompts_dir = PROJECT_ROOT / ".prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    
    console.print(f"[bold cyan]🤖 Agent Cube Autonomous Orchestration[/bold cyan]")
    console.print(f"Task: {task_id}")
    
    existing_state = load_state(task_id)
    
    if not existing_state and resume_from > 1:
        from ..core.state_backfill import backfill_state_from_artifacts
        console.print("[dim]Backfilling state from existing artifacts...[/dim]")
        existing_state = backfill_state_from_artifacts(task_id)
        console.print(f"[dim]Detected: {get_progress(task_id)}[/dim]")
    
    if existing_state:
        console.print(f"[dim]Progress: {get_progress(task_id)}[/dim]")
    
    if resume_from > 1:
        valid, msg = validate_resume(task_id, resume_from)
        if not valid:
            from ..core.output import print_error
            print_error(msg)
            raise typer.Exit(1)
        console.print(f"[yellow]Resuming from Phase {resume_from}[/yellow]")
    
    console.print()
    
    writer_prompt_path = prompts_dir / f"writer-prompt-{task_id}.md"
    panel_prompt_path = prompts_dir / f"panel-prompt-{task_id}.md"
    
    if resume_from <= 1:
        console.print("[yellow]═══ Phase 1: Generate Writer Prompt ═══[/yellow]")
        if not task_file:
            print_error("Task file required for Phase 1. Provide a task.md path.")
            raise typer.Exit(1)
        task_path = resolve_path(task_file)
        writer_prompt_path = await generate_writer_prompt(task_id, task_path.read_text(), prompts_dir)
        update_phase(task_id, 1, path="INIT")
    
    if resume_from <= 2:
        console.print()
        console.print("[yellow]═══ Phase 2: Dual Writers Execute ═══[/yellow]")
        await launch_dual_writers(task_id, writer_prompt_path, resume_mode=False)
        update_phase(task_id, 2, writers_complete=True)
    
    if resume_from <= 3:
        console.print()
        console.print("[yellow]═══ Phase 3: Generate Panel Prompt ═══[/yellow]")
        panel_prompt_path = await generate_panel_prompt(task_id, prompts_dir)
        update_phase(task_id, 3)
    
    if resume_from <= 4:
        console.print()
        console.print("[yellow]═══ Phase 4: Judge Panel Review ═══[/yellow]")
        await launch_judge_panel(task_id, panel_prompt_path, "panel", resume_mode=False)
        update_phase(task_id, 4, panel_complete=True)
    
    if resume_from <= 5:
        console.print()
        console.print("[yellow]═══ Phase 5: Aggregate Decisions ═══[/yellow]")
        result = run_decide_and_get_result(task_id)
        update_phase(task_id, 5, path=result["next_action"], winner=result["winner"], next_action=result["next_action"])
    else:
        import json
        result_file = prompts_dir / "decisions" / f"{task_id}-aggregated.json"
        if result_file.exists():
            try:
                with open(result_file) as f:
                    result = json.load(f)
                
                if "next_action" not in result:
                    raise RuntimeError(f"Aggregated decision missing 'next_action'. Re-run Phase 5.")
            except json.JSONDecodeError:
                raise RuntimeError(f"Corrupt aggregated decision file: {result_file}. Re-run Phase 5.")
        else:
            raise RuntimeError(f"Cannot resume from phase {resume_from}: No aggregated decision found. Run Phase 5 first.")
    
    if result["next_action"] == "SYNTHESIS":
        if resume_from <= 6:
            console.print()
            console.print("[yellow]═══ Phase 6: Synthesis ═══[/yellow]")
            await run_synthesis(task_id, result, prompts_dir)
            update_phase(task_id, 6, synthesis_complete=True)
        
        if resume_from <= 7:
            console.print()
            console.print("[yellow]═══ Phase 7: Peer Review ═══[/yellow]")
            await run_peer_review(task_id, result, prompts_dir)
            update_phase(task_id, 7, peer_review_complete=True)
        
        if resume_from <= 8:
            console.print()
            console.print("[yellow]═══ Phase 8: Final Decision ═══[/yellow]")
        
        final_result = run_decide_peer_review(task_id)
        update_phase(task_id, 8)
        
        if final_result["approved"] and not final_result["remaining_issues"]:
            await create_pr(task_id, result["winner"])
        elif final_result["approved"] and final_result["remaining_issues"]:
            console.print()
            print_warning(f"Peer review approved but has {len(final_result['remaining_issues'])} minor issue(s)")
            console.print()
            console.print("Minor issues to address:")
            for issue in final_result["remaining_issues"]:
                console.print(f"  • {issue}")
            console.print()
            
            if resume_from <= 9:
                console.print("[yellow]═══ Phase 9: Address Minor Issues ═══[/yellow]")
                await run_minor_fixes(task_id, result, final_result["remaining_issues"], prompts_dir)
                update_phase(task_id, 9)
            
            if resume_from <= 10:
                console.print()
                console.print("[yellow]═══ Phase 10: Final Peer Review ═══[/yellow]")
                await run_peer_review(task_id, result, prompts_dir)
                update_phase(task_id, 10)
            
            final_check = run_decide_peer_review(task_id)
            if final_check["approved"] and not final_check["remaining_issues"]:
                await create_pr(task_id, result["winner"])
            elif final_check["approved"] and final_check["remaining_issues"]:
                print_warning(f"Approved but still has {len(final_check['remaining_issues'])} issue(s) after minor fixes")
                console.print()
                console.print("Issues remaining:")
                for issue in final_check["remaining_issues"]:
                    console.print(f"  • {issue}")
                console.print()
                console.print("Creating PR anyway (issues are minor)...")
                await create_pr(task_id, result["winner"])
            else:
                print_warning("Minor fixes didn't resolve all issues")
                console.print()
                console.print("The iteration limit has been reached. Manual review needed.")
                console.print()
                console.print("Next steps:")
                console.print("  1. Read peer-review decisions for remaining issues")
                console.print(f"  2. Manually fix in winner's worktree")
                console.print(f"  3. Or adjust synthesis and retry from Phase 6")
        else:
            console.print()
            from ..core.user_config import get_judge_configs
            judge_configs = get_judge_configs()
            judge_nums = [j.key for j in judge_configs]
            total_judges = len(judge_nums)
            
            decisions_count = final_result.get("decisions_found", 0)
            approvals_count = final_result.get("approvals", 0)
            
            if decisions_count < total_judges:
                print_warning(f"Missing peer review decisions ({decisions_count}/{total_judges})")
                console.print()
                console.print("Options:")
                console.print(f"  1. Get missing judge(s) to file decisions:")
                for judge_key in judge_nums:
                    judge_label = judge_key.replace("_", "-")
                    peer_file = PROJECT_ROOT / ".prompts" / "decisions" / f"{judge_label}-{task_id}-peer-review.json"
                    if not peer_file.exists():
                        console.print(f"     cube resume {judge_label} {task_id} \"Write peer review decision\"")
                console.print()
                console.print(f"  2. Continue with {decisions_count}/{total_judges} decisions:")
                console.print(f"     cube auto task.md --resume-from 8")
            else:
                print_warning(f"Peer review rejected ({approvals_count}/{decisions_count} approved) - synthesis needs more work")
                console.print()
                console.print("Next steps:")
                console.print(f"  1. Review judge feedback in peer-review decisions")
                console.print(f"  2. Update synthesis prompt:")
                console.print(f"     .prompts/synthesis-{task_id}.md")
                console.print(f"  3. Re-run synthesis:")
                console.print(f"     cube auto task.md --resume-from 6")
                console.print()
                console.print("Or manually fix the issues and re-run peer review")
    
    elif result["next_action"] == "FEEDBACK":
        if resume_from <= 6:
            console.print()
            console.print("[yellow]═══ Phase 6: Generate Feedback for Both Writers ═══[/yellow]")
            await generate_dual_feedback(task_id, result, prompts_dir)
            update_phase(task_id, 6, path="FEEDBACK")
        
        console.print()
        print_warning("Both writers need major changes. Re-run panel after they complete:")
        console.print(f"  cube panel {task_id} .prompts/panel-prompt-{task_id}.md")
    
    elif result["next_action"] == "MERGE":
        if resume_from <= 6:
            console.print()
            console.print("[yellow]═══ Phase 6: Create PR ═══[/yellow]")
            await create_pr(task_id, result["winner"])
            update_phase(task_id, 6, path="MERGE")
    
    else:
        console.print()
        print_warning(f"Unexpected next action: {result['next_action']}")
        console.print()
        console.print("This shouldn't happen. Possible causes:")
        console.print("  - Corrupted aggregated decision file")
        console.print("  - Unknown decision path")
        console.print()
        console.print("Try:")
        console.print(f"  cube decide {task_id}  # Re-aggregate decisions")
        console.print(f"  cube status {task_id}  # Check current state")

async def generate_writer_prompt(task_id: str, task_content: str, prompts_dir: Path) -> Path:
    """Phase 1: Generate writer prompt using orchestrator agent."""
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
**Critical:** Tell writers to commit and push at the end!"""
    
    from ..core.single_layout import SingleAgentLayout
    
    parser = get_parser("cursor-agent")
    layout = SingleAgentLayout(title="Prompter")
    layout.start()
    
    stream = run_agent(PROJECT_ROOT, "sonnet-4.5-thinking", prompt, session_id=None, resume=False)
    
    async for line in stream:
        msg = parser.parse(line)
        if msg:
            formatted = format_stream_message(msg, "Prompter", "cyan")
            if formatted:
                if formatted.startswith("[thinking]"):
                    thinking_text = formatted.replace("[thinking]", "").replace("[/thinking]", "")
                    layout.add_thinking(thinking_text)
                elif msg.type == "assistant" and msg.content:
                    layout.add_assistant_message("agent", msg.content, "Prompter", "cyan")
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
    panel_prompt_path = prompts_dir / f"panel-prompt-{task_id}.md"
    
    if panel_prompt_path.exists():
        print_info(f"Panel prompt already exists: {panel_prompt_path}")
        return panel_prompt_path
    
    prompt = f"""Generate a panel review prompt for task: {task_id}

Review both writer implementations and create: `.prompts/panel-prompt-{task_id}.md`

Include evaluation criteria, scoring rubric, and decision JSON format."""
    
    from ..core.single_layout import SingleAgentLayout
    
    parser = get_parser("cursor-agent")
    layout = SingleAgentLayout(title="Prompter")
    layout.start()
    
    stream = run_agent(PROJECT_ROOT, "sonnet-4.5-thinking", prompt, session_id=None, resume=False)
    
    async for line in stream:
        msg = parser.parse(line)
        if msg:
            formatted = format_stream_message(msg, "Prompter", "cyan")
            if formatted:
                if formatted.startswith("[thinking]"):
                    thinking_text = formatted.replace("[thinking]", "").replace("[/thinking]", "")
                    layout.add_thinking(thinking_text)
                elif msg.type == "assistant" and msg.content:
                    layout.add_assistant_message("agent", msg.content, "Prompter", "cyan")
                else:
                    layout.add_output(formatted)
        
        if panel_prompt_path.exists():
            layout.close()
            print_success(f"Created: {panel_prompt_path}")
            break
    
    if not panel_prompt_path.exists():
        raise RuntimeError("Failed to generate panel prompt")
    
    return panel_prompt_path

def run_decide_and_get_result(task_id: str) -> dict:
    """Run decide and return parsed result."""
    import json
    decide_command(task_id)
    
    result_file = PROJECT_ROOT / ".prompts" / "decisions" / f"{task_id}-aggregated.json"
    with open(result_file) as f:
        return json.load(f)

def run_decide_peer_review(task_id: str) -> dict:
    """Check peer review decisions and extract any remaining issues."""
    import json
    from pathlib import Path
    from ..core.user_config import get_judge_configs
    
    decisions_dir = PROJECT_ROOT / ".prompts" / "decisions"
    all_issues = []
    approvals = 0
    decisions_found = 0
    judge_decisions = {}
    
    console.print(f"[cyan]📊 Checking peer review decisions for: {task_id}[/cyan]")
    console.print()
    
    from ..core.decision_files import find_decision_file
    
    has_request_changes = False
    judge_configs = get_judge_configs()
    judge_nums = [j.key for j in judge_configs]
    total_judges = len(judge_nums)
    
    for judge_key in judge_nums:
        peer_file = find_decision_file(judge_key, task_id, "peer-review")
        
        if peer_file and peer_file.exists():
            decisions_found += 1
            with open(peer_file) as f:
                data = json.load(f)
                decision = data.get("decision", "UNKNOWN")
                remaining = data.get("remaining_issues", [])
                
                judge_decisions[f"{judge_key}_decision"] = decision
                
                judge_label = judge_key.replace("_", "-")
                console.print(f"Judge {judge_label}: {decision}")
                if remaining:
                    console.print(f"  Issues: {len(remaining)}")
                    all_issues.extend(remaining)
                
                if decision == "APPROVED":
                    approvals += 1
                elif decision == "REQUEST_CHANGES":
                    has_request_changes = True
                    if not remaining:
                        console.print(f"  [yellow]⚠️  No issues listed (malformed decision)[/yellow]")
                        all_issues.append(f"Judge {judge_label} requested changes but didn't specify issues")
    
    console.print()
    
    if decisions_found == 0:
        print_warning("No peer review decisions found!")
        console.print("Expected files:")
        for judge_key in judge_nums:
            judge_label = judge_key.replace("_", "-")
            console.print(f"  .prompts/decisions/{judge_label}-{task_id}-peer-review.json")
        console.print()
        return {"approved": False, "remaining_issues": [], "decisions_found": 0, "approvals": 0}
    
    console.print(f"Decisions: {decisions_found}/{total_judges}, Approvals: {approvals}/{decisions_found}")
    
    # Unanimous approval required - all judges must approve
    approved = approvals == decisions_found
    
    if approved:
        console.print()
        print_info("All judges approved!")
    elif approvals > 0:
        console.print()
        print_warning(f"Not unanimous: {approvals}/{decisions_found} approved, {len(all_issues)} issue(s) to address")
    
    result = {
        "approved": approved,
        "remaining_issues": all_issues,
        "decisions_found": decisions_found,
        "approvals": approvals
    }
    result.update(judge_decisions)
    return result

async def run_synthesis(task_id: str, result: dict, prompts_dir: Path):
    """Phase 6: Run synthesis if needed."""
    from pathlib import Path as PathLib
    from ..core.user_config import get_writer_by_key_or_letter
    
    winner_cfg = get_writer_by_key_or_letter(result["winner"])
    winner_name = result["winner"]
    
    synthesis_path = prompts_dir / f"synthesis-{task_id}.md"
    
    if not synthesis_path.exists():
        console.print("Generating synthesis prompt...")
        
        logs_dir = PathLib.home() / ".cube" / "logs"
        
        from ..core.user_config import get_judge_configs
        judge_configs = get_judge_configs()
        judge_decision_files = '\n'.join([f"- `.prompts/decisions/{j.key.replace('_', '-')}-{task_id}-decision.json`" for j in judge_configs])
        judge_log_files = '\n'.join([f"- `~/.cube/logs/{j.key.replace('_', '-')}-{task_id}-panel-*.json`" for j in judge_configs])
        
        prompt = f"""Generate a synthesis prompt for the WINNING writer.

## Context

Task: {task_id}
Winner: Writer {winner_name} ({winner_cfg.label})
Winner's branch: writer-{winner_cfg.name}/{task_id}
Winner's location: ~/.cube/worktrees/PROJECT/writer-{winner_cfg.name}-{task_id}/

## Available Information

**Judge Decisions (JSON with detailed feedback):**
{judge_decision_files}

Read these for full context on what judges liked/disliked.

**IMPORTANT:** Some judges (like CodeRabbit) include:
- `review_output_files` - paths to FULL review output with "Prompt for AI Agent" sections
- `blocker_issues` - critical issues that must be fixed

Tell the winner to READ their review output file (e.g., `.prompts/reviews/{task_id}-writer-a-coderabbit.txt`)
for the FULL context including code diffs and detailed fix instructions.

**Judge Logs (reasoning and analysis):**
{judge_log_files}

Optional: Read for deeper understanding of judge concerns.

## Blocker Issues to Address

{chr(10).join('- ' + issue for issue in result['blocker_issues'])}

## Your Task

Create a synthesis prompt that:
1. **Points writer to their review file** (from `review_output_files` in CodeRabbit decision)
2. Lists blocker issues that MUST be fixed
3. References specific files/lines from winner's code  
4. Tells writer to READ the review file for full context and "Prompt for AI Agent" sections
5. Preserves what judges liked (winner's architecture)
6. Tells writer to commit and push when complete

**CRITICAL:** The CodeRabbit review file contains:
- Full output with code diffs
- "Prompt for AI Agent" sections with detailed fix instructions
- ALL issues, not just blockers

Tell the winner: "Read `.prompts/reviews/{task_id}-writer-{{a|b}}-coderabbit.txt` for full details"

Save to: `.prompts/synthesis-{task_id}.md`"""
        
        from ..core.single_layout import SingleAgentLayout
        
        parser = get_parser("cursor-agent")
        layout = SingleAgentLayout(title="Prompter")
        layout.start()
        
        stream = run_agent(PROJECT_ROOT, "sonnet-4.5-thinking", prompt, session_id=None, resume=False)
        
        async for line in stream:
            msg = parser.parse(line)
            if msg:
                formatted = format_stream_message(msg, "Prompter", "cyan")
                if formatted:
                    if formatted.startswith("[thinking]"):
                        thinking_text = formatted.replace("[thinking]", "").replace("[/thinking]", "")
                        layout.add_thinking(thinking_text)
                    elif msg.type == "assistant" and msg.content:
                        layout.add_assistant_message("agent", msg.content, "Prompter", "cyan")
                    else:
                        layout.add_output(formatted)
            
            if synthesis_path.exists():
                layout.close()
                print_success(f"Created: {synthesis_path}")
                break
        
        if not synthesis_path.exists():
            raise RuntimeError(f"Prompter failed to generate synthesis prompt at {synthesis_path}")
    
    print_info(f"Sending synthesis to Writer {winner_name}")
    from .feedback import send_feedback_async
    from ..core.session import load_session
    from ..core.config import WORKTREE_BASE
    from pathlib import Path
    
    session_id = load_session(f"WRITER_{winner_cfg.letter}", task_id)
    if not session_id:
        raise RuntimeError(f"No session found for Writer {winner_name}. Cannot send synthesis.")
    
    project_name = Path(PROJECT_ROOT).name
    worktree = WORKTREE_BASE / project_name / f"writer-{winner_cfg.name}-{task_id}"
    await send_feedback_async(winner_cfg.name, task_id, synthesis_path, session_id, worktree)

async def run_peer_review(task_id: str, result: dict, prompts_dir: Path):
    """Phase 7: Run peer review."""
    from ..core.user_config import get_writer_by_key_or_letter
    
    winner_cfg = get_writer_by_key_or_letter(result["winner"])
    winner_name = result["winner"]
    
    peer_review_path = prompts_dir / f"peer-review-{task_id}.md"
    
    if not peer_review_path.exists():
        console.print("Generating peer review prompt...")
        
        prompt = f"""Generate a peer review prompt for the WINNING writer.

## Context

Task: {task_id}
Winner: {winner_cfg.label} (key: {winner_cfg.key})
Branch: writer-{winner_cfg.name}/{task_id}

## Your Task

Create a peer review prompt that tells the 3 judges to:
1. Review ONLY {winner_cfg.label}'s updated implementation
2. Verify synthesis changes were made correctly
3. Confirm all blocker issues are resolved
4. Write decision JSON: `.prompts/decisions/judge-{{{{N}}}}-{task_id}-peer-review.json`

Save to: `.prompts/peer-review-{task_id}.md`

Include the worktree location and git commands for reviewing."""
        
        from ..core.single_layout import SingleAgentLayout
        
        parser = get_parser("cursor-agent")
        layout = SingleAgentLayout(title="Prompter")
        layout.start()
        
        stream = run_agent(PROJECT_ROOT, "sonnet-4.5-thinking", prompt, session_id=None, resume=False)
        
        async for line in stream:
            msg = parser.parse(line)
            if msg:
                formatted = format_stream_message(msg, "Prompter", "cyan")
                if formatted:
                    if formatted.startswith("[thinking]"):
                        thinking_text = formatted.replace("[thinking]", "").replace("[/thinking]", "")
                        layout.add_thinking(thinking_text)
                    elif msg.type == "assistant" and msg.content:
                        layout.add_assistant_message("agent", msg.content, "Prompter", "cyan")
                    else:
                        layout.add_output(formatted)
            
            if peer_review_path.exists():
                layout.close()
                print_success(f"Created: {peer_review_path}")
                break
        
        if not peer_review_path.exists():
            raise RuntimeError(f"Prompter failed to generate peer review prompt at {peer_review_path}")
    
    print_info(f"Launching peer review for Winner: Writer {winner_name}")
    await launch_judge_panel(task_id, peer_review_path, "peer-review", resume_mode=True, winner=winner_name)

async def run_minor_fixes(task_id: str, result: dict, issues: list, prompts_dir: Path):
    """Address minor issues from peer review."""
    from ..core.user_config import get_writer_by_key_or_letter
    
    winner_cfg = get_writer_by_key_or_letter(result["winner"])
    winner_name = winner_cfg.name
    
    minor_fixes_path = prompts_dir / f"minor-fixes-{task_id}.md"
    
    prompt = f"""Generate a minor fixes prompt for the winning writer.

## Context

Winner: Writer {result['winner']} ({winner_cfg.label})

## Minor Issues from Peer Review

{chr(10).join('- ' + issue for issue in issues)}

## Your Task

Create a brief prompt telling the winner to address these minor issues.
Keep their implementation intact, just fix these specific points.

Save to: `.prompts/minor-fixes-{task_id}.md`"""
    
    parser = get_parser("cursor-agent")
    stream = run_agent(PROJECT_ROOT, "sonnet-4.5-thinking", prompt, session_id=None, resume=False)
    
    async for line in stream:
        if minor_fixes_path.exists():
            print_success(f"Created: {minor_fixes_path}")
            break
    
    if minor_fixes_path.exists():
        from .feedback import send_feedback_async
        from ..core.session import load_session
        from ..core.config import WORKTREE_BASE
        from pathlib import Path
        
        session_id = load_session(f"WRITER_{winner_cfg.letter}", task_id)
        if not session_id:
            raise RuntimeError(f"No session found for Writer {winner_cfg.label}. Cannot send minor fixes.")
        
        project_name = Path(PROJECT_ROOT).name
        worktree = WORKTREE_BASE / project_name / f"writer-{winner_name}-{task_id}"
        await send_feedback_async(winner_name, task_id, minor_fixes_path, session_id, worktree)

async def generate_dual_feedback(task_id: str, result: dict, prompts_dir: Path):
    """Generate feedback prompts for both writers in parallel with dual layout."""
    
    feedback_a_path = prompts_dir / f"feedback-a-{task_id}.md"
    feedback_b_path = prompts_dir / f"feedback-b-{task_id}.md"
    
    decisions_dir = prompts_dir / "decisions"
    
    prompt_base = """## Available Information

**Judge Decisions (JSON):**
- `.prompts/decisions/judge-1-{task_id}-decision.json`
- `.prompts/decisions/judge-2-{task_id}-decision.json`
- `.prompts/decisions/judge-3-{task_id}-decision.json`

Read these to see what issues judges found for Writer {writer}.

**Writer {writer}'s Work:**
Branch: `writer-{writer_slug}/{task_id}`
Location: `~/.cube/worktrees/PROJECT/writer-{writer_slug}-{task_id}/`

## Your Task

Create a targeted feedback prompt for Writer {writer} that:
1. Lists specific issues judges found
2. Provides concrete fix suggestions
3. References specific files/lines
4. Keeps their good work, fixes problems

Save to: `.prompts/feedback-{writer_letter}-{task_id}.md`"""
    
    from ..core.user_config import get_writer_config
    writer_a = get_writer_config("writer_a")
    writer_b = get_writer_config("writer_b")
    
    prompt_a = f"""Generate a feedback prompt for {writer_a.label}.

Task: {task_id}
Both writers need changes based on judge reviews.

{prompt_base.format(task_id=task_id, writer=writer_a.letter, writer_slug=writer_a.name, writer_letter=writer_a.letter.lower())}"""
    
    prompt_b = f"""Generate a feedback prompt for {writer_b.label}.

Task: {task_id}
Both writers need changes based on judge reviews.

{prompt_base.format(task_id=task_id, writer=writer_b.letter, writer_slug=writer_b.name, writer_letter=writer_b.letter.lower())}"""
    
    console.print("Generating feedback for both writers in parallel...")
    console.print()
    
    # Create fresh layout for feedback prompters (closes previous if exists)
    from ..core.dynamic_layout import DynamicLayout
    from ..core.user_config import get_writer_config
    
    writer_a = get_writer_config("writer_a")
    writer_b = get_writer_config("writer_b")
    boxes = {"prompter_a": f"Prompter A ({writer_a.label})", "prompter_b": f"Prompter B ({writer_b.label})"}
    DynamicLayout.initialize(boxes, lines_per_box=2)
    layout = DynamicLayout
    layout.start()
    
    parser = get_parser("cursor-agent")
    
    async def generate_feedback_a():
        stream = run_agent(PROJECT_ROOT, "sonnet-4.5-thinking", prompt_a, session_id=None, resume=False)
        async for line in stream:
            msg = parser.parse(line)
            if msg:
                formatted = format_stream_message(msg, "Prompter A", "green")
                if formatted:
                    if formatted.startswith("[thinking]"):
                        thinking_text = formatted.replace("[thinking]", "").replace("[/thinking]", "")
                        layout.add_thinking("prompter_a", thinking_text)
                    elif msg.type == "assistant" and msg.content:
                        layout.add_assistant_message("prompter_a", msg.content, "Prompter A", "green")
                    else:
                        layout.add_output(formatted)
            
            if feedback_a_path.exists():
                return
    
    async def generate_feedback_b():
        stream = run_agent(PROJECT_ROOT, "sonnet-4.5-thinking", prompt_b, session_id=None, resume=False)
        async for line in stream:
            msg = parser.parse(line)
            if msg:
                formatted = format_stream_message(msg, "Prompter B", "blue")
                if formatted:
                    if formatted.startswith("[thinking]"):
                        thinking_text = formatted.replace("[thinking]", "").replace("[/thinking]", "")
                        layout.add_thinking("prompter_b", thinking_text)
                    elif msg.type == "assistant" and msg.content:
                        layout.add_assistant_message("prompter_b", msg.content, "Prompter B", "blue")
                    else:
                        layout.add_output(formatted)
            
            if feedback_b_path.exists():
                return
    
    await asyncio.gather(
        generate_feedback_a(),
        generate_feedback_b()
    )
    
    layout.close()
    
    if not feedback_a_path.exists():
        raise RuntimeError(f"Prompter A failed to generate feedback at {feedback_a_path}")
    if not feedback_b_path.exists():
        raise RuntimeError(f"Prompter B failed to generate feedback at {feedback_b_path}")
    
    print_success(f"Created: {feedback_a_path}")
    print_success(f"Created: {feedback_b_path}")
    
    if feedback_a_path.exists() and feedback_b_path.exists():
        console.print()
        print_info("Sending feedback to both writers...")
        from ..automation.dual_feedback import send_dual_feedback
        from ..core.session import load_session
        from ..core.config import WORKTREE_BASE
        
        session_a = load_session("WRITER_A", task_id)
        session_b = load_session("WRITER_B", task_id)
        
        if not session_a:
            raise RuntimeError("No session found for Writer A. Cannot send feedback.")
        if not session_b:
            raise RuntimeError("No session found for Writer B. Cannot send feedback.")
        
        from ..core.user_config import get_writer_config
        writer_a = get_writer_config("writer_a")
        writer_b = get_writer_config("writer_b")
        
        project_name = Path(PROJECT_ROOT).name
        worktree_a = WORKTREE_BASE / project_name / f"writer-{writer_a.name}-{task_id}"
        worktree_b = WORKTREE_BASE / project_name / f"writer-{writer_b.name}-{task_id}"
        
        await send_dual_feedback(
            task_id, feedback_a_path, feedback_b_path,
            session_a, session_b, worktree_a, worktree_b
        )

async def create_pr(task_id: str, winner: str):
    """Create PR automatically."""
    import subprocess
    from ..core.user_config import get_writer_by_key_or_letter
    
    winner_cfg = get_writer_by_key_or_letter(winner)
    branch = f"writer-{winner_cfg.name}/{task_id}"
    
    console.print(f"[green]✅ Creating PR from: {branch}[/green]")
    console.print()
    
    try:
        result = subprocess.run(
            [
                "gh", "pr", "create",
                "--base", "main",
                "--head", branch,
                "--title", f"feat: {task_id}",
                "--body", f"Autonomous implementation via Agent Cube\n\nWinner: Writer {winner}\nBranch: {branch}\n\nReview decisions in `.prompts/decisions/{task_id}-*.json`"
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            pr_url = result.stdout.strip().split('\n')[-1]
            print_success(f"✅ PR created: {pr_url}")
        else:
            print_warning("⚠️  PR creation failed (maybe already exists?)")
            console.print()
            console.print(f"[dim]{result.stderr}[/dim]")
            console.print()
            console.print("Create manually:")
            console.print(f"  gh pr create --base main --head {branch} --title 'feat: {task_id}'")
    
    except FileNotFoundError:
        print_warning("⚠️  gh CLI not installed")
        console.print()
        console.print("Install: https://cli.github.com")
        console.print()
        console.print("Or create PR manually:")
        console.print(f"  gh pr create --base main --head {branch} --title 'feat: {task_id}'")
    
    console.print()
    print_success("🎉 Autonomous workflow complete!")
