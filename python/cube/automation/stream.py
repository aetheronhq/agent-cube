"""Real-time JSON stream parsing from cursor-agent."""

import json
from typing import AsyncGenerator, Optional
import re

from ..core.output import format_duration, truncate_path, colorize
from ..models.types import StreamMessage
from ..core.config import PROJECT_ROOT

def strip_worktree_path(path: str) -> str:
    """Strip worktree path prefix from file paths."""
    if "/.cursor/worktrees/" in path:
        return "~worktrees/" + path.split("/")[-1]
    
    project_root_str = str(PROJECT_ROOT)
    if path.startswith(project_root_str):
        return path[len(project_root_str):].lstrip("/")
    
    return path

def parse_stream_message(line: str) -> Optional[StreamMessage]:
    """Parse a JSON line from cursor-agent stream."""
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
        
        if msg.type == "assistant":
            message_data = data.get("message", {})
            content_list = message_data.get("content", [])
            if content_list and len(content_list) > 0:
                text = content_list[0].get("text", "")
                if text and len(text) > 50:
                    msg.content = text
                    return msg
        
        if msg.type == "tool_call":
            tool_call = data.get("tool_call", {})
            
            if msg.subtype == "started":
                if "shellToolCall" in tool_call:
                    cmd = tool_call["shellToolCall"].get("args", {}).get("command", "unknown")
                    cmd = re.sub(r'^cd [^ ]+ && ', '', cmd)
                    cmd = strip_worktree_path(cmd)
                    msg.tool_name = "shell"
                    msg.tool_args = {"command": cmd}
                    return msg
                
                elif "writeToolCall" in tool_call:
                    path = tool_call["writeToolCall"].get("args", {}).get("path", "unknown")
                    path = strip_worktree_path(path)
                    msg.tool_name = "write"
                    msg.tool_args = {"path": path}
                    return msg
                
                elif "editToolCall" in tool_call:
                    path = tool_call["editToolCall"].get("args", {}).get("path", "unknown")
                    path = strip_worktree_path(path)
                    msg.tool_name = "edit"
                    msg.tool_args = {"path": path}
                    return msg
                
                elif "readToolCall" in tool_call:
                    path = tool_call["readToolCall"].get("args", {}).get("path", "unknown")
                    path = strip_worktree_path(path)
                    msg.tool_name = "read"
                    msg.tool_args = {"path": path}
                    return msg
            
            elif msg.subtype == "completed":
                if "shellToolCall" in tool_call:
                    result = tool_call["shellToolCall"].get("result", {})
                    if "success" in result:
                        msg.exit_code = result["success"].get("exitCode", 0)
                        if msg.exit_code != 0:
                            return msg
                
                elif "writeToolCall" in tool_call:
                    result = tool_call["writeToolCall"].get("result", {})
                    if "success" in result:
                        msg.tool_name = "write"
                        msg.tool_args = {"lines": result["success"].get("linesCreated", 0)}
                        return msg
                
                elif "editToolCall" in tool_call:
                    result = tool_call["editToolCall"].get("result", {})
                    if "success" in result:
                        msg.tool_name = "edit"
                        return msg
                
                elif "readToolCall" in tool_call:
                    result = tool_call["readToolCall"].get("result", {})
                    if "success" in result:
                        msg.tool_name = "read"
                        msg.tool_args = {"lines": result["success"].get("totalLines", 0)}
                        return msg
        
        if msg.type == "result":
            msg.duration_ms = data.get("duration_ms", 0)
            return msg
        
        return None
        
    except json.JSONDecodeError:
        return None
    except Exception:
        return None

def format_stream_message(msg: StreamMessage, prefix: str, color: str) -> Optional[str]:
    """Format a stream message for display."""
    colored_prefix = colorize(f"[{prefix}]", color)
    
    if msg.type == "system" and msg.subtype == "init":
        return f"{colored_prefix} 🤖 {msg.model} | Session: {msg.session_id}"
    
    if msg.type == "assistant" and msg.content:
        return f"{colored_prefix} 💭 {msg.content}"
    
    if msg.type == "tool_call" and msg.subtype == "started":
        if msg.tool_name == "shell" and msg.tool_args:
            cmd = msg.tool_args.get("command", "")
            if len(cmd) > 60:
                cmd = cmd[:57] + "..."
            return f"{colored_prefix} 🔧 {cmd}"
        
        elif msg.tool_name == "write" and msg.tool_args:
            path = msg.tool_args.get("path", "")
            if len(path) > 50:
                path = path[:47] + "..."
            return f"{colored_prefix} 📝 {path}"
        
        elif msg.tool_name == "edit" and msg.tool_args:
            path = msg.tool_args.get("path", "")
            if len(path) > 50:
                path = path[:47] + "..."
            return f"{colored_prefix} ✏️  {path}"
        
        elif msg.tool_name == "read" and msg.tool_args:
            path = msg.tool_args.get("path", "")
            if len(path) > 50:
                path = path[:47] + "..."
            return f"{colored_prefix} 📖 {path}"
    
    if msg.type == "tool_call" and msg.subtype == "completed":
        if msg.exit_code is not None and msg.exit_code != 0:
            return f"{colored_prefix}    ❌ Exit: {msg.exit_code}"
        
        if msg.tool_name == "write" and msg.tool_args:
            lines = msg.tool_args.get("lines", 0)
            return f"{colored_prefix}    ✅ {lines} lines"
        
        if msg.tool_name == "edit":
            return f"{colored_prefix}    ✅ Applied"
        
        if msg.tool_name == "read" and msg.tool_args:
            lines = msg.tool_args.get("lines", 0)
            return f"{colored_prefix}    ✅ {lines} lines"
    
    if msg.type == "result":
        duration = format_duration(msg.duration_ms or 0)
        return f"{colored_prefix} 🎯 Completed in {duration}"
    
    return None

async def parse_and_format_stream(
    stream: AsyncGenerator[str, None],
    prefix: str,
    color: str
) -> AsyncGenerator[tuple[Optional[str], Optional[str]], None]:
    """Parse JSON stream and format for display.
    
    Yields tuples of (formatted_output, session_id).
    """
    session_id = None
    
    async for line in stream:
        msg = parse_stream_message(line)
        if msg:
            if msg.session_id and not session_id:
                session_id = msg.session_id
            
            formatted = format_stream_message(msg, prefix, color)
            if formatted:
                yield (formatted, session_id)

