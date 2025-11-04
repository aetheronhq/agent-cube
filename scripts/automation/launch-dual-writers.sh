#!/bin/bash
# launch-dual-writers.sh - Launch two writers in parallel for a task
# Usage: ./launch-dual-writers.sh <task-id> <writer-prompt-file>

set -e

export PATH="$HOME/.local/bin:$PATH"

TASK_ID="$1"
PROMPT_FILE="$2"
PROJECT_ROOT="$(pwd)"
export PROJECT_ROOT

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

# Check if resume mode
if [ "$RESUME_MODE" = "true" ]; then
  echo "🎯 Resuming Dual Writers for Task: $TASK_ID"
  RESUME_A=$(cat "$PROJECT_ROOT/.agent-sessions/WRITER_A_${TASK_ID}_SESSION_ID.txt")
  RESUME_B=$(cat "$PROJECT_ROOT/.agent-sessions/WRITER_B_${TASK_ID}_SESSION_ID.txt")
  echo "📄 Session A: $RESUME_A"
  echo "📄 Session B: $RESUME_B"
else
  echo "🎯 Launching Dual Writers for Task: $TASK_ID"
  RESUME_A=""
  RESUME_B=""
fi
echo "📄 Prompt: $PROMPT_FILE"
echo ""

# Create worktrees with task-id for uniqueness (allows parallel tasks)
PROJECT_NAME=$(basename "$PROJECT_ROOT")
WORKTREE_BASE="$HOME/.cursor/worktrees/$PROJECT_NAME"
WORKTREE_SONNET="$WORKTREE_BASE/writer-sonnet-$TASK_ID"
WORKTREE_CODEX="$WORKTREE_BASE/writer-codex-$TASK_ID"

mkdir -p "$WORKTREE_BASE"

# Ensure main repo is on main branch
cd "$PROJECT_ROOT"
git checkout main 2>/dev/null || git checkout -b main

if [ ! -d "$WORKTREE_SONNET" ]; then
  echo "Creating worktree for Writer A (Sonnet)..."
  cd "$PROJECT_ROOT"
  git branch -D "writer-sonnet/$TASK_ID" 2>/dev/null || true
  # Create worktree with new branch directly (doesn't checkout in main repo)
  git worktree add -b "writer-sonnet/$TASK_ID" "$WORKTREE_SONNET"
fi

if [ ! -d "$WORKTREE_CODEX" ]; then
  echo "Creating worktree for Writer B (Codex)..."
  cd "$PROJECT_ROOT"
  git branch -D "writer-codex/$TASK_ID" 2>/dev/null || true
  # Create worktree with new branch directly (doesn't checkout in main repo)
  git worktree add -b "writer-codex/$TASK_ID" "$WORKTREE_CODEX"
fi

