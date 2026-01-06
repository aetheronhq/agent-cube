"PR review command - review any GitHub PR."

import asyncio
import json
from typing import Optional

import typer

from ..core.agent import run_agent
from ..core.config import PROJECT_ROOT
from ..core.output import console, print_error, print_info, print_success
from ..core.user_config import load_config
from ..github.pulls import PRData, fetch_pr
from ..github.reviews import Review, ReviewComment, post_review


def load_repo_context() -> str:
    """Load repo context for review."""
    context_parts = []

    # Planning docs
    planning_dir = PROJECT_ROOT / "planning"
    if planning_dir.exists():
        for doc in planning_dir.glob("*.md"):
            content = doc.read_text()[:2000]  # First 2000 chars
            context_parts.append(f"## {doc.name}\n{content}")

    # README
    readme = PROJECT_ROOT / "README.md"
    if readme.exists():
        context_parts.append(f"## README.md\n{readme.read_text()[:2000]}")

    # CONTRIBUTING
    contrib = PROJECT_ROOT / "CONTRIBUTING.md"
    if contrib.exists():
        context_parts.append(f"## CONTRIBUTING.md\n{contrib.read_text()[:2000]}")

    return "\n\n---\n\n".join(context_parts)


def build_review_prompt(pr: PRData, context: str, focus: Optional[str]) -> str:
    """Build the prompt for the reviewing agent."""
    focus_instruction = ""
    if focus:
        focus_instruction = f"\n**FOCUS AREA:** Pay special attention to {focus} issues.\n"

    return f"""# PR Review Task

You are reviewing PR #{pr.number}: {pr.title}

## PR Description
{pr.body or "(No description provided)"}

## Branch Info
- Head: {pr.head_branch}
- Base: {pr.base_branch}
{focus_instruction}## Repository Context
{context}

## Diff to Review
```diff
{pr.diff}
```

## Your Task

Review this PR and output a structured JSON response:

```json
{{
  "decision": "APPROVE" | "REQUEST_CHANGES" | "COMMENT",
  "summary": "2-3 sentence overall assessment",
  "comments": [
    {{
      "path": "relative/path/to/file.py",
      "line": 42,
      "body": "Specific issue or suggestion",
      "severity": "critical" | "warning" | "info" | "nitpick"
    }}
  ]
}}
```

## Review Criteria

1. **Security** - Auth issues, input validation, secrets exposure
2. **Performance** - N+1 queries, unbounded loops, missing caching
3. **Code Quality** - Type safety, error handling, readability
4. **Testing** - Missing tests, edge cases not covered
5. **Documentation** - Missing docstrings, unclear code

## Output Rules

- Max 20 comments (prioritize critical issues)
- Skip nitpicks unless --focus explicitly includes them
- Each comment must reference a specific line in the diff
- Use line numbers from the diff, not original file
- Be constructive, not just critical
- If code looks good, say so and APPROVE

Output ONLY the JSON response, no other text.
"""


def parse_review_output(output: str) -> Optional[Review]:
    """Parse agent output into Review object."""
    import re

    candidates = []

    # 1. Try to find JSON in markdown code blocks
    # Matches ```json ... ``` or just ``` ... ``` containing "decision"
    # We use non-greedy matching for the content
    blocks = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", output, re.DOTALL)
    candidates.extend(blocks)

    # 2. If no blocks or parsing failed, try finding raw JSON-like structures
    # Look for { ... "decision" ... }
    # This is a bit heuristic but helps if the model forgets code blocks
    if not candidates:
        try:
            # Find the last occurrence of "decision"
            idx = output.rfind('"decision"')
            if idx != -1:
                # Find the nearest opening brace before "decision"
                start = output.rfind("{", 0, idx)
                if start != -1:
                    # Find the last closing brace
                    end = output.rfind("}")
                    if end != -1 and end > start:
                        candidates.append(output[start : end + 1])
        except Exception:
            pass

    # Try to parse candidates in reverse order (assuming latest is best)
    for json_str in reversed(candidates):
        try:
            data = json.loads(json_str)

            # Basic validation
            if not isinstance(data, dict):
                continue
            if "decision" not in data:
                continue

            return Review(
                decision=data.get("decision", "COMMENT"),
                summary=data.get("summary", ""),
                comments=[
                    ReviewComment(path=c["path"], line=c["line"], body=c["body"], severity=c.get("severity", "info"))
                    for c in data.get("comments", [])
                ],
            )
        except (json.JSONDecodeError, KeyError, TypeError):
            continue

    return None


