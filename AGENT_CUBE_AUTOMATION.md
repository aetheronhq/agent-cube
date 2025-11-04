# Agent Cube Automation with Cursor CLI

**Date:** 2025-11-01  
**Status:** Production-ready

---

## Overview

This document describes how to automate Agent Cube workflows using `cursor-agent` CLI for headless, parallel agent execution. This enables fully automated dual-writer workflows with real-time progress tracking.

**Related:** See `AGENT_CUBE.md` for the core Agent Cube framework.

---

## ⚡ Quick Start (Recommended)

**Use the `cube` CLI for all orchestration tasks:**

```bash
# Install cube CLI (one-time setup)
bash install.sh  # or see INSTALL.md

# Authenticate cursor-agent
cursor-agent login

# Launch dual writers
cube writers <task-id> <prompt-file>

# Launch judge panel
cube panel <task-id> <panel-prompt-file>

# Send feedback/synthesis
cube feedback <writer> <task-id> <feedback-file>

# Resume a session
cube resume <writer|judge> <task-id> "<message>"

# Check status
cube status <task-id>
cube sessions

# See all commands
cube --help
```

**Everything below this section is for advanced users who want to understand the internals.**

---

## 🔧 Advanced: Direct cursor-agent Usage

> ⚠️ **Note:** Most users should use the `cube` CLI commands above instead of calling scripts directly.

If you need to work with cursor-agent CLI directly:

---

## Critical: The Right Mode for Automation

### ❌ WRONG: `--background` mode
```bash
cursor-agent --background --model sonnet-4.5 "prompt"
```
- Designed for **interactive use** with OS notifications
- Process stays running indefinitely
- No terminal output
- Not suitable for automation

### ✅ CORRECT: `--print` mode
```bash
cursor-agent --print --force --model sonnet-4.5-thinking "prompt"
```
- Designed for **scripting/automation**
- Prints output to console
- Exits when complete (detectable)
- Full tool access with `--force`

### ✅ BEST: Streaming mode with real-time progress
```bash
cursor-agent --print --force \
  --output-format stream-json \
  --stream-partial-output \
  --model sonnet-4.5-thinking \
  "prompt"
```
- Real-time progress tracking
- JSON events for tool calls, completions
- Can be parsed with `jq` for clean display

---

## Essential Flags

| Flag | Purpose | Required? |
|------|---------|-----------|
| `--print` | Enable headless mode with console output | ✅ Yes |
| `--force` | Allow shell commands without approval | ✅ Yes |
| `--model sonnet-4.5-thinking` | Use Claude Sonnet with extended thinking | ✅ Yes |
| `--output-format stream-json` | Enable structured JSON streaming | Recommended |
| `--stream-partial-output` | Stream incremental deltas | Recommended |

---

## Worktrees: Critical for Parallel Agents

**Problem:** Multiple agents in same directory will conflict.

**Solution:** Use git worktrees for isolation.

```bash
# Create worktrees for each writer
git worktree add ~/.cursor/worktrees/aetheron-connect-v2/writer-sonnet writer-sonnet/task-id
git worktree add ~/.cursor/worktrees/aetheron-connect-v2/writer-codex writer-codex/task-id

# Run agents in their own worktrees
cd ~/.cursor/worktrees/aetheron-connect-v2/writer-sonnet
cursor-agent --print --force --model sonnet-4.5-thinking "implement task"

cd ~/.cursor/worktrees/aetheron-connect-v2/writer-codex
cursor-agent --print --force --model sonnet-4.5-thinking "implement task"
```

---

## The Streaming Script

We've created `scripts/automation/stream-agent.sh` for clean, real-time output:

