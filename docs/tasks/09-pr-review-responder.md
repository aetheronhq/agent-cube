# Task 09: PR Commands

## Overview

Add two new PR-related commands:

1. **`cube auto --fix-comments`** - Continue auto workflow by fixing PR review comments
2. **`cube pr-review [PR_NUMBER]`** - Review someone else's PR (add comments, suggestions)

---

## Part A: Fix PR Comments (`cube auto --fix-comments`)

### Problem

After `cube auto` creates a PR, human reviewers and bots leave comments. Currently, developers must:
1. Manually read through all comments
2. Decide which to action
3. Make changes
4. Push commits
5. Reply to or resolve comments

This should be part of the `cube auto` workflow continuation.

### Solution

Extend `cube auto` with `--fix-comments` flag (or auto-detect when resuming a task with an open PR)

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

### CLI Interface

```bash
# Continue auto workflow - fix comments on the task's PR
cube auto my-task --fix-comments

# Or specify PR number directly
cube auto my-task --fix-comments --pr 123

# Auto-resume detects open PR and offers to fix comments
cube auto my-task --resume
# Output: "PR #123 has 5 unresolved comments. Fix them? [Y/n]"

# Only show what would be done (dry run)
cube auto my-task --fix-comments --dry-run

# Fix comments from specific reviewer only
cube auto my-task --fix-comments --from coderabbitai
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

---

## Part B: Review External PRs (`cube pr-review`)

### Problem

Reviewing PRs is time-consuming. Agent Cube's judge infrastructure already knows how to review code - we should expose this for reviewing any PR, not just cube-managed ones.

### Solution

New command: `cube pr-review [PR_NUMBER]`

### Workflow

1. **Fetch PR Context**
   - PR title, description, linked issues
   - Full diff (files changed)
   - Existing comments/reviews (to avoid duplicates)
   - Commit messages

2. **Load Repo Context**
   - `planning/` docs for architecture understanding
   - `README.md`, `CONTRIBUTING.md` for conventions
   - Recent related files for context

3. **Analyze Changes**
   - Security issues
   - Performance concerns
   - Code style / conventions
   - Missing tests
   - Documentation gaps
   - Potential bugs

4. **Generate Review**
   - Inline comments on specific lines
   - General review summary
   - Approve / Request Changes / Comment decision

5. **Submit Review**
   - Post as GitHub review (not individual comments)
   - Mark as "[Agent Cube]" so humans know it's automated

### CLI Interface

```bash
# Review PR #456
cube pr-review 456

# Review with specific focus
cube pr-review 456 --focus security
cube pr-review 456 --focus performance
cube pr-review 456 --focus tests

# Dry run - show what comments would be posted
cube pr-review 456 --dry-run

# Use specific judge model
cube pr-review 456 --model opus

# Review all open PRs (batch mode)
cube pr-review --all

# Review PR from different repo
cube pr-review owner/repo#456
```

### Review Template

```markdown
## 🤖 Agent Cube Review

**Overall**: [APPROVE / REQUEST_CHANGES / COMMENT]

### Summary
{high_level_assessment}

### Issues Found
- 🔴 **Critical**: {blocking_issues}
- 🟡 **Suggestions**: {improvements}
- 🟢 **Nitpicks**: {minor_style_issues}

### Security
{security_analysis}

### Testing
{test_coverage_assessment}

---
*This review was generated by [Agent Cube](https://github.com/aetheronhq/agent-cube). 
Feedback? Reply to this comment.*
```

### New Files

```
python/cube/commands/pr_review.py   # Review command
python/cube/github/pr_context.py    # Fetch PR + repo context  
python/cube/github/reviewer.py      # Generate review comments
python/cube/github/submit.py        # Post review to GitHub
```

### Configuration

```yaml
pr_review:
  auto_approve: false         # Never auto-approve, always REQUEST_CHANGES or COMMENT
  include_nitpicks: true      # Include minor style suggestions
  focus_areas:                # Default focus areas
    - security
    - bugs
    - tests
  sign_reviews: true          # Add Agent Cube signature
  max_comments: 20            # Don't overwhelm with too many comments
```

---

## Success Criteria

### Part A (Fix Comments)
- [ ] Detects open PR for a task automatically
- [ ] Fetches and categorizes all comment types
- [ ] Fixes actionable comments without breaking code
- [ ] Replies professionally to skipped items
- [ ] Resolves threads after fixing
- [ ] Integrates seamlessly with `cube auto --resume`

### Part B (Review PRs)
- [ ] Can review any PR in current repo
- [ ] Loads relevant repo context (planning docs, etc.)
- [ ] Posts inline comments on correct lines
- [ ] Submits as proper GitHub review (not individual comments)
- [ ] Clearly marks as automated review
- [ ] Respects rate limits and max comment settings

## Future Enhancements

### 🔥 Killer Feature: `cube pr-watch`

Daemon mode that runs continuously and handles the full PR lifecycle automatically:

```bash
# Start watching all PRs in current repo
cube pr-watch

# Watch specific PRs only
cube pr-watch --mine          # Only your PRs (fix comments)
cube pr-watch --others        # Only others' PRs (review them)
cube pr-watch --pr 123,456    # Specific PR numbers
```

**What it does:**
- **New PR opened by others** → Auto-review with `pr-review`
- **Comment on your PR** → Auto-fix with `--fix-comments`
- **PR approved** → Notify you / auto-merge if configured
- **CI fails** → Attempt auto-fix of failing tests

**Implementation options:**
1. **Polling**: Check every N minutes via `gh api`
2. **Webhooks**: GitHub App that receives events in real-time
3. **GitHub Actions**: Workflow that triggers on PR events

**Config:**
```yaml
pr_watch:
  poll_interval: 300          # Check every 5 minutes
  auto_review: true           # Review new PRs automatically
  auto_fix: true              # Fix comments on your PRs
  auto_merge: false           # Don't auto-merge (require human approval)
  notify: slack               # Send notifications to Slack
```

Set it up once, let Agent Cube handle the PR dance while you focus on writing code.

---

### Other Ideas

- `--complement` mode for `pr-review` that avoids duplicating CodeRabbit's checks
- Learning from past reviews to improve quality
- Batch mode: `cube auto --fix-comments --all` for all open PRs
- Cross-repo reviews with `cube pr-review owner/repo#123`
- Integration with Slack/Discord for notifications

