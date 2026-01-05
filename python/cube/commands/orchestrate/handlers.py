"""Phase handlers for workflow state machine."""

import json

import typer

from ...automation.dual_writers import launch_dual_writers
from ...automation.judge_panel import launch_judge_panel
from ...automation.single_writer import launch_single_writer
from ...core.config import PROJECT_ROOT, resolve_path
from ...core.output import console, print_error, print_info, print_success, print_warning
from ...core.user_config import get_judge_configs
from .decisions import clear_peer_review_decisions, run_decide_and_get_result, run_decide_peer_review
from .phases import run_minor_fixes, run_peer_review, run_synthesis
from .phases_registry import Phase, PhaseResult, WorkflowContext, WorkflowType
from .pr import create_pr
from .prompts import generate_dual_feedback, generate_panel_prompt, generate_writer_prompt


# =============================================================================
# SINGLE WRITER HANDLERS
# =============================================================================


async def single_generate_prompt(ctx: WorkflowContext) -> PhaseResult:
    """Phase 1: Generate writer prompt for single-writer mode."""
    if not ctx.task_file:
        print_error("Task file required for Phase 1.")
        raise typer.Exit(1)

    task_path = resolve_path(ctx.task_file)
    await generate_writer_prompt(ctx.task_id, task_path.read_text(), ctx.prompts_dir)
    return PhaseResult(data={"path": "SINGLE", "mode": "single", "writer_key": ctx.writer_key, "project_root": str(PROJECT_ROOT)})


async def single_run_writer(ctx: WorkflowContext) -> PhaseResult:
    """Phase 2: Run single writer."""
    await launch_single_writer(
        ctx.task_id, ctx.writer_prompt_path, ctx.writer_key or "", resume_mode=(ctx.resume_from == 2)
    )
    return PhaseResult(data={"writers_complete": True})


async def single_judge_panel(ctx: WorkflowContext) -> PhaseResult:
    """Phase 3: Judge panel reviews single writer's work."""
    clear_peer_review_decisions(ctx.task_id)
    fake_result = {"winner": ctx.writer_key}
    await run_peer_review(ctx.task_id, fake_result, ctx.prompts_dir, run_all_judges=True)
    return PhaseResult(data={"peer_review_complete": True})


async def single_minor_fixes(ctx: WorkflowContext) -> PhaseResult:
    """Phase 4: Address minor issues from judges."""
    final_result = run_decide_peer_review(ctx.task_id)
    ctx.final_result = final_result

    if not final_result["approved"]:
        if not final_result["remaining_issues"]:
            print_warning("Cannot proceed - missing judge decisions or not approved")
            judge_configs = get_judge_configs()
            submitted = set(final_result.get("judge_decisions", {}).keys())
            missing = [j for j in judge_configs if j.key not in submitted]
            if missing:
                console.print()
                console.print("Run missing judge(s):")
                for j in missing:
                    console.print(f"  cube peer-review {ctx.task_id} -j {j.key}")
            console.print()
            console.print("Or re-run all judges:")
            console.print(f"  cube auto {ctx.task_id} --resume-from 3")
            return PhaseResult(exit=True)

    if final_result["approved"] and not final_result["remaining_issues"]:
        print_success("All judges approved with no issues - skipping minor fixes")
    elif final_result["remaining_issues"]:
        print_info(f"Found {len(final_result['remaining_issues'])} issues to address.")
        fake_result = {"winner": ctx.writer_key}
        await run_minor_fixes(ctx.task_id, fake_result, final_result["remaining_issues"], ctx.prompts_dir)

        console.print()
        console.print("[yellow]═══ Re-running Judge Panel ═══[/yellow]")
        clear_peer_review_decisions(ctx.task_id)
        await run_peer_review(ctx.task_id, fake_result, ctx.prompts_dir, run_all_judges=True)

    return PhaseResult(data={"peer_review_complete": True})


async def single_create_pr(ctx: WorkflowContext) -> PhaseResult:
    """Phase 5: Create PR for single-writer mode."""
    final_check = run_decide_peer_review(ctx.task_id)
    if final_check["approved"]:
        print_success("Peer review approved. Creating PR.")
        await create_pr(ctx.task_id, ctx.writer_key or "")
    else:
        issues = final_check.get("remaining_issues", [])
        print_warning(f"Cannot create PR - {len(issues)} issue(s) outstanding.")
        if issues:
            for issue in issues[:3]:
                console.print(f"  • {issue[:80]}")
        console.print()
        console.print("Fix issues first, then resume:")
        console.print(f"  cube auto {ctx.task_id} --resume-from 4")
        return PhaseResult(exit=True)

    return PhaseResult(success=True)


