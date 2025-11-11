"""Launch AgentCube web UI."""

import webbrowser
import time
import uvicorn
from threading import Timer


def ui_command(port: int = 3030) -> None:
    """
    Launch the AgentCube web UI.
    
    Args:
        port: Port to run server on (default 3030)
    """
    url = f"http://localhost:{port}"
    
    print(f"🚀 Starting AgentCube UI server on {url}")
    print("📊 Dashboard will open in your browser...")
    print("Press Ctrl+C to stop")
    print()
    
    def open_browser():
        time.sleep(1.5)
        webbrowser.open(url)
    
    Timer(0.1, open_browser).start()
    
    uvicorn.run(
        "cube.ui.server:app",
        host="127.0.0.1",
        port=port,
        log_level="info"
    )
