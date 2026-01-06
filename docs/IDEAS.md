# Agent Cube Ideas

Future feature ideas and enhancements.

---

## 🔥 `cube pr-watch` - Autonomous PR Daemon

Daemon mode that runs continuously and handles the full PR lifecycle automatically.

### Usage

```bash
# Start watching all PRs in current repo
cube pr-watch

# Watch specific PRs only
cube pr-watch --mine          # Only your PRs (fix comments)
cube pr-watch --others        # Only others' PRs (review them)
cube pr-watch --pr 123,456    # Specific PR numbers
```

### What it does

- **New PR opened by others** → Auto-review with `cube pr-review`
- **Comment on your PR** → Auto-fix with `cube auto --fix-comments`
- **PR approved** → Notify you / auto-merge if configured
- **CI fails** → Attempt auto-fix of failing tests

### Implementation Options

1. **Polling**: Check every N minutes via `gh api`
2. **Webhooks**: GitHub App that receives events in real-time
3. **GitHub Actions**: Workflow that triggers on PR events

### Configuration

```yaml
pr_watch:
  poll_interval: 300          # Check every 5 minutes
  auto_review: true           # Review new PRs automatically
  auto_fix: true              # Fix comments on your PRs
  auto_merge: false           # Don't auto-merge (require human)
  notify: slack               # Send notifications
```

Set it up once, let Agent Cube handle the PR dance while you focus on writing code.

---

## `--complement` Mode for Reviews

When using `cube pr-review`, add a `--complement` flag that:
- Reads CodeRabbit's existing review first
- Avoids duplicating style/lint checks CR already caught
- Focuses on architecture, logic, and domain-specific issues
- Adds value rather than noise

---

## Cross-Repo Reviews

```bash
cube pr-review owner/repo#123
```

Review PRs in repos you don't have cloned locally. Fetches context via GitHub API.

---

## Slack/Discord Notifications

Integrate with team chat:
- "PR #123 has been reviewed by Agent Cube"
- "All comments on PR #456 have been addressed"
- "PR #789 is ready to merge (all judges approved)"

---

## Learning Mode

Track which review comments get accepted vs dismissed:
- Build a model of what the team cares about
- Reduce noise over time
- Personalize reviews per-repo or per-team

---

## `cube auto --watch`

Like `pr-watch` but for the full workflow:
- Watch a task file for changes
- Re-run relevant phases when task updates
- Hot-reload development for prompt engineering

