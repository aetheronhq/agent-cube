"""Reply to and resolve PR comment threads via gh CLI.

Note: The gh CLI auto-expands {owner} and {repo} placeholders in API paths
when called from within a git repository. This module relies on that behavior.

For GraphQL node IDs (from fetch_comment_threads), use reply_to_thread_graphql.
For REST numeric IDs (from fetch_pr_comments), use reply_to_comment.
"""

import json
import subprocess
import time
from typing import TYPE_CHECKING, Optional

from ..core.output import print_warning

if TYPE_CHECKING:
    from .comments import PRComment


def reply_to_comment(
    pr_number: int,
    comment_id: str,
    body: str,
    cwd: Optional[str] = None,
    rate_limit_delay: float = 0.5,
) -> bool:
    """Reply to a review comment using REST API (requires numeric ID).

    Args:
        pr_number: PR number
        comment_id: The numeric REST ID of the comment to reply to
        body: Reply body text
        cwd: Working directory
        rate_limit_delay: Seconds to wait after request

    Returns:
        True if reply was posted successfully
    """
    if comment_id.startswith("PRC_") or comment_id.startswith("PRRC_"):
        print_warning(f"GraphQL node ID detected ({comment_id[:10]}...), REST reply may fail")

    payload = {"body": body}

    try:
        result = subprocess.run(
            [
                "gh",
                "api",
                f"repos/{{owner}}/{{repo}}/pulls/{pr_number}/comments/{comment_id}/replies",
                "-X",
                "POST",
                "--input",
                "-",
            ],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        print_warning("Reply request timed out")
        return False

    time.sleep(rate_limit_delay)

    if result.returncode != 0:
        return False

    return True


def reply_to_thread_graphql(
    thread_id: str,
    body: str,
    cwd: Optional[str] = None,
    rate_limit_delay: float = 0.5,
) -> bool:
    """Reply to a review thread using GraphQL (works with node IDs).

    Args:
        thread_id: The GraphQL node ID of the thread
        body: Reply body text
        cwd: Working directory
        rate_limit_delay: Seconds to wait after request

    Returns:
        True if reply was posted successfully
    """
    mutation = """
    mutation($threadId: ID!, $body: String!) {
      addPullRequestReviewThreadReply(input: {pullRequestReviewThreadId: $threadId, body: $body}) {
        comment { id }
      }
    }
    """

    try:
        result = subprocess.run(
            [
                "gh",
                "api",
                "graphql",
                "-f",
                f"query={mutation}",
                "-f",
                f"threadId={thread_id}",
                "-f",
                f"body={body}",
            ],
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        print_warning("GraphQL reply request timed out")
        return False

    time.sleep(rate_limit_delay)

    if result.returncode != 0:
        return False

    try:
        data = json.loads(result.stdout)
        return data.get("data", {}).get("addPullRequestReviewThreadReply", {}).get("comment") is not None
    except json.JSONDecodeError:
        return False


def reply_to_thread(
    pr_number: int,
    thread_comment_id: str,
    body: str,
    cwd: Optional[str] = None,
    rate_limit_delay: float = 0.5,
) -> bool:
    """Reply to a review thread by replying to the first comment.

    Args:
        pr_number: PR number
        thread_comment_id: ID of any comment in the thread
        body: Reply body text
        cwd: Working directory
        rate_limit_delay: Seconds to wait after request

    Returns:
        True if reply was posted successfully
    """
    return reply_to_comment(pr_number, thread_comment_id, body, cwd, rate_limit_delay)


def resolve_thread(
    thread_id: str,
    cwd: Optional[str] = None,
    rate_limit_delay: float = 0.5,
) -> bool:
    """Resolve a review thread via GraphQL.

    Args:
        thread_id: The GraphQL node ID of the thread
        cwd: Working directory
        rate_limit_delay: Seconds to wait after request

    Returns:
        True if thread was resolved successfully
    """
    mutation = """
    mutation($threadId: ID!) {
      resolveReviewThread(input: {threadId: $threadId}) {
        thread { isResolved }
      }
    }
    """

    try:
        result = subprocess.run(
            [
                "gh",
                "api",
                "graphql",
                "-f",
                f"query={mutation}",
                "-f",
                f"threadId={thread_id}",
            ],
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        print_warning("Resolve thread request timed out")
        return False

    time.sleep(rate_limit_delay)

    if result.returncode != 0:
        return False

    try:
        data = json.loads(result.stdout)
        thread_data = data.get("data", {}).get("resolveReviewThread", {}).get("thread", {})
        return thread_data.get("isResolved", False)
    except (json.JSONDecodeError, KeyError):
        return False


def unresolve_thread(
    thread_id: str,
    cwd: Optional[str] = None,
    rate_limit_delay: float = 0.5,
) -> bool:
    """Unresolve a review thread via GraphQL.

    Args:
        thread_id: The GraphQL node ID of the thread
        cwd: Working directory
        rate_limit_delay: Seconds to wait after request

    Returns:
        True if thread was unresolved successfully
    """
    mutation = """
    mutation($threadId: ID!) {
      unresolveReviewThread(input: {threadId: $threadId}) {
        thread { isResolved }
      }
    }
    """

    try:
        result = subprocess.run(
            [
                "gh",
                "api",
                "graphql",
                "-f",
                f"query={mutation}",
                "-f",
                f"threadId={thread_id}",
            ],
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        print_warning("Unresolve thread request timed out")
        return False

    time.sleep(rate_limit_delay)

    if result.returncode != 0:
        return False

    try:
        data = json.loads(result.stdout)
        thread_data = data.get("data", {}).get("unresolveReviewThread", {}).get("thread", {})
        return not thread_data.get("isResolved", True)
    except (json.JSONDecodeError, KeyError):
        return False


def add_reaction(
    comment_id: str,
    reaction: str,
    cwd: Optional[str] = None,
    rate_limit_delay: float = 0.5,
) -> bool:
    """Add reaction to a PR comment.

    Args:
        comment_id: The comment ID
        reaction: Reaction type (+1, -1, laugh, confused, heart, hooray, rocket, eyes)
        cwd: Working directory
        rate_limit_delay: Seconds to wait after request

    Returns:
        True if reaction was added successfully
    """
    payload = {"content": reaction}

    try:
        result = subprocess.run(
            [
                "gh",
                "api",
                f"repos/{{owner}}/{{repo}}/pulls/comments/{comment_id}/reactions",
                "-X",
                "POST",
                "--input",
                "-",
            ],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        return False

    time.sleep(rate_limit_delay)

    return result.returncode == 0


def add_issue_comment(
    pr_number: int,
    body: str,
    cwd: Optional[str] = None,
    rate_limit_delay: float = 0.5,
) -> bool:
    """Add a top-level comment to a PR.

    Args:
        pr_number: PR number
        body: Comment body
        cwd: Working directory
        rate_limit_delay: Seconds to wait after request

    Returns:
        True if comment was posted successfully
    """
    try:
        result = subprocess.run(
            ["gh", "pr", "comment", str(pr_number), "--body", body],
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        return False

    time.sleep(rate_limit_delay)

    return result.returncode == 0


def reply_and_resolve(
    pr_number: int,
    comment: "PRComment",
    commit_sha: Optional[str] = None,
    cwd: Optional[str] = None,
) -> bool:
    """Reply to a comment, resolving if changes were committed.

    If commit_sha is provided (changes were made), resolves the thread.
    If no commit_sha (just acknowledging), replies but leaves open.

    Uses GraphQL for replies when thread_id is available (works with GraphQL node IDs).
    Falls back to REST API for numeric IDs.

    Args:
        pr_number: PR number
        comment: The PRComment object to reply to
        commit_sha: The commit SHA where the fix was made (None = no fix, just reply)
        cwd: Working directory

    Returns:
        True if reply was posted (thread resolution is best-effort)
    """
    if commit_sha:
        reply_body = f"Fixed in {commit_sha}\n\n---\n*Agent Cube*"
    else:
        reply_body = "Acknowledged\n\n---\n*Agent Cube*"

    if comment.thread_id:
        reply_success = reply_to_thread_graphql(comment.thread_id, reply_body, cwd)
        # Only resolve if we actually made changes
        if reply_success and commit_sha:
            resolve_thread(comment.thread_id, cwd)
    else:
        reply_success = reply_to_comment(pr_number, comment.id, reply_body, cwd)

    return reply_success


def format_fix_reply(
    fix_description: str,
    commit_sha: Optional[str] = None,
    include_signature: bool = True,
) -> str:
    """Format a reply indicating a fix was made.

    Args:
        fix_description: Description of the fix
        commit_sha: Optional commit SHA to reference
        include_signature: Whether to add Agent Cube signature

    Returns:
        Formatted reply body
    """
    if commit_sha:
        reply = f"✅ Fixed in {commit_sha}: {fix_description}"
    else:
        reply = f"Fixed: {fix_description}"

    if include_signature:
        reply += "\n\n---\n*Agent Cube*"

    return reply


def format_acknowledgment_reply(
    message: str = "Thanks for the feedback!",
    include_signature: bool = True,
) -> str:
    """Format an acknowledgment reply.

    Args:
        message: Acknowledgment message
        include_signature: Whether to add Agent Cube signature

    Returns:
        Formatted reply body
    """
    if include_signature:
        return f"{message}\n\n---\n*Agent Cube*"
    return message


def format_question_reply(
    answer: str,
    include_signature: bool = True,
) -> str:
    """Format a reply to a question.

    Args:
        answer: The answer to the question
        include_signature: Whether to add Agent Cube signature

    Returns:
        Formatted reply body
    """
    if include_signature:
        return f"{answer}\n\n---\n*Agent Cube*"
    return answer
