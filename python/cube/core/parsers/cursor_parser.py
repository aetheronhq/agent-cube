"""Cursor-agent JSON parser."""

import json
from typing import Optional
from ..parser_adapter import ParserAdapter
from ...models.types import StreamMessage

class CursorParser(ParserAdapter):
    """Parser for cursor-agent JSON format."""
    
    def parse(self, line: str) -> Optional[StreamMessage]:
        """Parse cursor-agent JSON line."""
        try:
            data = json.loads(line)
            
            msg = StreamMessage(
                type=data.get("type"),
                subtype=data.get("subtype"),
                model=data.get("model"),
                session_id=data.get("session_id")
            )
            
            # Handle direct content field (from CLIReviewAdapter and other internal tools)
            if "content" in data:
                msg.content = data["content"]
            
            if msg.type == "system" and msg.subtype == "init":
                return msg
            
            if msg.type == "user":
                message_data = data.get("message", {})
                content_list = message_data.get("content", [])
                if content_list and len(content_list) > 0:
                    text = content_list[0].get("text", "")
                    if text:
                        msg.content = text[:100] + "..." if len(text) > 100 else text
                        return msg
            
            if msg.type == "thinking":
                # Try "text" field first (standard cursor format), then use pre-set content
                text = data.get("text")
                if text:
                    msg.content = text
                    return msg
                # Empty thinking deltas are heartbeats - silently ignore
                return None
            
            if msg.type == "assistant":
                # Skip messages with model_call_id - they're summaries of already-streamed content
                if data.get("model_call_id"):
                    return None
                    
                message_data = data.get("message", {})
                content_list = message_data.get("content", [])
                if content_list and len(content_list) > 0:
                    text = content_list[0].get("text", "")
                    if text and len(text) >= 1:
                        msg.content = text
                        return msg
                # Also check direct content field (from CLIReviewAdapter)
                if msg.content:
                        return msg
            
            if msg.type == "tool_call":
                tool_call = data.get("tool_call", {})
                
                # If no tool_call data, ignore silently
                if not tool_call:
                    return None
                
                if msg.subtype == "started":
                    if "readToolCall" in tool_call:
                        path = tool_call["readToolCall"].get("args", {}).get("path", "unknown")
                        msg.tool_name = "read"
                        msg.tool_args = {"path": path}
                        return msg
                    elif "writeToolCall" in tool_call:
                        path = tool_call["writeToolCall"].get("args", {}).get("path", "unknown")
                        msg.tool_name = "write"
                        msg.tool_args = {"path": path}
                        return msg
                    elif "editToolCall" in tool_call:
                        path = tool_call["editToolCall"].get("args", {}).get("path", "unknown")
                        msg.tool_name = "edit"
                        msg.tool_args = {"path": path}
                        return msg
                    elif "shellToolCall" in tool_call:
                        cmd = tool_call["shellToolCall"].get("args", {}).get("command", "unknown")
                        msg.tool_name = "shell"
                        msg.tool_args = {"command": cmd}
                        return msg
                    elif "grepToolCall" in tool_call:
                        pattern = tool_call["grepToolCall"].get("args", {}).get("pattern", "")
                        msg.tool_name = "grep"
                        msg.tool_args = {"pattern": pattern}
                        return msg
                    elif "lsToolCall" in tool_call:
                        path = tool_call["lsToolCall"].get("args", {}).get("path", ".")
                        msg.tool_name = "ls"
                        msg.tool_args = {"path": path}
                        return msg
                    elif "deleteToolCall" in tool_call:
                        path = tool_call["deleteToolCall"].get("args", {}).get("path", "unknown")
                        msg.tool_name = "delete"
                        msg.tool_args = {"path": path}
                        return msg
                    elif "updateTodosToolCall" in tool_call:
                        todos = tool_call["updateTodosToolCall"].get("args", {}).get("todos", [])
                        msg.tool_name = "todos"
                        msg.tool_args = {"count": len(todos)}
                        return msg
                    else:
                        # Unknown tool type - show generic
                        tool_type = list(tool_call.keys())[0] if tool_call else "unknown"
                        msg.tool_name = tool_type.replace("ToolCall", "")
                        msg.tool_args = {}
                        return msg
                
                elif msg.subtype == "completed":
                    if "readToolCall" in tool_call:
                        result = tool_call["readToolCall"].get("result", {})
                        if "success" in result:
                            msg.tool_name = "read"
                            msg.tool_args = {"lines": result["success"].get("totalLines", 0)}
                            return msg
                    elif "writeToolCall" in tool_call:
                        result = tool_call["writeToolCall"].get("result", {})
                        if "success" in result:
                            msg.tool_name = "write"
                            msg.tool_args = {"lines": result["success"].get("linesCreated", 0)}
                            return msg
                    elif "editToolCall" in tool_call:
                        msg.tool_name = "edit"
                        msg.tool_args = {}
                        return msg
                    elif "shellToolCall" in tool_call:
                        result = tool_call["shellToolCall"].get("result", {})
                        if "success" in result:
                            msg.exit_code = result["success"].get("exitCode", 0)
                        elif "failure" in result:
                            msg.exit_code = result["failure"].get("exitCode", 1)
                        msg.tool_name = "shell"
                        msg.tool_args = {}
                        return msg
                    elif "grepToolCall" in tool_call:
                        msg.tool_name = "grep"
                        msg.tool_args = {}
                        return msg
                    elif "lsToolCall" in tool_call:
                        msg.tool_name = "ls"
                        msg.tool_args = {}
                        return msg
                    elif "deleteToolCall" in tool_call:
                        msg.tool_name = "delete"
                        msg.tool_args = {}
                        return msg
                    elif "updateTodosToolCall" in tool_call:
                        msg.tool_name = "todos"
                        msg.tool_args = {}
                        return msg
                    else:
                        # Unknown tool completion - ignore
                        return None
                
                # Unrecognized subtype - ignore
                return None
            
            if msg.type == "result":
                msg.duration_ms = data.get("duration_ms", 0)
                return msg
            
            if msg.type == "error":
                msg.content = data.get("message", line[:200])
                return msg
            
            # Known types that we intentionally ignore (heartbeats, internal messages)
            if msg.type in ("thinking", "user", "tool_call"):
                return None  # Already handled above if they had content
            
            # Return unknown types so they can be logged
            msg.type = "unknown"
            msg.content = line[:500]
            return msg
            
        except json.JSONDecodeError:
            # Non-JSON line - return as unknown
            msg = StreamMessage(type="unknown", content=line[:500])
            return msg
        except Exception as e:
            msg = StreamMessage(type="error", content=f"Parse error: {e}"[:200])
            return msg
    
    def supports_resume(self) -> bool:
        """Cursor-agent supports resume."""
        return True

