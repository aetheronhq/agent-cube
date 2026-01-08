"""Phase handlers for workflow state machine."""

import typer

from ...automation.dual_writers import launch_dual_writers
from ...automation.judge_panel import launch_judge_panel
from ...automation.single_writer import launch_single_writer
from ...core.config import PROJECT_ROOT, resolve_path
from ...core.output import console, print_error, print_info, print_success, print_warning
from ...core.user_config import get_judge_configs
from .decisions import clear_peer_review_decisions, run_decide_and_get_result, run_decide_peer_review
from .phases import run_minor_fixes, run_peer_review, run_synthesis
from .phases_registry import Phase, PhaseResult, WorkflowContext
from .pr import create_pr
from .prompts import generate_dual_feedback, generate_panel_prompt, generate_writer_prompt


def is_single_mode(ctx: WorkflowContext) -> bool:
    """Check if running in single writer mode."""
    return ctx.writer_key is not None


# =============================================================================
# UNIFIED PHASE HANDLERS (Phases 1-5)
# =============================================================================


async def phase1_generate_prompt(ctx: WorkflowContext) -> PhaseResult:
    """Phase 1: Generate writer prompt."""
    if not ctx.task_file:
        print_error("Task file required for Phase 1.")
        raise typer.Exit(1)

    task_path = resolve_path(ctx.task_file)
    await generate_writer_prompt(ctx.task_id, task_path.read_text(), ctx.prompts_dir)

    mode = "single" if is_single_mode(ctx) else "dual"
    return PhaseResult(data={"mode": mode, "writer_key": ctx.writer_key, "project_root": str(PROJECT_ROOT)})


async def phase2_run_writers(ctx: WorkflowContext) -> PhaseResult:
    """Phase 2: Run writer(s). Single or dual based on mode."""
    if is_single_mode(ctx):
        await launch_single_writer(
            ctx.task_id, ctx.writer_prompt_path, ctx.writer_key or "", resume_mode=(ctx.resume_from == 2)
        )
    else:
        await launch_dual_writers(ctx.task_id, ctx.writer_prompt_path, resume_mode=False)
    return PhaseResult(data={"writers_complete": True})


async def phase3_generate_panel_prompt(ctx: WorkflowContext) -> PhaseResult:
    """Phase 3: Generate panel review prompt. SKIP if single mode."""
    if is_single_mode(ctx):
        print_info("Single mode - skipping panel prompt generation")
        return PhaseResult(data={"skipped": True})

    await generate_panel_prompt(ctx.task_id, ctx.prompts_dir)
    return PhaseResult()


async def phase4_judge_panel(ctx: WorkflowContext) -> PhaseResult:
    """Phase 4: Judge panel compares writers. SKIP if single mode (no comparison)."""
    if is_single_mode(ctx):
        print_info("Single mode - skipping comparison panel")
        return PhaseResult(data={"skipped": True})

    should_resume = ctx.resume_from == 4
    await launch_judge_panel(ctx.task_id, ctx.panel_prompt_path, "panel", resume_mode=should_resume)
    return PhaseResult(data={"panel_complete": True})


async def phase5_aggregate(ctx: WorkflowContext) -> PhaseResult:
    """Phase 5: Aggregate decisions. SKIP if single mode (auto-set winner)."""
    if is_single_mode(ctx):
        print_info("Single mode - auto-setting winner")
        ctx.result = {"winner": ctx.writer_key, "all_approved": False}
        return PhaseResult(data={"winner": ctx.writer_key, "all_approved": False})

    result = run_decide_and_get_result(ctx.task_id)
    ctx.result = result

    return PhaseResult(data={"winner": result["winner"], "all_approved": result.get("all_approved", False)})


# =============================================================================
# SYNTHESIS PATH HANDLERS (Phases 6-10)
# =============================================================================


