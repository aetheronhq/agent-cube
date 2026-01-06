# Task 09: PR Review Responder

## Overview

Add a new `cube pr-fix` command that pulls GitHub PR review comments, categorizes them, fixes actionable ones, and responds appropriately to all comments.

## Problem

After a PR is created, human reviewers and bots (CodeRabbit, etc.) leave comments requesting changes. Currently, developers must:
1. Manually read through all comments
2. Decide which to action
3. Make changes
4. Push commits
5. Reply to or resolve comments

This is tedious and could be automated.

## Solution

New command: `cube pr-fix [PR_NUMBER]`

### Workflow

1. **Fetch PR Data**
   - Use `gh api` to pull:
     - PR description and title
     - Review comments (from formal reviews)
     - Issue comments (general discussion)
     - Inline code comments with file/line context
   - Identify comment authors (human vs bot)

2. **Categorize Comments**
   - `ACTIONABLE`: Clear code change requests with specific file/line references
   - `QUESTION`: Clarification requests - may need human input
   - `SUGGESTION`: Optional improvements (nitpicks, style)
   - `RESOLVED`: Already addressed or outdated
   - `SKIP`: Praise, acknowledgments, CI status updates

3. **Generate Fix Plan**
   - For each `ACTIONABLE` comment:
     - Extract file path and line numbers
     - Understand the requested change
     - Determine if change is safe/appropriate
   - Present plan to user (or auto-approve with `--auto` flag)

4. **Execute Fixes**
   - Checkout the PR branch
   - Apply changes using the writer agent
   - Run tests/lints to verify
   - Commit with message referencing addressed comments

5. **Respond to Comments**
   - **Fixed comments**: Reply with "✅ Fixed in [commit]" + resolve thread
   - **Skipped comments**: Reply explaining why (e.g., "This would break X" or "Intentional design choice")
   - **Questions**: Flag for human response

6. **Push & Update**
   - Push new commit(s)
   - Update PR description with summary of changes

## CLI Interface

```bash
# Fix comments on PR #123
cube pr-fix 123

# Auto-approve all safe fixes (no confirmation prompts)
cube pr-fix 123 --auto

# Only show what would be done (dry run)
cube pr-fix 123 --dry-run

# Fix comments from specific reviewer
cube pr-fix 123 --from coderabbitai

# Only fix actionable items, skip replies
cube pr-fix 123 --fixes-only

# Use specific writer model
cube pr-fix 123 --writer opus
```

## Implementation

### New Files

```
python/cube/commands/pr_fix.py      # Main command
python/cube/github/comments.py      # GitHub API for comments
python/cube/github/categorizer.py   # Comment classification
python/cube/github/responder.py     # Reply/resolve logic
```

### GitHub API Endpoints

```bash
# Get PR reviews
gh api repos/{owner}/{repo}/pulls/{pr}/reviews

# Get review comments (inline)
gh api repos/{owner}/{repo}/pulls/{pr}/comments

# Get issue comments (general)
gh api repos/{owner}/{repo}/issues/{pr}/comments

# Reply to review comment
gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies -f body="..."

# Resolve review thread (GraphQL)
gh api graphql -f query='mutation { resolveReviewThread(input: {threadId: "..."}) { ... } }'
```

### Comment Structure

```python
@dataclass
class PRComment:
    id: str
    author: str
    body: str
    path: str | None          # File path for inline comments
    line: int | None          # Line number
    diff_hunk: str | None     # Code context
    in_reply_to: str | None   # Thread parent
    created_at: datetime
    is_bot: bool
    review_id: str | None
    
@dataclass  
class CommentCategory:
    category: Literal["ACTIONABLE", "QUESTION", "SUGGESTION", "RESOLVED", "SKIP"]
    reason: str
    confidence: float         # 0-1 how confident in categorization
    fix_plan: str | None      # For actionable: what to change
```

### Agent Prompt Template

```markdown
# PR Comment Fixer

You are fixing review comments on PR #{pr_number}: {title}

## Comment to Address

Author: {author}
File: {path}:{line}
Comment: {body}

Code Context:
```{language}
{diff_hunk}
```

## Instructions

1. Understand what change is being requested
2. Make the minimal fix that addresses the comment
3. Do not make unrelated changes
4. If the request is unclear or would break functionality, explain why you're not making the change

## Response Format

If fixing:
- Make the code change
- Reply: "✅ Fixed in this commit"

If not fixing:
- Reply with explanation (be polite, acknowledge the feedback)
```

## Edge Cases

- **Outdated comments**: Check if line numbers still valid after other fixes
- **Conflicting comments**: Two reviewers suggest opposite changes
- **Already fixed**: Comment was addressed in a subsequent commit
- **Bot loops**: Don't respond to bot comments about our own bot comments
- **Rate limits**: GitHub API rate limiting for large PRs

## Configuration

Add to `cube.yaml`:

```yaml
pr_fix:
  auto_resolve: true          # Automatically resolve fixed threads
  skip_bots: ["dependabot"]   # Bots to ignore
  require_approval: true      # Require user approval before pushing
  max_comments: 50            # Don't process PRs with too many comments
```

## Success Criteria

- [ ] Can fetch all comment types from a PR
- [ ] Accurately categorizes 90%+ of comments
- [ ] Fixes actionable comments without breaking code
- [ ] Replies are professional and helpful
- [ ] Resolves threads after fixing
- [ ] Handles edge cases gracefully
- [ ] Works with CodeRabbit, GitHub Copilot, and human reviews

## Future Enhancements

- `cube pr-watch`: Continuously monitor PRs and auto-fix as comments come in
- Integration with `cube auto` workflow to auto-fix after peer review
- Learning from past fixes to improve categorization
- Batch mode: `cube pr-fix --all` to process all open PRs

