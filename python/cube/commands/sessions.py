"""Sessions command."""

import typer

from ..core.session import list_sessions
from ..core.output import console, print_info, print_warning

def sessions_command() -> None:
    """List all active sessions."""
    console.print("[cyan]📋 Active Sessions[/cyan]")
    console.print()
    
    sessions = list_sessions()
    
    if not sessions:
        print_warning("No active sessions found")
        return
    
    for name, session_id, metadata in sessions:
        console.print(f"[green]{name}[/green]")
        console.print(f"  Session ID: [cyan]{session_id}[/cyan]")
        if metadata:
            console.print(f"  {metadata}")
        console.print()
    
    console.print(f"[green]✅ Found {len(sessions)} active session(s)[/green]")

