"""Parallel judge panel execution."""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import List

from ..core.agent import run_agent
from ..core.git import fetch_branches, get_commit_hash, branch_exists
from ..core.session import save_session, load_session, SessionWatcher
from ..core.output import print_info, print_success, console
from ..core.config import JUDGE_MODELS, JUDGE_COLORS, PROJECT_ROOT, get_sessions_dir
from ..models.types import JudgeInfo
from .stream import parse_and_format_stream

async def run_judge(judge_info: JudgeInfo, prompt: str, resume: bool) -> None:
    """Run a single judge agent."""
    log_file = Path(f"/tmp/judge-{judge_info.number}-{judge_info.task_id}-{judge_info.review_type}-{int(datetime.now().timestamp())}.json")
    
    session_file = get_sessions_dir() / f"JUDGE_{judge_info.number}_{judge_info.task_id}_{judge_info.review_type}_SESSION_ID.txt"
    metadata = f"Judge {judge_info.number} - {judge_info.task_id} - {judge_info.review_type} - {datetime.now()}"
    
    watcher = SessionWatcher(log_file, session_file, metadata)
    watcher.start()
    
    try:
        with open(log_file, 'w') as f:
            session_id = judge_info.session_id if resume else None
            
            stream = run_agent(
                PROJECT_ROOT,
                judge_info.model,
                prompt,
                session_id=session_id,
                resume=resume
            )
            
            async for line in stream:
                f.write(line + '\n')
                f.flush()
                
                parsed_stream = parse_and_format_stream(
                    async_gen_from_line(line),
                    f"Judge {judge_info.number}",
                    judge_info.color
                )
                
                async for formatted, sess_id in parsed_stream:
                    if formatted:
                        console.print(formatted)
                    if sess_id and not judge_info.session_id:
                        judge_info.session_id = sess_id
    finally:
        watcher.stop()
    
    console.print(f"[{judge_info.color}][Judge {judge_info.number}][/{judge_info.color}] ✅ Completed")

async def async_gen_from_line(line: str):
    """Convert a single line to an async generator."""
    yield line

async def launch_judge_panel(
    task_id: str,
    prompt_file: Path,
    review_type: str = "initial",
    resume_mode: bool = False
) -> None:
    """Launch 3-judge panel in parallel."""
    
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    
    prompt = prompt_file.read_text()
    
    judges: List[JudgeInfo] = []
    for judge_num in [1, 2, 3]:
        session_id = None
        if resume_mode:
            session_id = load_session(f"JUDGE_{judge_num}", f"{task_id}_{review_type}")
            if not session_id:
                raise RuntimeError(f"No session found for Judge {judge_num}")
        
        judge = JudgeInfo(
            number=judge_num,
            model=JUDGE_MODELS[judge_num],
            color=JUDGE_COLORS[judge_num],
            task_id=task_id,
            review_type=review_type,
            session_id=session_id
        )
        judges.append(judge)
    
    if resume_mode:
        print_info(f"Resuming Judge Panel for Task: {task_id}")
    else:
        print_info(f"Launching Judge Panel for Task: {task_id}")
    
    print_info(f"Prompt: {prompt_file}")
    print_info(f"Review Type: {review_type}")
    console.print()
    
    print_info("Fetching latest changes from writer branches...")
    fetch_branches()
    
    for writer_name in ["sonnet", "codex"]:
        branch = f"writer-{writer_name}/{task_id}"
        if branch_exists(branch):
            commit = get_commit_hash(branch)
            console.print(f"  📍 {branch}: {commit}")
    console.print()
    
    console.print("━" * 60)
    console.print("⚖️  JUDGES: Review the latest code from writer branches")
    console.print(f"   Use: git diff main...writer-sonnet/{task_id}")
    console.print(f"   Use: git diff main...writer-codex/{task_id}")
    console.print("━" * 60)
    console.print()
    
    console.print("🚀 Starting Judge 1...")
    console.print("🚀 Starting Judge 2...")
    console.print("🚀 Starting Judge 3...")
    console.print()
    
    console.print("📊 All judges launched successfully!")
    console.print(f"📊 Judge 1 (Sonnet): PID ...")
    console.print(f"📊 Judge 2 (Codex): PID ...")
    console.print(f"📊 Judge 3 (Grok): PID ...")
    console.print()
    
    console.print("⏳ Waiting for all 3 judges to complete...")
    console.print()
    
    await asyncio.gather(
        run_judge(judges[0], prompt, resume_mode),
        run_judge(judges[1], prompt, resume_mode),
        run_judge(judges[2], prompt, resume_mode)
    )
    
    console.print()
    console.print("✅ All judges completed")
    console.print()
    
    print_success("Judge panel complete!")

