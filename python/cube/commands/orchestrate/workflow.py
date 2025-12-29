"""Main workflow orchestration for Agent Cube."""

import json
from pathlib import Path
import typer

from ...core.output import print_error, print_success, print_warning, print_info, console
from ...core.config import PROJECT_ROOT, resolve_path
from ...automation.dual_writers import launch_dual_writers
from ...automation.judge_panel import launch_judge_panel

from .prompts import generate_writer_prompt, generate_panel_prompt, generate_dual_feedback
from .phases import run_synthesis, run_peer_review, run_minor_fixes
from .decisions import run_decide_and_get_result, run_decide_peer_review, clear_peer_review_decisions
from .pr import create_pr


async def _orchestrate_single_writer_impl(
    task_file: str,
    resume_from: int,
    task_id: str,
    writer_key: str,
    resume_alias: str | None = None
) -> None:
    """Workflow for single-writer mode."""
    from ...core.state import update_phase
    from ...core.master_log import get_master_log
    from ...automation.single_writer import launch_single_writer
    from .prompts import generate_writer_prompt
    from .phases import run_peer_review, run_minor_fixes
    from .decisions import run_decide_peer_review, clear_peer_review_decisions
    from .pr import create_pr

    master_log = get_master_log()

    prompts_dir = PROJECT_ROOT / ".prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)

    console.print(f"[bold cyan]🤖 Agent Cube Single-Writer Orchestration[/bold cyan]")
    console.print(f"Task: {task_id}")
    console.print(f"Writer: {writer_key}")

    def log_phase(phase_num: int, phase_name: str):
        if master_log:
            master_log.write_phase_start(phase_num, phase_name)

    writer_prompt_path = prompts_dir / f"writer-prompt-{task_id}.md"

    # Phase 1: Generate Writer Prompt
    if resume_from <= 1:
        console.print("[yellow]═══ Phase 1: Generate Writer Prompt ═══[/yellow]")
        log_phase(1, "Generate Writer Prompt")
        if not task_file:
            print_error("Task file required for Phase 1.")
            raise typer.Exit(1)
        task_path = resolve_path(task_file)
        writer_prompt_path = await generate_writer_prompt(task_id, task_path.read_text(), prompts_dir)
        update_phase(task_id, 1, path="SINGLE", mode="single", writer_key=writer_key, project_root=str(PROJECT_ROOT))

    # Phase 2: Run Single Writer
    if resume_from <= 2:
        console.print()
        console.print("[yellow]═══ Phase 2: Run Single Writer ═══[/yellow]")
        log_phase(2, "Run Single Writer")
        await launch_single_writer(task_id, writer_prompt_path, writer_key, resume_mode=(resume_from == 2))
        update_phase(task_id, 2, writers_complete=True)

    # Phase 3: Peer Review
    if resume_from <= 3:
        console.print()
        console.print("[yellow]═══ Phase 3: Peer Review ═══[/yellow]")
        log_phase(3, "Peer Review")
        clear_peer_review_decisions(task_id)
        # This is a bit of a hack, but run_peer_review expects a "result" dict with a "winner"
        fake_result = {"winner": writer_key} 
        await run_peer_review(task_id, fake_result, prompts_dir)
        update_phase(task_id, 3, peer_review_complete=True)

    # Phase 4: Minor Fixes Loop
    if resume_from <= 4:
        console.print()
        console.print("[yellow]═══ Phase 4: Minor Fixes ═══[/yellow]")
        log_phase(4, "Address Minor Issues")
        
        final_result = run_decide_peer_review(task_id)
        update_phase(task_id, 4)

        if final_result["approved"] and not final_result["remaining_issues"]:
            print_success("All judges approved with no issues - skipping minor fixes")
        elif not final_result["remaining_issues"]:
            print_warning("No specific issues listed - skipping minor fixes")
        else:
            print_info(f"Found {len(final_result['remaining_issues'])} issues to address.")
            # another hack, run_minor_fixes expects a "result" dict
            fake_result = {"winner": writer_key}
            await run_minor_fixes(task_id, fake_result, final_result["remaining_issues"], prompts_dir)
            
            # Re-run peer review after fixes
            console.print()
            console.print("[yellow]═══ Re-running Peer Review ═══[/yellow]")
            clear_peer_review_decisions(task_id)
            await run_peer_review(task_id, fake_result, prompts_dir)
            update_phase(task_id, 4, peer_review_complete=True)


    # Phase 5: Create PR
    if resume_from <= 5:
        console.print()
        console.print("[yellow]═══ Phase 5: Create PR ═══[/yellow]")
        log_phase(5, "Create PR")

        final_check = run_decide_peer_review(task_id)
        if final_check["approved"]:
            print_success("Peer review approved. Creating PR.")
            await create_pr(task_id, writer_key)
        else:
            issues = final_check.get("remaining_issues", [])
            print_warning(f"Cannot create PR - {len(issues)} issue(s) outstanding.")
            if issues:
                for issue in issues[:3]:
                    console.print(f"  • {issue[:80]}")
            console.print()
            console.print("Fix issues first, then resume:")
            console.print(f"  cube auto {task_id} --resume-from 4")
            return
        update_phase(task_id, 5)


