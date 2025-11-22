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
    buffer_size: int = 8192,
    inactivity_timeout: Optional[int] = None
) -> AsyncGenerator[str, None]:
    """Helper to read subprocess stdout with buffering.
    
    Args:
        stdout: StreamReader to read from
        buffer_size: Bytes to read at once
        inactivity_timeout: Seconds of no data before timeout (None = no timeout)
    """
    buffer = ""
    while True:
        try:
            if inactivity_timeout:
                chunk = await asyncio.wait_for(
                    stdout.read(buffer_size),
                    timeout=inactivity_timeout
                )
            else:
                chunk = await stdout.read(buffer_size)
                
            if not chunk:
                break
                
            buffer += chunk.decode('utf-8', errors='replace')
            
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                line = line.strip()
                if line:
                    yield line
        except asyncio.TimeoutError:
            raise RuntimeError(
                f"Process inactive for {inactivity_timeout}s - appears hung or stalled"
            )
        except Exception:
            break
    
    if buffer.strip():
        yield buffer.strip()

