"""Status command."""

import subprocess
import typer
from pathlib import Path

from ..core.config import PROJECT_ROOT, get_sessions_dir
from ..core.output import console, print_error

def status_command(task_id: str) -> None:
    """Show task status (branches, sessions, worktrees)."""
    console.print(f"[cyan]📊 Task Status: [yellow]{task_id}[/yellow][/cyan]")
    console.print()
    
    console.print("[green]Branches:[/green]")
    try:
        result = subprocess.run(
            ["git", "branch", "-r"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        branches = [line.strip() for line in result.stdout.splitlines() if task_id in line]
        if branches:
            for branch in branches:
                console.print(f"  {branch}")
        else:
            console.print("  No branches found")
    except Exception:
        console.print("  Error listing branches")
    console.print()
    
    console.print("[green]Sessions:[/green]")
    sessions_dir = get_sessions_dir()
    if sessions_dir.exists():
        session_files = list(sessions_dir.glob(f"*{task_id}*SESSION_ID.txt"))
        if session_files:
            for session_file in session_files:
                name = session_file.stem.replace("_SESSION_ID", "")
                console.print(f"  {name}")
        else:
            console.print("  No sessions found")
    else:
        console.print("  No sessions directory")
    console.print()
    
    console.print("[green]Worktrees:[/green]")
    try:
        result = subprocess.run(
            ["git", "worktree", "list"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        worktrees = [line for line in result.stdout.splitlines() if task_id in line]
        if worktrees:
            for worktree in worktrees:
                console.print(f"  {worktree}")
        else:
            console.print("  No worktrees found")
    except Exception:
        console.print("  Error listing worktrees")

