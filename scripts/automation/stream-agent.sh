#!/bin/bash
# stream-agent.sh - Clean real-time agent output with session ID capture

WORKTREE_DIR="$1"
cd "$WORKTREE_DIR" || exit 1
shift

export PATH="$HOME/.local/bin:$PATH"

# Generate log file path based on worktree
LOG_FILE="/tmp/agent-$(basename "$WORKTREE_DIR")-$(date +%s).json"

# Save raw JSON to log file AND pipe to jq for pretty output
cursor-agent --print --force --output-format stream-json --stream-partial-output --model sonnet-4.5-thinking "$@" 2>&1 | \
  tee "$LOG_FILE" | \
  jq -r --unbuffered '
    def truncate_path:
      . as $path |
      if ($path | type) == "string" then
        # Remove full path up to and including the repo directory (e.g., "v2/", "agent-cube/", etc.)
        # Match pattern: /path/to/repo-name/ -> keep only what comes after
        $path | sub("^.*/([^/]+-[^/]+|[^/]+v[0-9]+)/"; "")
      else
        $path
      end;
    
    if .type == "system" and .subtype == "init" then
      "🤖 Model: \(.model)\n"
    elif .type == "assistant" then
      # Only show complete messages (non-delta)
      if (.message.content[0].text // "") != "" and (.message.content[0].text | length) > 50 then
        "💭 \(.message.content[0].text)\n"
      else
        empty
      end
    elif .type == "tool_call" then
      if .subtype == "started" then
        if .tool_call.shellToolCall then
          # Strip repo path from command and truncate long commands
          (.tool_call.shellToolCall.args.command // "unknown") as $cmd |
          ($cmd | sub("^cd [^ ]+ && "; "") | truncate_path) as $clean |
          if ($clean | length) > 60 then
            "🔧 \($clean[:57])..."
          else
            "🔧 \($clean)"
          end
        elif .tool_call.writeToolCall then
          (.tool_call.writeToolCall.args.path // "unknown" | truncate_path) as $p |
          if ($p | length) > 50 then
            "📝 \($p[:47])..."
          else
            "📝 \($p)"
          end
        elif .tool_call.editToolCall then
          (.tool_call.editToolCall.args.path // "unknown" | truncate_path) as $p |
          if ($p | length) > 50 then
            "✏️  \($p[:47])..."
          else
            "✏️  \($p)"
          end
        elif .tool_call.readToolCall then
          (.tool_call.readToolCall.args.path // "unknown" | truncate_path) as $p |
          if ($p | length) > 50 then
            "📖 \($p[:47])..."
          else
            "📖 \($p)"
          end
        else
          "🔧 Tool: \(.tool_call | keys[0])"
        end
      elif .subtype == "completed" then
        if .tool_call.shellToolCall.result.success then
          if (.tool_call.shellToolCall.result.success.exitCode // 0) != 0 then
            "   ❌ Exit: \(.tool_call.shellToolCall.result.success.exitCode)"
          else empty end
        elif .tool_call.writeToolCall.result.success then
          "   ✅ \(.tool_call.writeToolCall.result.success.linesCreated // 0) lines"
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

# Extract and display session ID from saved log
echo ""
echo "📝 Raw log saved: $LOG_FILE"
SESSION_ID=$(grep '"session_id"' "$LOG_FILE" | head -1 | jq -r '.session_id // "NOT_FOUND"')
if [ "$SESSION_ID" != "NOT_FOUND" ]; then
  echo "🔑 Session ID: $SESSION_ID"
  echo ""
  echo "To resume this agent:"
  echo "  cursor-agent --print --force --model sonnet-4.5-thinking --resume $SESSION_ID \"<prompt>\""
fi