# =============================================================================
# DUAL WRITER HANDLERS
# =============================================================================


async def dual_generate_prompt(ctx: WorkflowContext) -> PhaseResult:
    """Phase 1: Generate writer prompt for dual-writer mode."""
    if not ctx.task_file:
        print_error("Task file required for Phase 1. Provide a task.md path.")
        raise typer.Exit(1)

    task_path = resolve_path(ctx.task_file)
    await generate_writer_prompt(ctx.task_id, task_path.read_text(), ctx.prompts_dir)
    return PhaseResult(data={"path": "INIT", "project_root": str(PROJECT_ROOT)})


async def dual_run_writers(ctx: WorkflowContext) -> PhaseResult:
    """Phase 2: Run dual writers in parallel."""
    await launch_dual_writers(ctx.task_id, ctx.writer_prompt_path, resume_mode=False)
    return PhaseResult(data={"writers_complete": True})


async def dual_generate_panel_prompt(ctx: WorkflowContext) -> PhaseResult:
    """Phase 3: Generate panel review prompt."""
    await generate_panel_prompt(ctx.task_id, ctx.prompts_dir)
    return PhaseResult()


async def dual_judge_panel(ctx: WorkflowContext) -> PhaseResult:
    """Phase 4: Judge panel reviews both writers."""
    should_resume = ctx.resume_from == 4
    await launch_judge_panel(ctx.task_id, ctx.panel_prompt_path, "panel", resume_mode=should_resume)
    return PhaseResult(data={"panel_complete": True})


async def dual_aggregate_decisions(ctx: WorkflowContext) -> PhaseResult:
    """Phase 5: Aggregate judge decisions and determine path."""
    result = run_decide_and_get_result(ctx.task_id)
    ctx.result = result

    peer_status = run_decide_peer_review(ctx.task_id, require_decisions=result["next_action"] == "MERGE")
    has_peer_review_issues = (
        result["next_action"] == "MERGE"
        and not peer_status.get("approved")
        and peer_status.get("decisions_found", 0) > 0
    )

    effective_path = result["next_action"]
    if has_peer_review_issues and effective_path == "MERGE":
        print_info("Peer review found issues - switching to SYNTHESIS path")
        effective_path = "SYNTHESIS"

    next_workflow = {
        "SYNTHESIS": WorkflowType.SYNTHESIS,
        "MERGE": WorkflowType.MERGE,
        "FEEDBACK": WorkflowType.FEEDBACK,
    }.get(effective_path)

    return PhaseResult(
        data={"path": result["next_action"], "winner": result["winner"], "next_action": result["next_action"]},
        next_workflow=next_workflow,
    )


# =============================================================================
# SYNTHESIS PATH HANDLERS (Phases 6-10)
# =============================================================================


async def synthesis_run(ctx: WorkflowContext) -> PhaseResult:
    """Phase 6: Run synthesis on winner's code."""
    await run_synthesis(ctx.task_id, ctx.result, ctx.prompts_dir)
    return PhaseResult(data={"synthesis_complete": True})


async def synthesis_peer_review(ctx: WorkflowContext) -> PhaseResult:
    """Phase 7: Peer review after synthesis."""
    clear_peer_review_decisions(ctx.task_id)
    await run_peer_review(ctx.task_id, ctx.result, ctx.prompts_dir)
    return PhaseResult(data={"peer_review_complete": True})


async def synthesis_final_decision(ctx: WorkflowContext) -> PhaseResult:
    """Phase 8: Final decision after peer review."""
    final_result = run_decide_peer_review(ctx.task_id)
    ctx.final_result = final_result

    peer_review_judges = [j for j in get_judge_configs() if j.peer_review_only]
    total_peer_judges = len(peer_review_judges) if peer_review_judges else 1
    decisions_found = final_result.get("decisions_found", 0)

    if decisions_found < total_peer_judges:
        print_warning(f"Only {decisions_found}/{total_peer_judges} peer-review judges have decisions")
        print_warning("Run peer-review to get all judge decisions before proceeding")
        console.print()
        console.print("[cyan]To run missing judges:[/cyan]")
        console.print(f"  cube peer-review {ctx.task_id}")
        return PhaseResult(exit=True)

    if final_result["approved"] and not final_result["remaining_issues"]:
        await create_pr(ctx.task_id, ctx.result["winner"])
        return PhaseResult(exit=True)

    if not final_result["approved"] or final_result["remaining_issues"]:
        console.print()
        print_warning(f"Peer review has {len(final_result['remaining_issues'])} issue(s) to address")
        console.print()
        console.print("Issues to address:")
        for issue in final_result["remaining_issues"]:
            console.print(f"  • {issue}")

    return PhaseResult()


