#!/bin/bash
# launch-dual-writers.sh - Launch two writers in parallel for a task
# Usage: ./launch-dual-writers.sh <task-id> <writer-prompt-file>

set -e

export PATH="$HOME/.local/bin:$PATH"

TASK_ID="$1"
PROMPT_FILE="$2"
PROJECT_ROOT="/Users/jacob/dev/aetheron-connect-v2"

if [ -z "$TASK_ID" ] || [ -z "$PROMPT_FILE" ]; then
  echo "Usage: $0 <task-id> <writer-prompt-file>"
  echo "Example: $0 01-api-client-scaffold implementation/phase-01/orchestration/01-api-client-scaffold-writer-prompt.md"
  exit 1
fi

if [ ! -f "$PROJECT_ROOT/$PROMPT_FILE" ]; then
  echo "❌ Prompt file not found: $PROMPT_FILE"
  exit 1
fi

PROMPT=$(cat "$PROJECT_ROOT/$PROMPT_FILE")

echo "🎯 Launching Dual Writers for Task: $TASK_ID"
echo "📄 Prompt: $PROMPT_FILE"
echo ""

# Create worktrees if they don't exist
WORKTREE_SONNET="$HOME/.cursor/worktrees/aetheron-connect-v2/writer-sonnet"
WORKTREE_CODEX="$HOME/.cursor/worktrees/aetheron-connect-v2/writer-codex"

mkdir -p "$HOME/.cursor/worktrees/aetheron-connect-v2"

if [ ! -d "$WORKTREE_SONNET" ]; then
  echo "Creating worktree for Writer A (Sonnet)..."
  cd "$PROJECT_ROOT"
  git branch -D "writer-sonnet/$TASK_ID" 2>/dev/null || true
  git checkout -b "writer-sonnet/$TASK_ID"
  git worktree add "$WORKTREE_SONNET" "writer-sonnet/$TASK_ID"
fi

if [ ! -d "$WORKTREE_CODEX" ]; then
  echo "Creating worktree for Writer B (Codex)..."
  cd "$PROJECT_ROOT"
  git branch -D "writer-codex/$TASK_ID" 2>/dev/null || true
  git checkout -b "writer-codex/$TASK_ID"
  git worktree add "$WORKTREE_CODEX" "writer-codex/$TASK_ID"
fi