async def synthesis_run(ctx: WorkflowContext) -> PhaseResult:
    """Phase 6: Run synthesis on winner's code.

    - TIE: Generate feedback and tell user to re-run panel
    - all_approved: Skip synthesis
    - Otherwise: Run synthesis
    """
    winner = ctx.result.get("winner")

    # TIE case - need feedback loop
    if winner == "TIE":
        print_warning("TIE detected - both writers need feedback")
        await generate_dual_feedback(ctx.task_id, ctx.result, ctx.prompts_dir)
        console.print()
        console.print("[cyan]Feedback generated. Re-run panel:[/cyan]")
        console.print(f"  cube auto {ctx.task_id} --resume-from 4")
        return PhaseResult(exit=True, data={"needs_feedback": True})

    # All approved - skip synthesis
    if ctx.result.get("all_approved"):
        print_info("All judges approved - skipping synthesis")
        return PhaseResult(data={"synthesis_complete": True, "skipped": True})

    # Winner needs changes - run synthesis
    await run_synthesis(ctx.task_id, ctx.result, ctx.prompts_dir)
    return PhaseResult(data={"synthesis_complete": True})


async def synthesis_peer_review(ctx: WorkflowContext) -> PhaseResult:
    """Phase 7: Peer review - runs judges that haven't already approved."""
    import json

    from ...core.decision_parser import get_decision_file_path

    all_judges = get_judge_configs()

    # Find judges that need to run (haven't approved or are peer_review_only)
    judges_to_run = []
    for judge in all_judges:
        if judge.peer_review_only:
            judges_to_run.append(judge)
            continue

        # Check panel decision for this judge
        panel_file = get_decision_file_path(judge.key, ctx.task_id, review_type="panel")
        if not panel_file.exists():
            judges_to_run.append(judge)
            continue

        try:
            with open(panel_file) as f:
                decision = json.load(f)
            if decision.get("decision", "").upper() != "APPROVED":
                judges_to_run.append(judge)
        except (json.JSONDecodeError, KeyError):
            judges_to_run.append(judge)

    if not judges_to_run:
        print_info("All judges already approved - skipping peer review")
        return PhaseResult(data={"peer_review_complete": True, "approved": True})

    print_info(f"Running {len(judges_to_run)} judge(s) for peer review: {', '.join(j.label for j in judges_to_run)}")

    clear_peer_review_decisions(ctx.task_id)
    await run_peer_review(ctx.task_id, ctx.result, ctx.prompts_dir, judges_to_run=judges_to_run)
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
            peer_file = (
                PROJECT_ROOT
                / ".prompts"
                / "decisions"
                / f"{judge_cfg.key.replace('_', '-')}-{ctx.task_id}-peer-review.json"
            )
            if not peer_file.exists():
                console.print(f"     cube peer-review {ctx.task_id} -j {judge_cfg.key}")
        console.print()
        console.print(f"  2. Continue with {decisions_count}/{total_peer_judges} decisions:")
        console.print("     cube auto task.md --resume-from 8")
    else:
        console.print("[bold red]🔄 Fix Loop Detected[/bold red]")
        console.print()
        console.print(
            f"Minor fixes were applied but {decisions_count - approvals_count} judge(s) still request changes."
        )
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
# WORKFLOW REGISTRATION
# =============================================================================


def register_phases() -> None:
    """Register all phase handlers."""
    from .phases_registry import PHASES

    PHASES.clear()
    PHASES.extend(
        [
            # Phases 1-5: Writers and comparison (single mode skips 3-5)
            Phase(1, "Generate Writer Prompt", phase1_generate_prompt),
            Phase(2, "Run Writers", phase2_run_writers),
            Phase(3, "Generate Panel Prompt", phase3_generate_panel_prompt),
            Phase(4, "Judge Panel Review", phase4_judge_panel),
            Phase(5, "Aggregate Decisions", phase5_aggregate),
            # Phases 6-10: Synthesis and PR
            Phase(6, "Synthesis", synthesis_run),
            Phase(7, "Peer Review", synthesis_peer_review),
            Phase(8, "Final Decision", synthesis_final_decision),
            Phase(9, "Address Minor Issues", synthesis_minor_fixes),
            Phase(10, "Re-Review & PR", synthesis_final_peer_review),
        ]
    )


register_phases()
