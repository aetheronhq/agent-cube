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
    judge_key: str, task_id: str, decision_type: str = "decision", project_root: Optional[Union[str, Path]] = None
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

    # Also check hyphenated variant
    hyphen_filename = get_decision_filename(judge_key.replace("_", "-"), task_id, decision_type)
    hyphen_path = decisions_dir / hyphen_filename

    if primary_path.exists():
        return primary_path
    if hyphen_path.exists():
        return hyphen_path

    # Check fallback locations (e.g., ~/.cube for Gemini judges, worktrees for synthesis agents)
    # Check both underscore and hyphen variants
    fallback_paths = []
    for fn in [filename, hyphen_filename]:
        fallback_paths.extend(
            [
                WORKTREE_BASE.parent / ".prompts" / "decisions" / fn,
                Path.home() / ".cube" / ".prompts" / "decisions" / fn,
            ]
        )

    # Also check all worktrees for this task_id
    if WORKTREE_BASE.exists():
        for project_dir in WORKTREE_BASE.iterdir():
            if project_dir.is_dir():
                for worktree_dir in project_dir.iterdir():
                    if worktree_dir.is_dir() and task_id in worktree_dir.name:
                        for fn in [filename, hyphen_filename]:
                            worktree_decision = worktree_dir / ".prompts" / "decisions" / fn
                            if worktree_decision.exists():
                                fallback_paths.insert(0, worktree_decision)

    for fallback in fallback_paths:
        if fallback.exists():
            import shutil

            primary_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(fallback, primary_path)
            fallback.unlink()
            return primary_path

    return None
