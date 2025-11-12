"""Configuration and constants for Cube CLI."""

import os
from pathlib import Path
from typing import Final

VERSION: Final[str] = "1.0.0"

HOME_DIR: Path = Path.home()
WORKTREE_BASE: Path = HOME_DIR / ".cube" / "worktrees"
SESSIONS_DIR_NAME: Final[str] = ".agent-sessions"

def get_project_root() -> Path:
    """Get the current project root (runtime cwd)."""
    return Path.cwd()

# Use function for runtime evaluation
PROJECT_ROOT: Path = get_project_root()

def get_sessions_dir() -> Path:
    """Get the sessions directory path relative to current project."""
    return get_project_root() / SESSIONS_DIR_NAME

def get_worktree_path(project_name: str, writer_name: str, task_id: str) -> Path:
    """Get the worktree path for a specific writer and task."""
    return WORKTREE_BASE / project_name / f"writer-{writer_name}-{task_id}"

MODELS: Final[dict] = {
    "sonnet": "sonnet-4.5-thinking",
    "codex": "gpt-5-codex-high",
    "grok": "grok",
}

WRITER_COLORS: Final[dict] = {
    "sonnet": "green",
    "codex": "blue",
}

JUDGE_COLORS: Final[dict] = {
    1: "green",
    2: "yellow",
    3: "magenta",
}

WRITER_LABELS: Final[dict] = {
    "sonnet": "Writer A",
    "codex": "Writer B",
}

WRITER_LETTERS: Final[dict] = {
    "sonnet": "A",
    "codex": "B",
}

def _get_judge_models_from_config() -> dict:
    """Load judge models from cube.yaml config."""
    try:
        from .user_config import load_config
        config = load_config()
        return {
            1: config.judges.judge_1.model,
            2: config.judges.judge_2.model,
            3: config.judges.judge_3.model,
        }
    except:
        # Fallback to defaults if config fails
        return {
            1: "sonnet-4.5-thinking",
            2: "gpt-5-codex-high",
            3: "gemini-2.5-pro",
        }

JUDGE_MODELS: dict = _get_judge_models_from_config()