async def synthesis_minor_fixes(ctx: WorkflowContext) -> PhaseResult:
    """Phase 9: Address minor issues from peer review."""
    if ctx.resume_from > 8:
        ctx.final_result = run_decide_peer_review(ctx.task_id)

    final_result = ctx.final_result
    peer_review_judges = [j for j in get_judge_configs() if j.peer_review_only]
    total_peer_judges = len(peer_review_judges) if peer_review_judges else 1
    decisions_found = final_result.get("decisions_found", 0)

    if decisions_found < total_peer_judges:
        print_warning(f"Only {decisions_found}/{total_peer_judges} peer-review judges have decisions")
        print_warning("Run peer-review to get all judge decisions before proceeding")
        console.print()
        console.print("[cyan]To run missing judges:[/cyan]")
        console.print(f"  cube peer-review {ctx.task_id}")
        return PhaseResult(exit=True)

    if final_result["approved"] and not final_result["remaining_issues"]:
        print_success("All judges approved with no issues - skipping minor fixes")
    elif not final_result["remaining_issues"]:
        print_warning("No specific issues listed - skipping minor fixes")
    else:
        await run_minor_fixes(ctx.task_id, ctx.result, final_result["remaining_issues"], ctx.prompts_dir)

    return PhaseResult()


async def synthesis_final_peer_review(ctx: WorkflowContext) -> PhaseResult:
    """Phase 10: Final peer review and PR creation."""
    clear_peer_review_decisions(ctx.task_id)
    await run_peer_review(ctx.task_id, ctx.result, ctx.prompts_dir)

    final_check = run_decide_peer_review(ctx.task_id)
    if final_check["approved"] and not final_check["remaining_issues"]:
        await create_pr(ctx.task_id, ctx.result["winner"])
    elif final_check["approved"]:
        print_warning(f"Approved but still has {len(final_check['remaining_issues'])} issue(s) after minor fixes")
        console.print()
        console.print("Issues remaining:")
        for issue in final_check["remaining_issues"]:
            console.print(f"  • {issue}")
        console.print()
        console.print("Creating PR anyway (all judges approved)...")
        await create_pr(ctx.task_id, ctx.result["winner"])
    else:
        _handle_fix_loop(ctx, final_check)
        return PhaseResult(exit=True)

    return PhaseResult()


def _handle_fix_loop(ctx: WorkflowContext, final_check: dict) -> None:
    """Handle case where fixes didn't resolve all issues."""
    console.print()
    peer_review_judges = [j for j in get_judge_configs() if j.peer_review_only]
    total_peer_judges = len(peer_review_judges) if peer_review_judges else 1

    decisions_count = final_check.get("decisions_found", 0)
    approvals_count = final_check.get("approvals", 0)

    if decisions_count < total_peer_judges:
        print_warning(f"Missing peer review decisions ({decisions_count}/{total_peer_judges})")
        console.print()
        console.print("Options:")
        console.print("  1. Get missing judge(s) to file decisions:")
        for judge_cfg in peer_review_judges:
            peer_file = PROJECT_ROOT / ".prompts" / "decisions" / f"{judge_cfg.key.replace('_', '-')}-{ctx.task_id}-peer-review.json"
            if not peer_file.exists():
                console.print(f"     cube peer-review {ctx.task_id} -j {judge_cfg.key}")
        console.print()
        console.print(f"  2. Continue with {decisions_count}/{total_peer_judges} decisions:")
        console.print("     cube auto task.md --resume-from 8")
    else:
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
        console.print("  1. Check remaining issues in peer-review decisions:")
        console.print(f"     ls .prompts/decisions/*{ctx.task_id}*peer-review*")
        console.print("  2. Fix issues in winner's worktree:")
        console.print(f"     cd ~/.cube/worktrees/*/writer-*-{ctx.task_id}")
        console.print("  3. Commit and push, then re-run peer review:")
        console.print("     cube auto --resume-from 10")
        console.print()
        console.print("[cyan]Option 2:[/cyan] Run another round of minor fixes")
        console.print("  cube auto --resume-from 9")
        console.print()
        console.print("[cyan]Option 3:[/cyan] Start fresh from synthesis")
        console.print("  cube auto --resume-from 6")


