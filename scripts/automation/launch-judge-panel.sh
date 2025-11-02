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

echo "🎯 Launching 3-Judge Panel for Task: $TASK_ID"
echo "📄 Prompt: $PROMPT_FILE"
echo "📋 Review Type: $REVIEW_TYPE"
echo ""

# Judge 1 (Sonnet Thinking) - green
(
  cursor-agent --print --force --output-format stream-json --stream-partial-output \
    --model sonnet-4.5-thinking \
    "$(cat $TEMP_PROMPT_1)" 2>&1 | tee "/tmp/judge-1-$TASK_ID-$REVIEW_TYPE-$(date +%s).json" | \
    jq -rR --unbuffered --arg project_root "$PROJECT_ROOT" '
      try (fromjson |
      def truncate_path:
        . as $path |
        if ($path | type) == "string" then
          $path | sub("^\($project_root)/?"; "")
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
    '
) &
JUDGE_1_PID=$!

# Judge 2 (Codex High) - yellow
(
  cursor-agent --print --force --output-format stream-json --stream-partial-output \
    --model gpt-5-codex-high \
    "$(cat $TEMP_PROMPT_2)" 2>&1 | tee "/tmp/judge-2-$TASK_ID-$REVIEW_TYPE-$(date +%s).json" | \
    jq -rR --unbuffered --arg project_root "$PROJECT_ROOT" '
      try (fromjson |
      def truncate_path:
        . as $path |
        if ($path | type) == "string" then
          $path | sub("^\($project_root)/?"; "")
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
    '
) &
JUDGE_2_PID=$!

# Judge 3 (Composer) - magenta
(
  cursor-agent --print --force --output-format stream-json --stream-partial-output \
    --model composer-1 \
    "$(cat $TEMP_PROMPT_3)" 2>&1 | tee "/tmp/judge-3-$TASK_ID-$REVIEW_TYPE-$(date +%s).json" | \
    jq -rR --unbuffered --arg project_root "$PROJECT_ROOT" '
      try (fromjson |
      def truncate_path:
        . as $path |
        if ($path | type) == "string" then
          $path | sub("^\($project_root)/?"; "")
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
    '
) &
JUDGE_3_PID=$!

echo "📊 Judge 1 (Sonnet): PID $JUDGE_1_PID"
echo "📊 Judge 2 (Codex): PID $JUDGE_2_PID"
echo "📊 Judge 3 (Composer): PID $JUDGE_3_PID"
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

for i in 1 2 3; do
  LOG=$(ls -t /tmp/judge-$i-$TASK_ID-$REVIEW_TYPE-*.json 2>/dev/null | head -1)
  if [ -f "$LOG" ]; then
    SESSION=$(grep '"session_id"' "$LOG" | head -1 | jq -r '.session_id // "NOT_FOUND"')
    if [ "$SESSION" != "NOT_FOUND" ]; then
      echo "$SESSION" > "$PROJECT_ROOT/.agent-sessions/JUDGE_${i}_${TASK_ID}_${REVIEW_TYPE}_SESSION_ID.txt"
      echo "# Judge $i - $TASK_ID - $REVIEW_TYPE - $(date)" > "$PROJECT_ROOT/.agent-sessions/JUDGE_${i}_${TASK_ID}_${REVIEW_TYPE}_SESSION_ID.txt.meta"
      echo "🔑 Judge $i Session ID: $SESSION"
    fi
  fi
done

echo ""
echo "🎯 All 3 judges completed. Session IDs saved to .agent-sessions/"

