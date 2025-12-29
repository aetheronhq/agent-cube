"""CLI adapter interface (Port) for agent execution."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import AsyncGenerator, Optional, Set
import asyncio
import atexit
import signal

# Track active subprocesses for cleanup on exit
_active_processes: Set[asyncio.subprocess.Process] = set()

def _cleanup_processes():
    """Kill all tracked subprocesses on exit."""
    for proc in list(_active_processes):
        try:
            proc.terminate()
        except Exception:
            pass

atexit.register(_cleanup_processes)

def _signal_handler(signum, frame):
    """Handle SIGINT/SIGTERM by killing child processes."""
    _cleanup_processes()
    raise KeyboardInterrupt()

# Install signal handlers
signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)

class CLIAdapter(ABC):
    """Interface for agent CLI tools."""
    
    @abstractmethod
    async def run(
        self,
        worktree: Path,
        model: str,
        prompt: str,
        session_id: Optional[str] = None,
        resume: bool = False
    ) -> AsyncGenerator[str, None]:
        """Execute the agent and yield JSON output lines."""
        pass
    
    @abstractmethod
    def check_installed(self) -> bool:
        """Check if the CLI tool is installed."""
        pass
    
    @abstractmethod
    def get_install_instructions(self) -> str:
        """Get installation instructions for this CLI."""
        pass

async def read_stream_with_buffer(
    stdout: asyncio.StreamReader,
    buffer_size: int = 8192
) -> AsyncGenerator[str, None]:
    """Helper to read subprocess stdout with buffering."""
    buffer = ""
    while True:
        try:
            chunk = await stdout.read(buffer_size)
            if not chunk:
                break
                
            buffer += chunk.decode('utf-8', errors='replace')
            
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                line = line.strip()
                if line:
                    yield line
        except Exception:
            break
    
    if buffer.strip():
        yield buffer.strip()

async def monitor_process_health(
    process: 'asyncio.subprocess.Process',
    name: str,
    check_interval: float = 5.0,
    last_output_tracker: Optional[list] = None,
    output_timeout: float = 600.0  # 10 minutes
) -> None:
    """Monitor subprocess health and detect if it dies or stalls.
    
    Uses triple detection for maximum reliability:
    1. process.returncode - Check if process has exited
    2. os.kill(pid, 0) - Verify PID still exists
    3. output_timeout - Fail if no output for too long (hung process)
    
    Args:
        process: Subprocess to monitor
        name: Process name for error messages
        check_interval: How often to check (seconds)
        last_output_tracker: Mutable list [timestamp] updated by caller on output
        output_timeout: Fail if no output for this many seconds (default 10 min)
    """
    import os
    import time
    
    while True:
        await asyncio.sleep(check_interval)
        
        if process.returncode is not None:
            if process.returncode != 0:
                raise RuntimeError(f"{name} exited with code {process.returncode}")
            break
        
        try:
            os.kill(process.pid, 0)
        except OSError:
            raise RuntimeError(f"{name} process died (PID {process.pid} gone)")
        
        # Check for output stall (hung process)
        if last_output_tracker and len(last_output_tracker) > 0:
            elapsed = time.time() - last_output_tracker[0]
            if elapsed > output_timeout:
                process.kill()
                raise RuntimeError(f"{name} stalled (no output for {int(elapsed)}s, killed)")

async def run_subprocess_streaming(
    cmd: list[str],
    cwd: Path,
    tool_name: str,
    env: Optional[dict] = None,
    output_timeout: float = 600.0  # 10 minutes
) -> AsyncGenerator[str, None]:
    """Run a subprocess with health monitoring and stream output.
    
    Generic function for all CLI tools (cursor, gemini, coderabbit, etc.)
    
    Args:
        cmd: Command and arguments as list
        cwd: Working directory
        tool_name: Name for error messages
        env: Environment variables (defaults to os.environ.copy())
        output_timeout: Fail if no output for this many seconds (default 10 min)
    
    Yields:
        Lines of output from the subprocess
        
    Raises:
        RuntimeError: If process exits non-zero, dies, or stalls
    """
    import os
    import time
    
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=cwd,
        env=env or os.environ.copy(),
        limit=1024 * 1024 * 10
    )
    
    # Track process for cleanup on Ctrl+C
    _active_processes.add(process)
    
    # Track last output time for stall detection
    last_output_time = [time.time()]  # Mutable list so monitor can read it
    
    health_monitor = asyncio.create_task(
        monitor_process_health(
            process, tool_name, 
            check_interval=5.0,
            last_output_tracker=last_output_time,
            output_timeout=output_timeout
        )
    )
    
    try:
        if process.stdout:
            async for line in read_stream_with_buffer(process.stdout):
                last_output_time[0] = time.time()  # Update on each output
                yield line
    finally:
        health_monitor.cancel()
        try:
            await health_monitor
        except (asyncio.CancelledError, RuntimeError):
            pass
        # Remove from tracking
        _active_processes.discard(process)
        # Ensure process is terminated
        if process.returncode is None:
            try:
                process.terminate()
                await asyncio.wait_for(process.wait(), timeout=2.0)
            except Exception:
                process.kill()
    
    exit_code = await process.wait()
    if exit_code != 0:
        raise RuntimeError(f"{tool_name} exited with code {exit_code}")