# Launch Writer A (Sonnet) - green
(
  cd "$WORKTREE_SONNET"
  cursor-agent --print --force --output-format stream-json --stream-partial-output \
    --model sonnet-4.5-thinking \
    "$PROMPT" 2>&1 | tee "/tmp/writer-sonnet-$TASK_ID-$(date +%s).json" | \
    jq -r --unbuffered '
      if .type == "system" and .subtype == "init" then
        "\u001b[32m[Writer A]\u001b[0m 🤖 \(.model) | Session: \(.session_id)"
      elif .type == "assistant" then
        if (.message.content[0].text // "") != "" and (.message.content[0].text | length) > 50 then
          "\u001b[32m[Writer A]\u001b[0m 💭 \(.message.content[0].text)"
        else empty end
      elif .type == "tool_call" then
        if .subtype == "started" then
          if .tool_call.shellToolCall then "\u001b[32m[Writer A]\u001b[0m 🔧 \(.tool_call.shellToolCall.args.command[:60] // "unknown")"
          elif .tool_call.writeToolCall then "\u001b[32m[Writer A]\u001b[0m 📝 \(.tool_call.writeToolCall.args.path[:60] // "unknown")"
          elif .tool_call.editToolCall then "\u001b[32m[Writer A]\u001b[0m ✏️  \(.tool_call.editToolCall.args.path[:60] // "unknown")"
          elif .tool_call.readToolCall then "\u001b[32m[Writer A]\u001b[0m 📖 \(.tool_call.readToolCall.args.path[:60] // "unknown")"
          else empty end
        elif .subtype == "completed" then
          if .tool_call.shellToolCall.result.success then
            if (.tool_call.shellToolCall.result.success.exitCode // 0) != 0 then
              "\u001b[32m[Writer A]\u001b[0m    ❌ Exit: \(.tool_call.shellToolCall.result.success.exitCode)"
            else empty end
          elif .tool_call.writeToolCall.result.success then "\u001b[32m[Writer A]\u001b[0m    ✅ \(.tool_call.writeToolCall.result.success.linesCreated // 0) lines"
          elif .tool_call.editToolCall.result.success then "\u001b[32m[Writer A]\u001b[0m    ✅ Applied"
          elif .tool_call.readToolCall.result.success then "\u001b[32m[Writer A]\u001b[0m    ✅ \(.tool_call.readToolCall.result.success.totalLines // 0) lines"
          else empty end
        else empty end
      elif .type == "result" then "\u001b[32m[Writer A]\u001b[0m 🎯 Completed in \(.duration_ms // 0)ms"
      else empty end
    '
) &
WRITER_A_PID=$!

# Launch Writer B (Codex) - blue
(
  cd "$WORKTREE_CODEX"
  cursor-agent --print --force --output-format stream-json --stream-partial-output \
    --model gpt-5-codex-high \
    "$PROMPT" 2>&1 | tee "/tmp/writer-codex-$TASK_ID-$(date +%s).json" | \
    jq -r --unbuffered '
      if .type == "system" and .subtype == "init" then
        "\u001b[34m[Writer B]\u001b[0m 🤖 \(.model) | Session: \(.session_id)"
      elif .type == "assistant" then
        if (.message.content[0].text // "") != "" and (.message.content[0].text | length) > 50 then
          "\u001b[34m[Writer B]\u001b[0m 💭 \(.message.content[0].text)"
        else empty end
      elif .type == "tool_call" then
        if .subtype == "started" then
          if .tool_call.shellToolCall then "\u001b[34m[Writer B]\u001b[0m 🔧 \(.tool_call.shellToolCall.args.command[:60] // "unknown")"
          elif .tool_call.writeToolCall then "\u001b[34m[Writer B]\u001b[0m 📝 \(.tool_call.writeToolCall.args.path[:60] // "unknown")"
          elif .tool_call.editToolCall then "\u001b[34m[Writer B]\u001b[0m ✏️  \(.tool_call.editToolCall.args.path[:60] // "unknown")"
          elif .tool_call.readToolCall then "\u001b[34m[Writer B]\u001b[0m 📖 \(.tool_call.readToolCall.args.path[:60] // "unknown")"
          else empty end
        elif .subtype == "completed" then
          if .tool_call.shellToolCall.result.success then
            if (.tool_call.shellToolCall.result.success.exitCode // 0) != 0 then
              "\u001b[34m[Writer B]\u001b[0m    ❌ Exit: \(.tool_call.shellToolCall.result.success.exitCode)"
            else empty end
          elif .tool_call.writeToolCall.result.success then "\u001b[34m[Writer B]\u001b[0m    ✅ \(.tool_call.writeToolCall.result.success.linesCreated // 0) lines"
          elif .tool_call.editToolCall.result.success then "\u001b[34m[Writer B]\u001b[0m    ✅ Applied"
          elif .tool_call.readToolCall.result.success then "\u001b[34m[Writer B]\u001b[0m    ✅ \(.tool_call.readToolCall.result.success.totalLines // 0) lines"
          else empty end
        else empty end
      elif .type == "result" then "\u001b[34m[Writer B]\u001b[0m 🎯 Completed in \(.duration_ms // 0)ms"
      else empty end
    '
) &
WRITER_B_PID=$!

echo "📊 Writer A (Sonnet): PID $WRITER_A_PID"
echo "📊 Writer B (Codex): PID $WRITER_B_PID"
echo ""
echo "⏳ Waiting for both writers to complete..."
echo ""

# Wait for both
wait $WRITER_A_PID
WRITER_A_EXIT=$?
wait $WRITER_B_PID
WRITER_B_EXIT=$?

echo ""
echo "✅ Writer A completed with exit code: $WRITER_A_EXIT"
echo "✅ Writer B completed with exit code: $WRITER_B_EXIT"
echo ""

# Extract session IDs
mkdir -p "$PROJECT_ROOT/.agent-sessions"

WRITER_A_LOG=$(ls -t /tmp/writer-sonnet-$TASK_ID-*.json | head -1)
WRITER_B_LOG=$(ls -t /tmp/writer-codex-$TASK_ID-*.json | head -1)

if [ -f "$WRITER_A_LOG" ]; then
  SESSION_A=$(grep '"session_id"' "$WRITER_A_LOG" | head -1 | jq -r '.session_id // "NOT_FOUND"')
  if [ "$SESSION_A" != "NOT_FOUND" ]; then
    echo "$SESSION_A" > "$PROJECT_ROOT/.agent-sessions/WRITER_A_${TASK_ID}_SESSION_ID.txt"
    echo "# Writer A (Sonnet) - $TASK_ID - $(date)" > "$PROJECT_ROOT/.agent-sessions/WRITER_A_${TASK_ID}_SESSION_ID.txt.meta"
    echo "🔑 Writer A Session ID: $SESSION_A"
  fi
fi

if [ -f "$WRITER_B_LOG" ]; then
  SESSION_B=$(grep '"session_id"' "$WRITER_B_LOG" | head -1 | jq -r '.session_id // "NOT_FOUND"')
  if [ "$SESSION_B" != "NOT_FOUND" ]; then
    echo "$SESSION_B" > "$PROJECT_ROOT/.agent-sessions/WRITER_B_${TASK_ID}_SESSION_ID.txt"
    echo "# Writer B (Codex) - $TASK_ID - $(date)" > "$PROJECT_ROOT/.agent-sessions/WRITER_B_${TASK_ID}_SESSION_ID.txt.meta"
    echo "🔑 Writer B Session ID: $SESSION_B"
  fi
fi

echo ""
echo "🎯 Both writers completed. Session IDs saved to .agent-sessions/"
echo ""
echo "Next steps:"
echo "  1. Review both branches"
echo "  2. Run: ./scripts/automation/launch-judge-panel.sh $TASK_ID <panel-prompt-file>"

