"""Claude Code CLI JSON parser."""

import json
from typing import Optional
from .base import ParserAdapter
from ...models.types import StreamMessage


class ClaudeCodeParser(ParserAdapter):
    """Parser for Claude Code CLI JSON format.
    
    Claude Code output format (stream-json with --verbose):
    - {"type":"system","subtype":"init",...} - Session initialization
    - {"type":"assistant","message":{"content":[{"type":"text","text":"..."}],...}} - Text output
    - {"type":"assistant","message":{"content":[{"type":"tool_use","name":"...","input":{...}}]}} - Tool call
    - {"type":"user","message":{...},"tool_use_result":{...}} - Tool result
    - {"type":"result","subtype":"success","duration_ms":...,"result":"..."} - Completion
    """
    
    def parse(self, line: str) -> Optional[StreamMessage]:
        """Parse Claude Code CLI JSON line."""
        try:
            data = json.loads(line)
            
            if not isinstance(data, dict):
                return None
            
            msg_type = data.get("type")
            
            if msg_type == "system" and data.get("subtype") == "init":
                return StreamMessage(
                    type="system",
                    subtype="init",
                    model=data.get("model"),
                    session_id=data.get("session_id")
                )
            
            if msg_type == "assistant":
                message = data.get("message", {})
                content_list = message.get("content", [])
                
                for content in content_list:
                    content_type = content.get("type")
                    
                    if content_type == "text":
                        text = content.get("text", "")
                        if text:
                            return StreamMessage(
                                type="assistant",
                                content=text
                            )
                    
                    elif content_type == "tool_use":
                        tool_name = content.get("name", "")
                        tool_input = content.get("input", {})
                        
                        display_name = tool_name.lower()
                        display_args = {}
                        
                        if tool_name == "Read":
                            path = tool_input.get("file_path", "")
                            display_args = {"path": path}
                        elif tool_name == "Write":
                            path = tool_input.get("file_path", "")
                            display_args = {"path": path}
                        elif tool_name == "Edit":
                            path = tool_input.get("file_path", "")
                            display_args = {"path": path}
                        elif tool_name == "Bash":
                            cmd = tool_input.get("command", "")
                            display_name = "shell"
                            display_args = {"command": cmd[:100] if cmd else ""}
                        elif tool_name == "Grep":
                            pattern = tool_input.get("pattern", "")
                            display_args = {"pattern": pattern}
                        elif tool_name == "Glob":
                            pattern = tool_input.get("pattern", "")
                            display_args = {"pattern": pattern}
                        elif tool_name == "TodoWrite":
                            display_name = "todos"
                            display_args = {}
                        elif tool_name == "WebSearch":
                            query = tool_input.get("query", "")
                            display_args = {"query": query}
                        elif tool_name == "WebFetch":
                            url = tool_input.get("url", "")
                            display_args = {"url": url[:50] if url else ""}
                        else:
                            display_args = {}
                        
                        return StreamMessage(
                            type="tool_call",
                            subtype="started",
                            tool_name=display_name,
                            tool_args=display_args
                        )
                
                return None
            
            if msg_type == "user":
                tool_result = data.get("tool_use_result")
                if tool_result:
                    return StreamMessage(
                        type="tool_call",
                        subtype="completed",
                        tool_name="completed"
                    )
                return None
            
            if msg_type == "result":
                return StreamMessage(
                    type="result",
                    subtype=data.get("subtype", "success"),
                    duration_ms=data.get("duration_ms", 0),
                    session_id=data.get("session_id")
                )
            
            if msg_type == "error":
                return StreamMessage(
                    type="error",
                    content=data.get("message", data.get("error", line[:200]))
                )
            
            return None
            
        except json.JSONDecodeError:
            line = line.strip()
            if line:
                return StreamMessage(
                    type="system",
                    subtype="log",
                    content=f"[claude-code] {line[:200]}"
                )
            return None
        except (KeyError, TypeError, AttributeError):
            return None
    
    def supports_resume(self) -> bool:
        """Claude Code CLI supports session resume via --resume and --continue."""
        return True