```bash
#!/bin/bash
# stream-agent.sh - Clean real-time agent output

cd "$1" || exit 1
shift

export PATH="$HOME/.local/bin:$PATH"

cursor-agent --print --force --output-format stream-json --stream-partial-output --model sonnet-4.5-thinking "$@" 2>&1 | \
  jq -r --unbuffered '
    if .type == "system" and .subtype == "init" then
      "🤖 Model: \(.model)\n"
    elif .type == "assistant" then
      if (.message.content[0].text // "") != "" and (.message.content[0].text | length) > 50 then
        "💭 \(.message.content[0].text)\n"
      else
        empty
      end
    elif .type == "tool_call" then
      if .subtype == "started" then
        if .tool_call.shellToolCall then
          "🔧 Shell: \(.tool_call.shellToolCall.args.command // "unknown")"
        elif .tool_call.writeToolCall then
          "📝 Write: \(.tool_call.writeToolCall.args.path // "unknown")"
        elif .tool_call.editToolCall then
          "✏️  Edit: \(.tool_call.editToolCall.args.path // "unknown")"
        elif .tool_call.readToolCall then
          "📖 Read: \(.tool_call.readToolCall.args.path // "unknown")"
        else
          "🔧 Tool: \(.tool_call | keys[0])"
        end
      elif .subtype == "completed" then
        if .tool_call.shellToolCall.result.success then
          "   ✅ Exit code: \(.tool_call.shellToolCall.result.success.exitCode // 0)"
        elif .tool_call.writeToolCall.result.success then
          "   ✅ Created \(.tool_call.writeToolCall.result.success.linesCreated // 0) lines"
        elif .tool_call.editToolCall.result.success then
          "   ✅ Applied"
        else
          "   ✅ Done"
        end
      else
        empty
      end
    elif .type == "result" then
      "\n🎯 Completed in \(.duration_ms // 0)ms"
    else
      empty
    end
  '
```

**Usage:**
```bash
chmod +x scripts/automation/stream-agent.sh

./scripts/automation/stream-agent.sh \
  ~/.cursor/worktrees/aetheron-connect-v2/writer-sonnet \
  "Your prompt here"
```

**Output:**
```
🤖 Model: Claude 4.5 Sonnet (Thinking)

💭 I'll implement the API client package scaffold...

📖 Read: packages/api-client/package.json
   ✅ Done
🔧 Shell: pnpm install
   ✅ Exit code: 0
📝 Write: packages/api-client/src/runtime.ts
   ✅ Created 215 lines
🔧 Shell: git commit -m "feat: scaffold API client"
   ✅ Exit code: 0

🎯 Completed in 42500ms
```

---

## Resuming Agents

**Best practice:** When asking a writer to apply synthesis or fixes, **resume their existing chat** instead of creating a new agent.

### Finding the Chat ID

```bash
# List recent chats (interactive)
cursor-agent ls

# Or check logs from the original agent run
# The session_id is in the first JSON line of stream output
```

### Resuming a Writer

```bash
# Resume Writer A's original session
cursor-agent --print --force --model sonnet-4.5-thinking \
  --resume <chat-id> \
  "Apply panel synthesis: $(cat synthesis-instructions.md)"
```

**Why resume?**
- ✅ Agent has context about their original solution
- ✅ More efficient (no need to re-read files)
- ✅ Maintains continuity of the implementation
- ✅ Agent can build on their previous work

**When to create new agent:**
- Panel judges (need fresh perspective)
- Different task entirely
- Original agent session expired

---

## Complete Dual-Writer Workflow

### 1. Create Worktrees
```bash
cd /path/to/your-project

# Create branches and worktrees
git checkout main
git branch writer-sonnet/task-id
git branch writer-codex/task-id

git worktree add ~/.cursor/worktrees/your-project/writer-sonnet writer-sonnet/task-id
git worktree add ~/.cursor/worktrees/your-project/writer-codex writer-codex/task-id
```

### 2. Launch Both Writers in Parallel
```bash
# Setup session tracking directory
mkdir -p .agent-sessions

# Terminal 1: Writer A (Sonnet) - script auto-captures session ID
./scripts/automation/stream-agent.sh \
  ~/.cursor/worktrees/aetheron-connect-v2/writer-sonnet \
  "$(cat implementation/phase-01/orchestration/task-id-writer-prompt.md)"

# Copy session ID from script output (shown at end: "🔑 Session ID: xxx")
echo "<session-id>" > .agent-sessions/WRITER_A_SESSION_ID.txt
echo "# Writer A (Sonnet 4.5) - task-id implementation - $(date)" > .agent-sessions/WRITER_A_SESSION_ID.txt.meta

# Terminal 2: Writer B (Codex) - script auto-captures session ID
./scripts/automation/stream-agent.sh \
  ~/.cursor/worktrees/aetheron-connect-v2/writer-codex \
  "$(cat implementation/phase-01/orchestration/task-id-writer-prompt.md)"

# Copy session ID from script output
echo "<session-id>" > .agent-sessions/WRITER_B_SESSION_ID.txt
echo "# Writer B (Codex High) - task-id implementation - $(date)" > .agent-sessions/WRITER_B_SESSION_ID.txt.meta
```

