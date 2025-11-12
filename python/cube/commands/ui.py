"""Launch AgentCube web UI server."""

from __future__ import annotations

import logging
import subprocess
import webbrowser
import sys
import time
from pathlib import Path

import uvicorn

from cube.core.output import console
from cube.core.config import PROJECT_ROOT

logger = logging.getLogger(__name__)


def ui_command(port: int = 3030) -> None:
    """Start both backend and frontend, open browser."""
    backend_url = f"http://localhost:{port}"
    frontend_url = "http://localhost:5173"
    web_ui_dir = PROJECT_ROOT / "web-ui"
    
    if not web_ui_dir.exists():
        console.print("[red]❌ web-ui directory not found![/red]")
        console.print(f"Expected: {web_ui_dir}")
        sys.exit(1)

    console.print("[green]🚀 Starting AgentCube Web UI[/green]")
    console.print(f"  Backend:  {backend_url}")
    console.print(f"  Frontend: {frontend_url}")
    console.print("[dim]Press Ctrl+C to stop both servers[/dim]")
    console.print()

    # Start frontend in background
    try:
        frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=web_ui_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        console.print("[cyan]✅ Frontend starting...[/cyan]")
        time.sleep(2)  # Give it a moment to start
    except Exception as exc:
        console.print(f"[red]❌ Failed to start frontend: {exc}[/red]")
        sys.exit(1)

    # Open browser
    try:
        webbrowser.open(frontend_url, new=2, autoraise=True)
        console.print("[cyan]✅ Browser opened[/cyan]")
    except webbrowser.Error as exc:
        logger.warning("Failed to open browser: %s", exc)

    console.print("[green]✅ Backend starting...[/green]")
    console.print()

    # Start backend in foreground (blocks until Ctrl+C)
    try:
        uvicorn.run(
            "cube.ui.server:app",
            host="127.0.0.1",
            port=port,
            log_level="info",
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopping servers...[/yellow]")
    finally:
        # Kill frontend when backend stops
        if frontend_process:
            frontend_process.terminate()
            frontend_process.wait(timeout=5)
        console.print("[green]✅ UI stopped[/green]")
