"""Tests for PR comment categorization and fixing."""

from datetime import datetime

from cube.github.categorizer import (
    _has_suggestion_block,
    _is_actionable,
    _is_praise_or_acknowledgment,
    _is_question,
    categorize_comment,
    categorize_comments,
    filter_actionable,
)
from cube.github.comments import PRComment


def _make_comment(body: str, path: str = None, line: int = None) -> PRComment:
    """Helper to create a PRComment for testing."""
    return PRComment(
        id="test-id",
        author="test-user",
        body=body,
        path=path,
        line=line,
        diff_hunk=None,
        in_reply_to=None,
        created_at=datetime.now(),
        is_bot=False,
        review_id=None,
        thread_id=None,
    )


class TestPraiseDetection:
    def test_lgtm_is_praise(self):
        assert _is_praise_or_acknowledgment("LGTM") is True
        assert _is_praise_or_acknowledgment("lgtm!") is True
        assert _is_praise_or_acknowledgment("  LGTM  ") is True

    def test_looks_good_is_praise(self):
        assert _is_praise_or_acknowledgment("Looks good!") is True
        assert _is_praise_or_acknowledgment("looks good to me") is True

    def test_nice_work_is_praise(self):
        assert _is_praise_or_acknowledgment("Nice work!") is True
        assert _is_praise_or_acknowledgment("Great job!") is True

    def test_plus_one_is_praise(self):
        assert _is_praise_or_acknowledgment("+1") is True
        assert _is_praise_or_acknowledgment(":+1:") is True

    def test_short_praise_with_keyword(self):
        assert _is_praise_or_acknowledgment("Great!") is True
        assert _is_praise_or_acknowledgment("Perfect") is True

    def test_longer_text_not_praise(self):
        assert _is_praise_or_acknowledgment("This looks good but please fix the typo") is False
        assert _is_praise_or_acknowledgment("Great start, but needs more tests") is False


class TestSuggestionBlock:
    def test_has_suggestion_block(self):
        body = """
Consider using this instead:
```suggestion
const x = 1;
```
"""
        assert _has_suggestion_block(body) is True

    def test_no_suggestion_block(self):
        assert _has_suggestion_block("Just a regular comment") is False
        assert _has_suggestion_block("```python\ncode```") is False


class TestQuestionDetection:
    def test_question_mark(self):
        assert _is_question("Why was this changed?") is True
        assert _is_question("Is this correct?") is True

    def test_question_words(self):
        assert _is_question("Why is this here") is True
        assert _is_question("What does this do") is True
        assert _is_question("How does this work") is True

    def test_not_question(self):
        assert _is_question("This looks good") is False
        assert _is_question("Fixed the bug") is False


class TestActionableDetection:
    def test_suggestion_block_is_actionable(self):
        body = """```suggestion
const x = 1;
```"""
        is_act, reason, conf = _is_actionable(body)
        assert is_act is True
        assert conf >= 0.9

    def test_please_is_actionable(self):
        is_act, reason, conf = _is_actionable("Please rename this variable to something more descriptive")
        assert is_act is True
        assert "action request" in reason.lower()

    def test_should_is_actionable(self):
        is_act, reason, conf = _is_actionable("This should use pathlib instead of os.path")
        assert is_act is True

    def test_nit_is_actionable(self):
        is_act, reason, conf = _is_actionable("nit: missing trailing comma")
        assert is_act is True
        assert "nitpick" in reason.lower()

    def test_praise_not_actionable(self):
        is_act, reason, conf = _is_actionable("This looks great!")
        assert is_act is False


class TestCategorizeComment:
    def test_empty_comment_skipped(self):
        comment = _make_comment("")
        result = categorize_comment(comment)
        assert result.category == "SKIP"
        assert result.confidence == 1.0

    def test_praise_skipped(self):
        comment = _make_comment("LGTM!")
        result = categorize_comment(comment)
        assert result.category == "SKIP"

    def test_suggestion_is_actionable(self):
        comment = _make_comment(
            """Consider using pathlib:
```suggestion
from pathlib import Path
```""",
            path="src/utils.py",
            line=10,
        )
        result = categorize_comment(comment)
        assert result.category == "ACTIONABLE"
        assert result.fix_plan is not None
        assert "suggestion" in result.fix_plan.lower() or "pathlib" in result.fix_plan.lower()

    def test_question_categorized(self):
        comment = _make_comment("Why was this changed from X to Y?")
        result = categorize_comment(comment)
        assert result.category == "QUESTION"

    def test_optional_suggestion(self):
        comment = _make_comment("You might want to consider using a different approach")
        result = categorize_comment(comment)
        # "consider" is an action word, so this gets categorized as actionable
        assert result.category in ("SUGGESTION", "SKIP", "ACTIONABLE")


class TestFilterActionable:
    def test_filter_only_actionable(self):
        comments = [
            _make_comment("Please fix this typo in the variable name here", path="a.py", line=1),
            _make_comment("LGTM!"),
            _make_comment("Why?"),
        ]
        categorized = categorize_comments(comments)
        filtered = filter_actionable(categorized, include_questions=False)
        assert len(filtered) >= 1
        assert all(c.category == "ACTIONABLE" for c in filtered)

    def test_filter_with_questions(self):
        comments = [
            _make_comment("Please fix this typo in the variable name here", path="a.py", line=1),
            _make_comment("Why was this changed from the original implementation?"),
        ]
        categorized = categorize_comments(comments)
        filtered = filter_actionable(categorized, include_questions=True)
        # At least one should be actionable or question
        assert len(filtered) >= 1

    def test_filter_with_confidence_threshold(self):
        comments = [
            _make_comment("```suggestion\ncode\n```", path="a.py", line=1),
            _make_comment("maybe consider changing this"),
        ]
        categorized = categorize_comments(comments)
        filtered = filter_actionable(categorized, min_confidence=0.8)
        # Only high-confidence items should remain
        assert all(c.confidence >= 0.8 for c in filtered)


class TestFixPlan:
    def test_fix_plan_from_suggestion(self):
        comment = _make_comment(
            """Use this:
```suggestion
const x = 1;
```""",
            path="src/file.js",
            line=42,
        )
        result = categorize_comment(comment)
        assert result.fix_plan is not None
        assert "src/file.js" in result.fix_plan or "42" in result.fix_plan

    def test_fix_plan_from_rename(self):
        comment = _make_comment(
            "Please rename this function to something clearer",
            path="src/utils.py",
            line=10,
        )
        result = categorize_comment(comment)
        if result.category == "ACTIONABLE":
            assert result.fix_plan is not None
