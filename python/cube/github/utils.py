"""Shared GitHub utility functions."""

import json
import subprocess
from typing import Optional


def get_repo_info(cwd: Optional[str] = None) -> tuple[str, str]:
    """Get owner and repo name from gh CLI.

    The gh CLI auto-expands {owner} and {repo} placeholders in API paths,
    but this function provides explicit values when needed.

    Args:
        cwd: Working directory (defaults to current directory)

    Returns:
        Tuple of (owner, repo_name)

    Raises:
        RuntimeError: If repo info cannot be determined or request times out
    """
    try:
        result = subprocess.run(
            ["gh", "repo", "view", "--json", "owner,name"],
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=15,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("Timed out fetching repository info") from None

    if result.returncode != 0:
        raise RuntimeError(f"Failed to get repo info: {result.stderr.strip()}") from None

    try:
        data = json.loads(result.stdout)
        owner = data.get("owner", {}).get("login", "")
        repo = data.get("name", "")
        if not owner or not repo:
            raise RuntimeError("Could not determine owner/repo from gh CLI")
        return owner, repo
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse repo info: {e}") from e
