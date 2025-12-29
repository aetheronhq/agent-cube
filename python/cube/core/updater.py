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
    """Check if there are updates available from origin (remote ahead of local)."""
    try:
        subprocess.run(
            ["git", "fetch", "origin", branch],
            cwd=repo_root,
            capture_output=True,
            check=True
        )
        
        # Check if remote is ahead of local (has commits we don't have)
        result = subprocess.run(
            ["git", "rev-list", "HEAD..origin/" + branch, "--count"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True
        )
        commits_behind = int(result.stdout.strip())
        
        return commits_behind > 0
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
    # Skip if already updated in this execution chain
    if os.environ.get("CUBE_SKIP_UPDATE") == "1":
        return
    
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
                # Set flag to skip update check after re-exec
                os.environ["CUBE_SKIP_UPDATE"] = "1"
                os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception:
        pass

