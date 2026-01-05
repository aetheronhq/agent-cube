# Task 08: Refactor Workflow to State Machine Pattern

## Problem

The current workflow implementation in `python/cube/commands/orchestrate/workflow.py` uses nested if-statements to handle different workflow paths (SINGLE, DUAL→MERGE, DUAL→FEEDBACK). This leads to:

- Repetitive `if resume_from <= N:` checks throughout the code
- Hard-coded phase numbers that differ between paths
- Complex conditional logic in `cli.py` to calculate resume phases
- Difficult to add new workflow types or modify existing ones
- Phase numbering mismatches between paths causing bugs

## Solution

Implement a **Phase Registry / State Machine** pattern where workflows are defined declaratively.

## Implementation

### 1. Define Phase dataclass

```python
@dataclass
class Phase:
    num: int
    name: str
    handler: Callable[[WorkflowContext], Awaitable[PhaseResult]]
    state_updates: dict[str, Any] | None = None
```

### 2. Define workflows as phase sequences

```python
SINGLE_WORKFLOW = [
    Phase(1, "Generate Prompt", generate_writer_prompt),
    Phase(2, "Run Writer", run_single_writer),
    Phase(3, "Judge Panel", run_judge_panel),
    Phase(4, "Minor Fixes", run_minor_fixes),
    Phase(5, "Create PR", create_pr),
]

DUAL_WORKFLOW = [
    Phase(1, "Generate Prompt", generate_writer_prompt),
    Phase(2, "Run Writers", run_dual_writers),
    Phase(3, "Synthesis Prompt", generate_synthesis_prompt),
    Phase(4, "Judge Panel", run_judge_panel),
    Phase(5, "Decide Winner", run_decide),
    # Branches to MERGE or FEEDBACK based on result
]

MERGE_WORKFLOW = [
    Phase(6, "Peer Review", run_peer_review),
    Phase(7, "Final Decision", run_final_decision),
    Phase(8, "Minor Fixes", run_minor_fixes),
    Phase(9, "Create PR", create_pr),
]

FEEDBACK_WORKFLOW = [
    Phase(6, "Generate Feedback", generate_feedback_prompt),
    Phase(7, "Run Feedback", run_feedback),
    Phase(8, "Re-aggregate", run_decide),
    # Loops back or transitions to MERGE
]
```

### 3. Create workflow executor

```python
async def execute_workflow(
    workflow_type: str,
    task_id: str,
    resume_from: int,
    ctx: WorkflowContext
) -> None:
    workflow = get_workflow(workflow_type)
    
    for phase in workflow:
        if phase.num < resume_from:
            continue
            
        console.print(f"[yellow]═══ Phase {phase.num}: {phase.name} ═══[/yellow]")
        log_phase(phase.num, phase.name)
        
        result = await phase.handler(ctx)
        update_phase(task_id, phase.num, **(phase.state_updates or {}))
        
        # Handle branching
        if result.next_workflow:
            return await execute_workflow(result.next_workflow, task_id, phase.num + 1, ctx)
        if result.exit:
            return
```

### 4. Simplify CLI resume logic

```python
def get_resume_phase(state: WorkflowState) -> int:
    workflow = get_workflow(state.path)
    max_phase = workflow[-1].num
    
    if state.current_phase >= max_phase:
        return max_phase  # Complete
    return state.current_phase + 1
```

## Files to Modify

- `python/cube/commands/orchestrate/workflow.py` - Main refactor
- `python/cube/cli.py` - Simplify resume logic
- `python/cube/core/state.py` - May need WorkflowContext additions

## Files to Create

- `python/cube/commands/orchestrate/phases_registry.py` - Phase definitions
- `python/cube/commands/orchestrate/executor.py` - Workflow executor

## Benefits

1. **Declarative workflows** - Easy to see the full flow at a glance
2. **No phase number bugs** - Each workflow defines its own numbering
3. **Easy to extend** - Add new workflows by defining a new list
4. **Testable** - Can unit test individual phases and workflow transitions
5. **Self-documenting** - Phase names and order are explicit

## Acceptance Criteria

- [ ] All existing workflow paths (SINGLE, DUAL→MERGE, DUAL→FEEDBACK) work identically
- [ ] Resume from any phase works correctly for all paths
- [ ] No regression in existing functionality
- [ ] Phase handlers are individually testable
- [ ] Adding a new workflow type requires only defining a Phase list

