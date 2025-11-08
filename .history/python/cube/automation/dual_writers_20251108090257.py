"""Parallel dual writer execution."""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..core.agent import run_agent
from ..core.git import (
    create_worktree, has_uncommitted_changes, has_unpushed_commits, 
    commit_and_push
)
from ..core.session import save_session, load_session, SessionWatcher
from ..core.output import print_info, print_success, print_warning, console
from ..core.config import PROJECT_ROOT, get_sessions_dir, WRITER_LETTERS
from ..core.user_config import get_writer_config
from ..models.types import WriterInfo

async def run_writer(writer_info: WriterInfo, prompt: str, resume: bool) -> None:
    """Run a single writer agent."""
    from ..automation.stream import format_stream_message
    from ..core.user_config import load_config as load_user_config
    from ..core.parsers.registry import get_parser
    from ..core.shared_teleprompt import get_shared_teleprompt
    
    config = load_user_config()
    cli_name = config.cli_tools.get(writer_info.model, "cursor-agent")
    parser = get_parser(cli_name)
    teleprompt = get_shared_teleprompt()
    
    log_file = Path(f"/tmp/writer-{writer_info.name}-{writer_info.task_id}-{int(datetime.now().timestamp())}.json")
    
    session_file = get_sessions_dir() / f"WRITER_{writer_info.letter}_{writer_info.task_id}_SESSION_ID.txt"
    metadata = f"Writer {writer_info.letter} ({writer_info.model}) - {writer_info.task_id} - {datetime.now()}"
    
    watcher = SessionWatcher(log_file, session_file, metadata)
    watcher.start()
    
    line_count = 0
    try:
        with open(log_file, 'w') as f:
            session_id = writer_info.session_id if resume else None
            
            stream = run_agent(
                writer_info.worktree,
                writer_info.model,
                prompt,
                session_id=session_id,
                resume=resume
            )
            
            async for line in stream:
                line_count += 1
                f.write(line + '\n')
                f.flush()
                
                msg = parser.parse(line)
                if msg:
                    if msg.session_id and not writer_info.session_id:
                        writer_info.session_id = msg.session_id
                    
                    formatted = format_stream_message(msg, writer_info.label, writer_info.color)
                    if formatted:
                        if formatted.startswith("[thinking]"):
                            thinking_text = formatted.replace("[thinking]", "").replace("[/thinking]", "")
                            teleprompt.add_token(writer_info.letter, thinking_text)
                        else:
                            console.print(formatted)
    finally:
        watcher.stop()
    
    if line_count < 10:
        raise RuntimeError(f"{writer_info.label} completed suspiciously quickly ({line_count} lines). Check {log_file} for errors.")
    
    console.print(f"[{writer_info.color}][{writer_info.label}][/{writer_info.color}] ✅ Completed")

async def launch_dual_writers(
    task_id: str,
    prompt_file: Path,
    resume_mode: bool = False
) -> None:
    """Launch two writers in parallel."""
    
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    
    prompt = prompt_file.read_text()
    project_name = Path(PROJECT_ROOT).name
    
    writers = []
    for writer_key in ["writer_a", "writer_b"]:
        wconfig = get_writer_config(writer_key)
        worktree = create_worktree(task_id, wconfig.name)
        branch = f"writer-{wconfig.name}/{task_id}"
        
        session_id = None
        if resume_mode:
            letter = WRITER_LETTERS[wconfig.name]
            session_id = load_session(f"WRITER_{letter}", task_id)
            if not session_id:
                raise RuntimeError(f"No session found for writer {wconfig.name}")
        
        writer = WriterInfo(
            name=wconfig.name,
            model=wconfig.model,
            color=wconfig.color,
            label=wconfig.label,
            letter=WRITER_LETTERS[wconfig.name],
            task_id=task_id,
            worktree=worktree,
            branch=branch,
            session_id=session_id
        )
        writers.append(writer)
    
    if resume_mode:
        print_info(f"Resuming Dual Writers for Task: {task_id}")
        console.print()
        console.print("[yellow]📋 Found existing sessions to resume:[/yellow]")
        for writer in writers:
            console.print(f"  [{writer.color}]{writer.label}[/{writer.color}]: {writer.session_id}")
        console.print()
    else:
        print_info(f"Launching Dual Writers for Task: {task_id}")
    
    print_info(f"Prompt: {prompt_file}")
    console.print()
    
    console.print()
    console.print("🚀 Launching writers in parallel...")
    console.print()
    
    await asyncio.gather(
        run_writer(writers[0], prompt, resume_mode),
        run_writer(writers[1], prompt, resume_mode)
    )
    
    console.print()
    console.print("✅ Both writers completed")
    console.print()
    
    console.print("📤 Ensuring all changes are committed and pushed...")
    console.print()
    
    for writer in writers:
        if has_uncommitted_changes(writer.worktree):
            print_info(f"{writer.label}: Committing uncommitted changes...")
            message = f"{writer.label} ({writer.model}) - Task: {task_id}\n\nAuto-commit of remaining changes at end of session."
            if commit_and_push(writer.worktree, writer.branch, message):
                print_success(f"{writer.label}: Changes committed and pushed")
            else:
                print_warning(f"{writer.label}: Failed to commit/push")
        else:
            print_success(f"{writer.label}: All changes already committed")
            
            if has_unpushed_commits(writer.worktree, writer.branch):
                print_info(f"{writer.label}: Pushing unpushed commits...")
                commit_and_push(writer.worktree, writer.branch, "")
    
    console.print()
    print_success("All changes committed and pushed!")
    console.print()
    console.print("Next steps:")
    console.print(f"  1. Review both branches")
    console.print(f"  2. Run: cube-py panel {task_id} <panel-prompt-file>")

