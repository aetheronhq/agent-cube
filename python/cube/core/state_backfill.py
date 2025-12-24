"""Backfill workflow state from existing artifacts."""

import json
from pathlib import Path
from .state import WorkflowState, save_state
from .config import PROJECT_ROOT
from .session import load_session

def backfill_state_from_artifacts(task_id: str) -> WorkflowState:
    """Create state by analyzing existing sessions, decisions, etc."""
    
    prompts_dir = PROJECT_ROOT / ".prompts"
    decisions_dir = prompts_dir / "decisions"
    
    completed_phases = []
    current_phase = 0
    path = "UNKNOWN"
    winner = None
    next_action = None
    
    writer_a = load_session("WRITER_A", task_id)
    writer_b = load_session("WRITER_B", task_id)
    
    if writer_a or writer_b:
        completed_phases.extend([1, 2])
        current_phase = 2
    
    judge_1 = load_session("JUDGE_1", f"{task_id}_panel")
    judge_2 = load_session("JUDGE_2", f"{task_id}_panel")
    judge_3 = load_session("JUDGE_3", f"{task_id}_panel")
    
    if judge_1 or judge_2 or judge_3:
        completed_phases.extend([3, 4])
        current_phase = 4
    
    decision_1 = (decisions_dir / f"judge_1-{task_id}-decision.json").exists()
    decision_2 = (decisions_dir / f"judge_2-{task_id}-decision.json").exists()
    decision_3 = (decisions_dir / f"judge_3-{task_id}-decision.json").exists()
    
    aggregated_file = decisions_dir / f"{task_id}-aggregated.json"
    
    if decision_1 or decision_2 or decision_3:
        if 5 not in completed_phases:
            completed_phases.append(5)
        current_phase = max(current_phase, 5)
        
        if aggregated_file.exists():
            with open(aggregated_file) as f:
                result = json.load(f)
                path = result.get("next_action", "UNKNOWN")
                winner = result.get("winner")
                next_action = result.get("next_action")
    
    synthesis_file = prompts_dir / f"synthesis-{task_id}.md"
    if synthesis_file.exists():
        if path == "UNKNOWN":
            path = "SYNTHESIS"
        if path == "SYNTHESIS" and 6 not in completed_phases:
            completed_phases.append(6)
        if path == "SYNTHESIS":
            current_phase = max(current_phase, 6)
    
    feedback_a = prompts_dir / f"feedback-a-{task_id}.md"
    feedback_b = prompts_dir / f"feedback-b-{task_id}.md"
    if feedback_a.exists() or feedback_b.exists():
        if path == "UNKNOWN":
            path = "FEEDBACK"
        if path == "FEEDBACK" and 6 not in completed_phases:
            completed_phases.append(6)
        if path == "FEEDBACK":
            current_phase = max(current_phase, 6)
    
    peer_1 = load_session("JUDGE_1", f"{task_id}_peer-review")
    peer_2 = load_session("JUDGE_2", f"{task_id}_peer-review")
    peer_3 = load_session("JUDGE_3", f"{task_id}_peer-review")
    
    if peer_1 or peer_2 or peer_3:
        if 7 not in completed_phases:
            completed_phases.append(7)
        current_phase = max(current_phase, 7)
    
    minor_fixes_path = prompts_dir / f"minor-fixes-{task_id}.md"
    if minor_fixes_path.exists():
        if 9 not in completed_phases:
            completed_phases.append(9)
        current_phase = max(current_phase, 9)
    
    state = WorkflowState(
        task_id=task_id,
        current_phase=current_phase,
        path=path,
        completed_phases=sorted(list(set(completed_phases))),
        winner=winner,
        next_action=next_action,
        writers_complete=bool(writer_a and writer_b),
        panel_complete=bool(decision_1 or decision_2 or decision_3),
        synthesis_complete=synthesis_file.exists(),
        peer_review_complete=bool(peer_1 or peer_2 or peer_3)
    )
    
    save_state(state)
    return state

