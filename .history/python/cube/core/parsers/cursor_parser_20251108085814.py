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
            
            if msg.type == "system" and msg.subtype == "init":
                return msg
            
            if msg.type == "thinking":
                text = data.get("text", "")
                if text:
                    msg.content = text
                    return msg
            
            if msg.type == "assistant":
                message_data = data.get("message", {})
                content_list = message_data.get("content", [])
                if content_list and len(content_list) > 0:
                    text = content_list[0].get("text", "")
                    if text and len(text) > 200:
                        msg.content = text
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
                
                elif msg.subtype == "completed":
                    if "readToolCall" in tool_call:
                        result = tool_call["readToolCall"].get("result", {})
                        if "success" in result:
                            msg.tool_name = "read"
                            msg.tool_args = {"lines": result["success"].get("totalLines", 0)}
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

