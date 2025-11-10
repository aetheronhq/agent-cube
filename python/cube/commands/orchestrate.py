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

async def orchestrate_auto_command(task_file: str, resume_from: int = 1) -> None:
    """Fully autonomous orchestration - runs entire workflow.
    
    Args:
        task_file: Path to task file
        resume_from: Phase number to resume from (1-10)
    """
    
    task_path = PROJECT_ROOT / task_file
    
    if not task_path.exists():
        raise FileNotFoundError(f"Task file not found: {task_file}")
    
    task_id = extract_task_id_from_file(task_file)
    prompts_dir = PROJECT_ROOT / ".prompts"
    prompts_dir.mkdir(exist_ok=True)
    
    console.print(f"[bold cyan]🤖 Agent Cube Autonomous Orchestration[/bold cyan]")
    console.print(f"Task: {task_id}")
    if resume_from > 1:
        console.print(f"[yellow]Resuming from Phase {resume_from}[/yellow]")
    console.print()
    
    writer_prompt_path = prompts_dir / f"writer-prompt-{task_id}.md"
    panel_prompt_path = prompts_dir / f"panel-prompt-{task_id}.md"
    
    if resume_from <= 1:
        console.print("[yellow]═══ Phase 1: Generate Writer Prompt ═══[/yellow]")
        writer_prompt_path = await generate_writer_prompt(task_id, task_path.read_text(), prompts_dir)
    
    if resume_from <= 2:
        console.print()
        console.print("[yellow]═══ Phase 2: Dual Writers Execute ═══[/yellow]")
        await launch_dual_writers(task_id, writer_prompt_path, resume_mode=False)
    
    if resume_from <= 3:
        console.print()
        console.print("[yellow]═══ Phase 3: Generate Panel Prompt ═══[/yellow]")
        panel_prompt_path = await generate_panel_prompt(task_id, prompts_dir)
    
    if resume_from <= 4:
        console.print()
        console.print("[yellow]═══ Phase 4: Judge Panel Review ═══[/yellow]")
        await launch_judge_panel(task_id, panel_prompt_path, "panel", resume_mode=False)
    
    if resume_from <= 5:
        console.print()
        console.print("[yellow]═══ Phase 5: Aggregate Decisions ═══[/yellow]")
    
    result = run_decide_and_get_result(task_id)
    
    if result["next_action"] == "SYNTHESIS":
        console.print()
        console.print("[yellow]═══ Phase 6: Synthesis ═══[/yellow]")
        await run_synthesis(task_id, result, prompts_dir)
        
        console.print()
        console.print("[yellow]═══ Phase 7: Peer Review ═══[/yellow]")
        await run_peer_review(task_id, result, prompts_dir)
        
        console.print()
        console.print("[yellow]═══ Phase 8: Final Decision ═══[/yellow]")
        final_result = run_decide_peer_review(task_id)
        
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
            
            console.print("[yellow]═══ Phase 9: Address Minor Issues ═══[/yellow]")
            await run_minor_fixes(task_id, result, final_result["remaining_issues"], prompts_dir)
            
            console.print()
            console.print("[yellow]═══ Phase 10: Final Peer Review ═══[/yellow]")
            await run_peer_review(task_id, result, prompts_dir)
            
            final_check = run_decide_peer_review(task_id)
            if final_check["approved"]:
                await create_pr(task_id, result["winner"])
            else:
                print_warning("Still has issues - manual intervention needed")
        else:
            console.print()
            print_warning("Peer review requested more changes - manual intervention needed")
    
    elif result["next_action"] == "FEEDBACK":
        console.print()
        console.print("[yellow]═══ Phase 6: Generate Feedback for Both Writers ═══[/yellow]")
        
        await generate_dual_feedback(task_id, result, prompts_dir)
        
        console.print()
        print_warning("Both writers need major changes. Re-run panel after they complete:")
        console.print(f"  cube panel {task_id} .prompts/panel-prompt-{task_id}.md")
    
    elif result["next_action"] == "MERGE":
        console.print()
        console.print("[yellow]═══ Phase 6: Create PR ═══[/yellow]")
        await create_pr(task_id, result["winner"])
    
    else:
        console.print()
        print_warning(f"Next action: {result['next_action']} - manual intervention needed")

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
    
    decisions_dir = PROJECT_ROOT / ".prompts" / "decisions"
    all_issues = []
    approvals = 0
    decisions_found = 0
    
    console.print(f"[cyan]📊 Checking peer review decisions for: {task_id}[/cyan]")
    console.print()
    
    for judge_num in [1, 2, 3]:
        peer_file = decisions_dir / f"judge-{judge_num}-{task_id}-peer-review.json"
        if peer_file.exists():
            decisions_found += 1
            with open(peer_file) as f:
                data = json.load(f)
                decision = data.get("decision", "UNKNOWN")
                remaining = data.get("remaining_issues", [])
                
                console.print(f"Judge {judge_num}: {decision}")
                if remaining:
                    console.print(f"  Issues: {len(remaining)}")
                    all_issues.extend(remaining)
                
                if decision == "APPROVED":
                    approvals += 1
    
    console.print()
    
    if decisions_found == 0:
        print_warning("No peer review decisions found!")
        console.print("Expected files:")
        for judge_num in [1, 2, 3]:
            console.print(f"  .prompts/decisions/judge-{judge_num}-{task_id}-peer-review.json")
        console.print()
        return {"approved": False, "remaining_issues": []}
    
    console.print(f"Decisions: {decisions_found}/3, Approvals: {approvals}/{decisions_found}")
    
    return {
        "approved": approvals >= 2,
        "remaining_issues": all_issues
    }

