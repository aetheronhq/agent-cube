#!/bin/bash
# launch-judge-panel.sh - Launch 3-judge panel for a task
# Usage: ./launch-judge-panel.sh <task-id> <panel-prompt-file> [review-type]

set -e

export PATH="$HOME/.local/bin:$PATH"

TASK_ID="$1"
PROMPT_FILE="$2"
REVIEW_TYPE="${3:-initial}"  # initial or peer-review
PROJECT_ROOT="$(pwd)"
export PROJECT_ROOT

if [ -z "$TASK_ID" ] || [ -z "$PROMPT_FILE" ]; then
  echo "Usage: $0 <task-id> <panel-prompt-file> [review-type]"
  echo "Example: $0 01-api-client-scaffold implementation/phase-01/orchestration/01-api-client-scaffold-panel-prompt.md initial"
  echo "Example: $0 01-api-client-scaffold implementation/phase-01/orchestration/01-api-client-scaffold-peer-review-prompt.md peer-review"
  exit 1
fi

if [ ! -f "$PROJECT_ROOT/$PROMPT_FILE" ]; then
  echo "❌ Prompt file not found: $PROMPT_FILE"
  exit 1
fi

PROMPT_CONTENT=$(cat "$PROJECT_ROOT/$PROMPT_FILE")

# Write prompt to temp files to avoid shell parsing issues with special characters
TEMP_PROMPT_1=$(mktemp)
TEMP_PROMPT_2=$(mktemp)
TEMP_PROMPT_3=$(mktemp)
echo "$PROMPT_CONTENT" > "$TEMP_PROMPT_1"
echo "$PROMPT_CONTENT" > "$TEMP_PROMPT_2"
echo "$PROMPT_CONTENT" > "$TEMP_PROMPT_3"

# Cleanup temp files on exit
trap "rm -f $TEMP_PROMPT_1 $TEMP_PROMPT_2 $TEMP_PROMPT_3" EXIT

# Check if resume mode
if [ "$RESUME_MODE" = "true" ]; then
  echo "🎯 Resuming 3-Judge Panel for Task: $TASK_ID"
  RESUME_1=$(cat "$PROJECT_ROOT/.agent-sessions/JUDGE_1_${TASK_ID}_${REVIEW_TYPE}_SESSION_ID.txt")
  RESUME_2=$(cat "$PROJECT_ROOT/.agent-sessions/JUDGE_2_${TASK_ID}_${REVIEW_TYPE}_SESSION_ID.txt")
  RESUME_3=$(cat "$PROJECT_ROOT/.agent-sessions/JUDGE_3_${TASK_ID}_${REVIEW_TYPE}_SESSION_ID.txt")
  echo "📄 Session 1: $RESUME_1"
  echo "📄 Session 2: $RESUME_2"
  echo "📄 Session 3: $RESUME_3"
else
  echo "🎯 Launching 3-Judge Panel for Task: $TASK_ID"
  RESUME_1=""
  RESUME_2=""
  RESUME_3=""
fi
echo "📄 Prompt: $PROMPT_FILE"
echo "📋 Review Type: $REVIEW_TYPE"
echo ""

# Fetch latest changes from writer branches if they exist
echo "🔄 Fetching latest changes from writer branches..."
git fetch --all --quiet 2>/dev/null || true

# Check which writer branches exist and show their status
if git rev-parse --verify "writer-sonnet/$TASK_ID" >/dev/null 2>&1; then
  SONNET_COMMIT=$(git rev-parse --short "writer-sonnet/$TASK_ID" 2>/dev/null)
  echo "  📍 writer-sonnet/$TASK_ID: $SONNET_COMMIT"
fi

if git rev-parse --verify "writer-codex/$TASK_ID" >/dev/null 2>&1; then
  CODEX_COMMIT=$(git rev-parse --short "writer-codex/$TASK_ID" 2>/dev/null)
  echo "  📍 writer-codex/$TASK_ID: $CODEX_COMMIT"
fi
echo ""

# Create unique log files for each judge BEFORE launching
TIMESTAMP=$(date +%s)
LOG_FILE_1="/tmp/judge-1-$TASK_ID-$REVIEW_TYPE-$TIMESTAMP.json"
LOG_FILE_2="/tmp/judge-2-$TASK_ID-$REVIEW_TYPE-$TIMESTAMP.json"
LOG_FILE_3="/tmp/judge-3-$TASK_ID-$REVIEW_TYPE-$TIMESTAMP.json"

