"""Launch AgentCube web UI server."""

from __future__ import annotations

import logging
import webbrowser

import uvicorn

from cube.core.output import console

logger = logging.getLogger(__name__)


def ui_command(port: int = 3030) -> None:
    """Start the FastAPI UI server and open the dashboard."""
    backend_url = f"http://localhost:{port}"
    frontend_url = "http://localhost:5173"

    console.print(f"[green]🚀 Starting AgentCube UI backend on {backend_url}[/green]")
    console.print(f"[cyan]Frontend should be running on {frontend_url}[/cyan]")
    console.print("[yellow]Start frontend: cd web-ui && npm run dev[/yellow]")
    console.print("[dim]Press Ctrl+C to stop[/dim]")

    try:
        webbrowser.open(frontend_url, new=2, autoraise=True)
    except webbrowser.Error as exc:
        logger.warning("Failed to open browser for %s: %s", frontend_url, exc)

    try:
        uvicorn.run(
            "cube.ui.server:app",
            host="127.0.0.1",
            port=port,
            log_level="info",
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped by user[/yellow]")