**Note:** `stream-agent.sh` now automatically:
- Saves raw JSON output to `/tmp/agent-<worktree>-<timestamp>.json`
- Extracts and displays session ID at the end
- Shows resume command for easy copy/paste

### 3. Verify Completion
```bash
# Check both branches are pushed
git fetch origin
git log origin/writer-sonnet/task-id --oneline -1
git log origin/writer-codex/task-id --oneline -1
```

### 4. Ask Agents to Self-Verify
```bash
# Writer A verification
./scripts/automation/stream-agent.sh \
  ~/.cursor/worktrees/aetheron-connect-v2/writer-sonnet \
  "You just completed task-id. Confirm: 1) Everything committed and pushed? 2) Meets all acceptance criteria? 3) Ready for panel review?"

# Writer B verification
./scripts/automation/stream-agent.sh \
  ~/.cursor/worktrees/aetheron-connect-v2/writer-codex \
  "You just completed task-id. Confirm: 1) Everything committed and pushed? 2) Meets all acceptance criteria? 3) Ready for panel review?"
```

### 5. Fix Issues if Found
```bash
# BEST: Resume the original agent's session
WRITER_B_SESSION=$(cat .agent-sessions/WRITER_B_SESSION_ID.txt)
cursor-agent --print --force --model sonnet-4.5-thinking \
  --resume "$WRITER_B_SESSION" \
  "Fix all 27 ESLint errors. Run pnpm lint --fix, then manually fix remaining. Commit and push when done."

# OR: Create new agent (less efficient)
./scripts/automation/stream-agent.sh \
  ~/.cursor/worktrees/aetheron-connect-v2/writer-codex \
  "Fix all 27 ESLint errors. Run pnpm lint --fix, then manually fix remaining. Commit and push when done."
```

### 6. Launch Judge Panel (Capture Session IDs!)
```bash
# Judge 2 (GPT-5 Codex High) - save raw JSON output with session_id
cursor-agent --print --force --output-format stream-json --stream-partial-output \
  --model gpt-5-codex-high \
  "$(cat implementation/phase-01/orchestration/task-id-panel-prompt.md)" \
  2>&1 | tee /tmp/judge-2-review-$(date +%s).json

# Judge 3 (Cursor Composer) - save raw JSON output with session_id
cursor-agent --print --force --output-format stream-json --stream-partial-output \
  --model composer-1 \
  "$(cat implementation/phase-01/orchestration/task-id-panel-prompt.md)" \
  2>&1 | tee /tmp/judge-3-review-$(date +%s).json

# IMMEDIATELY extract and save session IDs from the JSON logs
JUDGE_2_LOG=$(ls -t /tmp/judge-2-review-*.json | head -1)
JUDGE_3_LOG=$(ls -t /tmp/judge-3-review-*.json | head -1)

grep '"session_id"' "$JUDGE_2_LOG" | head -1 | jq -r '.session_id' > .agent-sessions/JUDGE_2_SESSION_ID.txt
grep '"session_id"' "$JUDGE_3_LOG" | head -1 | jq -r '.session_id' > .agent-sessions/JUDGE_3_SESSION_ID.txt

# Add metadata comments for human readability (cursor-agent doesn't support --name)
echo "# Judge 2 (GPT-5 Codex High) - task-id panel review - $(date)" > .agent-sessions/JUDGE_2_SESSION_ID.txt.meta
echo "# Judge 3 (Cursor Composer) - task-id panel review - $(date)" > .agent-sessions/JUDGE_3_SESSION_ID.txt.meta

echo "✅ Judge session IDs saved:"
echo "  Judge 2: $(cat .agent-sessions/JUDGE_2_SESSION_ID.txt)"
echo "  Judge 3: $(cat .agent-sessions/JUDGE_3_SESSION_ID.txt)"
```

**Why capture judge session IDs?**
- ⚠️ **Cursor UI shows "New Agent" with no session ID or title** - There is NO `--name` flag in cursor-agent
- ⚠️ **session_id is ONLY in raw JSON output** - If you filter through jq/prettify, session_id is lost
- 📋 You'll need these IDs to resume judges for peer review after synthesis
- ⏱️ Without IDs, you'll waste time creating new judges who lack context
- 🔍 The UI lists 10+ "New Agent" sessions - impossible to identify which is which without saved session IDs

