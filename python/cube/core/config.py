"""Configuration and constants for Cube CLI."""

import os
from pathlib import Path
from typing import Final, Optional

VERSION: Final[str] = "1.1.0"

HOME_DIR: Path = Path.home()
WORKTREE_BASE: Path = HOME_DIR / ".cube" / "worktrees"
SESSIONS_DIR_NAME: Final[str] = ".agent-sessions"

def _find_git_root() -> Path:
    """Find git repository root by walking up from cwd."""
    current = Path.cwd()
    
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    
    return Path.cwd()

def get_project_root() -> Path:
    """Get the current project root (finds git repository root).
    
    This is called dynamically to ensure we always get the correct working directory,
    not a cached value from module import time.
    """
    return _find_git_root()

def resolve_path(path_str: str) -> Path:
    """Resolve a file path, trying multiple strategies.
    
    Resolution order:
    1. Absolute path - use as-is
    2. Relative to current directory
    3. Relative to PROJECT_ROOT
    
    Args:
        path_str: Path string (can be relative or absolute)
        
    Returns:
        Resolved Path object
        
    Raises:
        FileNotFoundError: If path cannot be resolved
    """
    path = Path(path_str)
    
    # Absolute path - use as-is
    if path.is_absolute():
        if path.exists():
            return path
        raise FileNotFoundError(f"File not found: {path}")
    
    # Try relative to current directory first
    cwd_path = Path.cwd() / path
    if cwd_path.exists():
        return cwd_path
    
    # Fall back to relative to PROJECT_ROOT
    root_path = get_project_root() / path
    if root_path.exists():
        return root_path
    
    # Not found anywhere
    raise FileNotFoundError(
        f"File not found: {path_str}\n"
        f"Tried:\n"
        f"  - {cwd_path}\n"
        f"  - {root_path}"
    )

# Proxy class that dynamically evaluates PROJECT_ROOT on each access
# This fixes issue #19: PROJECT_ROOT cached at module import time
class _ProjectRootProxy:
    """Proxy that acts like a Path but evaluates dynamically."""
    
    def __getattr__(self, name):
        return getattr(get_project_root(), name)
    
    def __str__(self) -> str:
        return str(get_project_root())
    
    def __repr__(self) -> str:
        return repr(get_project_root())
    
    def __fspath__(self) -> str:
        return str(get_project_root())
    
    def __truediv__(self, other) -> Path:
        return get_project_root() / other
    
    def __rtruediv__(self, other) -> Path:
        return other / get_project_root()
    
    def __eq__(self, other) -> bool:
        return get_project_root() == other
    
    def __ne__(self, other) -> bool:
        return get_project_root() != other
    
    def __hash__(self) -> int:
        return hash(get_project_root())
    
    def __bool__(self) -> bool:
        return bool(get_project_root())

# Type hint to help type checkers understand this is Path-like
PROJECT_ROOT: Path = _ProjectRootProxy()  # type: ignore[assignment]

def get_sessions_dir() -> Path:
    """Get the sessions directory path relative to current project."""
    return get_project_root() / SESSIONS_DIR_NAME

def get_worktree_path(project_name: str, writer_name: str, task_id: str) -> Path:
    """Get the worktree path for a specific writer and task."""
    return WORKTREE_BASE / project_name / f"writer-{writer_name}-{task_id}"

def _get_writer_metadata() -> tuple[dict, dict, dict, dict]:
    """Load writer metadata (model/color/label/letter) from user config."""
    try:
        from .user_config import load_config
        config = load_config()
        models = {}
        colors = {}
        labels = {}
        letters = {}
        for writer in config.writers.values():
            models[writer.name] = writer.model
            colors[writer.name] = writer.color
            labels[writer.name] = writer.label
            letters[writer.name] = writer.letter
        return models, colors, labels, letters
    except Exception:
        models = {
            "sonnet": "sonnet-4.5-thinking",
            "codex": "gpt-5-codex-high",
        }
        colors = {
            "sonnet": "green",
            "codex": "blue",
        }
        labels = {
            "sonnet": "Writer A",
            "codex": "Writer B",
        }
        letters = {
            "sonnet": "A",
            "codex": "B",
        }
        return models, colors, labels, letters

MODELS, WRITER_COLORS, WRITER_LABELS, WRITER_LETTERS = _get_writer_metadata()

def _get_judge_models_from_config() -> dict:
    """Load judge models from cube.yaml config."""
    try:
        from .user_config import get_judge_configs
        configs = get_judge_configs()
        return {judge.key: judge.model for judge in configs}
    except Exception:
        # Fallback to defaults if config fails
        return {
            "judge_1": "sonnet-4.5-thinking",
            "judge_2": "gpt-5-codex-high",
            "judge_3": "gemini-2.5-pro",
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
