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
    
    async def check_authenticated(self) -> bool:
        """Check if the CLI tool is authenticated.
        
        Returns:
            True if authenticated (or authentication not required), False if auth required but missing.
        
        Note:
            Most adapters don't require authentication and should return True.
            Only adapters like CodeRabbit that require explicit auth should override this.
        """
        return True

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