async def run_pr_review(pr_number: int, focus: Optional[str], dry_run: bool, model: Optional[str]) -> None:
    """Run the PR review workflow."""
    from ..core.adapters.registry import get_adapter
    from ..core.parsers.registry import get_parser
    from ..core.single_layout import SingleAgentLayout

    config = load_config()
    model_name = model or config.prompter_model
    cli_name = config.cli_tools.get(model_name, "cursor-agent")

    # Fetch PR data
    print_info(f"Fetching PR #{pr_number}...")
    try:
        pr = fetch_pr(pr_number)
    except Exception as e:
        print_error(f"Failed to fetch PR: {e}")
        raise typer.Exit(1)

    print_info(f"PR: {pr.title}")
    print_info(f"Branch: {pr.head_branch} → {pr.base_branch}")

    # Load repo context
    print_info("Loading repo context...")
    context = load_repo_context()

    # Build prompt
    prompt = build_review_prompt(pr, context, focus)

    # Run agent
    print_info(f"Running review with {model_name}...")

    adapter = get_adapter(cli_name)
    if not adapter.check_installed():
        print_error(f"{cli_name} not installed")
        raise typer.Exit(1)

    parser = get_parser(cli_name)

    # Initialize layout for streaming output
    # Note: SingleAgentLayout might need initialized differently depending on exact implementation in this repo
    # but following the prompt's snippet:
    SingleAgentLayout.initialize(f"PR Review #{pr_number}")
    SingleAgentLayout.start()

    output_buffer = []
    stream = run_agent(PROJECT_ROOT, model_name, prompt, session_id=None, resume=False)

    async for line in stream:
        msg = parser.parse(line)
        if msg and msg.content:
            output_buffer.append(msg.content)
            SingleAgentLayout.add_output(msg.content[:100])

    SingleAgentLayout.close()

    # Parse output
    full_output = "\n".join(output_buffer)
    review = parse_review_output(full_output)

    if not review:
        print_error("Failed to parse review output")
        console.print(full_output[:500])
        raise typer.Exit(1)

    # Display review
    console.print()
    console.print(f"[bold]Decision:[/bold] {review.decision}")
    console.print(f"[bold]Summary:[/bold] {review.summary}")
    console.print()

    if review.comments:
        console.print(f"[bold]Comments ({len(review.comments)}):[/bold]")
        for c in review.comments[:10]:  # Show first 10
            severity_color = {"critical": "red", "warning": "yellow", "info": "blue"}.get(c.severity, "white")
            console.print(f"  [{severity_color}]{c.severity.upper()}[/{severity_color}] {c.path}:{c.line}")
            console.print(f"    {c.body[:80]}...")

    # Post or dry-run
    if dry_run:
        print_info("Dry run - review NOT posted")
    else:
        print_info("Posting review to GitHub...")
        if post_review(pr_number, review):
            print_success(f"Review posted to PR #{pr_number}")
        else:
            print_error("Failed to post review")
            raise typer.Exit(1)


def pr_review_command(
    pr_number: int, focus: Optional[str] = None, dry_run: bool = False, model: Optional[str] = None
) -> None:
    """Review a GitHub PR and post inline comments."""
    try:
        asyncio.run(run_pr_review(pr_number, focus, dry_run, model))
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)
