"""Workflow executor for state machine pattern."""

from ...core.master_log import get_master_log
from ...core.output import console, print_error, print_success
from ...core.state import update_phase
from .phases_registry import Phase, PhaseResult, WorkflowContext, WorkflowType, get_workflow


async def execute_workflow(
    workflow_type: WorkflowType | str,
    ctx: WorkflowContext,
) -> PhaseResult:
    """Execute a workflow from the specified resume point.

    Args:
        workflow_type: The type of workflow to execute
        ctx: Workflow context with task info and state

    Returns:
        PhaseResult indicating success/failure and any workflow transitions
    """
    workflow = get_workflow(workflow_type)
    if not workflow:
        print_error(f"Unknown workflow type: {workflow_type}")
        return PhaseResult(success=False, exit=True, exit_message=f"Unknown workflow: {workflow_type}")

    master_log = get_master_log()

    def log_phase(phase_num: int, phase_name: str) -> None:
        if master_log:
            master_log.write_phase_start(phase_num, phase_name)

    for phase in workflow:
        if phase.num < ctx.resume_from:
            continue

        console.print()
        console.print(f"[yellow]═══ Phase {phase.num}: {phase.name} ═══[/yellow]")
        log_phase(phase.num, phase.name)

        result = await phase.handler(ctx)

        state_updates = phase.state_updates.copy() if phase.state_updates else {}
        state_updates.update(result.data)
        if state_updates:
            update_phase(ctx.task_id, phase.num, **state_updates)
        else:
            update_phase(ctx.task_id, phase.num)

        if result.exit:
            if result.exit_message:
                console.print(result.exit_message)
            return result

        if result.next_workflow:
            return await execute_workflow(result.next_workflow, ctx)

    return PhaseResult(success=True)


async def execute_single_workflow(ctx: WorkflowContext) -> PhaseResult:
    """Execute single-writer workflow."""
    console.print("[bold cyan]🤖 Agent Cube Single-Writer Orchestration[/bold cyan]")
    console.print(f"Task: {ctx.task_id}")
    console.print(f"Writer: {ctx.writer_key}")

    result = await execute_workflow(WorkflowType.SINGLE, ctx)

    if result.success and not result.exit:
        print_success("🎉 Single-writer workflow complete!")

    return result


async def execute_dual_workflow(ctx: WorkflowContext) -> PhaseResult:
    """Execute dual-writer workflow."""
    console.print("[bold cyan]🤖 Agent Cube Autonomous Orchestration[/bold cyan]")
    console.print(f"Task: {ctx.task_id}")

    result = await execute_workflow(WorkflowType.DUAL, ctx)

    if result.success and not result.exit:
        print_success("🎉 Autonomous workflow complete!")

    return result

