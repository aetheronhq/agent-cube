"""Launch AgentCube web UI server."""

from __future__ import annotations

import logging
import webbrowser

import uvicorn

from cube.core.output import console

logger = logging.getLogger(__name__)


def ui_command(port: int = 3030) -> None:
    """Start the FastAPI UI server and open the dashboard."""
    url = f"http://localhost:{port}"

    console.print(f"[green]🚀 Starting AgentCube UI server on {url}[/green]")
    console.print("[cyan]Dashboard will open in your browser...[/cyan]")
    console.print("[dim]Press Ctrl+C to stop[/dim]")

    try:
        webbrowser.open(url, new=2, autoraise=True)
    except webbrowser.Error as exc:
        logger.warning("Failed to open browser for %s: %s", url, exc)

    try:
        uvicorn.run(
            "cube.ui.server:app",
            host="127.0.0.1",
            port=port,
            log_level="info",
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped by user[/yellow]")
