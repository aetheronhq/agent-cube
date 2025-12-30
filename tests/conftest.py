import os
import sys
import time
import socket
import subprocess
import pytest
import requests
from pathlib import Path

# Add python directory to path so we can import cube modules if needed
sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

def get_free_port():
    """Get a free port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

@pytest.fixture(scope="session")
def mock_home(tmp_path_factory):
    """Create a temporary home directory for the test session."""
    home = tmp_path_factory.mktemp("home")
    (home / ".cube" / "state").mkdir(parents=True)
    (home / ".cube" / "logs").mkdir(parents=True)
    return home

@pytest.fixture(scope="session")
def backend_port():
    return get_free_port()

@pytest.fixture(scope="session")
def frontend_port():
    return get_free_port()

@pytest.fixture(scope="session")
def backend_server(backend_port, mock_home):
    """Start the backend server."""
    # We'll run uvicorn directly
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).parent.parent / "python")
    env["HOME"] = str(mock_home)
    
    proc = subprocess.Popen(
        [
            sys.executable, "-m", "uvicorn",
            "cube.ui.server:app",
            "--host", "127.0.0.1",
            "--port", str(backend_port)
        ],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    start_time = time.time()
    while time.time() - start_time < 10:
        try:
            response = requests.get(f"http://127.0.0.1:{backend_port}/health")
            if response.status_code == 200:
                break
        except requests.ConnectionError:
            time.sleep(0.1)
    else:
        proc.kill()
        _stdout, stderr = proc.communicate()
        raise RuntimeError(f"Backend failed to start:\n{stderr.decode()}")

    yield f"http://127.0.0.1:{backend_port}"
    
    proc.terminate()
    proc.wait()

@pytest.fixture(scope="session")
def frontend_server(frontend_port, backend_port):
    """Start the frontend server."""
    # We need to make sure the frontend knows about the backend port if it's configurable
    # Looking at the code, the frontend might expect 3030 or be hardcoded.
    # If it's hardcoded in the frontend build/code, we might have an issue using dynamic ports
    # without rebuilding or setting ENV vars that Vite picks up.
    
    # Assuming standard Vite proxy setup or env var. 
    # If the frontend calls localhost:3030 explicitly, we might need to mock that or use 3030.
    # For now, let's assume we can control it via VITE_API_URL or similar if the code supports it.
    # If not, we might have to use fixed ports or modify the frontend code to accept an env var.
    
    web_ui_dir = Path(__file__).parent.parent / "web-ui"
    
    if not (web_ui_dir / "node_modules").exists():
        pytest.skip("Skipping frontend tests: web-ui/node_modules missing")

    env = os.environ.copy()
    # Ensure we point to the API base, handling any trailing slashes if needed by frontend logic
    env["VITE_API_BASE_URL"] = f"http://127.0.0.1:{backend_port}/api"
    env["VITE_API_URL"] = f"http://127.0.0.1:{backend_port}/api" # Some parts might use this
    env["PORT"] = str(frontend_port) # Vite typically uses this or --port
    
    # Installing dependencies if needed (might be slow for every test run, best done in CI step)
    # We assume npm install is done.
    
    proc = subprocess.Popen(
        ["npm", "run", "dev", "--", "--port", str(frontend_port), "--strictPort"],
        cwd=web_ui_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for frontend
    base_url = f"http://localhost:{frontend_port}"
    start_time = time.time()
    while time.time() - start_time < 30:
        try:
            requests.get(base_url)
            break
        except requests.ConnectionError:
            time.sleep(0.5)
    else:
        proc.kill()
        _stdout, stderr = proc.communicate() 
        # Don't read all stdout/stderr as it might be huge if it's just hanging
        if stderr:
            print(f"Frontend stderr: {stderr.decode()}")
        raise RuntimeError("Frontend failed to start")

    yield base_url
    
    proc.terminate()
    proc.wait()

