"""Categorize PR comments for automated processing."""

import re
from dataclasses import dataclass
from typing import Literal, Optional

from .comments import PRComment

Category = Literal["ACTIONABLE", "QUESTION", "SUGGESTION", "RESOLVED", "SKIP"]


@dataclass
class CategorizedComment:
    """A comment with its category and analysis."""

    comment: PRComment
    category: Category
    reason: str
    confidence: float
    fix_plan: Optional[str]


def _is_praise_or_acknowledgment(body: str) -> bool:
    """Check if comment is positive feedback with no action required."""
    praise_patterns = [
        r"^\s*lgtm\s*!*\s*$",
        r"^\s*looks?\s+good\s*(to\s+me)?\s*!*\s*$",
        r"^\s*nice\s*(work|job|one)?\s*!*\s*$",
        r"^\s*great\s*(work|job|one)?\s*!*\s*$",
        r"^\s*awesome\s*!*\s*$",
        r"^\s*perfect\s*!*\s*$",
        r"^\s*thanks?\s*!*\s*$",
        r"^\s*thank\s+you\s*!*\s*$",
        r"^\s*\+1\s*$",
        r"^\s*:\+1:\s*$",
        r"^\s*:thumbsup:\s*$",
    ]
    body_lower = body.strip().lower()

    for pattern in praise_patterns:
        if re.match(pattern, body_lower, re.IGNORECASE):
            return True

    if len(body_lower) < 20 and any(
        word in body_lower for word in ["great", "nice", "good", "perfect", "awesome", "excellent"]
    ):
        return True

    return False


def _has_suggestion_block(body: str) -> bool:
    """Check if comment contains a GitHub suggestion block."""
    return "```suggestion" in body.lower()


def _is_question(body: str) -> bool:
    """Check if comment is a question."""
    question_indicators = [
        "?",
        "why ",
        "what ",
        "how ",
        "could you",
        "would you",
        "can you",
        "is this",
        "are these",
        "should this",
        "do we",
        "does this",
        "wondering",
    ]
    body_lower = body.lower()

    if "?" in body:
        return True

    for indicator in question_indicators:
        if indicator in body_lower:
            return True

    return False


def _extract_action_phrases(body: str) -> list[str]:
    """Extract phrases that indicate actionable items."""
    action_patterns = [
        r"please\s+(.{10,60})",
        r"should\s+(.{10,60})",
        r"needs?\s+to\s+(.{10,60})",
        r"must\s+(.{10,60})",
        r"consider\s+(.{10,60})",
        r"recommend\s+(.{10,60})",
        r"suggest\s+(.{10,60})",
        r"change\s+(.{10,60})",
        r"rename\s+(.{10,60})",
        r"refactor\s+(.{10,60})",
        r"update\s+(.{10,60})",
        r"add\s+(.{10,60})",
        r"remove\s+(.{10,60})",
        r"delete\s+(.{10,60})",
        r"fix\s+(.{10,60})",
    ]

    phrases = []
    for pattern in action_patterns:
        matches = re.findall(pattern, body.lower())
        phrases.extend(matches)

    return phrases


def _is_actionable(body: str) -> tuple[bool, str, float]:
    """Check if comment requests specific code change.

    Returns:
        Tuple of (is_actionable, reason, confidence)
    """
    if _has_suggestion_block(body):
        return True, "Contains suggestion block with specific code change", 0.95

    action_phrases = _extract_action_phrases(body)
    if action_phrases:
        return True, f"Contains action request: {action_phrases[0][:50]}", 0.85

    code_pattern = r"```\w*\n[\s\S]+?```"
    if re.search(code_pattern, body):
        action_words = ["instead", "should be", "change to", "use this", "try this"]
        if any(word in body.lower() for word in action_words):
            return True, "Contains code example with change suggestion", 0.80

    nit_patterns = [r"\bnit\b", r"\bnitpick\b", r"\bminor\b", r"\bstyle\b"]
    for pattern in nit_patterns:
        if re.search(pattern, body.lower()):
            return True, "Contains nitpick/style suggestion", 0.75

    return False, "", 0.0


