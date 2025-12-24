"""Phase handlers for orchestration workflow."""

import asyncio
from pathlib import Path

from ...core.agent import run_agent
from ...core.config import PROJECT_ROOT
from ...core.output import console, print_info, print_success
from ...core.parsers.registry import get_parser
from ...core.user_config import get_prompter_model, get_writer_by_key_or_letter, get_writer_config
from ...automation.stream import format_stream_message
from ...automation.judge_panel import launch_judge_panel


async def run_synthesis(task_id: str, result: dict, prompts_dir: Path):
    """Phase 6: Run synthesis if needed."""
    from pathlib import Path as PathLib
    from ...core.user_config import get_judge_configs
    from ...core.single_layout import SingleAgentLayout

    winner_cfg = get_writer_by_key_or_letter(result["winner"])
    winner_name = result["winner"]

    synthesis_path = prompts_dir / f"synthesis-{task_id}.md"

    if not synthesis_path.exists():
        console.print("Generating synthesis prompt...")

        logs_dir = PathLib.home() / ".cube" / "logs"

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

        parser = get_parser("cursor-agent")
        layout = SingleAgentLayout(title="Prompter")
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
    from ..feedback import send_feedback_async
    from ...core.session import load_session
    from ...core.config import WORKTREE_BASE

    session_id = load_session(f"WRITER_{winner_cfg.letter}", task_id)
    if not session_id:
        raise RuntimeError(f"No session found for Writer {winner_name}. Cannot send synthesis.")

    project_name = Path(PROJECT_ROOT).name
    worktree = WORKTREE_BASE / project_name / f"writer-{winner_cfg.name}-{task_id}"
    await send_feedback_async(winner_cfg.name, task_id, synthesis_path, session_id, worktree)


async def run_peer_review(task_id: str, result: dict, prompts_dir: Path):
    """Phase 7: Run peer review."""
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

        from ...core.single_layout import SingleAgentLayout

        parser = get_parser("cursor-agent")
        layout = SingleAgentLayout(title="Prompter")
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
    await launch_judge_panel(task_id, peer_review_path, "peer-review", resume_mode=False, winner=winner_name)


async def run_minor_fixes(task_id: str, result: dict, issues: list, prompts_dir: Path):
    """Address minor issues from peer review."""
    winner_cfg = get_writer_by_key_or_letter(result["winner"])
    winner_name = winner_cfg.name

    minor_fixes_path = prompts_dir / f"minor-fixes-{task_id}.md"

    if minor_fixes_path.exists():
        minor_fixes_path.unlink()

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
    stream = run_agent(PROJECT_ROOT, get_prompter_model(), prompt, session_id=None, resume=False)

    async for line in stream:
        if minor_fixes_path.exists():
            print_success(f"Created: {minor_fixes_path}")
            break

    if minor_fixes_path.exists():
        from ..feedback import send_feedback_async
        from ...core.session import load_session
        from ...core.config import WORKTREE_BASE

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
- `.prompts/decisions/judge_1-{task_id}-decision.json`
- `.prompts/decisions/judge_2-{task_id}-decision.json`
- `.prompts/decisions/judge_3-{task_id}-decision.json`

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

    from ...core.dynamic_layout import DynamicLayout

    writer_a = get_writer_config("writer_a")
    writer_b = get_writer_config("writer_b")
    boxes = {"prompter_a": f"Prompter A ({writer_a.label})", "prompter_b": f"Prompter B ({writer_b.label})"}
    DynamicLayout.initialize(boxes, lines_per_box=2)
    layout = DynamicLayout
    layout.start()

    parser = get_parser("cursor-agent")

    async def generate_feedback_a():
        stream = run_agent(PROJECT_ROOT, get_prompter_model(), prompt_a, session_id=None, resume=False)
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
        stream = run_agent(PROJECT_ROOT, get_prompter_model(), prompt_b, session_id=None, resume=False)
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

        writer_a = get_writer_config("writer_a")
        writer_b = get_writer_config("writer_b")

        project_name = Path(PROJECT_ROOT).name
        worktree_a = WORKTREE_BASE / project_name / f"writer-{writer_a.name}-{task_id}"
        worktree_b = WORKTREE_BASE / project_name / f"writer-{writer_b.name}-{task_id}"

        await send_dual_feedback(
            task_id, feedback_a_path, feedback_b_path,
            session_a, session_b, worktree_a, worktree_b
        )
