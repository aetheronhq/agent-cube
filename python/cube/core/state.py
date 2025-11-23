"""Workflow state management for autonomous orchestration."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class WorkflowState:
    """State of an autonomous workflow."""
    task_id: str
    current_phase: int
    path: str  # SYNTHESIS, FEEDBACK, MERGE
    completed_phases: List[int]
    winner: Optional[str] = None
    next_action: Optional[str] = None
    writers_complete: bool = False
    panel_complete: bool = False
    synthesis_complete: bool = False
    peer_review_complete: bool = False
    updated_at: str = ""
    
    def __post_init__(self):
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()

def get_state_file(task_id: str) -> Path:
    """Get state file path for a task."""
    state_dir = Path.home() / ".cube" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir / f"{task_id}.json"

def load_state(task_id: str) -> Optional[WorkflowState]:
    """Load workflow state for a task."""
    state_file = get_state_file(task_id)
    
    if not state_file.exists():
        return None
    
    try:
        with open(state_file) as f:
            data = json.load(f)
        
        return WorkflowState(
            task_id=data["task_id"],
            current_phase=data["current_phase"],
            path=data["path"],
            completed_phases=data["completed_phases"],
            winner=data.get("winner"),
            next_action=data.get("next_action"),
            writers_complete=data.get("writers_complete", False),
            panel_complete=data.get("panel_complete", False),
            synthesis_complete=data.get("synthesis_complete", False),
            peer_review_complete=data.get("peer_review_complete", False),
            updated_at=data.get("updated_at", "")
        )
    except Exception as exc:
        from .output import console_err
        console_err.print(
            f"[bold red]Failed to load workflow state for {task_id}[/bold red]\n"
            f"[dim]{state_file}[/dim]\nError: {exc}"
        )
        return None

def save_state(state: WorkflowState) -> None:
    """Save workflow state with atomic write."""
    import tempfile
    import shutil
    
    state.updated_at = datetime.now().isoformat()
    state_file = get_state_file(state.task_id)
    
    temp_fd, temp_path = tempfile.mkstemp(dir=state_file.parent, suffix='.json')
    try:
        with os.fdopen(temp_fd, 'w') as f:
            json.dump(asdict(state), f, indent=2)
        
        shutil.move(temp_path, state_file)
    except Exception:
        Path(temp_path).unlink(missing_ok=True)
        raise

def update_phase(task_id: str, phase: int, **kwargs) -> WorkflowState:
    """Update workflow to a new phase."""
    state = load_state(task_id)
    
    if not state:
        state = WorkflowState(
            task_id=task_id,
            current_phase=phase,
            path=kwargs.get("path", "UNKNOWN"),
            completed_phases=[]
        )
    
    if phase not in state.completed_phases:
        state.completed_phases.append(phase)
    
    state.completed_phases = sorted(set(state.completed_phases))
    state.current_phase = phase
    
    for key, value in kwargs.items():
        if hasattr(state, key) and value is not None:
            setattr(state, key, value)
    
    save_state(state)
    return state

def validate_resume(task_id: str, resume_from: int) -> tuple[bool, str]:
    """Validate if we can resume from a specific phase.
    
    Allows resuming from any phase (even skipping ahead) as long as
    basic artifacts might exist. It's up to the user to know what they're doing.
    """
    state = load_state(task_id)
    
    if not state:
        # If trying to skip ahead without ANY state, warn but allow if artifacts exist
        # (state backfill will handle this later)
        return True, ""
    
    # Always allow resuming - user knows best
    return True, ""

def clear_state(task_id: str) -> None:
    """Clear workflow state for a task."""
    state_file = get_state_file(task_id)
    if state_file.exists():
        state_file.unlink()

def get_progress(task_id: str) -> str:
    """Get human-readable progress for a task."""
    state = load_state(task_id)
    
    if not state:
        return "Not started"
    
    total_phases = 10
    progress_pct = (len(state.completed_phases) / total_phases) * 100
    
    return f"Phase {state.current_phase}/10 ({progress_pct:.0f}%) - Path: {state.path}"

