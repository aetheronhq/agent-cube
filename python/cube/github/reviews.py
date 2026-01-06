"""Post reviews to GitHub via gh CLI."""

import json
import subprocess
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ReviewComment:
    """A single inline comment on a PR."""

    path: str
    line: int
    body: str
    severity: str = "info"  # critical, warning, info, nitpick


@dataclass
class Review:
    """A complete PR review with decision and comments."""

    decision: str  # APPROVE, REQUEST_CHANGES, COMMENT
    summary: str
    comments: list[ReviewComment] = field(default_factory=list)


def post_review(pr_number: int, review: Review, cwd: Optional[str] = None) -> bool:
    """Post a review to GitHub.

    Args:
        pr_number: PR number to review
        review: Review object with decision, summary, and comments
        cwd: Working directory (defaults to current directory)

    Returns:
        True if review was posted successfully

    Raises:
        RuntimeError: If posting fails
    """
    body = f"## 🤖 Agent Cube Review\n\n{review.summary}"

    event_map = {
        "APPROVE": "--approve",
        "REQUEST_CHANGES": "--request-changes",
        "COMMENT": "--comment",
    }
    event_flag = event_map.get(review.decision, "--comment")

    if review.comments:
        return _post_review_with_comments(pr_number, review, body, cwd)

    cmd = ["gh", "pr", "review", str(pr_number), event_flag, "--body", body]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)

    if result.returncode != 0:
        raise RuntimeError(f"Failed to post review: {result.stderr.strip()}")

    return True


def _post_review_with_comments(pr_number: int, review: Review, body: str, cwd: Optional[str] = None) -> bool:
    """Post review with inline comments using gh api."""
    result = subprocess.run(
        ["gh", "pr", "view", str(pr_number), "--json", "headRefOid"],
        capture_output=True,
        text=True,
        cwd=cwd,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Failed to get PR commit: {result.stderr.strip()}")

    try:
        pr_data = json.loads(result.stdout)
        commit_id = pr_data.get("headRefOid", "")
    except json.JSONDecodeError:
        raise RuntimeError("Failed to parse PR data for commit SHA")

    if not commit_id:
        raise RuntimeError("Could not determine PR head commit")

    api_comments = []
    for c in review.comments:
        severity_prefix = f"**[{c.severity.upper()}]** " if c.severity != "info" else ""
        comment_body = f"{severity_prefix}{c.body}\n\n— 🤖 *Agent Cube*"
        api_comments.append({"path": c.path, "line": c.line, "body": comment_body})

    event_map = {
        "APPROVE": "APPROVE",
        "REQUEST_CHANGES": "REQUEST_CHANGES",
        "COMMENT": "COMMENT",
    }
    event = event_map.get(review.decision, "COMMENT")

    payload = {"commit_id": commit_id, "body": body, "event": event, "comments": api_comments}

    result = subprocess.run(
        ["gh", "api", "repos/{owner}/{repo}/pulls/" + str(pr_number) + "/reviews", "-X", "POST", "--input", "-"],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=cwd,
    )

    if result.returncode != 0:
        error = result.stderr.strip()
        try:
            err_data = json.loads(result.stdout)
            if "message" in err_data:
                error = err_data["message"]
            if "errors" in err_data:
                error += ": " + str(err_data["errors"])
        except (json.JSONDecodeError, KeyError):
            pass
        raise RuntimeError(f"Failed to post review: {error}")

    return True
