"""Phase execution handlers for Agent Cube workflow."""

import json
from pathlib import Path

from ...automation.judge_panel import launch_judge_panel
from ...automation.stream import format_stream_message
from ...core.agent import run_agent
from ...core.config import PROJECT_ROOT, WORKTREE_BASE
from ...core.output import console, print_info, print_success
from ...core.parsers.registry import get_parser
from ...core.session import get_prompter_session, save_prompter_session
from ...core.user_config import get_prompter_model


def _normalize_issue(issue) -> str:
    """Convert issue to string. Issues can be strings or dicts with file/line/issue keys."""
    if isinstance(issue, str):
        return issue
    if isinstance(issue, dict):
        # Handle inline comment format: {'file': '...', 'line': N, 'issue': '...'}
        if "issue" in issue:
            file_info = f"{issue.get('file', '')}:{issue.get('line', '')}" if issue.get("file") else ""
            return f"{file_info} {issue['issue']}" if file_info else issue["issue"]
        # Fallback: convert dict to string
        return str(issue)
    return str(issue)


async def run_prompter_with_session(task_id: str, prompt: str, layout, output_path, label: str = "Prompter"):
    """Run prompter with session management.

    Resumes existing session if available, otherwise captures and saves new session ID.
    """
    parser = get_parser("cursor-agent")
    session_id, should_resume = get_prompter_session(task_id)
    captured_session_id: str | None = None

    stream = run_agent(PROJECT_ROOT, get_prompter_model(), prompt, session_id=session_id, resume=should_resume)

    async for line in stream:
        # Capture session ID from first line if starting fresh
        if not should_resume and not captured_session_id:
            try:
                data = json.loads(line)
                if "session_id" in data:
                    captured_session_id = data["session_id"]
            except (json.JSONDecodeError, TypeError):
                pass

        msg = parser.parse(line)
        if msg:
            if msg.type == "system" and msg.subtype == "init":
                msg.resumed = should_resume
            formatted = format_stream_message(msg, label, "cyan")
            if formatted:
                if formatted.startswith("[thinking]"):
                    thinking_text = formatted.replace("[thinking]", "").replace("[/thinking]", "")
                    layout.add_thinking(thinking_text)
                elif msg.type == "assistant" and msg.content:
                    layout.add_assistant_message(msg.content, label, "cyan")
                else:
                    layout.add_output(formatted)

        if output_path.exists():
            print_success(f"Created: {output_path}")
            break

    # Save session ID if we captured a new one
    if captured_session_id and not should_resume:
        save_prompter_session(task_id, captured_session_id)

    if not output_path.exists():
        raise RuntimeError(f"Prompter failed to generate {output_path}")


async def run_synthesis(task_id: str, result: dict, prompts_dir: Path):
    """Phase 6: Run synthesis if needed."""
    import json

    from ...core.single_layout import SingleAgentLayout
    from ...core.user_config import get_writer_by_key_or_metadata

    winner_cfg = get_writer_by_key_or_metadata(result["winner"], task_id)
    winner_name = result["winner"]

    synthesis_path = prompts_dir / f"synthesis-{task_id}.md"

    if not synthesis_path.exists():
        console.print("Generating synthesis prompt...")

        from ...core.user_config import get_judge_configs

        judge_configs = get_judge_configs()
        judge_decision_files = "\n".join(
            [f"- `.prompts/decisions/{j.key}-{task_id}-decision.json`" for j in judge_configs]
        )
        judge_log_files = "\n".join([f"- `~/.cube/logs/{j.key}-{task_id}-panel-*.json`" for j in judge_configs])

        blocker_issues = result.get("blocker_issues", [])
        if not blocker_issues:
            decisions_dir = prompts_dir / "decisions"
            for j in judge_configs:
                decision_file = decisions_dir / f"{j.key}-{task_id}-decision.json"
                if decision_file.exists():
                    try:
                        data = json.loads(decision_file.read_text())
                        blocker_issues.extend(data.get("blocker_issues", []))
                    except (json.JSONDecodeError, OSError):
                        pass

        blocker_section = (
            chr(10).join("- " + _normalize_issue(issue) for issue in blocker_issues)
            if blocker_issues
            else "(Read judge decision files for issues)"
        )

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

{blocker_section}

## Your Task

