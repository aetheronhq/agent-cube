"""Workflow executor for state machine pattern."""

from ...core.master_log import get_master_log
from ...core.output import console, print_success
from ...core.state import update_phase
from .phases_registry import PhaseResult, WorkflowContext, get_phases


async def execute_workflow(ctx: WorkflowContext) -> PhaseResult:
    """Execute workflow from the specified resume point."""
    is_single = ctx.writer_key is not None

    if is_single:
        console.print("[bold cyan]🤖 Agent Cube Single-Writer Mode[/bold cyan]")
        console.print(f"Task: {ctx.task_id}")
        console.print(f"Writer: {ctx.writer_key}")
    else:
        console.print("[bold cyan]🤖 Agent Cube Dual-Writer Mode[/bold cyan]")
        console.print(f"Task: {ctx.task_id}")

    master_log = get_master_log()
    current_phase_idx = 0
    phases = get_phases()

    while current_phase_idx < len(phases):
        phase = phases[current_phase_idx]

        if phase.num < ctx.resume_from:
            current_phase_idx += 1
            continue

        console.print()
        console.print(f"[yellow]═══ Phase {phase.num}: {phase.name} ═══[/yellow]")
        if master_log:
            master_log.write_phase_start(phase.num, phase.name)

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

        # Handle phase jump (e.g., TIE -> back to panel)
        if result.next_phase is not None:
            ctx.resume_from = result.next_phase
            current_phase_idx = 0  # Reset to find the target phase
            continue

        current_phase_idx += 1

    print_success("🎉 Workflow complete!")
    return PhaseResult(success=True)
