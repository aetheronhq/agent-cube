"""Claude Code CLI JSON parser."""

import json
from typing import Optional

from ...models.types import StreamMessage
from .base import ParserAdapter


class ClaudeParser(ParserAdapter):
    """Parser for Claude Code CLI JSON format.

    Claude uses a similar format to cursor-agent with some differences:
    - system/init has tools, model, session_id
    - stream_event wraps content deltas
    - assistant has message.content with text blocks
    - tool_call has different structure
    - result has duration_ms, session_id, is_error
    """

    def parse(self, line: str) -> Optional[StreamMessage]:
        """Parse Claude CLI JSON line."""
        try:
            data = json.loads(line)

            msg = StreamMessage(
                type=data.get("type"),
                subtype=data.get("subtype"),
                model=data.get("model"),
                session_id=data.get("session_id"),
            )

            if msg.type == "system" and msg.subtype == "init":
                # Extract model from init message
                msg.model = data.get("model", "claude")
                return msg

            # Handle stream_event - extract content deltas
            if msg.type == "stream_event":
                event = data.get("event", {})
                event_type = event.get("type", "")

                # Content delta - streaming text
                if event_type == "content_block_delta":
                    delta = event.get("delta", {})
                    if delta.get("type") == "text_delta":
                        text = delta.get("text", "")
                        if text:
                            # Return as assistant chunk for display
                            msg.type = "assistant_chunk"
                            msg.content = text
                            return msg
                    elif delta.get("type") == "thinking_delta":
                        thinking = delta.get("thinking", "")
                        if thinking:
                            msg.type = "thinking"
                            msg.content = thinking
                            return msg

                # Tool use delta
                if event_type == "content_block_start":
                    content_block = event.get("content_block", {})
                    if content_block.get("type") == "tool_use":
                        msg.type = "tool_call"
                        msg.subtype = "started"
                        tool_name = content_block.get("name", "unknown")
                        # Map tool names
                        tool_map = {
                            "Read": "read",
                            "Write": "write",
                            "Edit": "edit",
                            "Bash": "shell",
                            "Grep": "grep",
                            "Glob": "glob",
                            "WebFetch": "web_fetch",
                            "WebSearch": "web_search",
                        }
                        msg.tool_name = tool_map.get(tool_name, tool_name.lower())
                        msg.tool_args = {}
                        return msg

                # Ignore other stream events
                return None

            if msg.type == "user":
                # User message - extract content
                message_data = data.get("message", {})
                content_list = message_data.get("content", [])
                if content_list:
                    text = (
                        content_list[0].get("text", "") if isinstance(content_list[0], dict) else str(content_list[0])
                    )
                    if text:
                        msg.content = text[:100] + "..." if len(text) > 100 else text
                        return msg

            if msg.type == "assistant":
                # Check for errors first
                if data.get("error"):
                    msg.type = "error"
                    message_data = data.get("message", {})
                    content_list = message_data.get("content", [])
                    if content_list and isinstance(content_list[0], dict):
                        msg.content = content_list[0].get("text", "")[:200]
                    return msg

                # Normal assistant message
                message_data = data.get("message", {})
                content_list = message_data.get("content", [])

                for content_block in content_list:
                    if isinstance(content_block, dict):
                        # Text block
                        if content_block.get("type") == "text":
                            text = content_block.get("text", "")
                            if text and len(text) > 50:
                                msg.content = text
                                return msg
                        # Thinking block
                        elif content_block.get("type") == "thinking":
                            msg.type = "thinking"
                            msg.content = content_block.get("thinking", "")
                            return msg
                        # Tool use block
                        elif content_block.get("type") == "tool_use":
                            msg.type = "tool_call"
                            msg.subtype = "started"
                            tool_name = content_block.get("name", "unknown")
                            tool_input = content_block.get("input", {})

                            # Map common tool names
                            if tool_name in ("Read", "read_file"):
                                msg.tool_name = "read"
                                msg.tool_args = {"path": tool_input.get("path", tool_input.get("file_path", ""))}
                            elif tool_name in ("Write", "write_file"):
                                msg.tool_name = "write"
                                msg.tool_args = {"path": tool_input.get("path", tool_input.get("file_path", ""))}
                            elif tool_name in ("Edit", "edit_file"):
                                msg.tool_name = "edit"
                                msg.tool_args = {"path": tool_input.get("path", tool_input.get("file_path", ""))}
                            elif tool_name in ("Bash", "run_shell_command"):
                                msg.tool_name = "shell"
                                msg.tool_args = {"command": tool_input.get("command", "")}
                            elif tool_name in ("Grep", "grep"):
                                msg.tool_name = "grep"
                                msg.tool_args = {"pattern": tool_input.get("pattern", "")}
                            elif tool_name in ("Glob", "glob"):
                                msg.tool_name = "glob"
                                msg.tool_args = {"pattern": tool_input.get("pattern", "")}
                            elif tool_name == "WebFetch":
                                msg.tool_name = "web_fetch"
                                msg.tool_args = {"url": tool_input.get("url", "")}
                            elif tool_name == "WebSearch":
                                msg.tool_name = "web_search"
                                msg.tool_args = {"query": tool_input.get("query", "")}
                            else:
                                msg.tool_name = tool_name.lower().replace("_", " ")
                                msg.tool_args = tool_input
                            return msg
                        # Tool result
                        elif content_block.get("type") == "tool_result":
                            msg.type = "tool_call"
                            msg.subtype = "completed"
                            # Try to get some info about the result
                            result = content_block.get("content", "")
                            if isinstance(result, list) and result:
                                result = result[0].get("text", "") if isinstance(result[0], dict) else str(result[0])
                            msg.tool_args = {"result": str(result)[:100] if result else ""}
                            return msg

            if msg.type == "result":
                msg.duration_ms = data.get("duration_ms", 0)
                if data.get("is_error"):
                    msg.type = "error"
                    msg.content = data.get("result", "")[:200]
                return msg

            # Unknown type - return as unknown for logging
            if msg.type not in ("system", "user", "assistant", "result"):
                msg.type = "unknown"
                msg.content = line[:500]
                return msg

            return None

        except json.JSONDecodeError:
            # Non-JSON line
            msg = StreamMessage(type="unknown", content=line[:200])
            return msg
        except Exception as e:
            msg = StreamMessage(type="error", content=f"Parse error: {e}"[:200])
            return msg

    def supports_resume(self) -> bool:
        """Claude Code supports resume."""
        return True
