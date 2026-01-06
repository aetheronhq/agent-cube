"""Fetch PR data via gh CLI."""

import json
import subprocess
from dataclasses import dataclass
from typing import Optional


@dataclass
class PRData:
    """PR metadata and diff content."""

    number: int
    title: str
    body: str
    diff: str
    head_branch: str
    base_branch: str
    head_sha: str
    existing_reviews: list[dict]


def check_gh_installed() -> bool:
    """Check if gh CLI is installed and authenticated."""
    try:
        result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def fetch_pr(pr_number: int, cwd: Optional[str] = None) -> PRData:
    """Fetch PR metadata and diff via gh CLI.

    Args:
        pr_number: The PR number to fetch
        cwd: Working directory (defaults to current directory)

    Returns:
        PRData with all PR information

    Raises:
        RuntimeError: If gh CLI fails or PR not found
    """
    if not check_gh_installed():
        raise RuntimeError(
            "gh CLI not installed or not authenticated.\n" "Install: https://cli.github.com/\n" "Auth: gh auth login"
        )

    # Get PR details as JSON
    result = subprocess.run(
        ["gh", "pr", "view", str(pr_number), "--json", "number,title,body,headRefName,baseRefName,headRefOid,reviews"],
        capture_output=True,
        text=True,
        cwd=cwd,
    )

    if result.returncode != 0:
        error_msg = result.stderr.strip() or f"PR #{pr_number} not found"
        raise RuntimeError(f"Failed to fetch PR: {error_msg}")

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse PR data: {e}")

    # Get diff separately
    diff_result = subprocess.run(
        ["gh", "pr", "diff", str(pr_number)],
        capture_output=True,
        text=True,
        cwd=cwd,
    )

    if diff_result.returncode != 0:
        raise RuntimeError(f"Failed to fetch PR diff: {diff_result.stderr.strip()}")

    return PRData(
        number=data.get("number", pr_number),
        title=data.get("title", ""),
        body=data.get("body") or "",
        diff=diff_result.stdout,
        head_branch=data.get("headRefName", ""),
        base_branch=data.get("baseRefName", ""),
        head_sha=data.get("headRefOid", "")[:7] if data.get("headRefOid") else "",
        existing_reviews=data.get("reviews") or [],
    )
