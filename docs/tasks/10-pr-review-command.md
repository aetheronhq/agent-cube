# Task 10: PR Review Command

## Overview

Add `cube pr-review [PR_NUMBER]` command to review any GitHub PR and post inline comments.

## Problem

Reviewing PRs is time-consuming. Agent Cube's judge infrastructure already knows how to review code - expose this for reviewing any PR, not just cube-managed ones.

## Solution

New command: `cube pr-review [PR_NUMBER]`

## Workflow

1. **Fetch PR Context**
   - PR title, description, linked issues via `gh api`
   - Full diff (files changed)
   - Existing comments/reviews (to avoid duplicates)
   - Commit messages

2. **Load Repo Context**
   - `planning/` docs for architecture understanding
   - `README.md`, `CONTRIBUTING.md` for conventions
   - Related files for context

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

## CLI Interface

```bash
# Review PR #456
cube pr-review 456

# Review with specific focus
cube pr-review 456 --focus security
cube pr-review 456 --focus performance

# Dry run - show what would be posted
cube pr-review 456 --dry-run

# Use specific model
cube pr-review 456 --model opus
```

## Implementation

### New Files

```
python/cube/commands/pr_review.py   # CLI command
python/cube/github/__init__.py      # GitHub API module
python/cube/github/pulls.py         # Fetch PR data
python/cube/github/reviews.py       # Post reviews
```

### Core Logic

```python
async def pr_review_command(pr_number: int, focus: str | None, dry_run: bool, model: str):
    # 1. Fetch PR data
    pr = fetch_pr(pr_number)  # gh api repos/{owner}/{repo}/pulls/{pr}
    diff = fetch_diff(pr_number)  # gh api ... with Accept: application/vnd.github.diff
    
    # 2. Load repo context
    context = load_repo_context()  # planning/, README, etc.
    
    # 3. Build prompt
    prompt = build_review_prompt(pr, diff, context, focus)
    
    # 4. Run agent to generate review
    review = await run_agent(prompt, model)
    
    # 5. Parse and post
    if dry_run:
        print_review(review)
    else:
        post_review(pr_number, review)
```

### Review Output Format

Agent should output structured JSON:

```json
{
  "decision": "REQUEST_CHANGES",
  "summary": "Overall assessment...",
  "comments": [
    {
      "path": "src/api/routes.py",
      "line": 42,
      "body": "This endpoint lacks authentication",
      "severity": "critical"
    }
  ]
}
```

### Posting Review

```bash
# Create review with inline comments
gh api repos/{owner}/{repo}/pulls/{pr}/reviews \
  -f event="REQUEST_CHANGES" \
  -f body="## 🤖 Agent Cube Review\n\n..." \
  -f comments='[{"path":"...","line":42,"body":"..."}]'
```

## Configuration

```yaml
pr_review:
  sign_reviews: true          # Add Agent Cube signature
  max_comments: 20            # Don't overwhelm
  include_nitpicks: false     # Skip minor style issues
```

## Success Criteria

- [ ] Can fetch PR diff and metadata via gh CLI
- [ ] Loads relevant repo context (planning docs)
- [ ] Agent generates structured review output
- [ ] Posts inline comments on correct lines
- [ ] Submits as proper GitHub review
- [ ] Clearly marked as automated review
- [ ] `--dry-run` shows what would be posted

