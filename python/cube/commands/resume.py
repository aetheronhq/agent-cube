"""Resume command."""

import asyncio
from pathlib import Path
import typer

from ..core.agent import check_cursor_agent, run_agent
from ..core.session import load_session
from ..core.output import print_error, print_info, console
from ..core.config import PROJECT_ROOT, MODELS, get_worktree_path, WRITER_LETTERS
from ..core.user_config import get_judge_config, get_writer_config_by_slug, get_writer_slugs, resolve_writer_alias
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
    
    writer_name = None
    writer_letter = None
    judge_num = None
    model = None
    target_label = target
    color = "green"
    
    target_lower = target.lower()
    
    if target_lower.startswith("judge-"):
        try:
            judge_num = int(target_lower.split("-")[1])
            if judge_num not in [1, 2, 3]:
                raise ValueError()
            
            jconfig = get_judge_config(judge_num)
            model = jconfig.model
        except:
            print_error(f"Invalid target: {target} (must be writer-sonnet, writer-codex, or judge-1/2/3)")
            raise typer.Exit(1)
    else:
        try:
            writer_cfg = resolve_writer_alias(target)
            writer_name = writer_cfg.name
        except KeyError:
            print_error(f"Invalid target: {target} (must be writer-sonnet, writer-codex, or judge-1/2/3)")
            raise typer.Exit(1)
    
    if writer_name:
        writer_letter = writer_cfg.letter
        model = MODELS.get(writer_name, writer_cfg.model)
    else:
        writer_cfg = None
    
    if judge_num:
        session_id = load_session(f"JUDGE_{judge_num}", f"{task_id}_panel")
        if not session_id:
            session_id = load_session(f"JUDGE_{judge_num}", f"{task_id}_peer-review")
        
        if not session_id:
            print_error(f"Session ID not found for {target}")
            print_info("Run 'cube sessions' to see available sessions")
            raise typer.Exit(1)
        
        worktree = PROJECT_ROOT
        target_label = f"judge-{judge_num}"
        color = "yellow"
    else:
        target_label = writer_cfg.label
        color = writer_cfg.color
        session_id = load_session(f"WRITER_{writer_letter}", task_id)
        
        if not session_id:
            print_error(f"Session ID not found for {target}")
            print_info("Run 'cube sessions' to see available sessions")
            raise typer.Exit(1)
        
        project_name = Path(PROJECT_ROOT).name
        worktree = get_worktree_path(project_name, writer_name, task_id)
    
    if not worktree.exists():
        print_error(f"Worktree not found: {worktree}")
        raise typer.Exit(1)
    
    print_info(f"Resuming {target} for task: {task_id}")
    console.print()
    console.print("[yellow]📋 Resuming session:[/yellow]")
    console.print(f"  Session ID: [cyan]{session_id}[/cyan]")
    console.print(f"  Message: {message}")
    console.print()
    
    asyncio.run(resume_async(target_label, task_id, message, session_id, worktree, model, color))

