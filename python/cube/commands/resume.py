"""Resume command."""

import asyncio
from pathlib import Path

import typer

from ..core.agent import check_cursor_agent, run_agent
from ..core.config import MODELS, PROJECT_ROOT, get_worktree_path
from ..core.output import console, print_error, print_info
from ..core.session import load_session
from ..core.user_config import resolve_writer_alias


async def resume_async(
    target_label: str, task_id: str, message: str, session_id: str, worktree: Path, model: str, color: str = "green"
) -> None:
    """Resume a session asynchronously."""
    from ..automation.stream import format_stream_message
    from ..core.parsers.registry import get_parser
    from ..core.user_config import load_config

    config = load_config()
    cli_name = config.cli_tools.get(model, "cursor-agent")
    parser = get_parser(cli_name)

    stream = run_agent(worktree, model, message, session_id=session_id, resume=True)

    from ..core.single_layout import SingleAgentLayout

    layout = SingleAgentLayout
    layout.initialize(target_label)
    layout.start()

    async for line in stream:
        msg = parser.parse(line)
        if msg:
            if msg.type == "system" and msg.subtype == "init":
                msg.resumed = True
            formatted = format_stream_message(msg, target_label, color)
            if formatted:
                if formatted.startswith("[thinking]"):
                    thinking_text = formatted.replace("[thinking]", "").replace("[/thinking]", "")
                    layout.add_thinking(thinking_text)
                elif msg.type == "assistant" and msg.content:
                    layout.add_assistant_message(msg.content, target_label, color)
                else:
                    layout.add_output(formatted)

    layout.close()


def resume_command(target: str, task_id: str, message: str = None) -> None:
    """Resume a writer or judge session with a message."""

    if not check_cursor_agent():
        print_error("cursor-agent CLI is not installed")
        raise typer.Exit(1)

    # Default message set later based on target type (judge vs writer)
    model = None
    target_label = target
    color = "green"
    writer_cfg = None
    judge_cfg = None

    target_lower = target.lower()

    # Try as judge first
    if target_lower.startswith("judge"):
        try:
            from ..core.user_config import resolve_judge_alias

            judge_cfg = resolve_judge_alias(target)
            if not model:
                model = judge_cfg.model
        except KeyError:
            pass

    # Try as writer if not a judge
    if not judge_cfg:
        try:
            writer_cfg = resolve_writer_alias(target)
            if not model:
                model = MODELS.get(writer_cfg.name, writer_cfg.model)
        except KeyError:
            pass  # Will try orphaned writer metadata below

    if judge_cfg:
        # Try peer-review first (more common for resume), then panel
        session_id = load_session(judge_cfg.key.upper(), f"{task_id}_peer-review")
        session_type = "peer-review"
        if not session_id:
            session_id = load_session(judge_cfg.key.upper(), f"{task_id}_panel")
            session_type = "panel"

        if not session_id:
            print_error(f"Session ID not found for {target}")
            print_info("Run 'cube sessions' to see available sessions")
            raise typer.Exit(1)

        worktree = PROJECT_ROOT
        target_label = judge_cfg.label
        color = judge_cfg.color

        # Build a more specific message for judges if not provided
        if not message:
            judge_key = judge_cfg.key.replace("_", "-")
            decision_file = f".prompts/decisions/{judge_key}-{task_id}-{session_type}.json"
            message = f"""Resume your {session_type} for task: {task_id}

**IMPORTANT: You are a JUDGE, not an orchestrator!**
- Do NOT checkout branches, merge code, or create PRs
- Do NOT push to main or modify the repository
- Your ONLY job is to review code and write your decision

Your decision file: `{decision_file}`

**⚠️ YOU MUST RE-REVIEW THE CODE** - the writer may have made changes!
- Run `git log` to see new commits since your last review
- Run `git diff` to see what changed
- Check each issue from your prior review: is it still there or fixed?
- **OVERWRITE** your decision file with a fresh assessment
- Do NOT say "already reviewed" - always re-check the current code"""
    elif writer_cfg:
        target_label = writer_cfg.label
        color = writer_cfg.color
        session_id = load_session(writer_cfg.key.upper(), task_id)

        if not session_id:
            print_error(f"Session ID not found for {target}")
            print_info("Run 'cube sessions' to see available sessions")
            raise typer.Exit(1)

        project_name = Path(PROJECT_ROOT).name
        worktree = get_worktree_path(project_name, writer_cfg.name, task_id)
    else:
        # Orphaned writer - not in config, try to load from worktree metadata
        from ..core.config import WORKTREE_BASE
        from ..core.writer_metadata import load_writer_metadata

        project_name = Path(PROJECT_ROOT).name
        worktree = WORKTREE_BASE / project_name / f"writer-{target.lower()}-{task_id}"

        # Try to load saved writer metadata
        metadata = load_writer_metadata(target.lower(), task_id)
        if metadata:
            model = metadata.model
            target_label = metadata.label
            color = metadata.color
            writer_key = metadata.key.upper()
        else:
            # No config, no metadata - can't proceed
            from ..core.user_config import get_judge_aliases, get_writer_aliases

            valid = ", ".join(list(get_writer_aliases())[:5] + list(get_judge_aliases())[:5])
            print_error(f"Unknown writer: {target}")
            print_info(f"Not in config and no metadata at .prompts/writers/{target.lower()}-{task_id}.json")
            print_info(f"Known targets: {valid}")
            raise typer.Exit(1)

        session_id = load_session(writer_key, task_id)
        if not session_id:
            print_error(f"Session ID not found for {target} (tried key: {writer_key})")
            print_info("Run 'cube sessions' to see available sessions")
            raise typer.Exit(1)

    if not worktree.exists():
        print_error(f"Worktree not found: {worktree}")
        raise typer.Exit(1)

    # Default message for writers if not provided and not already set (judges set their own)
    if not message:
        message = "Resume from where you left off. Complete any remaining tasks and push your changes."

    print_info(f"Resuming {target} for task: {task_id}")
    console.print()
    console.print("[yellow]📋 Resuming session:[/yellow]")
    console.print(f"  Session ID: [cyan]{session_id}[/cyan]")
    console.print(f"  Message: {message}")
    console.print()

    try:
        asyncio.run(resume_async(target_label, task_id, message, session_id, worktree, model, color))
    except RuntimeError as e:
        print_error(str(e))
        raise typer.Exit(1)


# Backwards compatibility
resume = resume_command
