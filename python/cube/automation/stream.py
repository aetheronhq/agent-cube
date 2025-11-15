"""Real-time JSON stream parsing from cursor-agent."""

import json
from typing import AsyncGenerator, Optional
import re

from ..core.output import format_duration, truncate_path, colorize
from ..models.types import StreamMessage
from ..core.config import PROJECT_ROOT

def strip_worktree_path(path: str) -> str:
    """Strip worktree path prefix from file paths, removing writer-sonnet/writer-codex dirs."""
    if "/.cube/worktrees/" in path or "/.cursor/worktrees/" in path:
        parts = path.split("/")
        for i, part in enumerate(parts):
            if part == "worktrees" and i + 2 < len(parts):
                # Skip the writer-sonnet-XX or writer-codex-XX directory entirely
                remaining_path = "/".join(parts[i+3:]) if i + 3 < len(parts) else ""
                if remaining_path:
                    return f"~worktrees/{remaining_path}"
                else:
                    return "~worktrees/"
        return "~worktrees/" + parts[-1]
    
    project_root_str = str(PROJECT_ROOT)
    if path.startswith(project_root_str):
        return path[len(project_root_str):].lstrip("/")
    
    return path

def parse_stream_message(line: str) -> Optional[StreamMessage]:
    """Parse a JSON line from agent stream (cursor-agent or gemini CLI)."""
    try:
        data = json.loads(line)
        
        msg = StreamMessage(
            type=data.get("type"),
            subtype=data.get("subtype"),
            model=data.get("model"),
            session_id=data.get("session_id")
        )
        
        if msg.type == "init":
            return msg
        
        if msg.type == "system" and msg.subtype == "init":
            return msg
        
        if msg.type == "message" and data.get("role") == "assistant":
            content = data.get("content", "")
            if content and len(content) > 50:
                msg.type = "assistant"
                msg.content = content
                return msg
        
        if msg.type == "assistant":
            message_data = data.get("message", {})
            content_list = message_data.get("content", [])
            if content_list and len(content_list) > 0:
                text = content_list[0].get("text", "")
                if text and len(text) > 50:
                    msg.content = text
                    return msg
        
        if msg.type == "tool_use":
            tool_name = data.get("tool_name", "")
            if tool_name:
                msg.type = "tool_call"
                msg.subtype = "started"
                msg.tool_name = tool_name.replace("_", " ")
                msg.tool_args = data.get("parameters", {})
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

def get_max_path_width() -> int:
    """Get maximum path width based on terminal width."""
    import os
    try:
        term_width = os.get_terminal_size().columns
        return max(40, term_width - 30)
    except:
        return 80

def format_stream_message(msg: StreamMessage, prefix: str, color: str) -> Optional[str]:
    """Format a stream message for display.
    
    Note: Returns Rich markup. Prefix should NOT contain markup tags.
    """
    
    if msg.type == "system" and msg.subtype == "init":
        # Escape any square brackets in session_id to prevent Rich markup conflicts
        session_safe = str(msg.session_id).replace("[", "\\[").replace("]", "\\]") if msg.session_id else ""
        return f"[{color}]{prefix}[/{color}] 🤖 {msg.model} | Session: {session_safe}"
    
    if msg.type == "thinking" and msg.content:
        return f"[thinking]{msg.content}[/thinking]"
    
    if msg.type == "assistant" and msg.content:
        if len(msg.content) > 100:
            return f"[{color}]{prefix}[/{color}] 💭 {msg.content}"
        return None
    
    max_width = get_max_path_width()
    
    if msg.type == "tool_call" and msg.subtype == "started":
        if msg.tool_name == "shell" and msg.tool_args:
            cmd = strip_worktree_path(msg.tool_args.get("command", ""))
            if len(cmd) > max_width:
                cmd = cmd[:max_width - 3] + "..."
            return f"[{color}]{prefix}[/{color}] 🔧 {cmd}"
        
        elif msg.tool_name == "write" and msg.tool_args:
            path = strip_worktree_path(msg.tool_args.get("path", ""))
            if len(path) > max_width:
                path = path[:max_width - 3] + "..."
            return f"[{color}]{prefix}[/{color}] 📝 {path}"
        
        elif msg.tool_name == "edit" and msg.tool_args:
            path = strip_worktree_path(msg.tool_args.get("path", ""))
            if len(path) > max_width:
                path = path[:max_width - 3] + "..."
            return f"[{color}]{prefix}[/{color}] ✏️  {path}"
        
        elif msg.tool_name == "read" and msg.tool_args:
            path = strip_worktree_path(msg.tool_args.get("path", ""))
            prefix_len = len(f"{prefix} 📖 ")
            available = max_width - prefix_len
            if len(path) > available:
                path = path[:available - 3] + "..."
            return f"[{color}]{prefix}[/{color}] 📖 {path}"
        
        elif msg.tool_name == "ls" and msg.tool_args:
            path = strip_worktree_path(msg.tool_args.get("path", "."))
            if len(path) > max_width:
                path = path[:max_width - 3] + "..."
            return f"[{color}]{prefix}[/{color}] 📂 ls {path}"
        
        elif msg.tool_name == "todos" and msg.tool_args:
            count = msg.tool_args.get("count", 0)
            return f"[{color}]{prefix}[/{color}] 📋 {count} todos"
    
    if msg.type == "tool_call" and msg.subtype == "completed":
        if msg.exit_code is not None and msg.exit_code != 0:
            return f"[{color}]{prefix}[/{color}]    ❌ Exit: {msg.exit_code}"
        
        if msg.tool_name == "write" and msg.tool_args:
            lines = msg.tool_args.get("lines", 0)
            return f"[{color}]{prefix}[/{color}]    ✅ {lines} lines"
        
        if msg.tool_name == "edit":
            return f"[{color}]{prefix}[/{color}]    ✅ Applied"
        
        if msg.tool_name == "read" and msg.tool_args:
            lines = msg.tool_args.get("lines", 0)
            return f"[{color}]{prefix}[/{color}]    ✅ {lines} lines"
    
    if msg.type == "result":
        duration = format_duration(msg.duration_ms or 0)
        return f"[{color}]{prefix}[/{color}] 🎯 Completed in {duration}"
    
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

