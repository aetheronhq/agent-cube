"""Resume command."""

import asyncio
from pathlib import Path
import typer

from ..core.agent import check_cursor_agent, run_agent
from ..core.session import load_session
from ..core.output import print_error, print_info, console
from ..core.config import PROJECT_ROOT, MODELS, get_worktree_path
from ..core.user_config import get_judge_config, resolve_writer_alias
async def resume_async(
    target_label: str,
    task_id: str,
    message: str,
    session_id: str,
    worktree: Path,
    model: str,
    color: str = "green"
) -> None:
    """Resume a session asynchronously."""
    from ..automation.stream import format_stream_message
    from ..core.user_config import load_config
    from ..core.parsers.registry import get_parser
    
    config = load_config()
    cli_name = config.cli_tools.get(model, "cursor-agent")
    parser = get_parser(cli_name)
    
    stream = run_agent(
        worktree,
        model,
        message,
        session_id=session_id,
        resume=True
    )
    
    from ..core.single_layout import SingleAgentLayout
    
    layout = SingleAgentLayout(title=target_label)
    layout.start()
    
    async for line in stream:
        msg = parser.parse(line)
        if msg:
            formatted = format_stream_message(msg, target_label, color)
            if formatted:
                if formatted.startswith("[thinking]"):
                    thinking_text = formatted.replace("[thinking]", "").replace("[/thinking]", "")
                    layout.add_thinking(thinking_text)
                elif msg.type == "assistant" and msg.content:
                    layout.add_assistant_message("agent", msg.content, target_label, color)
                else:
                    layout.add_output(formatted)
    
    layout.close()

def resume_command(
    target: str,
    task_id: str,
    message: str = None
) -> None:
    """Resume a writer or judge session with a message."""
    
    if not check_cursor_agent():
        print_error("cursor-agent CLI is not installed")
        raise typer.Exit(1)
    
    if not message:
        message = "Resume from where you left off. Complete any remaining tasks and push your changes."
    
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
            model = judge_cfg.model
        except KeyError:
            pass
    
    # Try as writer if not a judge
    if not judge_cfg:
        try:
            writer_cfg = resolve_writer_alias(target)
            model = MODELS.get(writer_cfg.name, writer_cfg.model)
        except KeyError:
            from ..core.user_config import get_writer_aliases, get_judge_aliases
            valid = ", ".join(list(get_writer_aliases())[:5] + list(get_judge_aliases())[:5])
            print_error(f"Invalid target: {target}. Examples: {valid}")
            raise typer.Exit(1) from None
    
    if judge_cfg:
        session_id = load_session(judge_cfg.key.upper(), f"{task_id}_panel")
        if not session_id:
            session_id = load_session(judge_cfg.key.upper(), f"{task_id}_peer-review")
        
        if not session_id:
            print_error(f"Session ID not found for {target}")
            print_info("Run 'cube sessions' to see available sessions")
            raise typer.Exit(1)
        
        worktree = PROJECT_ROOT
        target_label = judge_cfg.label
        color = judge_cfg.color
    else:
        target_label = writer_cfg.label
        color = writer_cfg.color
        session_id = load_session(writer_cfg.key.upper(), task_id)
        
        if not session_id:
            print_error(f"Session ID not found for {target}")
            print_info("Run 'cube sessions' to see available sessions")
            raise typer.Exit(1)
        
        project_name = Path(PROJECT_ROOT).name
        worktree = get_worktree_path(project_name, writer_cfg.name, task_id)
    
    if not worktree.exists():
        print_error(f"Worktree not found: {worktree}")
        raise typer.Exit(1)
    
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