async def run_synthesis(task_id: str, result: dict, prompts_dir: Path):
    """Phase 6: Run synthesis if needed."""
    winner = "sonnet" if result["winner"] == "A" else "codex"
    winner_name = result["winner"]
    
    synthesis_path = prompts_dir / f"synthesis-{task_id}.md"
    
    if not synthesis_path.exists():
        console.print("Generating synthesis prompt...")
        
        logs_dir = Path.home() / ".cube" / "logs"
        
        prompt = f"""Generate a synthesis prompt for the WINNING writer.

## Context

Task: {task_id}
Winner: Writer {winner_name} ({winner})
Winner's branch: writer-{winner}/{task_id}
Winner's location: ~/.cube/worktrees/PROJECT/writer-{winner}-{task_id}/

## Available Information

**Judge Decisions (JSON with detailed feedback):**
- `.prompts/decisions/judge-1-{task_id}-decision.json`
- `.prompts/decisions/judge-2-{task_id}-decision.json`
- `.prompts/decisions/judge-3-{task_id}-decision.json`

Read these for full context on what judges liked/disliked.

**Judge Logs (reasoning and analysis):**
- `~/.cube/logs/judge-1-{task_id}-panel-*.json`
- `~/.cube/logs/judge-2-{task_id}-panel-*.json`
- `~/.cube/logs/judge-3-{task_id}-panel-*.json`

Optional: Read for deeper understanding of judge concerns.

## Blocker Issues to Address

{chr(10).join('- ' + issue for issue in result['blocker_issues'])}

## Your Task

Create a synthesis prompt that:
1. References specific files/lines from winner's code
2. Addresses each blocker issue with concrete fixes
3. Preserves what judges liked (winner's architecture)
4. Tells writer to commit and push when complete

Read the judge decisions for full context!

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
                    else:
                        layout.add_output(formatted)
            
            if synthesis_path.exists():
                layout.close()
                print_success(f"Created: {synthesis_path}")
                break
        
        if not synthesis_path.exists():
            console.print(f"Create manually: {synthesis_path}")
            return
    
    print_info(f"Sending synthesis to Writer {winner_name}")
    from .feedback import send_feedback_async
    from ..core.session import load_session
    from ..core.config import WORKTREE_BASE
    from pathlib import Path
    
    session_id = load_session(f"WRITER_{'A' if winner == 'sonnet' else 'B'}", task_id)
    if session_id:
        project_name = Path(PROJECT_ROOT).name
        worktree = WORKTREE_BASE / project_name / f"writer-{winner}-{task_id}"
        await send_feedback_async(winner, task_id, synthesis_path, session_id, worktree)

async def run_peer_review(task_id: str, result: dict, prompts_dir: Path):
    """Phase 7: Run peer review."""
    winner = "sonnet" if result["winner"] == "A" else "codex"
    winner_name = result["winner"]
    
    peer_review_path = prompts_dir / f"peer-review-{task_id}.md"
    
    if not peer_review_path.exists():
        console.print("Generating peer review prompt...")
        
        prompt = f"""Generate a peer review prompt for the WINNING writer.

