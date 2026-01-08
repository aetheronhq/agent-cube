"""AI-powered comment deduplication for PR reviews."""

import json
from dataclasses import dataclass

from ..core.config import PROJECT_ROOT
from ..core.output import console, print_info
from ..core.user_config import get_prompter_model
from ..github.reviews import ExistingComment, ReviewComment


@dataclass
class InlineComment:
    """An inline comment with judge attribution."""

    comment: ReviewComment
    judges: list[str]


@dataclass
class SkippedItem:
    """A skipped feedback item with reason."""

    judge: str
    reason: str
    body: str


@dataclass
class DedupeResult:
    """Result of AI deduplication."""

    inline_comments: list[InlineComment]  # Comments with file:line to post as inline
    summary_issues: list[str]  # Issues without file:line to include in summary
    skipped: list[SkippedItem]  # Items that were skipped with reasons


@dataclass
class JudgeFeedback:
    """A piece of feedback from a judge - either inline or general."""

    judge: str
    body: str
    path: str | None = None  # None for general issues
    line: int | None = None
    severity: str = "warning"


def build_dedupe_prompt(
    feedback: list[JudgeFeedback],
    existing_comments: list[ExistingComment],
    pr_diff: str,
) -> str:
    """Build prompt for the deduplication agent."""

    # Format new feedback
    feedback_text = ""
    for i, f in enumerate(feedback, 1):
        loc = f"{f.path}:{f.line}" if f.path and f.line else "general"
        feedback_text += f"""
### Feedback {i}
- **Judge**: {f.judge}
- **Location**: {loc}
- **Severity**: {f.severity}
- **Body**: {f.body}
"""

    # Format existing comments
    existing_text = ""
    if existing_comments:
        for i, ex_c in enumerate(existing_comments, 1):
            loc = f"{ex_c.path}:{ex_c.line}" if ex_c.path else "top-level"
            existing_text += f"""
### Existing Comment {i}
- **Location**: {loc}
- **Author**: {ex_c.author}
- **Body**: {ex_c.body}
"""
    else:
        existing_text = "*No existing comments on this PR*"

    prompt = f"""# Feedback Deduplication Task

You are reviewing judge feedback before it's posted to a GitHub PR. Deduplicate and organize the feedback.

## PR Diff (for context)
```diff
{pr_diff[:8000] if len(pr_diff) > 8000 else pr_diff}
```

## Existing Comments on PR
{existing_text}

## New Feedback from Judges
{feedback_text}

## Your Task

Deduplicate and organize the feedback into two categories:
1. **inline_comments** - Issues with specific file:line locations → post as inline comments
2. **summary_issues** - General concerns without specific locations → include in summary

### Rules
- SKIP feedback that duplicates existing PR comments
- SKIP positive/praise feedback (👍, "good", "nice", etc.) - do NOT post as inline comments
- MERGE similar feedback from different judges into one
- ONLY include actual issues, concerns, or questions - things that need attention
- If feedback has file:line → inline_comments
- If feedback is general (no file:line) → summary_issues
- Credit all contributing judges in the `judges` field
- Clean up text - be concise, remove redundancy

## Output Format

Write to: `{PROJECT_ROOT}/.prompts/decisions/dedupe-result.json`

```json
{{
  "inline_comments": [
    {{
      "path": "file.py",
      "line": 42,
      "severity": "warning",
      "body": "Issue description",
      "judges": ["Judge Opus", "Judge Gemini"]
    }}
  ],
  "summary_issues": [
    "Documentation contradicts implementation - needs update",
    "Missing error handling in auth flow"
  ],
  "skipped": [
    {{"judge": "Judge Opus", "reason": "duplicate of existing comment", "body": "..."}},
    {{"judge": "Judge Gemini", "reason": "positive feedback", "body": "Good job on..."}}
  ]
}}
```
"""
    return prompt


async def run_dedupe_agent(
    feedback: list[JudgeFeedback],
    existing_comments: list[ExistingComment],
    pr_diff: str,
    pr_number: int,
) -> DedupeResult:
    """Run AI agent to deduplicate feedback.

    Args:
        feedback: List of JudgeFeedback (both inline comments and general issues)
        existing_comments: Existing comments already on the PR
        pr_diff: The PR diff for context
        pr_number: PR number for logging

    Returns:
        DedupeResult with inline_comments, summary_issues, and skipped
    """
    # Early return if nothing to process
    if not feedback:
        return DedupeResult(inline_comments=[], summary_issues=[], skipped=[])

    from ..core.agent import run_agent
    from ..core.parsers.registry import get_parser

    prompt = build_dedupe_prompt(feedback, existing_comments, pr_diff)
    output_file = PROJECT_ROOT / ".prompts" / "decisions" / "dedupe-result.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Clear old result
    if output_file.exists():
        output_file.unlink()

    model = get_prompter_model()
    print_info(f"Running dedupe agent ({model}) on {len(feedback)} items...")

    parser = get_parser("cursor-agent")
    agent_stream = run_agent(PROJECT_ROOT, model, prompt)

    try:
        async for line in agent_stream:
            msg = parser.parse(line)
            if msg and msg.type == "assistant" and msg.content:
                console.print(".", end="", style="dim")

            if output_file.exists():
                break

        console.print()

        if not output_file.exists():
            console.print("[yellow]Warning: Dedupe agent did not produce output file[/yellow]")
            return _fallback_result(feedback)

        data = json.loads(output_file.read_text())
        return _parse_dedupe_result(data)

    except Exception as e:
        console.print(f"\n[yellow]Dedupe agent failed: {e}. Using fallback.[/yellow]")
        return _fallback_result(feedback)
    finally:
        # Properly close async generator to avoid event loop warnings
        await agent_stream.aclose()


def _fallback_result(feedback: list[JudgeFeedback]) -> DedupeResult:
    """Create fallback result when deduper fails."""
    inline = []
    summary = []
    for f in feedback:
        if f.path and f.line:
            comment = ReviewComment(
                path=f.path,
                line=f.line,
                body=f"{f.body}\n\n— *Agent Cube / {f.judge}* 🤖",
                severity=f.severity,
            )
            inline.append(InlineComment(comment=comment, judges=[f.judge]))
        else:
            summary.append(f"[{f.judge}] {f.body}")
    return DedupeResult(inline_comments=inline, summary_issues=summary, skipped=[])


def _parse_dedupe_result(data: dict) -> DedupeResult:
    """Parse dedupe result JSON into DedupeResult."""
    inline_comments = []

    for item in data.get("inline_comments", []):
        judges = item.get("judges", [])
        judge_str = ", ".join(judges) if judges else "Agent Cube"
        body = f"{item['body']}\n\n— *Agent Cube / {judge_str}* 🤖"

        comment = ReviewComment(
            path=item["path"],
            line=item["line"],
            body=body,
            severity=item.get("severity", "warning"),
        )
        inline_comments.append(InlineComment(comment=comment, judges=judges))

    summary_issues = data.get("summary_issues", [])

    skipped = []
    for item in data.get("skipped", []):
        skipped.append(
            SkippedItem(
                judge=item.get("judge", "Unknown"),
                reason=item.get("reason", ""),
                body=item.get("body", "")[:100],  # Truncate long bodies
            )
        )

    return DedupeResult(
        inline_comments=inline_comments,
        summary_issues=summary_issues,
        skipped=skipped,
    )
