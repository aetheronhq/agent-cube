"""CLI adapter interface (Port) for agent execution."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import AsyncGenerator, Optional
import asyncio

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
    check_interval: float = 5.0
) -> None:
    """Monitor subprocess health and detect if it dies silently.
    
    Uses dual detection for maximum reliability:
    1. process.returncode - Check if process has exited
    2. os.kill(pid, 0) - Verify PID still exists
    
    Args:
        process: Subprocess to monitor
        name: Process name for error messages
        check_interval: How often to check (seconds)
    """
    import os
    
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

async def run_subprocess_streaming(
    cmd: list[str],
    cwd: Path,
    tool_name: str,
    env: Optional[dict] = None
) -> AsyncGenerator[str, None]:
    """Run a subprocess with health monitoring and stream output.
    
    Generic function for all CLI tools (cursor, gemini, coderabbit, etc.)
    
    Args:
        cmd: Command and arguments as list
        cwd: Working directory
        tool_name: Name for error messages
        env: Environment variables (defaults to os.environ.copy())
    
    Yields:
        Lines of output from the subprocess
        
    Raises:
        RuntimeError: If process exits non-zero or dies
    """
    import os
    
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=cwd,
        env=env or os.environ.copy(),
        limit=1024 * 1024 * 10
    )
    
    health_monitor = asyncio.create_task(
        monitor_process_health(process, tool_name, check_interval=5.0)
    )
    
    try:
        if process.stdout:
            async for line in read_stream_with_buffer(process.stdout):
                yield line
    finally:
        health_monitor.cancel()
        try:
            await health_monitor
        except (asyncio.CancelledError, RuntimeError):
            pass
    
    exit_code = await process.wait()
    if exit_code != 0:
        raise RuntimeError(f"{tool_name} exited with code {exit_code}")

