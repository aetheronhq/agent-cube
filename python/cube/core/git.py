"""Git operations for worktree and branch management."""

import subprocess
from pathlib import Path
from typing import Optional

import git
from git import Repo

from .config import PROJECT_ROOT, get_worktree_path
from .output import print_info, print_warning


def get_repo() -> Repo:
    """Get the current git repository."""
    try:
        return Repo(PROJECT_ROOT)
    except git.InvalidGitRepositoryError:
        raise RuntimeError(
            f"Not a git repository: {PROJECT_ROOT}\n"
            f"Make sure you're running from the git repository root directory, not a subdirectory."
        )


def create_worktree(task_id: str, writer_name: str) -> Path:
    """Create a git worktree for a writer and task."""
    repo = get_repo()
    project_name = Path(PROJECT_ROOT).name
    worktree_path = get_worktree_path(project_name, writer_name, task_id)
    branch_name = f"writer-{writer_name}/{task_id}"

    if worktree_path.exists():
        print_info(f"Worktree already exists: {worktree_path}")
        return worktree_path

    worktree_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        existing_branch = repo.heads[branch_name] if branch_name in repo.heads else None
        if existing_branch:
            repo.delete_head(branch_name, force=True)
    except Exception:
        pass

    try:
        subprocess.run(
            ["git", "worktree", "add", "-b", branch_name, str(worktree_path)],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
        )
        print_info(f"Created worktree: {worktree_path}")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to create worktree: {e.stderr.decode()}")

    return worktree_path


def fetch_branches() -> None:
    """Fetch all branches from origin."""
    repo = get_repo()
    try:
        repo.remotes.origin.fetch()
        print_info("Fetched latest changes from origin")
    except Exception as e:
        print_warning(f"Failed to fetch: {e}")


def get_commit_hash(branch: str) -> Optional[str]:
    """Get the short commit hash for a branch."""
    repo = get_repo()
    try:
        commit = repo.commit(branch)
        return commit.hexsha[:7]
    except Exception:
        return None


def has_uncommitted_changes(worktree_path: Path) -> bool:
    """Check if a worktree has uncommitted changes."""
    try:
        result = subprocess.run(["git", "status", "--porcelain"], cwd=worktree_path, capture_output=True, text=True)
        return bool(result.stdout.strip())
    except Exception:
        return False


def has_unpushed_commits(worktree_path: Path, branch: str) -> bool:
    """Check if a worktree has unpushed commits."""
    try:
        result = subprocess.run(
            ["git", "log", f"origin/{branch}..HEAD"], cwd=worktree_path, capture_output=True, text=True
        )
        return bool(result.stdout.strip())
    except Exception:
        return False


def commit_and_push(worktree_path: Path, branch: str, message: str) -> bool:
    """Commit all changes and push to origin."""
    try:
        subprocess.run(["git", "add", "-A"], cwd=worktree_path, check=True, capture_output=True)

        subprocess.run(["git", "commit", "-m", message], cwd=worktree_path, check=True, capture_output=True)

        subprocess.run(["git", "push", "origin", branch], cwd=worktree_path, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print_warning(f"Git operation failed: {e}")
        return False


def branch_exists(branch: str) -> bool:
    """Check if a branch exists locally or remotely."""
    repo = get_repo()
    try:
        repo.commit(branch)
        return True
    except Exception:
        return False


def sync_worktree(worktree_path: Path, branch: str) -> Optional[str]:
    """Fetch and reset a worktree to match remote branch.

    Creates the worktree if it doesn't exist.
    Returns commit hash on success, None on failure.
    """
    repo = get_repo()
    repo_path = Path(repo.working_dir)

    try:
        # Fetch the branch first
        subprocess.run(["git", "fetch", "origin", branch], cwd=repo_path, capture_output=True, timeout=30, check=False)

        if not worktree_path.exists():
            # Create worktree from origin branch
            worktree_path.parent.mkdir(parents=True, exist_ok=True)
            result = subprocess.run(
                ["git", "worktree", "add", str(worktree_path), f"origin/{branch}"],
                cwd=repo_path,
                capture_output=True,
                timeout=60,
            )
            if result.returncode != 0:
                return None
        else:
            # Reset existing worktree to match origin
            result = subprocess.run(
                ["git", "reset", "--hard", f"origin/{branch}"], cwd=worktree_path, capture_output=True, timeout=30
            )
            if result.returncode != 0:
                return None

        commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], cwd=worktree_path, capture_output=True, text=True, timeout=10
        )
        return commit.stdout.strip() if commit.returncode == 0 else "unknown"
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError):
        return None
