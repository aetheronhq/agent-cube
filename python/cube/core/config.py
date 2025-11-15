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
CURRENT_TASKS_FILE: Path = HOME_DIR / ".cube" / "current-tasks"


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
    
    # Get from TTY-based mapping
    tty = _get_current_tty()
    if not tty or not CURRENT_TASKS_FILE.exists():
        return None
    
    try:
        # Read TTY → task_id mapping
        tasks_map = {}
        for line in CURRENT_TASKS_FILE.read_text().splitlines():
            line = line.strip()
            if not line or ':' not in line:
                continue
            tty_id, task = line.split(':', 1)
            tasks_map[tty_id.strip()] = task.strip()
        
        return tasks_map.get(tty)
    except:
        return None


def set_current_task_id(task_id: str) -> None:
    """Save the current task ID for this terminal session (by TTY)."""
    tty = _get_current_tty()
    if not tty:
        return  # Can't track without TTY
    
    CURRENT_TASKS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Read existing mappings
    tasks_map = {}
    if CURRENT_TASKS_FILE.exists():
        try:
            for line in CURRENT_TASKS_FILE.read_text().splitlines():
                line = line.strip()
                if not line or ':' not in line:
                    continue
                tty_id, task = line.split(':', 1)
                tasks_map[tty_id.strip()] = task.strip()
        except:
            pass
    
    # Update this TTY's task
    tasks_map[tty] = task_id
    
    # Write back
    CURRENT_TASKS_FILE.write_text('\n'.join(f"{t}: {tid}" for t, tid in tasks_map.items()) + '\n')


def resolve_task_id(provided: Optional[str]) -> Optional[str]:
    """Resolve task ID: provided > CUBE_TASK_ID env > TTY mapping."""
    if provided:
        return provided
    return get_current_task_id()
