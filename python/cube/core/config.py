"""Configuration and constants for Cube CLI."""

import os
from pathlib import Path
from typing import Final

VERSION: Final[str] = "1.0.0"

PROJECT_ROOT: Path = Path.cwd()
HOME_DIR: Path = Path.home()

WORKTREE_BASE: Path = HOME_DIR / ".cursor" / "worktrees"
SESSIONS_DIR_NAME: Final[str] = ".agent-sessions"

def get_sessions_dir() -> Path:
    """Get the sessions directory path relative to current project."""
    return PROJECT_ROOT / SESSIONS_DIR_NAME

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

JUDGE_MODELS: Final[dict] = {
    1: "sonnet-4.5-thinking",
    2: "gpt-5-codex-high",
    3: "grok",
}

