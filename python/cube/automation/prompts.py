"""Shared prompt templates for judge reviews."""

from pathlib import Path

from ..core.config import PROJECT_ROOT


def build_review_checklist() -> str:
    """Build the shared review checklist section."""
    return """## Primary Standard

**The single most important criterion: is this code clean, elegant, and minimalistic?**

Every line should earn its place. Favour the simplest solution that correctly solves the problem.
Flag anything that violates these principles — they are the primary reason to REQUEST_CHANGES:

- **Best practice** — follows established patterns for the language/framework in use
- **Clean** — readable, well-named, no dead code, no commented-out blocks
- **KISS** — solves the problem directly; no unnecessary abstraction or indirection
- **Elegant** — the design feels obvious in hindsight, not clever or convoluted
- **Minimalistic** — does exactly what's needed, nothing more; no speculative code

> If the implementation works but is over-engineered, verbose, or adds complexity without
> clear justification — that IS a blocking issue, not a nitpick.

---

## Review Checklist

### 0. Writer Responses (CHECK FIRST IF EXISTS)
- Check `.prompts/responses/writer-*-{task_id}.md` for writer explanations/challenges
- If a writer has challenged previous judge feedback, consider their reasoning carefully
- Writers may have context judges missed (architecture decisions, requirements, constraints)
- If the writer's explanation is valid, remove or downgrade the related issue
- If the writer's explanation is insufficient, keep the issue and explain why

### 1. Planning & Architecture Alignment
- **Read planning docs** - Check `docs/`, `planning/`, `ARCHITECTURE.md`, `ADR/` in the repo
- **Verify documented decisions** - Does this change align with existing architecture?
- **Flag conflicts immediately** - If changes contradict documented patterns (auth, data flow, credentials)

### 2. Scope & Intent
- **Task alignment** - Do the changes match the original task requirements?
- **Undocumented changes** - Flag significant changes not mentioned in the task
- **Question unclear intent** - Ask "Why was this done?" for unexplained changes
- **Scope creep** - Identify unnecessary changes that weren't required

### 3. Technical Review
- Security issues (auth changes, secrets handling, input validation)
- Performance concerns (N+1 queries, unbounded operations)
- Code quality and maintainability
- Missing tests for new functionality
- Error handling

### 4. KISS, Elegance & Minimalism
- **Existing patterns** - Could this use existing modules/utilities instead of new code?
- **Redundant config** - Is this specifying default behaviour explicitly?
- **Over-engineering** - Is the solution more complex than the problem demands?
- **Dead weight** - Any code, abstraction, or config that isn't actively needed?
- **Naming** - Do names clearly convey intent without needing a comment to explain?
- **Simpler alternative** - Could this be written in fewer lines with equal clarity?
"""


def build_decision_file_instructions(task_id: str, include_inline_comments: bool = True) -> str:
    """Build decision file format instructions.

    Args:
        task_id: The task/PR ID
        include_inline_comments: Whether to include inline_comments field (for PR reviews)
    """
    inline_comments_section = (
        """
    "inline_comments": [
      {
        "path": "relative/path/to/file.py",
        "line": 42,
        "body": "Specific issue or suggestion",
        "severity": "critical" | "warning" | "nitpick"
      }
    ],"""
        if include_inline_comments
        else ""
    )

    inline_rules = (
        """
## Inline Comment Rules

- **ONLY post issues** - things that need attention or questions
- **NO positive feedback** as inline comments - put "Good: ..." observations in summary instead
- **Max 10 comments** per judge (prioritize critical issues)
- **severity**: "critical" (must fix), "warning" (should fix), "nitpick" (minor style issue)
- **line**: Use line numbers from NEW file (lines starting with +)
- **path**: Use relative path from repo root
- Questions count as comments: "Why was this changed from X to Y?"
- **NO signatures** - do NOT add "Agent Cube", emojis, or attribution to comment body (added automatically)
"""
        if include_inline_comments
        else ""
    )

    return f"""## Decision File

**You MUST create this JSON file at the end of your review:**

**File:** `{PROJECT_ROOT}/.prompts/decisions/{{{{judge_key}}}}-{task_id}-peer-review.json`

⚠️ **Use this EXACT absolute path. Do NOT write to a worktree.**

**REQUIRED FORMAT:**
```json
{{{{
  "judge": "{{{{judge_key}}}}",
  "task_id": "{task_id}",
  "review_type": "peer-review",
  "decision": "APPROVED" | "REQUEST_CHANGES",
  "summary": "2-3 sentence overall assessment",{inline_comments_section}
  "remaining_issues": ["Any blocking issues not tied to specific lines"]
}}}}
```

**⚠️ CRITICAL - EXACT SPELLING:**
- Use EXACT strings: `"APPROVED"` or `"REQUEST_CHANGES"`
- NOT "Approved", "approve", "APPROVE" - use exactly `"APPROVED"`
{inline_rules}
## Decision Rules

- **APPROVED**: ONLY if NO critical or warning issues. Nitpicks alone are OK to approve.
- **REQUEST_CHANGES**: If ANY critical or warning issues exist (even unanswered questions)
- Do NOT approve if you have warnings - warnings mean "should fix" before merge

## Complete Review Required

⚠️ **YOU MUST RE-REVIEW THE CODE** - even if your decision file already exists!
- The writer may have made fixes since your last review
- Run `git log` and `git diff` to see what changed
- **OVERWRITE** your decision file with a fresh assessment
- Do NOT say "already reviewed" - that is WRONG, always re-check the code

This is a COMPLETE review - include ALL issues you find, even if mentioned previously.
- Report every issue that exists in the current code
- Only omit a previously-reported issue if you verify it has been RESOLVED
- Do not assume previous feedback was addressed - CHECK THE CODE
"""


