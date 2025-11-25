"""Main orchestration loop."""

import asyncio
from pathlib import Path
import typer

from ...core.output import print_error, print_success, print_warning, print_info, console
from ...core.config import PROJECT_ROOT, resolve_path
from ...automation.dual_writers import launch_dual_writers
from ...automation.judge_panel import launch_judge_panel

from .prompts import generate_writer_prompt, generate_panel_prompt
from .synthesis import run_synthesis, run_peer_review, run_decide_and_get_result, run_decide_peer_review
from .feedback import generate_dual_feedback, run_minor_fixes
from .utils import extract_task_id_from_file, create_pr

async def orchestrate_auto_command(
    task_file: str | None,
    resume_from: int = 1,
    task_id: str | None = None
) -> None:
    """Fully autonomous orchestration - runs entire workflow.
    
    Args:
        task_file: Path to task file (can be None if resuming from phase > 1)
        resume_from: Phase number to resume from (1-10)
        task_id: Optional task ID (if not provided, extracted from task_file)
    """
    from ...core.state import validate_resume, update_phase, load_state, get_progress
    
    # Get task_id - either provided directly or from file
    if task_id is None:
        if task_file is None:
            raise ValueError("task_id is required when task_file is None")
        task_id = extract_task_id_from_file(task_file)
    
    prompts_dir = PROJECT_ROOT / ".prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    
    console.print(f"[bold cyan]🤖 Agent Cube Autonomous Orchestration[/bold cyan]")
    console.print(f"Task: {task_id}")
    
    existing_state = load_state(task_id)
    
    if not existing_state and resume_from > 1:
        from ...core.state_backfill import backfill_state_from_artifacts
        console.print("[dim]Backfilling state from existing artifacts...[/dim]")
        existing_state = backfill_state_from_artifacts(task_id)
        console.print(f"[dim]Detected: {get_progress(task_id)}[/dim]")
    
    if existing_state:
        console.print(f"[dim]Progress: {get_progress(task_id)}[/dim]")
    
    if resume_from > 1:
        valid, msg = validate_resume(task_id, resume_from)
        if not valid:
            from ...core.output import print_error
            print_error(msg)
            raise typer.Exit(1)
        console.print(f"[yellow]Resuming from Phase {resume_from}[/yellow]")
    
    console.print()
    
    writer_prompt_path = prompts_dir / f"writer-prompt-{task_id}.md"
    panel_prompt_path = prompts_dir / f"panel-prompt-{task_id}.md"
    
    if resume_from <= 1:
        console.print("[yellow]═══ Phase 1: Generate Writer Prompt ═══[/yellow]")
        if not task_file:
            print_error("Task file required for Phase 1. Provide a task.md path.")
            raise typer.Exit(1)
        task_path = resolve_path(task_file)
        writer_prompt_path = await generate_writer_prompt(task_id, task_path.read_text(), prompts_dir)
        update_phase(task_id, 1, path="INIT")
    
    if resume_from <= 2:
        console.print()
        console.print("[yellow]═══ Phase 2: Dual Writers Execute ═══[/yellow]")
        await launch_dual_writers(task_id, writer_prompt_path, resume_mode=False)
        update_phase(task_id, 2, writers_complete=True)
    
    if resume_from <= 3:
        console.print()
        console.print("[yellow]═══ Phase 3: Generate Panel Prompt ═══[/yellow]")
        panel_prompt_path = await generate_panel_prompt(task_id, prompts_dir)
        update_phase(task_id, 3)
    
    if resume_from <= 4:
        console.print()
        console.print("[yellow]═══ Phase 4: Judge Panel Review ═══[/yellow]")
        await launch_judge_panel(task_id, panel_prompt_path, "panel", resume_mode=False)
        update_phase(task_id, 4, panel_complete=True)
    
    if resume_from <= 5:
        console.print()
        console.print("[yellow]═══ Phase 5: Aggregate Decisions ═══[/yellow]")
        result = run_decide_and_get_result(task_id)
        update_phase(task_id, 5, path=result["next_action"], winner=result["winner"], next_action=result["next_action"])
    else:
        import json
        result_file = prompts_dir / "decisions" / f"{task_id}-aggregated.json"
        if result_file.exists():
            try:
                with open(result_file) as f:
                    result = json.load(f)
                
                if "next_action" not in result:
                    raise RuntimeError(f"Aggregated decision missing 'next_action'. Re-run Phase 5.")
            except json.JSONDecodeError:
                raise RuntimeError(f"Corrupt aggregated decision file: {result_file}. Re-run Phase 5.")
        else:
            raise RuntimeError(f"Cannot resume from phase {resume_from}: No aggregated decision found. Run Phase 5 first.")
    
    if result["next_action"] == "SYNTHESIS":
        if resume_from <= 6:
            console.print()
            console.print("[yellow]═══ Phase 6: Synthesis ═══[/yellow]")
            await run_synthesis(task_id, result, prompts_dir)
            update_phase(task_id, 6, synthesis_complete=True)
        
        if resume_from <= 7:
            console.print()
            console.print("[yellow]═══ Phase 7: Peer Review ═══[/yellow]")
            await run_peer_review(task_id, result, prompts_dir)
            update_phase(task_id, 7, peer_review_complete=True)
        
        if resume_from <= 8:
            console.print()
            console.print("[yellow]═══ Phase 8: Final Decision ═══[/yellow]")
        
        final_result = run_decide_peer_review(task_id)
        update_phase(task_id, 8)
        
        if final_result["approved"] and not final_result["remaining_issues"]:
            await create_pr(task_id, result["winner"])
        elif final_result["approved"] and final_result["remaining_issues"]:
            console.print()
            print_warning(f"Peer review approved but has {len(final_result['remaining_issues'])} minor issue(s)")
            console.print()
            console.print("Minor issues to address:")
            for issue in final_result["remaining_issues"]:
                console.print(f"  • {issue}")
            console.print()
            
            if resume_from <= 9:
                console.print("[yellow]═══ Phase 9: Address Minor Issues ═══[/yellow]")
                await run_minor_fixes(task_id, result, final_result["remaining_issues"], prompts_dir)
                update_phase(task_id, 9)
            
            if resume_from <= 10:
                console.print()
                console.print("[yellow]═══ Phase 10: Final Peer Review ═══[/yellow]")
                await run_peer_review(task_id, result, prompts_dir)
                update_phase(task_id, 10)
            
            final_check = run_decide_peer_review(task_id)
            if final_check["approved"]:
                await create_pr(task_id, result["winner"])
            else:
                print_warning("Minor fixes didn't resolve all issues")
                console.print()
                console.print("The iteration limit has been reached. Manual review needed.")
                console.print()
                console.print("Next steps:")
                console.print("  1. Read peer-review decisions for remaining issues")
                console.print(f"  2. Manually fix in winner's worktree")
                console.print(f"  3. Or adjust synthesis and retry from Phase 6")
        else:
            from ...core.user_config import get_judge_configs
            judge_configs = get_judge_configs()
            judge_nums = [j.key for j in judge_configs]
            total_judges = len(judge_nums)
            
            decisions_count = final_result.get("decisions_found", 0)
            approvals_count = final_result.get("approvals", 0)
            
            if decisions_count < total_judges:
                print_warning(f"Missing peer review decisions ({decisions_count}/{total_judges})")
                console.print()
                console.print("Options:")
                console.print(f"  1. Get missing judge(s) to file decisions:")
                for judge_key in judge_nums:
                    judge_label = judge_key.replace("_", "-")
                    peer_file = PROJECT_ROOT / ".prompts" / "decisions" / f"{judge_label}-{task_id}-peer-review.json"
                    if not peer_file.exists():
                        console.print(f"     cube resume {judge_label} {task_id} \"Write peer review decision\"")
                console.print()
                console.print(f"  2. Continue with {decisions_count}/{total_judges} decisions:")
                console.print(f"     cube auto task.md --resume-from 8")
            else:
                print_warning(f"Peer review rejected ({approvals_count}/{decisions_count} approved) - synthesis needs more work")
                console.print()
                console.print("Next steps:")
                console.print(f"  1. Review judge feedback in peer-review decisions")
                console.print(f"  2. Update synthesis prompt:")
                console.print(f"     .prompts/synthesis-{task_id}.md")
                console.print(f"  3. Re-run synthesis:")
                console.print(f"     cube auto task.md --resume-from 6")
                console.print()
                console.print("Or manually fix the issues and re-run peer review")
    
    elif result["next_action"] == "FEEDBACK":
        if resume_from <= 6:
            console.print()
            console.print("[yellow]═══ Phase 6: Generate Feedback for Both Writers ═══[/yellow]")
            await generate_dual_feedback(task_id, result, prompts_dir)
            update_phase(task_id, 6, path="FEEDBACK")
        
        console.print()
        print_warning("Both writers need major changes. Re-run panel after they complete:")
        console.print(f"  cube panel {task_id} .prompts/panel-prompt-{task_id}.md")
    
    elif result["next_action"] == "MERGE":
        if resume_from <= 6:
            console.print()
            console.print("[yellow]═══ Phase 6: Create PR ═══[/yellow]")
            await create_pr(task_id, result["winner"])
            update_phase(task_id, 6, path="MERGE")
    
    else:
        console.print()
        print_warning(f"Unexpected next action: {result['next_action']}")
        console.print()
        console.print("This shouldn't happen. Possible causes:")
        console.print("  - Corrupted aggregated decision file")
        console.print("  - Unknown decision path")
        console.print()
        console.print("Try:")
        console.print(f"  cube decide {task_id}  # Re-aggregate decisions")
        console.print(f"  cube status {task_id}  # Check current state")