def _generate_fix_plan(comment: PRComment, body: str) -> Optional[str]:
    """Generate a plan for fixing the comment."""
    if _has_suggestion_block(body):
        suggestion_match = re.search(r"```suggestion\n([\s\S]*?)```", body)
        if suggestion_match:
            suggested_code = suggestion_match.group(1).strip()
            if comment.path and comment.line:
                return f"Apply suggestion at {comment.path}:{comment.line}: Replace with:\n{suggested_code}"
            return f"Apply suggested code: {suggested_code[:100]}"

    action_phrases = _extract_action_phrases(body)
    if action_phrases:
        phrase = action_phrases[0]
        if comment.path:
            return f"In {comment.path}: {phrase}"
        return phrase.capitalize()

    if comment.path and "rename" in body.lower():
        return f"Rename entity in {comment.path}"

    if comment.path:
        return f"Review and address feedback in {comment.path}"

    return None


def categorize_comment(
    comment: PRComment,
    existing_code: Optional[dict[str, str]] = None,
) -> CategorizedComment:
    """Categorize a single comment.

    Args:
        comment: The comment to categorize
        existing_code: Optional dict of path -> file content

    Returns:
        CategorizedComment with category, reason, confidence, and fix_plan
    """
    body = comment.body

    if not body or len(body.strip()) == 0:
        return CategorizedComment(
            comment=comment,
            category="SKIP",
            reason="Empty comment",
            confidence=1.0,
            fix_plan=None,
        )

    if _is_praise_or_acknowledgment(body):
        return CategorizedComment(
            comment=comment,
            category="SKIP",
            reason="Positive feedback with no actionable request",
            confidence=0.95,
            fix_plan=None,
        )

    if _has_suggestion_block(body):
        fix_plan = _generate_fix_plan(comment, body)
        return CategorizedComment(
            comment=comment,
            category="ACTIONABLE",
            reason="Contains suggestion block with specific code change",
            confidence=0.95,
            fix_plan=fix_plan,
        )

    is_actionable, action_reason, action_confidence = _is_actionable(body)
    if is_actionable:
        fix_plan = _generate_fix_plan(comment, body)
        return CategorizedComment(
            comment=comment,
            category="ACTIONABLE",
            reason=action_reason,
            confidence=action_confidence,
            fix_plan=fix_plan,
        )

    if _is_question(body):
        return CategorizedComment(
            comment=comment,
            category="QUESTION",
            reason="Contains a question that may need response",
            confidence=0.80,
            fix_plan=None,
        )

    if any(word in body.lower() for word in ["consider", "might want", "could also", "alternatively"]):
        return CategorizedComment(
            comment=comment,
            category="SUGGESTION",
            reason="Contains optional suggestion",
            confidence=0.70,
            fix_plan=_generate_fix_plan(comment, body),
        )

    return CategorizedComment(
        comment=comment,
        category="SKIP",
        reason="No clear actionable request detected",
        confidence=0.60,
        fix_plan=None,
    )


def categorize_comments(
    comments: list[PRComment],
    existing_code: Optional[dict[str, str]] = None,
) -> list[CategorizedComment]:
    """Categorize a list of comments.

    Args:
        comments: List of comments to categorize
        existing_code: Optional dict of path -> file content

    Returns:
        List of CategorizedComment objects
    """
    return [categorize_comment(c, existing_code) for c in comments]


def filter_actionable(
    categorized: list[CategorizedComment],
    include_questions: bool = False,
    include_suggestions: bool = False,
    min_confidence: float = 0.0,
) -> list[CategorizedComment]:
    """Filter to only actionable comments.

    Args:
        categorized: List of categorized comments
        include_questions: Include QUESTION category
        include_suggestions: Include SUGGESTION category
        min_confidence: Minimum confidence threshold

    Returns:
        Filtered list of categorized comments
    """
    categories_to_include = {"ACTIONABLE"}
    if include_questions:
        categories_to_include.add("QUESTION")
    if include_suggestions:
        categories_to_include.add("SUGGESTION")

    return [c for c in categorized if c.category in categories_to_include and c.confidence >= min_confidence]
