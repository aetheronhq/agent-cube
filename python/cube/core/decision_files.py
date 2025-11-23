"""Helper functions for finding decision files across locations."""

from pathlib import Path
from typing import Optional
from .config import PROJECT_ROOT, WORKTREE_BASE

def find_decision_file(judge_key: str, task_id: str, decision_type: str = "decision") -> Optional[Path]:
    """Find a decision file, checking fallback locations and auto-copying.
    
    Args:
        judge_key: Judge key (e.g., "judge_1", "judge_3", "foobar")
        task_id: Task ID
        decision_type: 'decision' for panel, 'peer-review' for peer review
    
    Returns:
        Path to decision file in primary location (after copying if needed), or None
    """
    filename = f"{judge_key}-{task_id}-{decision_type}.json".replace("_", "-")
    primary_path = PROJECT_ROOT / ".prompts" / "decisions" / filename
    
    if primary_path.exists():
        return primary_path
    
    fallback_paths = [
        WORKTREE_BASE.parent / ".prompts" / "decisions" / filename,
        Path.home() / ".cube" / ".prompts" / "decisions" / filename,
        WORKTREE_BASE.parent / "decisions" / filename,
    ]
    
    for fallback in fallback_paths:
        if fallback.exists():
            import shutil
            primary_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(fallback, primary_path)
            return primary_path
    
    return None

