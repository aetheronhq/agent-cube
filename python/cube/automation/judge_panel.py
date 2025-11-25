"""Parallel judge panel execution."""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import List

from ..core.agent import run_agent

logger = logging.getLogger(__name__)
from ..core.git import fetch_branches, get_commit_hash, branch_exists
from ..core.session import save_session, load_session, SessionWatcher
from ..core.output import print_info, print_success, print_warning, print_error, console
from ..core.config import PROJECT_ROOT, get_sessions_dir
from ..core.user_config import get_judge_config
from ..models.types import JudgeInfo

async def run_judge(judge_info: JudgeInfo, prompt: str, resume: bool, layout) -> int:
    """Run a single judge agent and return line count."""
    from .stream import format_stream_message
    from ..core.user_config import load_config as load_user_config
    from ..core.parsers.registry import get_parser
    from ..core.adapters.registry import get_adapter
    
    config = load_user_config()
    
    # Determine CLI tool based on judge type or model mapping
    if judge_info.adapter_config and judge_info.adapter_config.get("type") == "cli-review":
        cli_name = "cli-review"
    else:
        cli_name = config.cli_tools.get(judge_info.model, "cursor-agent")
        
    adapter = get_adapter(cli_name, judge_info.adapter_config)
    
    # For CLI review adapters, set writer worktree paths programmatically
    if cli_name == "cli-review":
        from ..core.user_config import get_writer_config
        from ..core.config import get_worktree_path, get_project_root
        from pathlib import Path
        
        writers = [get_writer_config("writer_a"), get_writer_config("writer_b")]
        project_name = Path(get_project_root()).name
        
        worktrees = {
            "Writer A": get_worktree_path(project_name, writers[0].name, judge_info.task_id),
            "Writer B": get_worktree_path(project_name, writers[1].name, judge_info.task_id)
        }
        adapter.set_writer_worktrees(worktrees)
    
    parser = get_parser(cli_name)
    
    from pathlib import Path
    logs_dir = Path.home() / ".cube" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = logs_dir / f"{judge_info.key}-{judge_info.task_id}-{judge_info.review_type}-{int(datetime.now().timestamp())}.json"
    
    session_file = get_sessions_dir() / f"{judge_info.key.upper()}_{judge_info.task_id}_{judge_info.review_type}_SESSION_ID.txt"
    metadata = f"{judge_info.label} ({judge_info.key}) - {judge_info.task_id} - {judge_info.review_type} - {datetime.now()}"
    
    watcher = SessionWatcher(log_file, session_file, metadata)
    watcher.start()
    
    line_count = 0
    try:
        with open(log_file, 'w') as f:
            session_id = judge_info.session_id if resume else None
            
            console.print(f"[dim]{judge_info.label}: Starting with model {judge_info.model} (CLI: {cli_name})...[/dim]")
            
            from ..core.config import WORKTREE_BASE
            run_dir = WORKTREE_BASE.parent if cli_name == "gemini" else PROJECT_ROOT
            
            judge_specific_prompt = prompt.replace("{{judge_key}}", judge_info.key).replace("{judge_key}", judge_info.key)
            
            stream = adapter.run(
                run_dir,
                judge_info.model,
                judge_specific_prompt,
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
                    
                    formatted = format_stream_message(msg, judge_info.label, judge_info.color)
                    if formatted:
                        if formatted.startswith("[thinking]"):
                            # Thinking message -> thinking box (buffered)
                            thinking_text = formatted.replace("[thinking]", "").replace("[/thinking]", "")
                            layout.add_thinking(judge_info.key, thinking_text)
                        elif msg.type == "assistant" and msg.content:
                            # Assistant message -> buffered per agent, no emoji logic
                            layout.add_assistant_message(judge_info.key, msg.content, judge_info.label, judge_info.color)
                        else:
                            # Tool calls, errors, etc -> immediate
                            layout.add_output(formatted)
            
            # Flush any remaining buffered content
            layout.flush_buffers()
    finally:
        watcher.stop()
    
    if line_count < 10:
        raise RuntimeError(f"{judge_info.label} completed suspiciously quickly ({line_count} lines). Check {log_file}")
    
    from ..core.decision_files import find_decision_file
    import json
    
    status = "Review complete"
    decision_file = find_decision_file(judge_info.key, judge_info.task_id, 
                                       "peer-review" if judge_info.review_type == "peer-review" else "decision")
    
    if decision_file and decision_file.exists():
        try:
            with open(decision_file) as f:
                data = json.load(f)
                decision = data.get("decision", "")
                winner = data.get("winner", "")
                scores = data.get("scores", {})
                remaining_issues = data.get("remaining_issues", [])
                blocker_issues = data.get("blocker_issues", [])
                
                score_a = None
                score_b = None
                if scores:
                    writer_a_scores = scores.get("writer_a", {})
                    writer_b_scores = scores.get("writer_b", {})
                    score_a = writer_a_scores.get("total_weighted") or writer_a_scores.get("total")
                    score_b = writer_b_scores.get("total_weighted") or writer_b_scores.get("total")
                
                if judge_info.review_type == "peer-review":
                    if decision == "APPROVED":
                        status = "✓ APPROVED → Ready to merge"
                    elif decision == "REQUEST_CHANGES":
                        issue_count = len(remaining_issues)
                        status = f"⚠ REQUEST_CHANGES → {issue_count} issue{'s' if issue_count != 1 else ''}"
                    elif decision == "REJECTED":
                        status = "✗ REJECTED → Major issues"
                    else:
                        status = f"Review complete → {decision}"
                else:
                    from ..core.user_config import get_writer_config
                    winner_text = ""
                    if winner == "TIE":
                        winner_text = "TIE"
                    elif winner in ["A", "writer_a", "Writer A"]:
                        try:
                            wcfg = get_writer_config("writer_a")
                            winner_text = f"{wcfg.label} wins"
                        except Exception as e:
                            logger.debug(f"Could not get writer_a config: {e}")
                            winner_text = "Writer A wins"
                    elif winner in ["B", "writer_b", "Writer B"]:
                        try:
                            wcfg = get_writer_config("writer_b")
                            winner_text = f"{wcfg.label} wins"
                        except Exception as e:
                            logger.debug(f"Could not get writer_b config: {e}")
                            winner_text = "Writer B wins"
                    else:
                        winner_text = f"Winner: {winner}"
                    
                    score_text = ""
                    if score_a is not None and score_b is not None:
                        score_text = f" ({score_a:.0f}/{score_b:.0f})"
                    
                    if decision == "APPROVED":
                        if blocker_issues:
                            blocker_count = len(blocker_issues)
                            status = f"✓ APPROVED → {winner_text}{score_text} → {blocker_count} blocker{'s' if blocker_count != 1 else ''}"
                        else:
                            status = f"✓ APPROVED → {winner_text}{score_text}"
                    elif decision == "REQUEST_CHANGES":
                        status = f"⚠ REQUEST_CHANGES → {winner_text}{score_text}"
                    elif decision == "REJECTED":
                        status = f"✗ REJECTED → {winner_text}{score_text}"
                    else:
                        status = f"{winner_text}{score_text}"
                        
        except (json.JSONDecodeError, KeyError, FileNotFoundError):
            pass
    
    layout.mark_complete(judge_info.key, status)
    console.print(f"[{judge_info.color}][{judge_info.label}][/{judge_info.color}] ✅ {status}")
    return line_count

async def launch_judge_panel(
    task_id: str,
    prompt_file: Path,
    review_type: str = "initial",
    resume_mode: bool = False
) -> None:
    """Launch judge panel in parallel."""
    
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    
    # Create fresh layout for judges (closes previous if exists)
    from ..core.dynamic_layout import DynamicLayout
    from ..core.user_config import get_judge_configs
    
    all_judges = get_judge_configs()
    
    # Filter judges based on review type
    if review_type == "panel":
        judge_configs = [j for j in all_judges if not j.peer_review_only]
    else:
        judge_configs = all_judges
    
    boxes = {j.key: j.label for j in judge_configs}
    DynamicLayout.initialize(boxes, lines_per_box=2)
    panel_layout = DynamicLayout
    
    base_prompt = prompt_file.read_text()
    
    from ..core.config import WORKTREE_BASE
    project_name = Path(PROJECT_ROOT).name
    
    judge_assignments = f"""# YOUR JUDGE KEY

You are **Judge {{judge_key}}** in this panel.

When creating your decision file, use judge key {{judge_key}}.

---

"""
    
    if review_type == "peer-review":
        review_instructions = f"""# Peer Review Context

**You are reviewing the WINNING implementation only.**

The winning writer's code is at:
**Location:** `{WORKTREE_BASE}/{project_name}/writer-{{winner}}-{task_id}/`

Use read_file or git commands to review the updated code.

---

# REQUIRED: Peer Review Decision File

**You MUST create this JSON file at the end of your review:**

**File:** `.prompts/decisions/{{judge_key}}-{task_id}-peer-review.json`
(Replace underscores with hyphens in your judge key for the filename)

**REQUIRED FORMAT (TOP-LEVEL FIELDS MANDATORY):**
```json
{{
  "judge": "{{judge_key}}",
  "task_id": "{task_id}",
  "review_type": "peer-review",
  "timestamp": "{{current-iso-timestamp}}",
  "decision": "APPROVED" | "REQUEST_CHANGES" | "REJECTED",
  "remaining_issues": [
    "Specific issue to fix (REQUIRED if REQUEST_CHANGES, empty array if APPROVED)"
  ],
  "recommendation": "Ready to merge" | "Needs more work",
  "verification": {{
    "your_detailed_checks": "optional_object"
  }}
}}
```

**⚠️ CRITICAL - DECISION FIELD IS MANDATORY:**
- The "decision" field MUST be at the TOP LEVEL of the JSON
- Valid values: "APPROVED", "REQUEST_CHANGES", or "REJECTED"
- Do NOT bury the decision inside nested objects
- The parser will fail if "decision" is missing or misspelled

**If decision is REQUEST_CHANGES:**
- You MUST list specific issues in "remaining_issues" array
- Empty remaining_issues with REQUEST_CHANGES will be treated as malformed

**If decision is APPROVED:**
- Set "remaining_issues" to empty array: []
- You may include additional verification details in nested objects

---

"""
    else:
        from ..core.user_config import get_writer_config
        writer_a = get_writer_config("writer_a")
        writer_b = get_writer_config("writer_b")
        
        review_instructions = f"""# Code Review Locations

## Writer A ({writer_a.label}) Implementation

**Branch:** `writer-{writer_a.name}/{task_id}`  
**Location:** `{WORKTREE_BASE}/{project_name}/writer-{writer_a.name}-{task_id}/`

## Writer B ({writer_b.label}) Implementation

**Branch:** `writer-{writer_b.name}/{task_id}`  
**Location:** `{WORKTREE_BASE}/{project_name}/writer-{writer_b.name}-{task_id}/`

Use read_file or git commands to view their code.

---

# REQUIRED: Panel Decision File

**You MUST create this JSON file at the end of your review:**

**File:** `.prompts/decisions/{{judge_key}}-{task_id}-decision.json`
(Replace underscores with hyphens in your judge key for the filename)

**CRITICAL for Gemini users:**
You're running from `~/.cube`. You MUST write your decision to:
- `{PROJECT_ROOT}/.prompts/decisions/{{judge_key}}-{task_id}-decision.json`
(Replace underscores with hyphens in your judge key for the filename)

Use absolute path when writing the file. The project root is available in your workspace context.

**Format:**
```json
{{
  "judge": "{{judge_key}}",
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
    
    prompt = judge_assignments + review_instructions + base_prompt
    
    from ..core.user_config import load_config as load_user_config, get_judge_configs
    
    judge_configs = get_judge_configs()
    
    # Filter judges based on review type and peer_review_only flag
    if review_type == "panel":
        # Skip peer-review-only judges in panel
        judge_configs = [j for j in judge_configs if not j.peer_review_only]
    
    judges: List[JudgeInfo] = []
    for jconfig in judge_configs:
        session_id = None
        if resume_mode:
            if review_type == "peer-review":
                session_id = load_session(jconfig.key.upper(), f"{task_id}_panel")
            else:
                session_id = load_session(jconfig.key.upper(), f"{task_id}_{review_type}")
            
            if not session_id:
                raise RuntimeError(f"No session found for {jconfig.label}")
        
        judges.append(
            JudgeInfo(
                key=jconfig.key,
            model=jconfig.model,
            color=jconfig.color,
            label=jconfig.label,
            task_id=task_id,
            review_type=review_type,
                session_id=session_id,
                adapter_config={
                    "type": jconfig.type,
                    "cmd": jconfig.cmd,
                    "name": jconfig.label
                } if jconfig.type == "cli-review" else None
            )
        )
    
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
    
    config = load_user_config()
    
    for writer_key in config.writer_order:
        writer_cfg = config.writers[writer_key]
        branch = f"writer-{writer_cfg.name}/{task_id}"
        if branch_exists(branch):
            commit = get_commit_hash(branch)
            console.print(f"  📍 {branch}: {commit}")
    console.print()
    
    console.print("━" * 60)
    console.print("[bold yellow]⚖️  JUDGES: Review all writer implementations[/bold yellow]")
    console.print()
    for writer_key in config.writer_order:
        writer_cfg = config.writers[writer_key]
        console.print(
            f"{writer_cfg.label}: [green]~/.cube/worktrees/{project_name}/writer-{writer_cfg.name}-{task_id}/[/green]"
        )
    console.print()
    console.print("Use your native tools (read_file, git commands, etc.)")
    console.print("━" * 60)
    console.print()
    
    from ..core.adapters.registry import get_adapter
    
    for judge in judges:
        cli_name = config.cli_tools.get(judge.model, "cursor-agent")
        adapter = get_adapter(cli_name)
        if not adapter.check_installed():
            print_error(f"{cli_name} not installed (needed for {judge.model})")
            console.print()
            console.print(adapter.get_install_instructions())
            raise RuntimeError(f"{cli_name} not installed")
    
    for judge in judges:
        console.print(f"🚀 Starting {judge.label} with {judge.model}...")
    console.print()
    console.print(f"⏳ Waiting for all {len(judges)} judges to complete...")
    console.print()
    
    # Start layout AFTER printing startup messages
    panel_layout.start()
    
    results = await asyncio.gather(
        *(run_judge(judge, prompt, resume_mode, panel_layout) for judge in judges),
        return_exceptions=True
    )
    
    from ..core.triple_layout import get_triple_layout
    get_triple_layout().close()
    
    errors = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            errors.append((judges[i].label, result))
    
    console.print()
    
    if errors:
        print_error("Some judges failed:")
        for label, error in errors:
            console.print(f"  {label}: {error}")
        
        total_judges = len(judges)
        failed = len(errors)
        if failed == total_judges:
            raise RuntimeError("All judges failed")
        else:
            print_warning(f"{failed} judge(s) failed but {total_judges - failed} completed successfully")
            console.print()
    else:
        console.print("✅ All judges completed successfully")
    
    console.print()
    
    print_success("Judge panel complete!")