### 7. Apply Synthesis
```bash
# Resume winning writer with their session ID
WINNER_SESSION=$(cat .agent-sessions/WRITER_A_SESSION_ID.txt)
cursor-agent --print --force --model sonnet-4.5-thinking \
  --resume "$WINNER_SESSION" \
  "$(cat implementation/panel/synthesis-instructions-task-id.md)"
```

### 8. Resume Judges for Peer Review
```bash
# Resume Judge 2 with their original session context
JUDGE_2_SESSION=$(cat .agent-sessions/JUDGE_2_SESSION_ID.txt)
cursor-agent --print --force --model gpt-5-codex-high \
  --resume "$JUDGE_2_SESSION" \
  "$(cat implementation/phase-01/orchestration/task-id-peer-review-prompt.md)" \
  2>&1 | tee /tmp/judge-2-peer-review.log

# Resume Judge 3 with their original session context
JUDGE_3_SESSION=$(cat .agent-sessions/JUDGE_3_SESSION_ID.txt)
cursor-agent --print --force --model composer-1 \
  --resume "$JUDGE_3_SESSION" \
  "$(cat implementation/phase-01/orchestration/task-id-peer-review-prompt.md)" \
  2>&1 | tee /tmp/judge-3-peer-review.log
```

---

## Real-World Example: 01-api-client-scaffold

**What happened:**
1. Created worktrees for both writers
2. Launched agents in parallel with streaming output
3. Writer A completed cleanly
4. Writer B had 27 ESLint errors
5. Used agent to self-verify and fix issues
6. Both pushed successfully

**Commands used:**
```bash
# 1. Create worktrees
git worktree add ~/.cursor/worktrees/aetheron-connect-v2/writer-sonnet writer-sonnet/01-api-client-scaffold
git worktree add ~/.cursor/worktrees/aetheron-connect-v2/writer-codex writer-codex/01-api-client-scaffold

# 2. Launch Writer A (save session ID from first JSON line)
./scripts/automation/stream-agent.sh \
  ~/.cursor/worktrees/aetheron-connect-v2/writer-sonnet \
  "$(cat implementation/phase-01/orchestration/01-api-client-scaffold-writer-prompt.md)" \
  | tee writer-a-output.log
# Extract session_id: 789003f3-8585-40ae-802f-1f4b433e75aa

# 3. Launch Writer B (parallel, save session ID)
./scripts/automation/stream-agent.sh \
  ~/.cursor/worktrees/aetheron-connect-v2/writer-codex \
  "$(cat implementation/phase-01/orchestration/01-api-client-scaffold-writer-prompt.md)" \
  | tee writer-b-output.log
# Extract session_id: abc123...

# 4. Verify both (RESUME their sessions)
cursor-agent --print --force --model sonnet-4.5-thinking \
  --resume 789003f3-8585-40ae-802f-1f4b433e75aa \
  "Review commit a6111af. Ready for panel review?"

cursor-agent --print --force --model sonnet-4.5-thinking \
  --resume <writer-b-session-id> \
  "Review commit 4700e7f. Ready for panel review?"

# 5. Fix issues (RESUME Writer B's session)
cursor-agent --print --force --model sonnet-4.5-thinking \
  --resume <writer-b-session-id> \
  "Fix all 27 ESLint errors, commit, and push"

# 6. Apply synthesis (RESUME Writer A's winning session)
cursor-agent --print --force --model sonnet-4.5-thinking \
  --resume 789003f3-8585-40ae-802f-1f4b433e75aa \
  "$(cat implementation/phase-01/orchestration/01-api-client-scaffold-synthesis-instructions.md)"
```

**Key improvement:** Always capture and reuse session IDs for continuity.

**Results:**
- Writer A: 1 commit, clean implementation, ready
- Writer B: 2 commits (initial + lint fixes), ready
- Total time: ~10 minutes for dual implementation
- Both branches pushed and verified

---

## Troubleshooting

### Agent produces no output
- ✅ Ensure using `--print` mode (not `--background`)
- ✅ Check `cursor-agent status` to verify authentication

### "Shell command issues" error
- ✅ Add `--force` flag to allow shell commands
- ✅ Verify agent is in correct directory (use `cd` in prompt if needed)

### Changes not committed
- ✅ Be explicit: "commit with message X and push to branch Y"
- ✅ Use self-verification prompts to catch incomplete work

### Processes won't exit
- ✅ You're using `--background` mode - switch to `--print`
- ✅ `--background` is for interactive use, not automation