# Launch Writer A (Sonnet) - green
(
  cd "$WORKTREE_SONNET"
  if [ -n "$RESUME_A" ]; then
    cursor-agent --print --force --output-format stream-json --stream-partial-output \
      --model sonnet-4.5-thinking \
      --resume "$RESUME_A" "$PROMPT" 2>&1 | tee "/tmp/writer-sonnet-$TASK_ID-$(date +%s).json"
  else
    cursor-agent --print --force --output-format stream-json --stream-partial-output \
      --model sonnet-4.5-thinking \
      "$PROMPT" 2>&1 | tee "/tmp/writer-sonnet-$TASK_ID-$(date +%s).json"
  fi
) | jq -rR --unbuffered --arg project_root "$PROJECT_ROOT" '
      try (fromjson |
      def truncate_path:
        . as $path |
        if ($path | type) == "string" then
          # Remove worktree paths - match project-name/worktree-name
          if ($path | test("/.cursor/worktrees/[^/]+/[^/]+/")) then
            $path | sub(".*/\\.cursor/worktrees/[^/]+/[^/]+/"; "~worktrees/")
          # Remove PROJECT_ROOT prefix from paths (escape regex special chars)
          else
            ("^" + ($project_root | gsub("[.^$*+?()\\[\\]{}|]"; "\\\\&")) + "/?") as $pattern |
            $path | sub($pattern; "")
          end
        else $path end;
      
      def format_duration:
        . as $ms |
        if $ms < 1000 then "\($ms)ms"
        elif $ms < 60000 then "\(($ms / 1000 | floor))s"
        else "\(($ms / 60000 | floor))m \((($ms % 60000) / 1000 | floor))s"
        end;
      
      if .type == "system" and .subtype == "init" then
        "\u001b[32m[Writer A]\u001b[0m 🤖 \(.model) | Session: \(.session_id)"
      elif .type == "assistant" then
        if (.message.content[0].text // "") != "" and (.message.content[0].text | length) > 50 then
          "\u001b[32m[Writer A]\u001b[0m 💭 \(.message.content[0].text)"
        else empty end
      elif .type == "tool_call" then
        if .subtype == "started" then
          if .tool_call.shellToolCall then 
            ((.tool_call.shellToolCall.args.command // "unknown") | sub("^cd [^ ]+ && "; "") | truncate_path) as $cmd |
            if ($cmd | length) > 60 then "\u001b[32m[Writer A]\u001b[0m 🔧 \($cmd[:57])..."
            else "\u001b[32m[Writer A]\u001b[0m 🔧 \($cmd)" end
          elif .tool_call.writeToolCall then
            ((.tool_call.writeToolCall.args.path // "unknown") | truncate_path) as $p |
            if ($p | length) > 50 then "\u001b[32m[Writer A]\u001b[0m 📝 \($p[:47])..."
            else "\u001b[32m[Writer A]\u001b[0m 📝 \($p)" end
          elif .tool_call.editToolCall then
            ((.tool_call.editToolCall.args.path // "unknown") | truncate_path) as $p |
            if ($p | length) > 50 then "\u001b[32m[Writer A]\u001b[0m ✏️  \($p[:47])..."
            else "\u001b[32m[Writer A]\u001b[0m ✏️  \($p)" end
          elif .tool_call.readToolCall then
            ((.tool_call.readToolCall.args.path // "unknown") | truncate_path) as $p |
            if ($p | length) > 50 then "\u001b[32m[Writer A]\u001b[0m 📖 \($p[:47])..."
            else "\u001b[32m[Writer A]\u001b[0m 📖 \($p)" end
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
      elif .type == "result" then "\u001b[32m[Writer A]\u001b[0m 🎯 Completed in \((.duration_ms // 0) | format_duration)"
      else empty end
      ) catch ("\u001b[32m[Writer A]\u001b[0m ⚠️  Invalid JSON: " + .)
    ' &
WRITER_A_PID=$!

# Launch Writer B (Codex) - blue
(
  cd "$WORKTREE_CODEX"
  if [ -n "$RESUME_B" ]; then
    cursor-agent --print --force --output-format stream-json --stream-partial-output \
      --model gpt-5-codex-high \
      --resume "$RESUME_B" "$PROMPT" 2>&1 | tee "/tmp/writer-codex-$TASK_ID-$(date +%s).json"
  else
    cursor-agent --print --force --output-format stream-json --stream-partial-output \
      --model gpt-5-codex-high \
      "$PROMPT" 2>&1 | tee "/tmp/writer-codex-$TASK_ID-$(date +%s).json"
  fi
) | jq -rR --unbuffered --arg project_root "$PROJECT_ROOT" '
      try (fromjson |
      def truncate_path:
        . as $path |
        if ($path | type) == "string" then
          # Remove worktree paths - match project-name/worktree-name
          if ($path | test("/.cursor/worktrees/[^/]+/[^/]+/")) then
            $path | sub(".*/\\.cursor/worktrees/[^/]+/[^/]+/"; "~worktrees/")
          # Remove PROJECT_ROOT prefix from paths (escape regex special chars)
          else
            ("^" + ($project_root | gsub("[.^$*+?()\\[\\]{}|]"; "\\\\&")) + "/?") as $pattern |
            $path | sub($pattern; "")
          end
        else $path end;
      
      def format_duration:
        . as $ms |
        if $ms < 1000 then "\($ms)ms"
        elif $ms < 60000 then "\(($ms / 1000 | floor))s"
        else "\(($ms / 60000 | floor))m \((($ms % 60000) / 1000 | floor))s"
        end;
      
      if .type == "system" and .subtype == "init" then
        "\u001b[34m[Writer B]\u001b[0m 🤖 \(.model) | Session: \(.session_id)"
      elif .type == "assistant" then
        if (.message.content[0].text // "") != "" and (.message.content[0].text | length) > 50 then
          "\u001b[34m[Writer B]\u001b[0m 💭 \(.message.content[0].text)"
        else empty end
      elif .type == "tool_call" then
        if .subtype == "started" then
          if .tool_call.shellToolCall then 
            ((.tool_call.shellToolCall.args.command // "unknown") | sub("^cd [^ ]+ && "; "") | truncate_path) as $cmd |
            if ($cmd | length) > 60 then "\u001b[34m[Writer B]\u001b[0m 🔧 \($cmd[:57])..."
            else "\u001b[34m[Writer B]\u001b[0m 🔧 \($cmd)" end
          elif .tool_call.writeToolCall then
            ((.tool_call.writeToolCall.args.path // "unknown") | truncate_path) as $p |
            if ($p | length) > 50 then "\u001b[34m[Writer B]\u001b[0m 📝 \($p[:47])..."
            else "\u001b[34m[Writer B]\u001b[0m 📝 \($p)" end
          elif .tool_call.editToolCall then
            ((.tool_call.editToolCall.args.path // "unknown") | truncate_path) as $p |
            if ($p | length) > 50 then "\u001b[34m[Writer B]\u001b[0m ✏️  \($p[:47])..."
            else "\u001b[34m[Writer B]\u001b[0m ✏️  \($p)" end
          elif .tool_call.readToolCall then
            ((.tool_call.readToolCall.args.path // "unknown") | truncate_path) as $p |
            if ($p | length) > 50 then "\u001b[34m[Writer B]\u001b[0m 📖 \($p[:47])..."
            else "\u001b[34m[Writer B]\u001b[0m 📖 \($p)" end
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
      elif .type == "result" then "\u001b[34m[Writer B]\u001b[0m 🎯 Completed in \((.duration_ms // 0) | format_duration)"
      else empty end
      ) catch ("\u001b[34m[Writer B]\u001b[0m ⚠️  Invalid JSON: " + .)
    ' &
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

