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


def fetch_failed_ci_logs(pr_number: int, cwd: Optional[str] = None, max_log_lines: int = 200) -> list[dict]:
    """Fetch logs from failed CI/GHA checks on a PR.

    Returns a list of dicts with 'name', 'status', and 'log' keys for each
    failed check.
    """
    # Get failed checks for the PR
    result = subprocess.run(
        [
            "gh",
            "pr",
            "checks",
            str(pr_number),
            "--json",
            "name,state,link",
            "--jq",
            '.[] | select(.state == "FAILURE")',
        ],
        capture_output=True,
        text=True,
        cwd=cwd,
        timeout=30,
    )

    if result.returncode != 0 or not result.stdout.strip():
        # Try alternate: get all checks and filter
        result = subprocess.run(
            ["gh", "pr", "checks", str(pr_number), "--json", "name,state,link"],
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=30,
        )
        if result.returncode != 0:
            return []

    try:
        checks = json.loads(result.stdout)
    except json.JSONDecodeError:
        # jq output is newline-delimited JSON objects, not an array
        checks = []
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                try:
                    checks.append(json.loads(line))
                except json.JSONDecodeError:
                    pass

    failed = [c for c in checks if c.get("state") in ("FAILURE", "ERROR")]
    if not failed:
        return []

    results = []
    for check in failed:
        name = check.get("name", "unknown")
        log = _fetch_run_log(pr_number, name, cwd, max_log_lines)
        results.append({"name": name, "status": check.get("state", "FAILURE"), "log": log})

    return results


def _fetch_run_log(pr_number: int, check_name: str, cwd: Optional[str], max_lines: int) -> str:
    """Fetch the log output for a specific failed GHA run on a PR."""
    # Find the run ID for this check
    result = subprocess.run(
        [
            "gh",
            "pr",
            "checks",
            str(pr_number),
            "--json",
            "name,link",
            "--jq",
            f'.[] | select(.name == "{check_name}") | .link',
        ],
        capture_output=True,
        text=True,
        cwd=cwd,
        timeout=15,
    )

    run_id = None
    if result.returncode == 0 and result.stdout.strip():
        # Extract run ID from URL like https://github.com/org/repo/actions/runs/12345/job/67890
        import re

        match = re.search(r"/runs/(\d+)", result.stdout.strip())
        if match:
            run_id = match.group(1)

    if not run_id:
        return "(could not fetch log - run ID not found)"

    # Fetch failed job logs
    result = subprocess.run(
        ["gh", "run", "view", run_id, "--log-failed"],
        capture_output=True,
        text=True,
        cwd=cwd,
        timeout=60,
    )

    if result.returncode != 0 or not result.stdout.strip():
        # Fallback: try full log
        result = subprocess.run(
            ["gh", "run", "view", run_id, "--log"],
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=60,
        )

    if result.returncode != 0:
        return f"(failed to fetch log: {result.stderr.strip()[:200]})"

    log = result.stdout
    lines = log.split("\n")
    if len(lines) > max_lines:
        lines = lines[-max_lines:]
        log = f"... (truncated, showing last {max_lines} lines) ...\n" + "\n".join(lines)
    return log
