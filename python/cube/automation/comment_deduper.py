"""AI-powered comment deduplication for PR reviews."""

import json
from dataclasses import dataclass

from ..core.config import PROJECT_ROOT
from ..core.output import console, print_info
from ..core.user_config import get_prompter_model
from ..github.reviews import ExistingComment, ReviewComment


@dataclass
class DedupeResult:
    """Result of AI deduplication."""

    comments_to_post: list[ReviewComment]
    skipped: list[dict]  # {reason: str, original: ReviewComment}
    merged: list[dict]  # {from: list[ReviewComment], into: ReviewComment}


def build_dedupe_prompt(
    new_comments: list[tuple[str, ReviewComment]],  # (judge_label, comment)
    existing_comments: list[ExistingComment],
    pr_diff: str,
) -> str:
    """Build prompt for the deduplication agent."""

    # Format new comments
    new_comments_text = ""
    for i, (judge, new_c) in enumerate(new_comments, 1):
        new_comments_text += f"""
### New Comment {i}
- **Judge**: {judge}
- **File**: {new_c.path}
- **Line**: {new_c.line}
- **Severity**: {new_c.severity}
- **Body**:
```
{new_c.body}
```
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
- **Body**:
```
{ex_c.body}
```
"""
    else:
        existing_text = "*No existing comments on this PR*"

    prompt = f"""# Comment Deduplication Task

You are reviewing new judge comments before they're posted to a GitHub PR. Your job is to decide which comments to POST, SKIP, or MERGE.

## PR Diff (for context)
```diff
{pr_diff[:8000] if len(pr_diff) > 8000 else pr_diff}
```

## Existing Comments on PR
{existing_text}

## New Comments from Judges
{new_comments_text}

## Your Task

For each new comment, decide:
1. **POST** - Comment is novel, valuable, and not covered by existing comments
2. **SKIP** - Comment duplicates an existing comment (same issue, same location)
3. **MERGE** - Multiple new comments address the same issue - combine into one

### Decision Rules
- If an existing comment already raises the same concern at the same location → SKIP
- If multiple judges raise the same issue → MERGE into one comment, credit all judges
- If a new comment adds value beyond existing feedback → POST
- Prefer quality over quantity - skip low-value comments

## Output Format

Write your decision to: `{PROJECT_ROOT}/.prompts/decisions/dedupe-result.json`

```json
{{
  "comments_to_post": [
    {{
      "path": "file.py",
      "line": 42,
      "severity": "warning",
      "body": "Combined/cleaned comment text",
      "judges": ["Judge Opus", "Judge Gemini"]
    }}
  ],
  "skipped": [
    {{
      "original_index": 3,
      "reason": "Duplicates existing comment #2 about error handling"
    }}
  ],
  "merged": [
    {{
      "merged_indices": [1, 4],
      "into_index": 0,
      "reason": "Both comments about missing null check"
    }}
  ]
}}
```

Notes:
- `comments_to_post` is the final list to actually post to GitHub
- `judges` field should list all judges whose feedback was incorporated
- Clean up and improve comment text - fix grammar, remove redundancy
- Keep severity from the most severe contributing comment
- Add context if it helps clarify the issue
"""
    return prompt


async def run_dedupe_agent(
    new_comments: list[tuple[str, ReviewComment]],
    existing_comments: list[ExistingComment],
    pr_diff: str,
    pr_number: int,
) -> DedupeResult:
    """Run AI agent to deduplicate comments.

    Args:
        new_comments: List of (judge_label, ReviewComment) tuples
        existing_comments: Existing comments already on the PR
        pr_diff: The PR diff for context
        pr_number: PR number for logging

    Returns:
        DedupeResult with comments to post, skipped, and merged
    """
    from ..core.agent import run_agent
    from ..core.parsers.registry import get_parser

    prompt = build_dedupe_prompt(new_comments, existing_comments, pr_diff)
    output_file = PROJECT_ROOT / ".prompts" / "decisions" / "dedupe-result.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Clear old result
    if output_file.exists():
        output_file.unlink()

    model = get_prompter_model()
    print_info(f"Running dedupe agent ({model}) on {len(new_comments)} comments...")

    parser = get_parser("cursor-agent")

    try:
        async for line in run_agent(PROJECT_ROOT, model, prompt):
            msg = parser.parse(line)
            if msg and msg.type == "assistant" and msg.content:
                # Show progress dots
                console.print(".", end="", style="dim")

            if output_file.exists():
                break

        console.print()  # newline after dots

        if not output_file.exists():
            console.print("[yellow]Warning: Dedupe agent did not produce output file[/yellow]")
            return DedupeResult(
                comments_to_post=[c for _, c in new_comments],
                skipped=[],
                merged=[],
            )

        data = json.loads(output_file.read_text())
        return _parse_dedupe_result(data, new_comments)

    except Exception as e:
        console.print(f"\n[yellow]Dedupe agent failed: {e}. Posting all comments.[/yellow]")
        return DedupeResult(
            comments_to_post=[c for _, c in new_comments],
            skipped=[],
            merged=[],
        )


def _parse_dedupe_result(
    data: dict,
    original_comments: list[tuple[str, ReviewComment]],
) -> DedupeResult:
    """Parse dedupe result JSON into DedupeResult."""
    comments_to_post = []

    for item in data.get("comments_to_post", []):
        comment = ReviewComment(
            path=item["path"],
            line=item["line"],
            body=item["body"],
            severity=item.get("severity", "info"),
        )
        # Add judge attribution to body
        judges = item.get("judges", [])
        if judges:
            judge_str = ", ".join(judges)
            comment.body = f"{comment.body}\n\n— *Agent Cube / {judge_str}* 🤖"
        else:
            comment.body = f"{comment.body}\n\n— *Agent Cube* 🤖"
        comments_to_post.append(comment)

    skipped = data.get("skipped", [])
    merged = data.get("merged", [])

    return DedupeResult(
        comments_to_post=comments_to_post,
        skipped=skipped,
        merged=merged,
    )