def build_pr_review_prompt(
    pr_number: int,
    title: str,
    body: str,
    head_branch: str,
    head_sha: str,
    base_branch: str,
    task_id: str,
    repo_context: str = "",
    prior_comments: str = "",
) -> str:
    """Build complete prompt for PR review."""
    context_section = f"\n## Repository Context\n{repo_context}\n" if repo_context else ""
    prior_section = f"\n## Prior Review Comments\n\n{prior_comments}\n" if prior_comments else ""

    return f"""# Peer Review: PR #{pr_number}

## PR: {title}

{body or "(No description)"}

## Branch
- Head: `{head_branch}` ({head_sha[:8]})
- Base: `{base_branch}`
{context_section}{prior_section}
## View Changes

Run these commands to review the PR (using origin/ to ensure you see the latest remote commits):

```bash
# See what files changed
git diff origin/{base_branch}...origin/{head_branch} --stat

# View full diff
git diff origin/{base_branch}...origin/{head_branch}

# View specific file
git diff origin/{base_branch}...origin/{head_branch} -- path/to/file.ts
```

## Your Task

Do a **full code review** of this PR:
1. Review all changed files using `git diff` commands
2. Look for bugs, security issues, missing error handling, etc.
3. Check code quality, patterns, and best practices
4. If prior review comments are listed above, verify resolved threads were actually fixed correctly — don't just trust the "resolved" status

**⚠️ MANDATORY RE-REVIEW** - If you have a prior decision file:
- The writer has likely made changes since your last review
- Run `git log` to see new commits, `git diff` to see changes
- **You MUST re-check all code and OVERWRITE your decision file**
- Do NOT just say "already reviewed" - that is incorrect behavior
- Verify each prior issue: is it STILL there? Remove any that are now fixed
- Add any NEW issues you find in this review

{build_review_checklist()}

{build_decision_file_instructions(task_id, include_inline_comments=True)}
"""


def _get_focus_checklist(focus_area: str) -> str:
    """Get focused review checklist for a specific area."""
    focus_checklists = {
        "security": """## Security-Focused Review Checklist

### Authentication & Authorization
- Are all endpoints properly authenticated?
- Are authorization checks in place for sensitive operations?
- Are tokens/credentials handled securely (not logged, not in URLs)?

### Input Validation
- Is user input properly validated and sanitized?
- Are SQL queries parameterized (no string concatenation)?
- Are file paths validated to prevent path traversal?

### Secrets & Credentials
- Are secrets loaded from environment variables or secret managers?
- Are .env files properly gitignored?
- Are API keys or tokens exposed in logs or error messages?

### Dependencies
- Are there known vulnerabilities in dependencies?
- Are dependencies pinned to specific versions?

### Data Handling
- Is sensitive data encrypted at rest and in transit?
- Are PII fields properly handled (no logging, proper access controls)?
""",
        "tests": """## Test Coverage Review Checklist

### Unit Tests
- Are new functions/methods covered by unit tests?
- Are edge cases and error conditions tested?
- Are mock objects used appropriately?

### Integration Tests
- Do integration tests cover new API endpoints?
- Are database operations tested with proper setup/teardown?
- Are external service calls properly mocked?

### Test Quality
- Do tests assert the right things (not just "no errors")?
- Are tests independent and not relying on execution order?
- Are test descriptions clear about what they're testing?

### Coverage Gaps
- What code paths are NOT covered by tests?
- Are critical business logic functions fully tested?
""",
        "performance": """## Performance Review Checklist

### Database Queries
- Are there N+1 query patterns?
- Are indexes used for frequently queried fields?
- Are large result sets paginated?

### Memory & Resources
- Are large objects properly disposed/closed?
- Are there memory leaks from event listeners or subscriptions?
- Are file handles and connections properly closed?

### Algorithmic Efficiency
- Are there O(n²) or worse algorithms that could be optimized?
- Are expensive operations cached where appropriate?
- Are loops performing unnecessary work?

### Async & Concurrency
- Are blocking operations properly async?
- Are there race conditions or deadlock risks?
- Is parallelism used where appropriate?
""",
        "bugs": """## Bug Detection Review Checklist

### Logic Errors
- Are conditional statements correct (boundary conditions, negation)?
- Are loop termination conditions correct?
- Are null/undefined values handled?

### Error Handling
- Are exceptions caught and handled appropriately?
- Are error messages informative without leaking sensitive info?
- Are resources cleaned up in error paths?

### State Management
- Is mutable state handled correctly?
- Are there race conditions in shared state?
- Are default values appropriate?

### Edge Cases
- What happens with empty input?
- What happens with very large input?
- What happens with invalid or malformed input?
""",
    }

    return focus_checklists.get(focus_area.lower(), build_review_checklist())


