"""Logs command - view agent log files."""

import logging
import typer
from pathlib import Path
from typing import Optional

from ..core.output import print_error, print_info, console

logger = logging.getLogger(__name__)

def logs_command(
    task_id: Optional[str] = None,
    agent: Optional[str] = None,
    tail: int = 50
) -> None:
    """View agent log files.
    
    Examples:
        cube logs                          # List all recent logs
        cube logs 03-sdk-build             # Show logs for task
        cube logs 03-sdk-build writer-a    # Show specific agent
        cube logs 03-sdk-build judge-2 --tail 100
    """
    
    log_dir = Path.home() / ".cube" / "logs"
    
    if not log_dir.exists():
        print_error("No logs directory found")
        console.print(f"Expected: {log_dir}")
        console.print()
        console.print("Logs are created when you run agents")
        return
    
    if task_id:
        pattern = f"*{task_id}*.json"
        if agent:
            agent_slug = agent.lower().replace(" ", "-")
            pattern = f"*{agent_slug}*{task_id}*.json"
        
        logs = sorted(log_dir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
        
        if not logs:
            print_error(f"No logs found for task: {task_id}")
            return
        
        if len(logs) == 1 or agent:
            log_file = logs[0]
            console.print(f"[cyan]📄 {log_file.name}[/cyan]")
            console.print()
            
            with open(log_file) as f:
                lines = f.readlines()
            
            console.print(f"[dim]Showing last {min(tail, len(lines))} lines:[/dim]")
            console.print()
            
            for line in lines[-tail:]:
                try:
                    import json
                    data = json.loads(line)
                    msg_type = data.get("type", "")
                    
                    if msg_type == "thinking":
                        text = data.get("text", "")
                        if text:
                            console.print(f"[dim]💭 {text}[/dim]", end="")
                    elif msg_type == "assistant":
                        msg = data.get("message", {})
                        content = msg.get("content", [])
                        if content:
                            text = content[0].get("text", "")
                            console.print(f"[green]💬 {text}[/green]")
                    elif msg_type == "tool_call":
                        subtype = data.get("subtype", "")
                        if subtype == "started":
                            console.print(f"[yellow]🔧 Tool call started[/yellow]")
                except (json.JSONDecodeError, ValueError, TypeError) as e:
                    # Skip unparseable lines without clogging output, but log to debug
                    logger.debug(f"Failed to parse log line: {e}")
                    pass
        else:
            console.print(f"[cyan]📋 Found {len(logs)} log files for {task_id}:[/cyan]")
            console.print()
            
            for log in logs[:10]:
                size_kb = log.stat().st_size / 1024
                console.print(f"  {log.name:<60} {size_kb:>6.1f} KB")
            
            if len(logs) > 10:
                console.print(f"\n[dim]  ... and {len(logs) - 10} more[/dim]")
            
            console.print()
            console.print("View specific log:")
            console.print(f"  cube logs {task_id} writer-a")
            console.print(f"  cube logs {task_id} judge-1")
    
    else:
        logs = sorted(log_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        
        writer_logs = [l for l in logs if "writer-" in l.name]
        judge_logs = [l for l in logs if "judge-" in l.name]
        
        console.print("[cyan]📋 Recent Agent Logs:[/cyan]")
        console.print()
        
        if writer_logs:
            console.print("[green]Writers:[/green]")
            for log in writer_logs[:5]:
                size_kb = log.stat().st_size / 1024
                console.print(f"  {log.name:<60} {size_kb:>6.1f} KB")
            console.print()
        
        if judge_logs:
            console.print("[yellow]Judges:[/yellow]")
            for log in judge_logs[:5]:
                size_kb = log.stat().st_size / 1024
                console.print(f"  {log.name:<60} {size_kb:>6.1f} KB")
            console.print()
        
        console.print("View logs for specific task:")
        console.print("  cube logs <task-id>")

