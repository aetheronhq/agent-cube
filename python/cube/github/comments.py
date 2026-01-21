"""Fetch PR comments via gh CLI."""

import json
import subprocess
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class PRComment:
    """A single comment on a PR."""

    id: str
    author: str
    body: str
    path: Optional[str]
    line: Optional[int]
    diff_hunk: Optional[str]
    in_reply_to: Optional[str]
    created_at: datetime
    is_bot: bool
    review_id: Optional[str]
    thread_id: Optional[str]


@dataclass
class CommentThread:
    """A thread of review comments."""

    id: str
    path: Optional[str]
    line: Optional[int]
    comments: list[PRComment]
    is_resolved: bool
    is_outdated: bool


def _get_repo_info(cwd: Optional[str] = None) -> tuple[str, str]:
    """Get owner and repo name from gh CLI."""
    result = subprocess.run(
        ["gh", "repo", "view", "--json", "owner,name"],
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to get repo info: {result.stderr.strip()}")

    try:
        data = json.loads(result.stdout)
        owner = data.get("owner", {}).get("login", "")
        repo = data.get("name", "")
        if not owner or not repo:
            raise RuntimeError("Could not determine owner/repo")
        return owner, repo
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse repo info: {e}")


def _is_bot_author(author: str, skip_bots: Optional[list[str]] = None) -> bool:
    """Check if author is a bot."""
    if author.endswith("[bot]"):
        return True
    default_bots = ["dependabot", "github-actions", "renovate"]
    bots = skip_bots or default_bots
    return author.lower() in [b.lower() for b in bots]


def _parse_datetime(dt_str: str) -> datetime:
    """Parse ISO datetime string from GitHub."""
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except (ValueError, TypeError, AttributeError):
        return datetime.min


def fetch_pr_comments(pr_number: int, cwd: Optional[str] = None) -> list[PRComment]:
    """Fetch all review comments from a PR (inline comments).

    Args:
        pr_number: The PR number
        cwd: Working directory

    Returns:
        List of PRComment objects
    """
    result = subprocess.run(
        ["gh", "api", f"repos/{{owner}}/{{repo}}/pulls/{pr_number}/comments", "--paginate"],
        capture_output=True,
        text=True,
        cwd=cwd,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Failed to fetch PR comments: {result.stderr.strip()}")

    comments: list[PRComment] = []
    try:
        data = json.loads(result.stdout)
        for c in data:
            author = c.get("user", {}).get("login", "unknown")
            comments.append(
                PRComment(
                    id=str(c.get("id", "")),
                    author=author,
                    body=c.get("body", ""),
                    path=c.get("path"),
                    line=c.get("line") or c.get("original_line"),
                    diff_hunk=c.get("diff_hunk"),
                    in_reply_to=str(c.get("in_reply_to_id", "")) if c.get("in_reply_to_id") else None,
                    created_at=_parse_datetime(c.get("created_at", "")),
                    is_bot=_is_bot_author(author),
                    review_id=str(c.get("pull_request_review_id", "")) if c.get("pull_request_review_id") else None,
                    thread_id=None,
                )
            )
    except json.JSONDecodeError:
        pass

    return comments


def fetch_issue_comments(pr_number: int, cwd: Optional[str] = None) -> list[PRComment]:
    """Fetch issue comments (top-level, not inline).

    Args:
        pr_number: The PR number
        cwd: Working directory

    Returns:
        List of PRComment objects
    """
    result = subprocess.run(
        ["gh", "api", f"repos/{{owner}}/{{repo}}/issues/{pr_number}/comments", "--paginate"],
        capture_output=True,
        text=True,
        cwd=cwd,
    )

    if result.returncode != 0:
        return []

    comments: list[PRComment] = []
    try:
        data = json.loads(result.stdout)
        for c in data:
            author = c.get("user", {}).get("login", "unknown")
            comments.append(
                PRComment(
                    id=str(c.get("id", "")),
                    author=author,
                    body=c.get("body", ""),
                    path=None,
                    line=None,
                    diff_hunk=None,
                    in_reply_to=None,
                    created_at=_parse_datetime(c.get("created_at", "")),
                    is_bot=_is_bot_author(author),
                    review_id=None,
                    thread_id=None,
                )
            )
    except json.JSONDecodeError:
        pass

    return comments


def fetch_comment_threads(pr_number: int, cwd: Optional[str] = None) -> list[CommentThread]:
    """Fetch comment threads with resolution status via GraphQL.

    Args:
        pr_number: The PR number
        cwd: Working directory

    Returns:
        List of CommentThread objects
    """
    try:
        owner, repo = _get_repo_info(cwd)
    except RuntimeError:
        return []

    query = """
    query($owner: String!, $repo: String!, $pr: Int!) {
      repository(owner: $owner, name: $repo) {
        pullRequest(number: $pr) {
          reviewThreads(first: 100) {
            nodes {
              id
              isResolved
              isOutdated
              line
              path
              comments(first: 50) {
                nodes {
                  id
                  body
                  createdAt
                  author { login }
                  replyTo { id }
                }
              }
            }
          }
        }
      }
    }
    """

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

    if result.returncode != 0:
        return []

    threads: list[CommentThread] = []
    try:
        data = json.loads(result.stdout)
        thread_nodes = (
            data.get("data", {}).get("repository", {}).get("pullRequest", {}).get("reviewThreads", {}).get("nodes", [])
        )

        for thread in thread_nodes:
            thread_id = thread.get("id", "")
            path = thread.get("path")
            line = thread.get("line")
            is_resolved = thread.get("isResolved", False)
            is_outdated = thread.get("isOutdated", False)

            comment_nodes = thread.get("comments", {}).get("nodes", [])
            comments: list[PRComment] = []

            for c in comment_nodes:
                author = c.get("author", {}).get("login", "unknown") if c.get("author") else "unknown"
                reply_to = c.get("replyTo", {})
                reply_to_id = reply_to.get("id") if reply_to else None

                comments.append(
                    PRComment(
                        id=c.get("id", ""),
                        author=author,
                        body=c.get("body", ""),
                        path=path,
                        line=line,
                        diff_hunk=None,
                        in_reply_to=reply_to_id,
                        created_at=_parse_datetime(c.get("createdAt", "")),
                        is_bot=_is_bot_author(author),
                        review_id=None,
                        thread_id=thread_id,
                    )
                )

            threads.append(
                CommentThread(
                    id=thread_id,
                    path=path,
                    line=line,
                    comments=comments,
                    is_resolved=is_resolved,
                    is_outdated=is_outdated,
                )
            )
    except (json.JSONDecodeError, KeyError):
        pass

    return threads


def fetch_all_comments(pr_number: int, cwd: Optional[str] = None) -> list[PRComment]:
    """Fetch all comments (review + issue) from a PR.

    Args:
        pr_number: The PR number
        cwd: Working directory

    Returns:
        Combined list of all comments, sorted by creation time
    """
    review_comments = fetch_pr_comments(pr_number, cwd)
    issue_comments = fetch_issue_comments(pr_number, cwd)

    all_comments = review_comments + issue_comments
    all_comments.sort(key=lambda c: c.created_at)

    return all_comments
