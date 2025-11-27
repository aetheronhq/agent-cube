"""Feedback generation functions."""

import asyncio
from pathlib import Path

from ...core.output import print_error, print_success, print_warning, print_info, console
from ...core.config import PROJECT_ROOT
from ...core.agent import run_agent
from ...core.parsers.registry import get_parser
from ...automation.stream import format_stream_message
from ...core.single_layout import SingleAgentLayout

async def generate_dual_feedback(task_id: str, prompts_dir: Path):
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
    
    from ...core.user_config import get_writer_config
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
    from ...core.dynamic_layout import DynamicLayout
    from ...core.user_config import get_writer_config
    
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
        from ...automation.dual_feedback import send_dual_feedback
        from ...core.session import load_session
        from ...core.config import WORKTREE_BASE
        
        session_a = load_session("WRITER_A", task_id)
        session_b = load_session("WRITER_B", task_id)
        
        if not session_a:
            raise RuntimeError("No session found for Writer A. Cannot send feedback.")
        if not session_b:
            raise RuntimeError("No session found for Writer B. Cannot send feedback.")
        
        from ...core.user_config import get_writer_config
        writer_a = get_writer_config("writer_a")
        writer_b = get_writer_config("writer_b")
        
        project_name = Path(PROJECT_ROOT).name
        worktree_a = WORKTREE_BASE / project_name / f"writer-{writer_a.name}-{task_id}"
        worktree_b = WORKTREE_BASE / project_name / f"writer-{writer_b.name}-{task_id}"
        
        await send_dual_feedback(
            task_id, feedback_a_path, feedback_b_path,
            session_a, session_b, worktree_a, worktree_b
        )

async def run_minor_fixes(task_id: str, result: dict, issues: list, prompts_dir: Path):
    """Address minor issues from peer review."""
    from ...core.user_config import get_writer_by_key_or_letter
    
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
        from ...commands.feedback import send_feedback_async
        from ...core.session import load_session
        from ...core.config import WORKTREE_BASE
        from pathlib import Path
        
        session_id = load_session(f"WRITER_{winner_cfg.letter}", task_id)
        if not session_id:
            raise RuntimeError(f"No session found for Writer {winner_cfg.label}. Cannot send minor fixes.")
        
        project_name = Path(PROJECT_ROOT).name
        worktree = WORKTREE_BASE / project_name / f"writer-{winner_name}-{task_id}"
        await send_feedback_async(winner_name, task_id, minor_fixes_path, session_id, worktree)
