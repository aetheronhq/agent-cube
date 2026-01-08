"""Shared prompt templates for judge reviews."""

from pathlib import Path

from ..core.config import PROJECT_ROOT


def build_review_checklist() -> str:
    """Build the shared review checklist section."""
    return """## Review Checklist

### 1. Planning & Architecture Alignment (CHECK FIRST)
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

### 4. KISS & Simplicity
- **Existing patterns** - Could this use existing modules/utilities?
- **Redundant config** - Is this specifying default behavior explicitly?
- **Over-engineering** - Is the solution more complex than needed?
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

This is a COMPLETE review - include ALL issues you find, even if mentioned previously.
- Report every issue that exists in the current code
- Only omit a previously-reported issue if you verify it has been RESOLVED
- Do not assume previous feedback was addressed - check the code
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
) -> str:
    """Build complete prompt for PR review."""
    context_section = f"\n## Repository Context\n{repo_context}\n" if repo_context else ""

    return f"""# Peer Review: PR #{pr_number}

## PR: {title}

{body or "(No description)"}

## Branch
- Head: `{head_branch}` ({head_sha[:8]})
- Base: `{base_branch}`
{context_section}
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

**If you have a prior decision file:** You MUST verify each issue before keeping it:
1. Read your decision file: `.prompts/decisions/{{judge_key}}-{task_id}-peer-review.json`
2. For EACH inline_comment: `read_file` the path and check the specific line - is the issue STILL there?
3. For EACH remaining_issue: verify with git commands or read_file - is it STILL a problem?
4. **REMOVE any issue that has been FIXED** - do NOT blindly copy old issues
5. Only keep issues you have VERIFIED still exist in the CURRENT code
6. Update decision: APPROVED if all issues resolved, REQUEST_CHANGES only if verified issues remain

⚠️ DO NOT just rewrite your old issues - you MUST check each one against current code!

**If no prior decision:** Review this PR for issues, then create your decision file.

{build_review_checklist()}

{build_decision_file_instructions(task_id, include_inline_comments=True)}
"""


def build_peer_review_prompt(
    task_id: str,
    worktree_base: Path,
    project_name: str,
    is_pr_review: bool = False,
) -> str:
    """Build prompt for peer review of worktree implementations."""
    if is_pr_review:
        # PR reviews use a dedicated worktree synced to origin
        worktree_path = f"{worktree_base}/{project_name}/pr-{task_id}"
        branch_ref = "origin/{branch}"  # Filled in by caller
    else:
        # Writer reviews use writer-specific worktrees
        worktree_path = f"{worktree_base}/{project_name}/writer-{{{{winner}}}}-{task_id}"
        branch_ref = f"writer-{{{{winner}}}}/{task_id}"

    return f"""# Peer Review Context

**You are reviewing the {'PR' if is_pr_review else 'WINNING implementation'}.**

The code is at:
**Worktree:** `{worktree_path}/`
**Branch:** `{branch_ref}`

## Review Scope

Check what was changed since branching from main:
```bash
cd {worktree_path}/
git log --oneline main..HEAD
git diff main...HEAD --stat
```

Use read_file to review the actual code changes.

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
