"""PR review command - review any GitHub PR."""

import asyncio
import json
from pathlib import Path
from typing import Optional

import typer

from ..core.agent import run_agent
from ..core.config import PROJECT_ROOT
from ..core.output import console, print_error, print_info, print_success, print_warning
from ..core.user_config import load_config
from ..github.pulls import PRData, check_gh_installed, fetch_pr
from ..github.reviews import Review, ReviewComment, post_review


def load_repo_context() -> str:
    """Load repo context for review (planning docs, README, CONTRIBUTING)."""
    context_parts = []
    project_root = Path(PROJECT_ROOT)

    # Planning docs
    planning_dir = project_root / "planning"
    if planning_dir.exists():
        for doc in sorted(planning_dir.glob("*.md"))[:5]:  # Limit to 5 docs
            try:
                content = doc.read_text()[:2000]
                context_parts.append(f"## {doc.name}\n{content}")
            except (OSError, IOError):
                pass

    # README
    readme = project_root / "README.md"
    if readme.exists():
        try:
            context_parts.append(f"## README.md\n{readme.read_text()[:2000]}")
        except (OSError, IOError):
            pass

    # CONTRIBUTING
    contrib = project_root / "CONTRIBUTING.md"
    if contrib.exists():
        try:
            context_parts.append(f"## CONTRIBUTING.md\n{contrib.read_text()[:2000]}")
        except (OSError, IOError):
            pass

    return "\n\n---\n\n".join(context_parts) if context_parts else "(No repo context found)"


def build_review_prompt(pr: PRData, context: str, focus: Optional[str]) -> str:
    """Build the prompt for the reviewing agent."""
    focus_instruction = ""
    if focus:
        focus_map = {
            "security": "Pay special attention to security issues: auth vulnerabilities, input validation, secrets exposure, SQL injection, XSS.",
            "performance": "Pay special attention to performance issues: N+1 queries, unbounded loops, missing caching, memory leaks.",
            "tests": "Pay special attention to testing: missing tests, edge cases not covered, test quality.",
            "types": "Pay special attention to type safety: missing types, incorrect types, any/unknown usage.",
        }
        focus_instruction = f"\n**FOCUS AREA:** {focus_map.get(focus, f'Pay special attention to {focus} issues.')}\n"

    return f"""# PR Review Task

You are reviewing PR #{pr.number}: {pr.title}

## PR Description
{pr.body or "(No description provided)"}

## Branch Info
- Head: {pr.head_branch} ({pr.head_sha})
- Base: {pr.base_branch}
{focus_instruction}
## Repository Context
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

- Max 15 comments (prioritize critical and warning issues)
- Skip nitpicks unless focus explicitly includes them
- Each comment must reference a specific line in the diff
- Use line numbers from the NEW file (lines starting with +)
- Be constructive, not just critical
- If code looks good, say so and APPROVE

Output ONLY the JSON response, no other text.
"""


def parse_review_output(output: str) -> Optional[Review]:
    """Parse agent output into Review object."""
    import re

    try:
        # Remove streaming artifacts (spaces between characters from thinking mode)
        # Look for JSON code block first
        json_match = re.search(r"```json\s*(\{[\s\S]*?\})\s*```", output)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Find JSON in output (agent may include extra text)
            start = output.find("{")
            end = output.rfind("}") + 1
            if start == -1 or end == 0:
                return None
            json_str = output[start:end]

        # Clean up the JSON string - remove excess whitespace
        json_str = re.sub(r"\s+", " ", json_str)
        json_str = json_str.replace("{ ", "{").replace(" }", "}").replace("[ ", "[").replace(" ]", "]")

        data = json.loads(json_str)

        decision = data.get("decision", "COMMENT")
        if decision not in ("APPROVE", "REQUEST_CHANGES", "COMMENT"):
            decision = "COMMENT"

        comments = []
        for c in data.get("comments", []):
            if "path" in c and "line" in c and "body" in c:
                try:
                    line_num = int(c["line"])
                    if line_num <= 0:
                        continue
                except (ValueError, TypeError):
                    continue
                comments.append(
                    ReviewComment(path=c["path"], line=line_num, body=c["body"], severity=c.get("severity", "info"))
                )

        return Review(
            decision=decision,
            summary=data.get("summary", ""),
            comments=comments[:15],  # Cap at 15
        )
    except (json.JSONDecodeError, KeyError, ValueError, TypeError):
        return None