## Context

Task: {task_id}
Winner: Writer {winner_name} ({winner})
Branch: writer-{winner}/{task_id}

## Your Task

Create a peer review prompt that tells the 3 judges to:
1. Review ONLY Writer {winner_name}'s updated implementation
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
                    else:
                        layout.add_output(formatted)
            
            if peer_review_path.exists():
                layout.close()
                print_success(f"Created: {peer_review_path}")
                break
        
        if not peer_review_path.exists():
            console.print(f"Create manually: {peer_review_path}")
            return
    
    print_info(f"Launching peer review for Winner: Writer {winner_name}")
    await launch_judge_panel(task_id, peer_review_path, "panel", resume_mode=True)

async def run_minor_fixes(task_id: str, result: dict, issues: list, prompts_dir: Path):
    """Address minor issues from peer review."""
    winner = "sonnet" if result["winner"] == "A" else "codex"
    
    minor_fixes_path = prompts_dir / f"minor-fixes-{task_id}.md"
    
    prompt = f"""Generate a minor fixes prompt for the winning writer.

## Context

Winner: Writer {result['winner']} ({winner})

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
        
        session_id = load_session(f"WRITER_{'A' if winner == 'sonnet' else 'B'}", task_id)
        if session_id:
            project_name = Path(PROJECT_ROOT).name
            worktree = WORKTREE_BASE / project_name / f"writer-{winner}-{task_id}"
            await send_feedback_async(winner, task_id, minor_fixes_path, session_id, worktree)

async def generate_dual_feedback(task_id: str, result: dict, prompts_dir: Path):
    """Generate feedback prompts for both writers in parallel with dual layout."""
    from ..core.dual_layout import get_dual_layout, DualWriterLayout
    
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
    
    prompt_a = f"""Generate a feedback prompt for Writer A (Sonnet).

Task: {task_id}
Both writers need changes based on judge reviews.

{prompt_base.format(task_id=task_id, writer='A', writer_slug='sonnet', writer_letter='a')}"""
    
    prompt_b = f"""Generate a feedback prompt for Writer B (Codex).

Task: {task_id}
Both writers need changes based on judge reviews.

{prompt_base.format(task_id=task_id, writer='B', writer_slug='codex', writer_letter='b')}"""
    
    console.print("Generating feedback for both writers in parallel...")
    console.print()
    
    DualWriterLayout.reset()
    layout = get_dual_layout()
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
                        layout.add_thinking("A", thinking_text)
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
                        layout.add_thinking("B", thinking_text)
                    else:
                        layout.add_output(formatted)
            
            if feedback_b_path.exists():
                return
    
    await asyncio.gather(
        generate_feedback_a(),
        generate_feedback_b()
    )
    
    layout.close()
    
    if feedback_a_path.exists():
        print_success(f"Created: {feedback_a_path}")
    if feedback_b_path.exists():
        print_success(f"Created: {feedback_b_path}")
    
    if feedback_a_path.exists() and feedback_b_path.exists():
        console.print()
        print_info("Sending feedback to both writers...")
        from ..automation.dual_feedback import send_dual_feedback
        from ..core.session import load_session
        from ..core.config import WORKTREE_BASE
        
        session_a = load_session("WRITER_A", task_id)
        session_b = load_session("WRITER_B", task_id)
        
        project_name = Path(PROJECT_ROOT).name
        worktree_a = WORKTREE_BASE / project_name / f"writer-sonnet-{task_id}"
        worktree_b = WORKTREE_BASE / project_name / f"writer-codex-{task_id}"
        
        if session_a and session_b:
            await send_dual_feedback(
                task_id, feedback_a_path, feedback_b_path,
                session_a, session_b, worktree_a, worktree_b
            )

async def create_pr(task_id: str, winner: str):
    """Create PR."""
    winner_name = "sonnet" if winner == "A" else "codex"
    branch = f"writer-{winner_name}/{task_id}"
    
    console.print(f"[green]✅ Ready to create PR from: {branch}[/green]")
    console.print()
    console.print("Manual PR creation:")
    console.print(f"  gh pr create --base main --head {branch} --title 'feat: {task_id}'")
    console.print()
    print_success("Autonomous workflow complete! 🎉")