# Pre-create log files to avoid race conditions
touch "$LOG_FILE_1" "$LOG_FILE_2" "$LOG_FILE_3"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚖️  JUDGES: Review both writer implementations"
echo ""
echo "Writer A: ~/.cube/worktrees/\$(basename \$PWD)/writer-sonnet-$TASK_ID/"
echo "Writer B: ~/.cube/worktrees/\$(basename \$PWD)/writer-codex-$TASK_ID/"
echo ""
echo "Use your native tools (read_file, git commands, etc.)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 Starting Judge 1..."

# Judge 1 (Sonnet Thinking) - green
(
  set +e  # Don't exit subshell on errors
  if [ -n "$RESUME_1" ]; then
    cursor-agent --print --force --output-format stream-json --stream-partial-output \
      --model sonnet-4.5-thinking \
      --resume "$RESUME_1" "$(cat $TEMP_PROMPT_1)" 2>&1 | tee "$LOG_FILE_1"
  else
    cursor-agent --print --force --output-format stream-json --stream-partial-output \
      --model sonnet-4.5-thinking \
      "$(cat $TEMP_PROMPT_1)" 2>&1 | tee "$LOG_FILE_1"
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
      
      if .type == "system" and .subtype == "init" then "\u001b[32m[Judge 1]\u001b[0m 🤖 \(.model)"
      elif .type == "assistant" then
        if (.message.content[0].text // "") != "" and (.message.content[0].text | length) > 50 then "\u001b[32m[Judge 1]\u001b[0m 💭 \(.message.content[0].text)"
        else empty end
      elif .type == "tool_call" then
        if .subtype == "started" then
          if .tool_call.shellToolCall then
            ((.tool_call.shellToolCall.args.command // "unknown") | sub("^cd [^ ]+ && "; "") | truncate_path) as $cmd |
            if ($cmd | length) > 60 then "\u001b[32m[Judge 1]\u001b[0m 🔧 \($cmd[:57])..."
            else "\u001b[32m[Judge 1]\u001b[0m 🔧 \($cmd)" end
          elif .tool_call.readToolCall then
            ((.tool_call.readToolCall.args.path // "unknown") | truncate_path) as $p |
            if ($p | length) > 50 then "\u001b[32m[Judge 1]\u001b[0m 📖 \($p[:47])..."
            else "\u001b[32m[Judge 1]\u001b[0m 📖 \($p)" end
          else empty end
        elif .subtype == "completed" then
          if .tool_call.shellToolCall.result.success then
            if (.tool_call.shellToolCall.result.success.exitCode // 0) != 0 then
              "\u001b[32m[Judge 1]\u001b[0m    ❌ Exit: \(.tool_call.shellToolCall.result.success.exitCode)"
            else empty end
          elif .tool_call.readToolCall.result.success then "\u001b[32m[Judge 1]\u001b[0m    ✅ \(.tool_call.readToolCall.result.success.totalLines // 0) lines"
          else empty end
        else empty end
      elif .type == "result" then "\u001b[32m[Judge 1]\u001b[0m 🎯 Completed in \((.duration_ms // 0) | format_duration)"
      else empty end
      ) catch ("\u001b[32m[Judge 1]\u001b[0m ⚠️  Invalid JSON: " + .)
    ' &
JUDGE_1_PID=$!
echo "✅ Judge 1 launched (PID: $JUDGE_1_PID)"
echo "🚀 Starting Judge 2..."

# Judge 2 (Codex High) - yellow
(
  set +e  # Don't exit subshell on errors
  if [ -n "$RESUME_2" ]; then
    cursor-agent --print --force --output-format stream-json --stream-partial-output \
      --model gpt-5-codex-high \
      --resume "$RESUME_2" "$(cat $TEMP_PROMPT_2)" 2>&1 | tee "$LOG_FILE_2"
  else
    cursor-agent --print --force --output-format stream-json --stream-partial-output \
      --model gpt-5-codex-high \
      "$(cat $TEMP_PROMPT_2)" 2>&1 | tee "$LOG_FILE_2"
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
      
      if .type == "system" and .subtype == "init" then "\u001b[33m[Judge 2]\u001b[0m 🤖 \(.model)"
      elif .type == "assistant" then
        if (.message.content[0].text // "") != "" and (.message.content[0].text | length) > 50 then "\u001b[33m[Judge 2]\u001b[0m 💭 \(.message.content[0].text)"
        else empty end
      elif .type == "tool_call" then
        if .subtype == "started" then
          if .tool_call.shellToolCall then
            ((.tool_call.shellToolCall.args.command // "unknown") | sub("^cd [^ ]+ && "; "") | truncate_path) as $cmd |
            if ($cmd | length) > 60 then "\u001b[33m[Judge 2]\u001b[0m 🔧 \($cmd[:57])..."
            else "\u001b[33m[Judge 2]\u001b[0m 🔧 \($cmd)" end
          elif .tool_call.readToolCall then
            ((.tool_call.readToolCall.args.path // "unknown") | truncate_path) as $p |
            if ($p | length) > 50 then "\u001b[33m[Judge 2]\u001b[0m 📖 \($p[:47])..."
            else "\u001b[33m[Judge 2]\u001b[0m 📖 \($p)" end
          else empty end
        elif .subtype == "completed" then
          if .tool_call.shellToolCall.result.success then
            if (.tool_call.shellToolCall.result.success.exitCode // 0) != 0 then
              "\u001b[33m[Judge 2]\u001b[0m    ❌ Exit: \(.tool_call.shellToolCall.result.success.exitCode)"
            else empty end
          elif .tool_call.readToolCall.result.success then "\u001b[33m[Judge 2]\u001b[0m    ✅ \(.tool_call.readToolCall.result.success.totalLines // 0) lines"
          else empty end
        else empty end
      elif .type == "result" then "\u001b[33m[Judge 2]\u001b[0m 🎯 Completed in \((.duration_ms // 0) | format_duration)"
      else empty end
      ) catch ("\u001b[33m[Judge 2]\u001b[0m ⚠️  Invalid JSON: " + .)
    ' &
JUDGE_2_PID=$!
echo "✅ Judge 2 launched (PID: $JUDGE_2_PID)"
echo "🚀 Starting Judge 3..."

# Judge 3 (Grok) - magenta
(
  set +e  # Don't exit subshell on errors
  if [ -n "$RESUME_3" ]; then
    cursor-agent --print --force --output-format stream-json --stream-partial-output \
      --model grok \
      --resume "$RESUME_3" "$(cat $TEMP_PROMPT_3)" 2>&1 | tee "$LOG_FILE_3"
  else
    cursor-agent --print --force --output-format stream-json --stream-partial-output \
      --model grok \
      "$(cat $TEMP_PROMPT_3)" 2>&1 | tee "$LOG_FILE_3"
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
      
      if .type == "system" and .subtype == "init" then "\u001b[35m[Judge 3]\u001b[0m 🤖 \(.model)"
      elif .type == "assistant" then
        if (.message.content[0].text // "") != "" and (.message.content[0].text | length) > 50 then "\u001b[35m[Judge 3]\u001b[0m 💭 \(.message.content[0].text)"
        else empty end
      elif .type == "tool_call" then
        if .subtype == "started" then
          if .tool_call.shellToolCall then
            ((.tool_call.shellToolCall.args.command // "unknown") | sub("^cd [^ ]+ && "; "") | truncate_path) as $cmd |
            if ($cmd | length) > 60 then "\u001b[35m[Judge 3]\u001b[0m 🔧 \($cmd[:57])..."
            else "\u001b[35m[Judge 3]\u001b[0m 🔧 \($cmd)" end
          elif .tool_call.readToolCall then
            ((.tool_call.readToolCall.args.path // "unknown") | truncate_path) as $p |
            if ($p | length) > 50 then "\u001b[35m[Judge 3]\u001b[0m 📖 \($p[:47])..."
            else "\u001b[35m[Judge 3]\u001b[0m 📖 \($p)" end
          else empty end
        elif .subtype == "completed" then
          if .tool_call.shellToolCall.result.success then
            if (.tool_call.shellToolCall.result.success.exitCode // 0) != 0 then
              "\u001b[35m[Judge 3]\u001b[0m    ❌ Exit: \(.tool_call.shellToolCall.result.success.exitCode)"
            else empty end
          elif .tool_call.readToolCall.result.success then "\u001b[35m[Judge 3]\u001b[0m    ✅ \(.tool_call.readToolCall.result.success.totalLines // 0) lines"
          else empty end
        else empty end
      elif .type == "result" then "\u001b[35m[Judge 3]\u001b[0m 🎯 Completed in \((.duration_ms // 0) | format_duration)"
      else empty end
      ) catch ("\u001b[35m[Judge 3]\u001b[0m ⚠️  Invalid JSON: " + .)
    ' &
JUDGE_3_PID=$!
echo "✅ Judge 3 launched (PID: $JUDGE_3_PID)"
echo ""
echo "📊 All judges launched successfully!"
echo "📊 Judge 1 (Sonnet): PID $JUDGE_1_PID"
echo "📊 Judge 2 (Codex): PID $JUDGE_2_PID"
echo "📊 Judge 3 (Grok): PID $JUDGE_3_PID"
echo ""

# Verify judges are running
sleep 2
FAILED=0
JUDGE_PIDS=($JUDGE_1_PID $JUDGE_2_PID $JUDGE_3_PID)
JUDGE_NAMES=("Judge 1 (Sonnet)" "Judge 2 (Codex)" "Judge 3 (Grok)")

for i in 0 1 2; do
  pid=${JUDGE_PIDS[$i]}
  name="${JUDGE_NAMES[$i]}"
  if ! kill -0 $pid 2>/dev/null; then
    echo "⚠️  WARNING: $name (PID $pid) failed to start or crashed immediately!"
    FAILED=1
  else
    echo "✅ $name (PID $pid) is running"
  fi
done

if [ $FAILED -eq 1 ]; then
  echo ""
  echo "🔍 Debug: Log file sizes..."
  ls -lh /tmp/judge-*-$TASK_ID-$REVIEW_TYPE-*.json 2>/dev/null | tail -10
  echo ""
  echo "💡 Tip: Check /tmp/judge-*.json files for error messages"
fi
echo ""

echo "⏳ Waiting for all 3 judges to complete..."
echo ""

# Wait for all
wait $JUDGE_1_PID; JUDGE_1_EXIT=$?
wait $JUDGE_2_PID; JUDGE_2_EXIT=$?
wait $JUDGE_3_PID; JUDGE_3_EXIT=$?

echo ""
echo "✅ Judge 1 completed with exit code: $JUDGE_1_EXIT"
echo "✅ Judge 2 completed with exit code: $JUDGE_2_EXIT"
echo "✅ Judge 3 completed with exit code: $JUDGE_3_EXIT"
echo ""

# Extract session IDs
mkdir -p "$PROJECT_ROOT/.agent-sessions"

# Use the known log files instead of searching
for i in 1 2 3; do
  case $i in
    1) LOG="$LOG_FILE_1" ;;
    2) LOG="$LOG_FILE_2" ;;
    3) LOG="$LOG_FILE_3" ;;
  esac
  
  if [ -f "$LOG" ]; then
    LOG_SIZE=$(stat -f%z "$LOG" 2>/dev/null || stat -c%s "$LOG" 2>/dev/null)
    if [ "$LOG_SIZE" -eq 0 ]; then
      echo "🔑 Judge $i Session ID: (empty log - process may have failed or timed out)"
      echo "   💡 Check: $LOG"
    else
      SESSION=$(grep '"session_id"' "$LOG" | head -1 | jq -r '.session_id // "NOT_FOUND"')
      if [ "$SESSION" != "NOT_FOUND" ]; then
        echo "$SESSION" > "$PROJECT_ROOT/.agent-sessions/JUDGE_${i}_${TASK_ID}_${REVIEW_TYPE}_SESSION_ID.txt"
        echo "# Judge $i - $TASK_ID - $REVIEW_TYPE - $(date)" > "$PROJECT_ROOT/.agent-sessions/JUDGE_${i}_${TASK_ID}_${REVIEW_TYPE}_SESSION_ID.txt.meta"
        echo "🔑 Judge $i Session ID: $SESSION"
      else
        echo "🔑 Judge $i Session ID: (not found in log)"
        echo "   💡 Check: $LOG"
      fi
    fi
  else
    echo "🔑 Judge $i Session ID: (log file missing: $LOG)"
  fi
done

echo ""
echo "🎯 All 3 judges completed. Session IDs saved to .agent-sessions/"