Create a synthesis prompt that:
1. **First step**: Tell writer to merge latest main (`git fetch origin main && git merge origin/main --no-edit`) and fix any conflicts programmatically using read_file/write_file (no interactive editors!)
2. **Points writer to their review file** (from `review_output_files` in CodeRabbit decision)
3. Lists blocker issues that MUST be fixed
4. References specific files/lines from winner's code
5. Tells writer to READ the review file for full context and "Prompt for AI Agent" sections
6. Preserves what judges liked (winner's architecture)
7. Tells writer to commit and push when complete

**CRITICAL:** The CodeRabbit review file contains:
- Full output with code diffs
- "Prompt for AI Agent" sections with detailed fix instructions
- ALL issues, not just blockers

Tell the winner: "Read `.prompts/reviews/{task_id}-writer-{{a|b}}-coderabbit.txt` for full details"

Save to: `.prompts/synthesis-{task_id}.md`"""

        layout = SingleAgentLayout
        layout.initialize("Prompter")
        layout.start()

        try:
            await run_prompter_with_session(task_id, prompt, layout, synthesis_path)
        finally:
            layout.close()

    print_info(f"Sending synthesis to {winner_cfg.label}")
    from ...core.session import load_session
    from ..feedback import send_feedback_async

    session_id = load_session(winner_cfg.key.upper(), task_id)
    if not session_id:
        raise RuntimeError(f"No session found for {winner_cfg.label}. Cannot send synthesis.")

    project_name = Path(PROJECT_ROOT).name
    worktree = WORKTREE_BASE / project_name / f"writer-{winner_cfg.name}-{task_id}"
    await send_feedback_async(
        task_id=task_id,
        feedback_file=synthesis_path,
        session_id=session_id,
        worktree=worktree,
        writer_name=winner_cfg.name,
        writer_model=winner_cfg.model,
        writer_label=winner_cfg.label,
        writer_key=winner_cfg.key,
        writer_color=winner_cfg.color,
    )


async def run_peer_review(
    task_id: str,
    result: dict,
    prompts_dir: Path,
    run_all_judges: bool = False,
    judges_to_run: list = None,
    resume_mode: bool = False,
):
    """Phase 7: Run peer review. Set run_all_judges=True for single writer mode, or pass specific judges_to_run."""
    from ...core.single_layout import SingleAgentLayout
    from ...core.user_config import get_writer_by_key_or_metadata

    winner_cfg = get_writer_by_key_or_metadata(result["winner"], task_id)

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

        layout = SingleAgentLayout
        layout.initialize("Prompter")
        layout.start()

        try:
            await run_prompter_with_session(task_id, prompt, layout, peer_review_path)
        finally:
            layout.close()

    print_info(f"Launching peer review for Winner: {winner_cfg.label}")
    await launch_judge_panel(
        task_id,
        peer_review_path,
        "peer-review",
        resume_mode=resume_mode,
        winner=result["winner"],
        run_all_judges=run_all_judges,
        judges_to_run=judges_to_run,
    )


async def run_minor_fixes(
    task_id: str,
    result: dict,
    issues: list,
    prompts_dir: Path,
    fresh_writer: bool = False,
    resume_prompt: str | None = None,
):
    """Address minor issues from peer review."""
    from ...core.user_config import get_writer_by_key_or_metadata

    winner_cfg = get_writer_by_key_or_metadata(result["winner"], task_id)
    winner_name = winner_cfg.name

    minor_fixes_path = prompts_dir / f"minor-fixes-{task_id}.md"

    if minor_fixes_path.exists():
        minor_fixes_path.unlink()

    branch_name = f"writer-{winner_name}/{task_id}"

    # Include additional context if provided
    additional_context = ""
    if resume_prompt:
        additional_context = f"""
## Additional Context from User

{resume_prompt}

"""

    prompt = f"""Generate a minor fixes prompt for the winning writer.

## Context

Winner: Writer {result['winner']} ({winner_cfg.label})
Branch: `{branch_name}`
Worktree: `~/.cube/worktrees/{Path(PROJECT_ROOT).name}/writer-{winner_name}-{task_id}/`
{additional_context}
## Minor Issues from Peer Review

{chr(10).join('- ' + _normalize_issue(issue) for issue in issues)}

## Your Task

Create a brief prompt telling the winner to:
1. **First**: Merge latest main (`git fetch origin main && git merge origin/main --no-edit`) and fix any conflicts programmatically using read_file/write_file (no interactive editors!)
2. Address the minor issues listed above
3. Keep their implementation intact, just fix these specific points
4. Commit and push when complete

**CRITICAL**: Include these warnings in the prompt:
- ⚠️ DO NOT create new branches! Stay on `{branch_name}`
- ⚠️ DO NOT checkout other branches
- ⚠️ Work only in your worktree directory
- ⚠️ Commit and push to your existing branch

Save to: `.prompts/minor-fixes-{task_id}.md`"""

    from ...core.single_layout import SingleAgentLayout

    layout = SingleAgentLayout
    layout.initialize("Prompter")
    layout.start()

    try:
        await run_prompter_with_session(task_id, prompt, layout, minor_fixes_path)
    finally:
        layout.close()

    from ...core.session import load_session
    from ..feedback import send_feedback_async

    session_id = None if fresh_writer else load_session(winner_cfg.key.upper(), task_id)
    if not session_id and not fresh_writer:
        raise RuntimeError(f"No session found for {winner_cfg.label}. Use --fresh-writer to start new.")

    project_name = Path(PROJECT_ROOT).name
    worktree = WORKTREE_BASE / project_name / f"writer-{winner_name}-{task_id}"
    await send_feedback_async(
        task_id=task_id,
        feedback_file=minor_fixes_path,
        session_id=session_id,
        worktree=worktree,
        writer_name=winner_cfg.name,
        writer_model=winner_cfg.model,
        writer_label=winner_cfg.label,
        writer_key=winner_cfg.key,
        writer_color=winner_cfg.color,
    )
