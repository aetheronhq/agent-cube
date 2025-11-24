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
            
            if msg.type == "thinking":
                # Try "text" field first (standard cursor format), then use pre-set content
                text = data.get("text")
                if text:
                    msg.content = text
                if msg.content:
                    return msg
            
            if msg.type == "assistant":
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
            
            if msg.type == "result":
                msg.duration_ms = data.get("duration_ms", 0)
                return msg
            
            return None
            
        except (json.JSONDecodeError, Exception):
            return None
    
    def supports_resume(self) -> bool:
        """Cursor-agent supports resume."""
        return True

