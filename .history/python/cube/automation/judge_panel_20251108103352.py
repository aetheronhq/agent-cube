"""Parallel judge panel execution."""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import List

from ..core.agent import run_agent
from ..core.git import fetch_branches, get_commit_hash, branch_exists
from ..core.session import save_session, load_session, SessionWatcher
from ..core.output import print_info, print_success, console
from ..core.config import PROJECT_ROOT, get_sessions_dir
from ..core.user_config import get_judge_config
from ..models.types import JudgeInfo

async def run_judge(judge_info: JudgeInfo, prompt: str, resume: bool) -> int:
    """Run a single judge agent and return line count."""
    from .stream import format_stream_message
    from ..core.user_config import load_config as load_user_config
    from ..core.parsers.registry import get_parser
    from ..core.triple_layout import get_triple_layout
    
    config = load_user_config()
    cli_name = config.cli_tools.get(judge_info.model, "cursor-agent")
    parser = get_parser(cli_name)
    layout = get_triple_layout()
    layout.start()
    
    log_file = Path(f"/tmp/judge-{judge_info.number}-{judge_info.task_id}-{judge_info.review_type}-{int(datetime.now().timestamp())}.json")
    
    session_file = get_sessions_dir() / f"JUDGE_{judge_info.number}_{judge_info.task_id}_{judge_info.review_type}_SESSION_ID.txt"
    metadata = f"Judge {judge_info.number} - {judge_info.task_id} - {judge_info.review_type} - {datetime.now()}"
    
    watcher = SessionWatcher(log_file, session_file, metadata)
    watcher.start()
    
    line_count = 0
    try:
        with open(log_file, 'w') as f:
            session_id = judge_info.session_id if resume else None
            
            console.print(f"[dim]Judge {judge_info.number}: Starting with model {judge_info.model} (CLI: {cli_name})...[/dim]")
            
            from ..core.config import WORKTREE_BASE
            run_dir = WORKTREE_BASE.parent if cli_name == "gemini" else PROJECT_ROOT
            
            stream = run_agent(
                run_dir,
                judge_info.model,
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
                    if msg.session_id and not judge_info.session_id:
                        judge_info.session_id = msg.session_id
                    
                    formatted = format_stream_message(msg, f"Judge {judge_info.number}", judge_info.color)
                    if formatted and not formatted.startswith("[thinking]"):
                        console.print(formatted)
    finally:
        watcher.stop()
    
    if line_count < 10:
        raise RuntimeError(f"Judge {judge_info.number} completed suspiciously quickly ({line_count} lines). Check {log_file}")
    
    console.print(f"[{judge_info.color}][Judge {judge_info.number}][/{judge_info.color}] ✅ Completed")
    return line_count

async def launch_judge_panel(
    task_id: str,
    prompt_file: Path,
    review_type: str = "initial",
    resume_mode: bool = False
) -> None:
    """Launch 3-judge panel in parallel."""
    
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    
    base_prompt = prompt_file.read_text()
    
    from ..core.config import WORKTREE_BASE
    project_name = Path(PROJECT_ROOT).name
    
    if review_type == "peer-review":
        review_instructions = f"""# Peer Review Context

**You are reviewing the WINNING implementation only.**

The winning writer's code is at:
**Location:** `{WORKTREE_BASE}/{project_name}/writer-{{winner}}-{task_id}/`

Use read_file or git commands to review the updated code.

---

# REQUIRED: Peer Review Decision File

**You MUST create this JSON file at the end of your review:**

**File:** `.prompts/decisions/judge-{{your-number}}-{task_id}-peer-review.json`

**Format:**
```json
{{
  "judge": {{your-judge-number}},
  "task_id": "{task_id}",
  "review_type": "peer-review",
  "timestamp": "{{current-iso-timestamp}}",
  "decision": "APPROVED" | "REQUEST_CHANGES" | "REJECTED",
  "concerns_addressed": true | false,
  "remaining_issues": [
    "Description of any remaining issues"
  ],
  "recommendation": "Ready to merge" | "Needs more work"
}}
```

---

"""
    else:
        review_instructions = f"""# Code Review Locations

## Writer A (Sonnet) Implementation

**Branch:** `writer-sonnet/{task_id}`  
**Location:** `{WORKTREE_BASE}/{project_name}/writer-sonnet-{task_id}/`

## Writer B (Codex) Implementation

**Branch:** `writer-codex/{task_id}`  
**Location:** `{WORKTREE_BASE}/{project_name}/writer-codex-{task_id}/`

Use read_file or git commands to view their code.

---

# REQUIRED: Panel Decision File

**You MUST create this JSON file at the end of your review:**

**File:** `.prompts/decisions/judge-{{your-number}}-{task_id}-decision.json`

**Format:**
```json
{{
  "judge": {{your-judge-number}},
  "task_id": "{task_id}",
  "timestamp": "{{current-iso-timestamp}}",
  "decision": "APPROVED" | "REQUEST_CHANGES" | "REJECTED",
  "winner": "A" | "B" | "TIE",
  "scores": {{
    "writer_a": {{
      "kiss_compliance": 0-10,
      "architecture": 0-10,
      "type_safety": 0-10,
      "tests": 0-10,
      "production_ready": 0-10,
      "total_weighted": 0-10
    }},
    "writer_b": {{
      "kiss_compliance": 0-10,
      "architecture": 0-10,
      "type_safety": 0-10,
      "tests": 0-10,
      "production_ready": 0-10,
      "total_weighted": 0-10
    }}
  }},
  "blocker_issues": [
    "Description of blocking issues that must be fixed"
  ],
  "recommendation": "Brief explanation of why winner was chosen"
}}
```

---

"""
    
    prompt = review_instructions + base_prompt
    
    judges: List[JudgeInfo] = []
    for judge_num in [1, 2, 3]:
        jconfig = get_judge_config(judge_num)
        
        session_id = None
        if resume_mode:
            session_id = load_session(f"JUDGE_{judge_num}", f"{task_id}_{review_type}")
            if not session_id:
                raise RuntimeError(f"No session found for Judge {judge_num}")
        
        judge = JudgeInfo(
            number=judge_num,
            model=jconfig.model,
            color=jconfig.color,
            label=jconfig.label,
            task_id=task_id,
            review_type=review_type,
            session_id=session_id
        )
        judges.append(judge)
    
    if resume_mode:
        print_info(f"Resuming Judge Panel for Task: {task_id}")
        console.print()
        console.print("[yellow]📋 Found existing judge sessions to resume:[/yellow]")
        for judge in judges:
            if judge.session_id:
                console.print(f"  [{judge.color}]{judge.label}[/{judge.color}] ({judge.model}): {judge.session_id}")
            else:
                console.print(f"  [{judge.color}]{judge.label}[/{judge.color}] ({judge.model}): [red]No session found[/red]")
        console.print()
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
    console.print("[bold yellow]⚖️  JUDGES: Review both writer implementations[/bold yellow]")
    console.print()
    console.print(f"Writer A: [green]~/.cube/worktrees/{project_name}/writer-sonnet-{task_id}/[/green]")
    console.print(f"Writer B: [blue]~/.cube/worktrees/{project_name}/writer-codex-{task_id}/[/blue]")
    console.print()
    console.print("Use your native tools (read_file, git commands, etc.)")
    console.print("━" * 60)
    console.print()
    
    from ..core.user_config import load_config as load_user_config
    from ..core.adapters.registry import get_adapter
    
    config = load_user_config()
    for judge in judges:
        cli_name = config.cli_tools.get(judge.model, "cursor-agent")
        adapter = get_adapter(cli_name)
        if not adapter.check_installed():
            from ..core.output import print_error
            print_error(f"{cli_name} not installed (needed for {judge.model})")
            console.print()
            console.print(adapter.get_install_instructions())
            raise RuntimeError(f"{cli_name} not installed")
    
    console.print(f"🚀 Starting {judges[0].label} with {judges[0].model}...")
    console.print(f"🚀 Starting {judges[1].label} with {judges[1].model}...")
    console.print(f"🚀 Starting {judges[2].label} with {judges[2].model}...")
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

