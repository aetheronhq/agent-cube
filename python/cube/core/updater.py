"""Auto-update functionality for cube CLI."""

import os
import sys
from pathlib import Path
import subprocess
from typing import Optional

from .config import PROJECT_ROOT
from .output import print_info, print_success

def get_cube_repo_root() -> Optional[Path]:
    """Get the cube repository root if we're in a git repo."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True
        )
        return Path(result.stdout.strip())
    except Exception:
        return None

def get_current_branch(repo_root: Path) -> Optional[str]:
    """Get the current git branch."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except Exception:
        return None

def has_updates(repo_root: Path, branch: str) -> bool:
    """Check if there are updates available from origin."""
    try:
        subprocess.run(
            ["git", "fetch", "origin", branch],
            cwd=repo_root,
            capture_output=True,
            check=True
        )
        
        local_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True
        )
        local_commit = local_result.stdout.strip()
        
        remote_result = subprocess.run(
            ["git", "rev-parse", f"origin/{branch}"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True
        )
        remote_commit = remote_result.stdout.strip()
        
        return local_commit != remote_commit
    except Exception:
        return False

def pull_updates(repo_root: Path, branch: str) -> bool:
    """Pull updates from origin."""
    try:
        subprocess.run(
            ["git", "pull", "origin", branch],
            cwd=repo_root,
            capture_output=True,
            check=True
        )
        return True
    except Exception:
        return False

def auto_update() -> None:
    """Auto-update cube if running from a git repo on main branch.
    
    If updates are pulled, re-execs the current process to use new code.
    """
    try:
        cube_file = Path(__file__).resolve()
        cube_repo_root = cube_file
        
        while cube_repo_root.parent != cube_repo_root:
            if (cube_repo_root / ".git").exists():
                break
            cube_repo_root = cube_repo_root.parent
        
        if not (cube_repo_root / ".git").exists():
            return
        
        current_branch = get_current_branch(cube_repo_root)
        
        if current_branch not in ("main", "master"):
            return
        
        if has_updates(cube_repo_root, current_branch):
            print_info("Updating cube...")
            if pull_updates(cube_repo_root, current_branch):
                print_success("Cube updated successfully")
                # Re-exec to use the new code
                os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception:
        pass

