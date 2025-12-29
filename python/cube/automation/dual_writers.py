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
from ..core.session import save_session, load_session
from ..core.output import print_info, print_success, print_warning, print_error, console
from ..core.config import PROJECT_ROOT
from ..core.user_config import get_writer_config
from ..models.types import WriterInfo

async def run_writer(writer_info: WriterInfo, prompt: str, resume: bool) -> None:
    """Run a single writer agent."""
    from ..automation.stream import format_stream_message
    from ..core.user_config import load_config as load_user_config
    from ..core.parsers.registry import get_parser
    from ..core.dynamic_layout import DynamicLayout
    from ..core.agent_logger import agent_logging_context
    
    config = load_user_config()
    cli_name = config.cli_tools.get(writer_info.model, "cursor-agent")
    parser = get_parser(cli_name)
    
    # Get layout (initialize done in launch_dual_writers)
    layout = DynamicLayout
    layout.start()
    
    session_id = writer_info.session_id if resume else None
    
    stream = run_agent(
        writer_info.worktree,
        writer_info.model,
        prompt,
        session_id=session_id,
        resume=resume
    )
    
    # Box key for layout operations - use config key (writer_a, writer_b)
    box_key = writer_info.key
    
    # Use generic logging context
    async with agent_logging_context(
        agent_type="writer",
        agent_name=writer_info.name,
        task_id=writer_info.task_id,
        session_key=writer_info.key.upper(),
        session_task_key=writer_info.task_id,
        metadata=f"{writer_info.label} ({writer_info.model}) - {writer_info.task_id} - {datetime.now()}"
    ) as logger:
        async for line in stream:
            logger.write_line(line)
            
            msg = parser.parse(line)
            if msg:
                if msg.session_id and not writer_info.session_id:
                    writer_info.session_id = msg.session_id
                
                formatted = format_stream_message(msg, writer_info.label, writer_info.color)
                if formatted:
                    if formatted.startswith("[thinking]"):
                        thinking_text = formatted.replace("[thinking]", "").replace("[/thinking]", "")
                        layout.add_thinking(box_key, thinking_text)
                    elif msg.type == "assistant" and msg.content:
                        layout.add_assistant_message(box_key, msg.content, writer_info.label, writer_info.color)
                    else:
                        layout.add_output(formatted)
        
        if logger.line_count < 10:
            raise RuntimeError(f"{writer_info.label} completed suspiciously quickly ({logger.line_count} lines). Check {logger.log_file} for errors.")
        
        final_line_count = logger.line_count
    
    status = f"{final_line_count} events"
    
    try:
        import subprocess
        result = subprocess.run(
            ["git", "diff", "--stat", "HEAD"],
            cwd=writer_info.worktree,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout:
            lines = result.stdout.strip().split('\n')
            if lines:
                files_changed = len([line for line in lines if '|' in line])
                if files_changed > 0:
                    status = f"{files_changed} file{'s' if files_changed != 1 else ''}"
    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
        pass
    
    layout.mark_complete(box_key, status)
    console.print(f"[{writer_info.color}][{writer_info.label}][/{writer_info.color}] ✅ Completed")

async def launch_dual_writers(
    task_id: str,
    prompt_file: Path,
    resume_mode: bool = False
) -> None:
    """Launch two writers in parallel."""
    
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    
    # Create fresh layout for this run (closes previous if exists)
    from ..core.dynamic_layout import DynamicLayout
    
    writer_a = get_writer_config("writer_a")
    writer_b = get_writer_config("writer_b")
    boxes = {"writer_a": writer_a.label, "writer_b": writer_b.label}
    DynamicLayout.initialize(boxes, lines_per_box=3)
    layout = DynamicLayout
    
    # Create minimal state file for UI tracking
    if not resume_mode:
        from ..core.state import save_state, WorkflowState
        state = WorkflowState(
            task_id=task_id,
            current_phase=2,
            path="INIT",
            completed_phases=[1, 2],
            writers_complete=False
        )
        save_state(state)
    
    prompt = prompt_file.read_text()
    project_name = Path(PROJECT_ROOT).name
    
    writers = []
    for writer_key in ["writer_a", "writer_b"]:
        wconfig = get_writer_config(writer_key)
        worktree = create_worktree(task_id, wconfig.name)
        branch = f"writer-{wconfig.name}/{task_id}"
        
        session_id = None
        if resume_mode:
            session_id = load_session(wconfig.key.upper(), task_id)
            if not session_id:
                raise RuntimeError(f"No session found for writer {wconfig.name}")
        
        writer = WriterInfo(
            key=wconfig.key,
            name=wconfig.name,
            model=wconfig.model,
            color=wconfig.color,
            label=wconfig.label,
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
    
    # Show which models/CLIs are being used
    from ..core.user_config import load_config
    config = load_config()
    for w in writers:
        cli_name = config.cli_tools.get(w.model, "cursor-agent")
        console.print(f"[dim]{w.label}: Starting with model {w.model} (CLI: {cli_name})...[/dim]")
    console.print()
    
    results = await asyncio.gather(
        run_writer(writers[0], prompt, resume_mode),
        run_writer(writers[1], prompt, resume_mode),
        return_exceptions=True
    )
    
    from ..core.dynamic_layout import DynamicLayout
    DynamicLayout.close()
    
    errors = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            errors.append((writers[i], result))
    
    console.print()
    
    if errors:
        print_error("Some writers failed:")
        for writer, error in errors:
            console.print(f"  [{writer.color}]{writer.label}[/{writer.color}]: {error}")
        
        if len(errors) == 2:
            raise RuntimeError("Both writers failed")
        else:
            print_warning("One writer failed but the other completed successfully")
            console.print()
    else:
        console.print("✅ Both writers completed successfully")
    
    console.print()
    
    # Update state file
    from ..core.state import load_state, save_state
    state = load_state(task_id)
    if state:
        state.writers_complete = True
        state.current_phase = 2
        if 2 not in state.completed_phases:
            state.completed_phases.append(2)
        save_state(state)
    
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