def extract_task_id_from_file(task_file: str) -> str:
    """Extract task ID from filename."""
    name = Path(task_file).stem

    if not name:
        raise ValueError(f"Cannot extract task ID from: {task_file}")

    prefixes = ["writer-prompt-", "task-", "synthesis-", "panel-prompt-", "peer-review-", "minor-fixes-", "feedback-"]
    task_id = name
    for prefix in prefixes:
        if task_id.startswith(prefix):
            task_id = task_id[len(prefix):]
            break

    if not task_id or task_id.startswith("-") or task_id.endswith("-"):
        raise ValueError(f"Invalid task ID extracted: '{task_id}' from {task_file}")

    return task_id


async def _orchestrate_auto_impl(
    task_file: str, 
    resume_from: int, 
    task_id: str, 
    resume_alias: str | None = None,
    single_mode: bool = False,
    writer_key: str | None = None
) -> None:
    """Internal implementation of orchestrate_auto_command."""
    from ...core.state import validate_resume, update_phase, load_state, get_progress
    from ...core.master_log import get_master_log

    master_log = get_master_log()

    prompts_dir = PROJECT_ROOT / ".prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)

    console.print(f"[bold cyan]🤖 Agent Cube Autonomous Orchestration[/bold cyan]")
    console.print(f"Task: {task_id}")

    existing_state = load_state(task_id)

    # Check if we are resuming a single-writer mode task
    if existing_state and existing_state.mode == "single":
        single_mode = True
        writer_key = existing_state.writer_key
        print_info(f"Resuming in single-writer mode with [bold cyan]{writer_key}[/bold cyan]")

    if single_mode:
        if not writer_key:
            from ...core.user_config import get_default_writer
            writer_key = get_default_writer()
        await _orchestrate_single_writer_impl(
            task_file, resume_from, task_id, 
            writer_key,
            resume_alias
        )
        return

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
            print_error(msg)
            raise typer.Exit(1)
        console.print(f"[yellow]Resuming from Phase {resume_from}[/yellow]")

    console.print()

    writer_prompt_path = prompts_dir / f"writer-prompt-{task_id}.md"
    panel_prompt_path = prompts_dir / f"panel-prompt-{task_id}.md"

    def log_phase(phase_num: int, phase_name: str):
        if master_log:
            master_log.write_phase_start(phase_num, phase_name)

    if resume_from <= 1:
        console.print("[yellow]═══ Phase 1: Generate Writer Prompt ═══[/yellow]")
        log_phase(1, "Generate Writer Prompt")
        if not task_file:
            print_error("Task file required for Phase 1. Provide a task.md path.")
            raise typer.Exit(1)
        task_path = resolve_path(task_file)
        writer_prompt_path = await generate_writer_prompt(task_id, task_path.read_text(), prompts_dir)
        update_phase(task_id, 1, path="INIT", project_root=str(PROJECT_ROOT))

    if resume_from <= 2:
        console.print()
        console.print("[yellow]═══ Phase 2: Dual Writers Execute ═══[/yellow]")
        log_phase(2, "Dual Writers Execute")
        await launch_dual_writers(task_id, writer_prompt_path, resume_mode=False)
        update_phase(task_id, 2, writers_complete=True)

    if resume_from <= 3:
        console.print()
        console.print("[yellow]═══ Phase 3: Generate Panel Prompt ═══[/yellow]")
        log_phase(3, "Generate Panel Prompt")
        panel_prompt_path = await generate_panel_prompt(task_id, prompts_dir)
        update_phase(task_id, 3)

    if resume_from <= 4:
        console.print()
        console.print("[yellow]═══ Phase 4: Judge Panel Review ═══[/yellow]")
        log_phase(4, "Judge Panel Review")
        should_resume = resume_from == 4
        await launch_judge_panel(task_id, panel_prompt_path, "panel", resume_mode=should_resume)
        update_phase(task_id, 4, panel_complete=True)

    if resume_from <= 5:
        console.print()
        console.print("[yellow]═══ Phase 5: Aggregate Decisions ═══[/yellow]")
        log_phase(5, "Aggregate Decisions")
        result = run_decide_and_get_result(task_id)
        update_phase(task_id, 5, path=result["next_action"], winner=result["winner"], next_action=result["next_action"])
    else:
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

    peer_status = run_decide_peer_review(
        task_id,
        require_decisions=result["next_action"] == "MERGE"
    )
    has_peer_review_issues = (
        result["next_action"] == "MERGE"
        and not peer_status.get("approved")
        and peer_status.get("decisions_found", 0) > 0
    )

    effective_path = result["next_action"]
    if has_peer_review_issues and effective_path == "MERGE":
        print_info("Peer review found issues - switching to SYNTHESIS path")
        effective_path = "SYNTHESIS"

    if effective_path == "SYNTHESIS":
        send_both_feedback = result.get("winner") and result.get("next_action") == "SYNTHESIS"
        if resume_from <= 6:
            console.print()
            console.print("[yellow]═══ Phase 6: Synthesis ═══[/yellow]")
            log_phase(6, "Synthesis")
            await run_synthesis(task_id, result, prompts_dir, both_writers=send_both_feedback)
            update_phase(task_id, 6, synthesis_complete=True)

        if resume_from <= 7:
            console.print()
            console.print("[yellow]═══ Phase 7: Peer Review ═══[/yellow]")
            log_phase(7, "Peer Review")
            clear_peer_review_decisions(task_id)
            await run_peer_review(task_id, result, prompts_dir)
            update_phase(task_id, 7, peer_review_complete=True)

        if resume_from <= 8:
            console.print()
            console.print("[yellow]═══ Phase 8: Final Decision ═══[/yellow]")
            log_phase(8, "Final Decision")

            final_result = run_decide_peer_review(task_id)
            update_phase(task_id, 8)

            from ...core.user_config import get_judge_configs
            peer_review_judges = [j for j in get_judge_configs() if j.peer_review_only]
            total_peer_judges = len(peer_review_judges) if peer_review_judges else 1
            decisions_found = final_result.get("decisions_found", 0)

            if decisions_found < total_peer_judges:
                print_warning(f"Only {decisions_found}/{total_peer_judges} peer-review judges have decisions")
                print_warning("Run peer-review to get all judge decisions before proceeding")
                console.print()
                console.print("[cyan]To run missing judges:[/cyan]")
                console.print(f"  cube peer-review {task_id}")
                return

            if final_result["approved"] and not final_result["remaining_issues"]:
                await create_pr(task_id, result["winner"])
                return
            elif not final_result["approved"] or final_result["remaining_issues"]:
                console.print()
                print_warning(f"Peer review has {len(final_result['remaining_issues'])} issue(s) to address")
                console.print()
                console.print("Issues to address:")
                for issue in final_result["remaining_issues"]:
                    console.print(f"  • {issue}")
                console.print()

        if resume_from <= 9:
            console.print("[yellow]═══ Phase 9: Address Minor Issues ═══[/yellow]")
            log_phase(9, "Address Minor Issues")
            if resume_from > 8:
                final_result = run_decide_peer_review(task_id)

            from ...core.user_config import get_judge_configs
            peer_review_judges = [j for j in get_judge_configs() if j.peer_review_only]
            total_peer_judges = len(peer_review_judges) if peer_review_judges else 1
            decisions_found = final_result.get("decisions_found", 0)

            if decisions_found < total_peer_judges:
                print_warning(f"Only {decisions_found}/{total_peer_judges} peer-review judges have decisions")
                print_warning("Run peer-review to get all judge decisions before proceeding")
                console.print()
                console.print("[cyan]To run missing judges:[/cyan]")
                console.print(f"  cube peer-review {task_id}")
                return

            if final_result["approved"] and not final_result["remaining_issues"]:
                print_success("All judges approved with no issues - skipping minor fixes")
                update_phase(task_id, 9)
            elif not final_result["remaining_issues"]:
                print_warning("No specific issues listed - skipping minor fixes")
                update_phase(task_id, 9)
            else:
                await run_minor_fixes(task_id, result, final_result["remaining_issues"], prompts_dir)
                update_phase(task_id, 9)

        if resume_from <= 10:
            console.print()
            console.print("[yellow]═══ Phase 10: Final Peer Review ═══[/yellow]")
            log_phase(10, "Final Peer Review")
            clear_peer_review_decisions(task_id)
            await run_peer_review(task_id, result, prompts_dir)
            update_phase(task_id, 10)

        final_check = run_decide_peer_review(task_id)
        if final_check["approved"] and not final_check["remaining_issues"]:
            await create_pr(task_id, result["winner"])
        elif final_check["approved"]:
            print_warning(f"Approved but still has {len(final_check['remaining_issues'])} issue(s) after minor fixes")
            console.print()
            console.print("Issues remaining:")
            for issue in final_check["remaining_issues"]:
                console.print(f"  • {issue}")
            console.print()
            console.print("Creating PR anyway (all judges approved)...")
            await create_pr(task_id, result["winner"])
        else:
            console.print()
            from ...core.user_config import get_judge_configs
            judge_configs = get_judge_configs()
            peer_review_judges = [j for j in judge_configs if j.peer_review_only]
            total_peer_judges = len(peer_review_judges) if peer_review_judges else 1

            decisions_count = final_check.get("decisions_found", 0)
            approvals_count = final_check.get("approvals", 0)

            if decisions_count < total_peer_judges:
                print_warning(f"Missing peer review decisions ({decisions_count}/{total_peer_judges})")
                console.print()
                console.print("Options:")
                console.print(f"  1. Get missing judge(s) to file decisions:")
                for judge_cfg in peer_review_judges:
                    judge_label = judge_cfg.key.replace("_", "-")
                    peer_file = PROJECT_ROOT / ".prompts" / "decisions" / f"{judge_label}-{task_id}-peer-review.json"
                    if not peer_file.exists():
                        console.print(f"     cube resume {judge_label} {task_id} \"Write peer review decision\"")
                console.print()
                console.print(f"  2. Continue with {decisions_count}/{total_peer_judges} decisions:")
                console.print(f"     cube auto task.md --resume-from 8")
            else:
                console.print()
                console.print("[bold red]🔄 Fix Loop Detected[/bold red]")
                console.print()
                console.print(f"Minor fixes were applied but {decisions_count - approvals_count} judge(s) still request changes.")
                console.print("This usually means:")
                console.print("  • The writer didn't fully address all issues")
                console.print("  • New issues were introduced while fixing others")
                console.print("  • The judge found additional problems on re-review")
                console.print()
                console.print("[yellow]To avoid infinite loops, manual intervention is required:[/yellow]")
                console.print()
                console.print("[cyan]Option 1:[/cyan] Review and fix manually")
                console.print(f"  1. Check remaining issues in peer-review decisions:")
                console.print(f"     ls .prompts/decisions/*{task_id}*peer-review*")
                console.print(f"  2. Fix issues in winner's worktree:")
                console.print(f"     cd ~/.cube/worktrees/*/writer-*-{task_id}")
                console.print(f"  3. Commit and push, then re-run peer review:")
                console.print(f"     cube auto --resume-from 10")
                console.print()
                console.print("[cyan]Option 2:[/cyan] Run another round of minor fixes")
                console.print(f"  cube auto --resume-from 9")
                console.print()
                console.print("[cyan]Option 3:[/cyan] Start fresh from synthesis")
                console.print(f"  cube auto --resume-from 6")

    elif result["next_action"] == "FEEDBACK":
        # FEEDBACK path only has phases 6-8, adjust if resuming from invalid phase
        if resume_from > 8:
            print_info(f"FEEDBACK path only has phases 6-8, adjusting resume from {resume_from} to 7")
            resume_from = 7
        
        winner_key = result.get("winner")
        split_feedback = (
            winner_key.upper() == "TIE" if winner_key else False
            or any("Writer B" in issue for issue in result.get("blocker_issues", []))
        )
        if resume_from <= 6:
            console.print()
            if split_feedback:
                console.print("[yellow]═══ Phase 6: Generate Feedback for Both Writers ═══[/yellow]")
                log_phase(6, "Generate Dual Feedback")
                await generate_dual_feedback(task_id, prompts_dir)
            else:
                console.print("[yellow]═══ Phase 6: Generate Feedback for Winner ═══[/yellow]")
                log_phase(6, "Generate Winner Feedback")
                await generate_dual_feedback(
                    task_id,
                    prompts_dir,
                    winner_only=True,
                    winner_key=winner_key
                )
            update_phase(task_id, 6, path="FEEDBACK")

        if resume_from <= 7:
            console.print()
            console.print("[yellow]═══ Phase 7: Re-run Panel Review ═══[/yellow]")
            log_phase(7, "Re-run Panel Review")
            await launch_judge_panel(task_id, panel_prompt_path, "panel", resume_mode=False)
            update_phase(task_id, 7, path="FEEDBACK", panel_complete=True)

        if resume_from <= 8:
            console.print()
            console.print("[yellow]═══ Phase 8: Re-aggregate Decisions ═══[/yellow]")
            log_phase(8, "Re-aggregate Decisions")
            new_result = run_decide_and_get_result(task_id)
            update_phase(task_id, 8, path=new_result["next_action"], winner=new_result["winner"])

            if new_result["next_action"] == "MERGE":
                print_success("Writers addressed feedback - ready for merge!")
                await create_pr(task_id, new_result["winner"])
            elif new_result["next_action"] == "SYNTHESIS":
                print_info("Winner selected after feedback - continuing to synthesis")
                console.print("Resume with:")
                console.print(f"  cube auto {task_id} --resume-from 6")
            elif new_result["next_action"] == "FEEDBACK":
                print_warning("Still needs FEEDBACK. Send more feedback and re-run panel:")
                console.print(f"  cube auto {task_id} --resume-from 6")
            else:
                print_warning("Unexpected state. Check decisions and decide next action:")
                console.print(f"  cube decide {task_id}")

    elif effective_path == "MERGE":
        from ...core.user_config import get_judge_configs
        peer_only_judges = [j for j in get_judge_configs() if j.peer_review_only]

        wants_peer_review = resume_alias in ("peer-review", "peer", "peer-panel")

        if peer_only_judges and (resume_from <= 6 or wants_peer_review):
            console.print()
            console.print("[yellow]═══ Phase 6: Automated Review ═══[/yellow]")
            log_phase(6, "Automated Review")
            print_info(f"Running {len(peer_only_judges)} automated reviewer(s) before PR: {', '.join(j.label for j in peer_only_judges)}")

            temp_prompt = prompts_dir / f"temp-peer-review-{task_id}.md"
            temp_prompt.write_text(task_id)

            # Clear existing peer-review decision files to prevent concatenation
            clear_peer_review_decisions(task_id)

            await launch_judge_panel(task_id, temp_prompt, "peer-review", resume_mode=False, winner=result["winner"])

            auto_result = run_decide_peer_review(task_id)

            if auto_result.get("approved") and auto_result.get("decisions_found", 0) > 0:
                print_info("✅ Automated review passed!")
                update_phase(task_id, 6, path="MERGE", peer_review_complete=True)
            else:
                issues = auto_result.get("remaining_issues", [])
                decisions_found = auto_result.get("decisions_found", 0)
                approvals = auto_result.get("approvals", 0)

                console.print()
                if issues:
                    print_warning(f"Automated review found {len(issues)} issue(s) - running minor fixes")
                    for issue in issues[:5]:
                        console.print(f"  • {issue[:100]}")
                    if len(issues) > 5:
                        console.print(f"  ... and {len(issues) - 5} more")
                    
                    # Run minor fixes for the automated review issues
                    await run_minor_fixes(task_id, result, issues, prompts_dir)
                    update_phase(task_id, 6, path="MERGE")
                    
                    # Re-run automated review after fixes
                    console.print()
                    console.print("[yellow]═══ Re-running Automated Review ═══[/yellow]")
                    clear_peer_review_decisions(task_id)
                    await launch_judge_panel(task_id, temp_prompt, "peer-review", resume_mode=False, winner=result["winner"])
                    
                    recheck = run_decide_peer_review(task_id)
                    if recheck.get("approved"):
                        print_success("✅ Automated review passed after fixes!")
                        update_phase(task_id, 6, path="MERGE", peer_review_complete=True)
                    else:
                        remaining = recheck.get("remaining_issues", [])
                        console.print()
                        print_warning(f"Still {len(remaining)} issue(s) after fixes")
                        console.print()
                        winner = result.get("winner", "writer_b").replace("writer_", "")
                        console.print("Send targeted feedback to address remaining issues:")
                        console.print(f"  cube feedback {winner} {task_id} \"<fix instructions>\"")
                        console.print(f"  cube auto {task_id} --resume-from peer-review")
                        return
                elif decisions_found == 0:
                    print_warning("No automated review decisions found!")
                    console.print("Retry:")
                    console.print(f"  cube auto {task_id} --resume-from peer-review")
                    return
                else:
                    print_warning(f"Automated review not approved ({approvals}/{decisions_found} approved)")
                    update_phase(task_id, 6, path="MERGE", peer_review_complete=True)

                console.print()
                console.print("Fix issues or wait for decisions, then resume:")
                console.print(f"  cube auto {task_id} --resume-from 6")
                update_phase(task_id, 6, path="MERGE")
                return

            update_phase(task_id, 6, path="MERGE", peer_review_complete=True)

        if resume_from <= 7:
            console.print()
            console.print("[yellow]═══ Phase 7: Create PR ═══[/yellow]")
            log_phase(7, "Create PR")

            pr_check = run_decide_peer_review(task_id)
            if not pr_check.get("approved") or pr_check.get("remaining_issues"):
                issues = pr_check.get("remaining_issues", [])
                print_warning(f"Cannot create PR - {len(issues)} issue(s) outstanding")
                if issues:
                    for issue in issues[:3]:
                        console.print(f"  • {issue[:80]}")
                console.print()
                console.print("Fix issues first, then resume:")
                console.print(f"  cube auto {task_id} --resume-from peer-review")
                return

            await create_pr(task_id, result["winner"])
            update_phase(task_id, 7, path="MERGE")

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
