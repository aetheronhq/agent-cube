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
from ..core.config import (
    MODELS, WRITER_COLORS, WRITER_LABELS, WRITER_LETTERS,
    PROJECT_ROOT, get_sessions_dir
)
from ..models.types import WriterInfo
from .stream import parse_and_format_stream

async def run_writer(writer_info: WriterInfo, prompt: str, resume: bool) -> None:
    """Run a single writer agent."""
    log_file = Path(f"/tmp/writer-{writer_info.name}-{writer_info.task_id}-{int(datetime.now().timestamp())}.json")
    
    session_file = get_sessions_dir() / f"WRITER_{writer_info.letter}_{writer_info.task_id}_SESSION_ID.txt"
    metadata = f"Writer {writer_info.letter} ({writer_info.model}) - {writer_info.task_id} - {datetime.now()}"
    
    watcher = SessionWatcher(log_file, session_file, metadata)
    watcher.start()
    
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
                f.write(line + '\n')
                f.flush()
                
                parsed_stream = parse_and_format_stream(
                    async_gen_from_line(line),
                    writer_info.label,
                    writer_info.color
                )
                
                async for formatted, sess_id in parsed_stream:
                    if formatted:
                        console.print(formatted)
                    if sess_id and not writer_info.session_id:
                        writer_info.session_id = sess_id
    finally:
        watcher.stop()
    
    console.print(f"[{writer_info.color}][{writer_info.label}][/{writer_info.color}] ✅ Completed")

async def async_gen_from_line(line: str):
    """Convert a single line to an async generator."""
    yield line

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
    for writer_name in ["sonnet", "codex"]:
        worktree = create_worktree(task_id, writer_name)
        branch = f"writer-{writer_name}/{task_id}"
        
        session_id = None
        if resume_mode:
            letter = WRITER_LETTERS[writer_name]
            session_id = load_session(f"WRITER_{letter}", task_id)
            if not session_id:
                raise RuntimeError(f"No session found for writer {writer_name}")
        
        writer = WriterInfo(
            name=writer_name,
            model=MODELS[writer_name],
            color=WRITER_COLORS[writer_name],
            label=WRITER_LABELS[writer_name],
            letter=WRITER_LETTERS[writer_name],
            task_id=task_id,
            worktree=worktree,
            branch=branch,
            session_id=session_id
        )
        writers.append(writer)
    
    if resume_mode:
        print_info(f"Resuming Dual Writers for Task: {task_id}")
    else:
        print_info(f"Launching Dual Writers for Task: {task_id}")
    
    print_info(f"Prompt: {prompt_file}")
    console.print()
    
    console.print(f"📊 {writers[0].label} (PID: ...)")
    console.print(f"📊 {writers[1].label} (PID: ...)")
    console.print()
    console.print("⏳ Waiting for both writers to complete...")
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

