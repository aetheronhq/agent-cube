"""Output formatting and colored terminal output."""

from rich.console import Console
from rich.text import Text
import sys

console = Console()
console_err = Console(stderr=True)

def print_error(message: str) -> None:
    """Print an error message in bold red."""
    console_err.print(f"[bold red]❌ Error: {message}[/bold red]")

def print_success(message: str) -> None:
    """Print a success message in green."""
    console.print(f"[bold green]✅ {message}[/bold green]")

def print_info(message: str) -> None:
    """Print an info message in cyan."""
    console.print(f"[cyan]ℹ️  {message}[/cyan]")

def print_warning(message: str) -> None:
    """Print a warning message in yellow."""
    console.print(f"[bold yellow]⚠️  {message}[/bold yellow]")

def colorize(text: str, color: str) -> str:
    """Colorize text with ANSI color codes."""
    colors = {
        "red": "\033[0;31m",
        "green": "\033[0;32m",
        "yellow": "\033[1;33m",
        "blue": "\033[0;34m",
        "magenta": "\033[0;35m",
        "cyan": "\033[0;36m",
    }
    nc = "\033[0m"
    return f"{colors.get(color, '')}{text}{nc}"

def print_colored(text: str, color: str) -> None:
    """Print colored text."""
    console.print(Text(text, style=color))

def print_header(text: str) -> None:
    """Print a header with separator."""
    console.print()
    console.print("━" * 60)
    console.print(f"[bold]{text}[/bold]")
    console.print("━" * 60)
    console.print()

def truncate_path(path: str, max_length: int = 50) -> str:
    """Truncate a path if it's too long."""
    if len(path) <= max_length:
        return path
    return path[:max_length-3] + "..."

def format_duration(ms: int) -> str:
    """Format duration in milliseconds to human-readable string."""
    if ms < 1000:
        return f"{ms}ms"
    elif ms < 60000:
        return f"{ms // 1000}s"
    else:
        minutes = ms // 60000
        seconds = (ms % 60000) // 1000
        return f"{minutes}m {seconds}s"

