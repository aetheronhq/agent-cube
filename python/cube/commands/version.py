"""Version command."""

import typer

from ..core.config import VERSION
from ..core.output import console

def version_command() -> None:
    """Show version information."""
    console.print(f"[cyan]cube-py[/cyan] version [green]{VERSION}[/green]")
    console.print("Agent Cube - Parallel LLM Coding Workflow Orchestrator (Python)")

