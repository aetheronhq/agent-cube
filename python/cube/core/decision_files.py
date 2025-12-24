"""Helper functions for finding decision files across locations."""

from pathlib import Path
from typing import Optional, Union
from .config import PROJECT_ROOT, WORKTREE_BASE


def get_decision_filename(judge_key: str, task_id: str, decision_type: str = "decision") -> str:
    """Get the canonical decision filename.
    
    Format: {judge_key}-{task_id}-{decision_type}.json
    Example: judge_1-my-task-peer-review.json
    
    Note: judge_key keeps its underscore (e.g., judge_1, judge_2)
    """
    return f"{judge_key}-{task_id}-{decision_type}.json"


def find_decision_file(
    judge_key: str, 
    task_id: str, 
    decision_type: str = "decision",
    project_root: Optional[Union[str, Path]] = None
) -> Optional[Path]:
    """Find a decision file in the canonical location.
    
    Args:
        judge_key: Judge key (e.g., "judge_1", "judge_3")
        task_id: Task ID
        decision_type: 'decision' for panel, 'peer-review' for peer review
        project_root: Optional project root to search in (defaults to current PROJECT_ROOT)
    
    Returns:
        Path to decision file, or None if not found
    """
    root = Path(project_root) if project_root else PROJECT_ROOT
    decisions_dir = root / ".prompts" / "decisions"
    
    filename = get_decision_filename(judge_key, task_id, decision_type)
    primary_path = decisions_dir / filename
    
    if primary_path.exists():
        return primary_path
    
    # Check fallback locations (e.g., ~/.cube for Gemini judges)
    fallback_paths = [
        WORKTREE_BASE.parent / ".prompts" / "decisions" / filename,
        Path.home() / ".cube" / ".prompts" / "decisions" / filename,
    ]
    
    for fallback in fallback_paths:
        if fallback.exists():
            import shutil
            primary_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(fallback, primary_path)
            return primary_path
    
    return None

