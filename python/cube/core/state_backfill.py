"""Backfill workflow state from existing artifacts."""

import json

from .config import PROJECT_ROOT
from .session import load_session
from .state import WorkflowState, save_state


def backfill_state_from_artifacts(task_id: str) -> WorkflowState:
    """Create state by analyzing existing sessions, decisions, etc.

    Note: This only determines WHAT phase we're at, not WHICH path to take.
    The orchestrator computes the path at runtime from current decisions.
    """
    from .user_config import load_config

    config = load_config()

    prompts_dir = PROJECT_ROOT / ".prompts"
    decisions_dir = prompts_dir / "decisions"

    completed_phases = []
    current_phase = 0
    winner = None
    next_action = None

    # Check writers
    writers_active = False
    writers_complete = True
    for writer_key in config.writer_order:
        if load_session(writer_key.upper(), task_id):
            writers_active = True
        else:
            writers_complete = False

    if writers_active:
        completed_phases.extend([1, 2])
        current_phase = 2

    # Check panel sessions
    panel_active = False
    for judge_key in config.judge_order:
        if config.judges[judge_key].peer_review_only:
            continue
        if load_session(judge_key.upper(), f"{task_id}_panel"):
            panel_active = True
            break

    if panel_active:
        completed_phases.extend([3, 4])
        current_phase = 4

    # Check panel decisions
    from .decision_files import find_decision_file

    decisions_found = False
    for judge_key in config.judge_order:
        if config.judges[judge_key].peer_review_only:
            continue
        decision_file = find_decision_file(judge_key, task_id, "decision")
        if decision_file:
            decisions_found = True
            break

    aggregated_file = decisions_dir / f"{task_id}-aggregated.json"

    if decisions_found:
        if 5 not in completed_phases:
            completed_phases.append(5)
        current_phase = max(current_phase, 5)

        # Get winner from aggregated if it exists
        if aggregated_file.exists():
            with open(aggregated_file) as f:
                result = json.load(f)
                winner = result.get("winner")
                next_action = result.get("next_action")

    # Check synthesis artifacts
    synthesis_file = prompts_dir / f"synthesis-{task_id}.md"
    if synthesis_file.exists():
        if 6 not in completed_phases:
            completed_phases.append(6)
        current_phase = max(current_phase, 6)

    # Check feedback artifacts
    feedback_found = False
    for writer_key in config.writer_order:
        wconfig = config.writers[writer_key]
        if (prompts_dir / f"feedback-{wconfig.name}-{task_id}.md").exists():
            feedback_found = True
            break

    if feedback_found:
        if 6 not in completed_phases:
            completed_phases.append(6)
        current_phase = max(current_phase, 6)

    # Check peer review sessions
    peer_active = False
    for judge_key in config.judge_order:
        # Check any judge for peer review session
        if load_session(judge_key.upper(), f"{task_id}_peer-review"):
            peer_active = True
            break

    if peer_active:
        if 7 not in completed_phases:
            completed_phases.append(7)
        current_phase = max(current_phase, 7)

    # Check minor fixes
    minor_fixes_path = prompts_dir / f"minor-fixes-{task_id}.md"
    if minor_fixes_path.exists():
        if 9 not in completed_phases:
            completed_phases.append(9)
        current_phase = max(current_phase, 9)

    state = WorkflowState(
        task_id=task_id,
        current_phase=current_phase,
        path=next_action or "PENDING",  # Just for display, orchestrator computes actual path
        completed_phases=sorted(list(set(completed_phases))),
        winner=winner,
        next_action=next_action,
        writers_complete=writers_complete,
        panel_complete=decisions_found,
        synthesis_complete=synthesis_file.exists(),
        peer_review_complete=peer_active,
    )

    save_state(state)
    return state