### Agents conflict with each other
- ✅ You're running in same directory - use worktrees
- ✅ Each agent must have its own isolated worktree

---

## Advanced: Panel Automation

**Coming soon:** The same approach can automate panel judges:

```bash
# Judge 1 (Sonnet)
./scripts/automation/stream-agent.sh \
  ~/.cursor/worktrees/aetheron-connect-v2/main \
  "You are Judge 1 (Claude Sonnet 4.5). $(cat panel-prompt.md)"

# Judge 2 (GPT-5)
./scripts/automation/stream-agent.sh \
  ~/.cursor/worktrees/aetheron-connect-v2/main \
  "You are Judge 2 (GPT-5 High Fast). $(cat panel-prompt.md)"

# Judge 3 (Gemini)
./scripts/automation/stream-agent.sh \
  ~/.cursor/worktrees/aetheron-connect-v2/main \
  "You are Judge 3 (Gemini 2.5 Pro). $(cat panel-prompt.md)"
```

---

## 📋 Best Practices for Writer Prompts

When creating prompts for writers, **always** include instructions to commit and push their work:

### Essential Instructions

Add this to every writer prompt:

```markdown
## Final Steps - CRITICAL

After completing all tasks:

1. **Commit your changes:**
   ```bash
   git add -A
   git commit -m "Task: <task-id> - <brief description>
   
   - List of changes
   - Made by Writer <A/B>"
   ```

2. **Push to your branch:**
   ```bash
   git push origin writer-<model>/<task-id>
   ```

3. **Verify push succeeded:**
   ```bash
   git log origin/writer-<model>/<task-id>..HEAD
   # Should show no unpushed commits
   ```

⚠️ **CRITICAL**: The judge panel needs your pushed changes to review!
```

### Automatic Fallback

The `cube writers` command automatically commits and pushes any remaining changes after writers complete. However:

- **Best practice**: Writers should commit and push themselves
- **Reason**: Better commit messages and incremental commits
- **Fallback**: Auto-commit only catches uncommitted work at the end

### Why This Matters

- Judges review from remote branches (via `git fetch`)
- Uncommitted/unpushed changes won't be reviewed
- Auto-commit is a safety net, not the primary strategy

---

## Key Learnings

1. **Always use `sonnet-4.5-thinking`** - Better reasoning, fewer errors
2. **Always use `--print --force`** - Enable automation and shell commands
3. **Always use worktrees** - Prevent conflicts between parallel agents
4. **Always verify completion** - Ask agents to self-verify before panel review
5. **Stream output is essential** - Real-time progress prevents blind waiting
6. **Agents can fix their own issues** - Self-verification and error correction works
7. **Resume agents for continuity** - Use `--resume <chat-id>` when asking same agent to continue work (synthesis, fixes)
8. **Save ALL session IDs** - Capture `session_id` from first JSON line for:
   - **Writers**: Resume for synthesis, fixes, iterations
   - **Judges**: Resume for peer review (after synthesis is complete)
   - Store in files: `.agent-sessions/WRITER_A_SESSION_ID.txt`, `.agent-sessions/JUDGE_2_SESSION_ID.txt`, etc.
   - ⚠️ **CRITICAL**: session_id is ONLY in raw JSON output - use `--output-format stream-json` and `tee` to save before filtering
   - `stream-agent.sh` now auto-saves raw JSON and displays session_id at the end

---

## Performance

**Observed metrics:**
- Writer task completion: 2-5 minutes per agent
- Self-verification: 30-60 seconds
- Fix iteration (e.g., lint errors): 3-6 minutes
- Total dual-writer cycle: ~10 minutes (vs 30+ minutes manual)

**Bottlenecks:**
- Model API latency (largest factor)
- Dependency installation (`pnpm install`)
- Test execution time

---

## Future Improvements

- [ ] Batch verification script for both writers
- [ ] Auto-cleanup of worktrees after merge
- [ ] Panel judge automation
- [ ] Synthesis writer automation
- [ ] Metrics collection and analysis
- [ ] Parallel panel judge execution
- [ ] Git conflict detection and resolution
- [ ] CI integration for automated PR creation

---

## References

- **Cursor CLI Docs:** https://cursor.com/cli
- **Agent Cube Framework:** `AGENT_CUBE.md`
- **Stream Agent Script:** `scripts/automation/stream-agent.sh`
- **Orchestration Guide:** `implementation/automation/orchestrator-automation-guide.md`

