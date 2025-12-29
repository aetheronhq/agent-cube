"""Phase execution handlers for Agent Cube workflow."""

from pathlib import Path

from ...core.output import print_success, print_info, console
from ...core.config import PROJECT_ROOT, WORKTREE_BASE
from ...core.agent import run_agent
from ...core.parsers.registry import get_parser
from ...core.user_config import get_prompter_model
from ...automation.stream import format_stream_message
from ...automation.judge_panel import launch_judge_panel


async def run_synthesis(task_id: str, result: dict, prompts_dir: Path):
    """Phase 6: Run synthesis if needed."""
    from ...core.user_config import get_writer_by_key_or_letter
    from ...core.single_layout import SingleAgentLayout

    winner_cfg = get_writer_by_key_or_letter(result["winner"])
    winner_name = result["winner"]

    synthesis_path = prompts_dir / f"synthesis-{task_id}.md"

    if not synthesis_path.exists():
        console.print("Generating synthesis prompt...")

        from ...core.user_config import get_judge_configs
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

    session_id = load_session(f"WRITER_{winner_cfg.letter}", task_id)
    if not session_id:
        raise RuntimeError(f"No session found for Writer {winner_name}. Cannot send synthesis.")

    project_name = Path(PROJECT_ROOT).name
    worktree = WORKTREE_BASE / project_name / f"writer-{winner_cfg.name}-{task_id}"
    await send_feedback_async(winner_cfg.name, task_id, synthesis_path, session_id, worktree)


async def run_peer_review(task_id: str, result: dict, prompts_dir: Path):
    """Phase 7: Run peer review."""
    from ...core.user_config import get_writer_by_key_or_letter
    from ...core.single_layout import SingleAgentLayout

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
    from ...core.user_config import get_writer_by_key_or_letter

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

        if minor_fixes_path.exists():
            layout.close()
            print_success(f"Created: {minor_fixes_path}")
            break

    if not minor_fixes_path.exists():
        layout.close()
        raise RuntimeError(f"Failed to generate minor fixes prompt for {winner_name} (task: {task_id})")

    from ..feedback import send_feedback_async
    from ...core.session import load_session

    session_id = load_session(f"WRITER_{winner_cfg.letter}", task_id)
    if not session_id:
        raise RuntimeError(f"No session found for Writer {winner_cfg.label}. Cannot send minor fixes.")

    project_name = Path(PROJECT_ROOT).name
    worktree = WORKTREE_BASE / project_name / f"writer-{winner_name}-{task_id}"
    await send_feedback_async(winner_name, task_id, minor_fixes_path, session_id, worktree)