def build_focused_review_prompt(
    pr_number: int,
    title: str,
    body: str,
    head_branch: str,
    head_sha: str,
    base_branch: str,
    task_id: str,
    focus_area: str,
    repo_context: str = "",
    prior_comments: str = "",
) -> str:
    """Build prompt for focused PR review.

    Args:
        pr_number: PR number
        title: PR title
        body: PR description
        head_branch: Source branch
        head_sha: Head commit SHA
        base_branch: Target branch
        task_id: Task/PR ID
        focus_area: Area to focus on (security, tests, performance, bugs)
        repo_context: Additional repo context
        prior_comments: Formatted prior review threads for context
    """
    context_section = f"\n## Repository Context\n{repo_context}\n" if repo_context else ""
    prior_section = f"\n## Prior Review Comments\n\n{prior_comments}\n" if prior_comments else ""
    focus_checklist = _get_focus_checklist(focus_area)

    return f"""# Focused PR Review: {focus_area.upper()}

## PR #{pr_number}: {title}

{body or "(No description)"}

## Branch
- Head: `{head_branch}` ({head_sha[:8]})
- Base: `{base_branch}`
{context_section}{prior_section}
## View Changes

```bash
# See what files changed
git diff origin/{base_branch}...origin/{head_branch} --stat

# View full diff
git diff origin/{base_branch}...origin/{head_branch}
```

## Focus Area: {focus_area.upper()}

This is a **focused review** specifically looking for **{focus_area}** issues.
If prior review comments are listed above, verify resolved threads were actually fixed — don't re-raise issues that are genuinely addressed, but flag any that were resolved without a proper fix.

{focus_checklist}

{build_decision_file_instructions(task_id, include_inline_comments=True)}
"""


def build_peer_review_prompt(
    task_id: str,
    worktree_base: Path,
    project_name: str,
    is_pr_review: bool = False,
    head_sha: str = "",
) -> str:
    """Build prompt for peer review of worktree implementations."""
    if is_pr_review:
        # PR reviews use a dedicated worktree synced to origin
        # task_id is already "pr-XXX" so just use it directly
        worktree_path = f"{worktree_base}/{project_name}/{task_id}"
        branch_ref = "origin/{branch}"  # Filled in by caller
    else:
        # Writer reviews use writer-specific worktrees
        worktree_path = f"{worktree_base}/{project_name}/writer-{{{{winner}}}}-{task_id}"
        branch_ref = f"writer-{{{{winner}}}}/{task_id}"

    sha_verification = ""
    if head_sha:
        sha_verification = f"""
⚠️ **VERIFY COMMIT BEFORE REVIEWING:**
```bash
cd {worktree_path}/ && git rev-parse HEAD
```
Expected: `{head_sha}`

If the SHA doesn't match, run: `git fetch origin && git reset --hard origin/{{branch}}`
"""

    return f"""# Peer Review Context

**You are reviewing the {'PR' if is_pr_review else 'WINNING implementation'}.**

## ⚠️ CRITICAL: Code Location

**ALL files MUST be read from this worktree:**
```
{worktree_path}/
```

**Branch:** `{branch_ref}`
{sha_verification}
❌ **DO NOT** read files without the worktree prefix (e.g., `apps/...` is WRONG)
✅ **ALWAYS** use full path: `{worktree_path}/apps/...`

## Review Scope

Check what was changed since branching from main:
```bash
cd {worktree_path}/
git fetch origin main
git log --oneline origin/main..HEAD
git diff origin/main...HEAD --stat
```

Use read_file WITH THE FULL WORKTREE PATH to review code.

---

{build_review_checklist()}

### Questions to Include
For any change that seems significant but unexplained:
- "Why was X changed from Y to Z?"
- "Is this architectural change intentional?"

Add questions to `remaining_issues` even if approving.

---

{build_decision_file_instructions(task_id, include_inline_comments=False)}
"""