# =============================================================================
# MERGE PATH HANDLERS (Phases 6-7)
# =============================================================================


async def merge_automated_review(ctx: WorkflowContext) -> PhaseResult:
    """Phase 6: Automated review before PR."""
    peer_only_judges = [j for j in get_judge_configs() if j.peer_review_only]
    wants_peer_review = ctx.resume_alias in ("peer-review", "peer", "peer-panel")

    if not peer_only_judges and not wants_peer_review:
        return PhaseResult(data={"path": "MERGE"})

    print_info(f"Running {len(peer_only_judges)} automated reviewer(s) before PR: {', '.join(j.label for j in peer_only_judges)}")

    temp_prompt = ctx.prompts_dir / f"temp-peer-review-{ctx.task_id}.md"
    temp_prompt.write_text(ctx.task_id)

    clear_peer_review_decisions(ctx.task_id)
    await launch_judge_panel(ctx.task_id, temp_prompt, "peer-review", resume_mode=False, winner=ctx.result["winner"])

    auto_result = run_decide_peer_review(ctx.task_id)

    if auto_result.get("approved") and auto_result.get("decisions_found", 0) > 0:
        print_info("✅ Automated review passed!")
        return PhaseResult(data={"path": "MERGE", "peer_review_complete": True})

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

        await run_minor_fixes(ctx.task_id, ctx.result, issues, ctx.prompts_dir)

        console.print()
        console.print("[yellow]═══ Re-running Automated Review ═══[/yellow]")
        clear_peer_review_decisions(ctx.task_id)
        await launch_judge_panel(ctx.task_id, temp_prompt, "peer-review", resume_mode=False, winner=ctx.result["winner"])

        recheck = run_decide_peer_review(ctx.task_id)
        if recheck.get("approved"):
            print_success("✅ Automated review passed after fixes!")
            return PhaseResult(data={"path": "MERGE", "peer_review_complete": True})

        remaining = recheck.get("remaining_issues", [])
        console.print()
        print_warning(f"Still {len(remaining)} issue(s) after fixes")
        console.print()
        from ...core.user_config import load_config

        config = load_config()
        default_winner = config.writer_order[0] if config.writer_order else ""
        winner = ctx.result.get("winner", default_winner).replace("writer_", "")
        console.print("Send targeted feedback to address remaining issues:")
        console.print(f'  cube feedback {winner} {ctx.task_id} "<fix instructions>"')
        console.print(f"  cube auto {ctx.task_id} --resume-from peer-review")
        return PhaseResult(exit=True, data={"path": "MERGE"})

    elif decisions_found == 0:
        print_warning("No automated review decisions found!")
        console.print("Retry:")
        console.print(f"  cube auto {ctx.task_id} --resume-from peer-review")
        return PhaseResult(exit=True)
    else:
        print_warning(f"Automated review not approved ({approvals}/{decisions_found} approved)")
        console.print()
        console.print("Fix issues or wait for decisions, then resume:")
        console.print(f"  cube auto {ctx.task_id} --resume-from 6")
        return PhaseResult(exit=True, data={"path": "MERGE"})


async def merge_create_pr(ctx: WorkflowContext) -> PhaseResult:
    """Phase 7: Create PR for merge path."""
    pr_check = run_decide_peer_review(ctx.task_id)
    if not pr_check.get("approved") or pr_check.get("remaining_issues"):
        issues = pr_check.get("remaining_issues", [])
        print_warning(f"Cannot create PR - {len(issues)} issue(s) outstanding")
        if issues:
            for issue in issues[:3]:
                console.print(f"  • {issue[:80]}")
        console.print()
        console.print("Fix issues first, then resume:")
        console.print(f"  cube auto {ctx.task_id} --resume-from peer-review")
        return PhaseResult(exit=True)

    await create_pr(ctx.task_id, ctx.result["winner"])
    return PhaseResult(data={"path": "MERGE"})


# =============================================================================
# FEEDBACK PATH HANDLERS (Phases 6-8)
# =============================================================================


