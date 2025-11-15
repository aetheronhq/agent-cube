"""Configuration and constants for Cube CLI."""

import os
from pathlib import Path
from typing import Final, Optional

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


# Current task tracking (per-terminal using TTY)
TTY_SESSIONS_DIR: Path = HOME_DIR / ".cube" / "tty-sessions"


def _get_current_tty() -> Optional[str]:
    """Get current TTY identifier (e.g., ttys001)."""
    try:
        import subprocess
        # Use full path to avoid zsh conflicts
        result = subprocess.run(['/usr/bin/tty'], capture_output=True, text=True)
        tty = result.stdout.strip()
        # Extract just the device name (e.g., /dev/ttys001 -> ttys001)
        if tty and tty.startswith('/dev/'):
            return tty.split('/')[-1]
        return None
    except:
        return None


def get_current_task_id() -> Optional[str]:
    """Get the current task ID for this terminal session."""
    # Environment variable takes precedence (for manual override)
    task_id = os.getenv("CUBE_TASK_ID")
    if task_id:
        return task_id
    
    # Get from TTY-specific file
    tty = _get_current_tty()
    if not tty:
        return None
    
    tty_file = TTY_SESSIONS_DIR / f"tty-{tty}"
    if tty_file.exists():
        try:
            return tty_file.read_text().strip()
        except:
            return None
    
    return None


def set_current_task_id(task_id: str) -> None:
    """Save the current task ID for this terminal session (by TTY)."""
    tty = _get_current_tty()
    if not tty:
        return  # Can't track without TTY
    
    tty_file = TTY_SESSIONS_DIR / f"tty-{tty}"
    tty_file.parent.mkdir(parents=True, exist_ok=True)
    tty_file.write_text(task_id)


def resolve_task_id(provided: Optional[str]) -> Optional[str]:
    """Resolve task ID: provided > CUBE_TASK_ID env > TTY file."""
    if provided:
        return provided
    return get_current_task_id()
