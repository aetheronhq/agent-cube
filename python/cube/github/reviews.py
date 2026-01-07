"""Post reviews to GitHub via gh CLI."""

import json
import subprocess
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ExistingComment:
    """An existing comment on a PR."""

    path: Optional[str]  # None for top-level comments
    line: Optional[int]
    body: str
    author: str
    is_review_comment: bool = True  # False for issue comments


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
        comment_body = f"{severity_prefix}{c.body}"
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


def fetch_existing_comments(pr_number: int, cwd: Optional[str] = None) -> list[ExistingComment]:
    """Fetch all existing comments on a PR (review comments + issue comments).

    Only returns active, non-resolved, non-outdated comments.

    Returns:
        List of existing comments with path, line, body, and author
    """
    comments: list[ExistingComment] = []

    # Use GraphQL to get review threads with resolved/outdated status
    query = """
    query($owner: String!, $repo: String!, $pr: Int!) {
      repository(owner: $owner, name: $repo) {
        pullRequest(number: $pr) {
          reviewThreads(first: 100) {
            nodes {
              isResolved
              isOutdated
              line
              path
              comments(first: 10) {
                nodes {
                  body
                  author { login }
                }
              }
            }
          }
        }
      }
    }
    """

    # Get owner/repo from gh
    result = subprocess.run(
        ["gh", "repo", "view", "--json", "owner,name"],
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    if result.returncode == 0:
        try:
            repo_info = json.loads(result.stdout)
            owner = repo_info.get("owner", {}).get("login", "")
            repo = repo_info.get("name", "")

            result = subprocess.run(
                [
                    "gh",
                    "api",
                    "graphql",
                    "-f",
                    f"query={query}",
                    "-f",
                    f"owner={owner}",
                    "-f",
                    f"repo={repo}",
                    "-F",
                    f"pr={pr_number}",
                ],
                capture_output=True,
                text=True,
                cwd=cwd,
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                threads = (
                    data.get("data", {})
                    .get("repository", {})
                    .get("pullRequest", {})
                    .get("reviewThreads", {})
                    .get("nodes", [])
                )
                for thread in threads:
                    # Skip resolved or outdated threads
                    if thread.get("isResolved") or thread.get("isOutdated"):
                        continue
                    path = thread.get("path")
                    line = thread.get("line")
                    if not path or not line:
                        continue
                    # Get first comment body
                    thread_comments = thread.get("comments", {}).get("nodes", [])
                    if thread_comments:
                        first_comment = thread_comments[0]
                        comments.append(
                            ExistingComment(
                                path=path,
                                line=line,
                                body=first_comment.get("body", ""),
                                author=first_comment.get("author", {}).get("login", "unknown"),
                                is_review_comment=True,
                            )
                        )
        except (json.JSONDecodeError, KeyError):
            pass

    # Fetch issue comments (top-level comments)
    result = subprocess.run(
        ["gh", "api", f"repos/{{owner}}/{{repo}}/issues/{pr_number}/comments", "--paginate"],
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    if result.returncode == 0:
        try:
            issue_comments = json.loads(result.stdout)
            for c in issue_comments:
                comments.append(
                    ExistingComment(
                        path=None,
                        line=None,
                        body=c.get("body", ""),
                        author=c.get("user", {}).get("login", "unknown"),
                        is_review_comment=False,
                    )
                )
        except json.JSONDecodeError:
            pass

    return comments


def is_duplicate_comment(new_comment: ReviewComment, existing: list[ExistingComment], threshold: float = 0.7) -> bool:
    """Check if a new comment is a duplicate of an existing one.

    Considers a comment duplicate if:
    - Same file and line, and
    - Body is similar (contains key phrases or high overlap)
    """
    new_body_lower = new_comment.body.lower()
    # Extract key phrases (first 50 chars, ignoring markdown formatting)
    new_key = "".join(c for c in new_body_lower[:100] if c.isalnum() or c.isspace())

    for existing_comment in existing:
        # For inline comments, check file:line match
        if existing_comment.path == new_comment.path and existing_comment.line == new_comment.line:
            existing_body_lower = existing_comment.body.lower()
            existing_key = "".join(c for c in existing_body_lower[:100] if c.isalnum() or c.isspace())

            # Check for substantial overlap
            if new_key and existing_key:
                # Simple word overlap check
                new_words = set(new_key.split())
                existing_words = set(existing_key.split())
                if new_words and existing_words:
                    overlap = len(new_words & existing_words) / max(len(new_words), len(existing_words))
                    if overlap >= threshold:
                        return True

    return False


def filter_duplicate_comments(
    new_comments: list[ReviewComment], existing: list[ExistingComment]
) -> tuple[list[ReviewComment], list[ReviewComment]]:
    """Filter out duplicate comments.

    Returns:
        Tuple of (comments_to_post, skipped_duplicates)
    """
    to_post = []
    skipped = []

    for comment in new_comments:
        if is_duplicate_comment(comment, existing):
            skipped.append(comment)
        else:
            to_post.append(comment)

    return to_post, skipped