async def run_pr_review(pr_number: int, focus: Optional[str], dry_run: bool, model: Optional[str]) -> None:
    """Run the PR review workflow."""
    from ..automation.stream import format_stream_message
    from ..core.adapters.registry import get_adapter
    from ..core.parsers.registry import get_parser
    from ..core.single_layout import SingleAgentLayout

    config = load_config()
    model_name = model or config.prompter_model
    cli_name = config.cli_tools.get(model_name, "cursor-agent")

    # Fetch PR data
    print_info(f"Fetching PR #{pr_number}...")
    try:
        pr = fetch_pr(pr_number, cwd=str(PROJECT_ROOT))
    except RuntimeError as e:
        print_error(str(e))
        raise typer.Exit(1)

    print_info(f"PR: {pr.title}")
    print_info(f"Branch: {pr.head_branch} → {pr.base_branch}")

    if not pr.diff.strip():
        print_warning("PR has no diff - nothing to review")
        raise typer.Exit(0)

    # Load repo context
    print_info("Loading repo context...")
    context = load_repo_context()

    # Build prompt
    prompt = build_review_prompt(pr, context, focus)

    # Check adapter
    adapter = get_adapter(cli_name)
    if not adapter.check_installed():
        print_error(f"{cli_name} not installed (needed for {model_name})")
        console.print()
        console.print(adapter.get_install_instructions())
        raise typer.Exit(1)

    parser = get_parser(cli_name)

    # Run agent
    print_info(f"Running review with {model_name}...")
    console.print()

    SingleAgentLayout.initialize(f"PR Review #{pr_number}")
    SingleAgentLayout.start()

    output_buffer: list[str] = []

    try:
        stream = run_agent(Path(PROJECT_ROOT), model_name, prompt, session_id=None, resume=False)

        async for line in stream:
            msg = parser.parse(line)
            if msg:
                formatted = format_stream_message(msg, "Reviewer", "cyan")
                if formatted:
                    if formatted.startswith("[thinking]"):
                        thinking_text = formatted.replace("[thinking]", "").replace("[/thinking]", "")
                        SingleAgentLayout.add_thinking(thinking_text)
                    elif msg.type == "assistant" and msg.content:
                        output_buffer.append(msg.content)
                        SingleAgentLayout.add_assistant_message(msg.content, "Reviewer", "cyan")
                    else:
                        SingleAgentLayout.add_output(formatted)
    finally:
        SingleAgentLayout.close()

    # Parse output
    full_output = "\n".join(output_buffer)
    review = parse_review_output(full_output)

    if not review:
        print_error("Failed to parse review output")
        console.print()
        console.print("[dim]Raw output (first 500 chars):[/dim]")
        console.print(full_output[:500])
        raise typer.Exit(1)

    # Display review
    console.print()
    decision_colors = {"APPROVE": "green", "REQUEST_CHANGES": "red", "COMMENT": "yellow"}
    decision_color = decision_colors.get(review.decision, "white")
    console.print(f"[bold]Decision:[/bold] [{decision_color}]{review.decision}[/{decision_color}]")
    console.print(f"[bold]Summary:[/bold] {review.summary}")
    console.print()

    # Split comments by severity - post actionable + nitpicks, info goes in summary
    actionable = [c for c in review.comments if c.severity in ("critical", "warning", "nitpick")]
    info_comments = [c for c in review.comments if c.severity == "info"]

    if review.comments:
        console.print(f"[bold]Comments ({len(review.comments)}):[/bold]")
        severity_colors = {"critical": "red", "warning": "yellow", "info": "blue", "nitpick": "dim"}
        for c in review.comments:
            color = severity_colors.get(c.severity, "white")
            console.print(f"  [{color}]{c.severity.upper():8}[/{color}] {c.path}:{c.line}")
            body_preview = c.body[:80] + "..." if len(c.body) > 80 else c.body
            console.print(f"           {body_preview}")
    else:
        console.print("[dim]No inline comments[/dim]")

    console.print()

    # Build summary with positive feedback (info comments not posted inline)
    summary_with_positives = review.summary
    if info_comments:
        positives = "\n\n**Positive observations:**\n" + "\n".join(
            f"- `{c.path}`: {c.body[:100]}" for c in info_comments[:5]
        )
        summary_with_positives += positives

    summary_with_positives += "\n\n---\n🤖 Agent Cube Review"

    # Only post actionable comments (critical/warning/nitpick) as inline, not info
    review_to_post = Review(
        decision=review.decision,
        summary=summary_with_positives,
        comments=actionable,
    )

    # Post or dry-run
    if dry_run:
        print_warning("Dry run - review NOT posted to GitHub")
        if info_comments:
            console.print(f"[dim]({len(info_comments)} info comments included in summary, not as inline)[/dim]")
    else:
        print_info("Posting review to GitHub...")
        if info_comments:
            console.print(f"[dim]({len(info_comments)} info comments in summary, {len(actionable)} inline)[/dim]")
        try:
            post_review(pr_number, review_to_post, cwd=str(PROJECT_ROOT))
            print_success(f"Review posted to PR #{pr_number}")
        except RuntimeError as e:
            print_error(f"Failed to post review: {e}")
            raise typer.Exit(1)


def pr_review_command(
    pr_number: int, focus: Optional[str] = None, dry_run: bool = False, model: Optional[str] = None
) -> None:
    """Review a GitHub PR and post inline comments."""
    # Pre-check gh CLI before doing anything else
    if not check_gh_installed():
        print_error("gh CLI not installed or not authenticated")
        console.print()
        console.print("Install: [cyan]https://cli.github.com/[/cyan]")
        console.print("Auth:    [cyan]gh auth login[/cyan]")
        raise typer.Exit(1)

    try:
        asyncio.run(run_pr_review(pr_number, focus, dry_run, model))
    except RuntimeError as e:
        print_error(str(e))
        raise typer.Exit(1)