async def feedback_generate(ctx: WorkflowContext) -> PhaseResult:
    """Phase 6: Generate feedback for writers."""
    winner_key = ctx.result.get("winner")
    split_feedback = not winner_key or winner_key.upper() == "TIE"

    if split_feedback:
        console.print("Generating feedback for both writers...")
        await generate_dual_feedback(ctx.task_id, ctx.prompts_dir)
    else:
        console.print(f"Generating feedback for winner ({winner_key})...")
        await generate_dual_feedback(ctx.task_id, ctx.prompts_dir, winner_only=True, winner_key=winner_key)

    return PhaseResult(data={"path": "FEEDBACK"})


async def feedback_rerun_panel(ctx: WorkflowContext) -> PhaseResult:
    """Phase 7: Re-run panel review after feedback."""
    await launch_judge_panel(ctx.task_id, ctx.panel_prompt_path, "panel", resume_mode=False)
    return PhaseResult(data={"path": "FEEDBACK", "panel_complete": True})


async def feedback_reaggregate(ctx: WorkflowContext) -> PhaseResult:
    """Phase 8: Re-aggregate decisions after feedback."""
    new_result = run_decide_and_get_result(ctx.task_id)

    if new_result["next_action"] == "MERGE":
        print_success("Writers addressed feedback - ready for merge!")
        await create_pr(ctx.task_id, new_result["winner"])
        return PhaseResult(exit=True, data={"path": new_result["next_action"], "winner": new_result["winner"]})
    elif new_result["next_action"] == "SYNTHESIS":
        print_info("Winner selected after feedback - continuing to synthesis")
        console.print("Resume with:")
        console.print(f"  cube auto {ctx.task_id} --resume-from 6")
        return PhaseResult(exit=True, data={"path": new_result["next_action"], "winner": new_result["winner"]})
    elif new_result["next_action"] == "FEEDBACK":
        print_warning("Still needs FEEDBACK. Send more feedback and re-run panel:")
        console.print(f"  cube auto {ctx.task_id} --resume-from 6")
        return PhaseResult(exit=True, data={"path": "FEEDBACK"})
    else:
        print_warning("Unexpected state. Check decisions and decide next action:")
        console.print(f"  cube decide {ctx.task_id}")
        return PhaseResult(exit=True)


# =============================================================================
# WORKFLOW REGISTRATION
# =============================================================================


def register_all_workflows() -> None:
    """Register all phase handlers to their workflows."""
    from .phases_registry import (
        DUAL_WORKFLOW,
        FEEDBACK_WORKFLOW,
        MERGE_WORKFLOW,
        Phase,
        SINGLE_WORKFLOW,
        SYNTHESIS_WORKFLOW,
    )

    SINGLE_WORKFLOW.clear()
    SINGLE_WORKFLOW.extend([
        Phase(1, "Generate Writer Prompt", single_generate_prompt),
        Phase(2, "Run Single Writer", single_run_writer),
        Phase(3, "Judge Panel", single_judge_panel),
        Phase(4, "Minor Fixes", single_minor_fixes),
        Phase(5, "Create PR", single_create_pr),
    ])

    DUAL_WORKFLOW.clear()
    DUAL_WORKFLOW.extend([
        Phase(1, "Generate Writer Prompt", dual_generate_prompt),
        Phase(2, "Dual Writers Execute", dual_run_writers),
        Phase(3, "Generate Panel Prompt", dual_generate_panel_prompt),
        Phase(4, "Judge Panel Review", dual_judge_panel),
        Phase(5, "Aggregate Decisions", dual_aggregate_decisions),
    ])

    SYNTHESIS_WORKFLOW.clear()
    SYNTHESIS_WORKFLOW.extend([
        Phase(6, "Synthesis", synthesis_run),
        Phase(7, "Peer Review", synthesis_peer_review),
        Phase(8, "Final Decision", synthesis_final_decision),
        Phase(9, "Address Minor Issues", synthesis_minor_fixes),
        Phase(10, "Final Peer Review", synthesis_final_peer_review),
    ])

    MERGE_WORKFLOW.clear()
    MERGE_WORKFLOW.extend([
        Phase(6, "Automated Review", merge_automated_review),
        Phase(7, "Create PR", merge_create_pr),
    ])

    FEEDBACK_WORKFLOW.clear()
    FEEDBACK_WORKFLOW.extend([
        Phase(6, "Generate Feedback", feedback_generate),
        Phase(7, "Re-run Panel Review", feedback_rerun_panel),
        Phase(8, "Re-aggregate Decisions", feedback_reaggregate),
    ])


register_all_workflows()

