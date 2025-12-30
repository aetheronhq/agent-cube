"""Helper functions for finding decision files across locations."""

import shutil
from pathlib import Path
from typing import Optional, Union, List
from .config import PROJECT_ROOT, WORKTREE_BASE


def sync_decisions_from_worktrees(task_id: str, decision_type: str = "peer-review") -> int:
    """Move all decision files for a task from worktrees to PROJECT_ROOT.
    
    Call this before checking decisions to ensure all judge decisions are found.
    
    Args:
        task_id: Task identifier
        decision_type: 'decision' for panel, 'peer-review' for peer review
    
    Returns:
        Number of decision files moved
    """
    if not WORKTREE_BASE.exists():
        return 0
    
    moved = 0
    dest_dir = PROJECT_ROOT / ".prompts" / "decisions"
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    pattern = f"*-{task_id}-{decision_type}.json"
    
    # Search ALL worktrees (not just ones with task_id in name)
    # because judges might run in different worktrees
    for project_dir in WORKTREE_BASE.iterdir():
        if not project_dir.is_dir():
            continue
        for worktree_dir in project_dir.iterdir():
            if not worktree_dir.is_dir():
                continue
            
            decisions_dir = worktree_dir / ".prompts" / "decisions"
            if not decisions_dir.exists():
                continue
            
            # Search for any decision files matching the task_id pattern
            for decision_file in decisions_dir.glob(pattern):
                dest_path = dest_dir / decision_file.name
                if not dest_path.exists() or decision_file.stat().st_mtime > dest_path.stat().st_mtime:
                    shutil.copy(decision_file, dest_path)
                    decision_file.unlink()
                    moved += 1
    
    # Also check ~/.cube/.prompts/decisions/ (Gemini)
    cube_decisions = Path.home() / ".cube" / ".prompts" / "decisions"
    if cube_decisions.exists():
        for decision_file in cube_decisions.glob(pattern):
            dest_path = dest_dir / decision_file.name
            if not dest_path.exists() or decision_file.stat().st_mtime > dest_path.stat().st_mtime:
                shutil.copy(decision_file, dest_path)
                decision_file.unlink()
                moved += 1
    
    return moved


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
    
    # Check fallback locations (e.g., ~/.cube for Gemini judges, worktrees for synthesis agents)
    fallback_paths = [
        WORKTREE_BASE.parent / ".prompts" / "decisions" / filename,
        Path.home() / ".cube" / ".prompts" / "decisions" / filename,
    ]
    
    # Also check all worktrees for this task_id
    if WORKTREE_BASE.exists():
        # Worktrees are in ~/.cube/worktrees/{project_name}/writer-{name}-{task_id}/
        for project_dir in WORKTREE_BASE.iterdir():
            if project_dir.is_dir():
                for worktree_dir in project_dir.iterdir():
                    if worktree_dir.is_dir() and task_id in worktree_dir.name:
                        worktree_decision = worktree_dir / ".prompts" / "decisions" / filename
                        if worktree_decision.exists():
                            fallback_paths.insert(0, worktree_decision)
    
    for fallback in fallback_paths:
        if fallback.exists():
            import shutil
            primary_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(fallback, primary_path)
            # Delete source after copying (move operation) to avoid stale data
            fallback.unlink()
            return primary_path
    
    return None

