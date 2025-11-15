"""CodeRabbit CLI adapter for Agent Cube judge workflow."""

import asyncio
import os
import shutil
from pathlib import Path
from typing import AsyncGenerator, Optional

from ..cli_adapter import CLIAdapter, read_stream_with_buffer


class CodeRabbitAdapter(CLIAdapter):
    """Adapter for executing CodeRabbit CLI reviews.
    
    This adapter runs the CodeRabbit CLI tool and streams its JSON output.
    It does not parse or interpret the output - that's handled by the parser.
    """
    
    async def run(
        self,
        worktree: Path,
        model: str,
        prompt: str,
        session_id: Optional[str] = None,
        resume: bool = False
    ) -> AsyncGenerator[str, None]:
        """Run CodeRabbit review and yield JSON output lines.
        
        Args:
            worktree: Path to git repository to review
            model: Model name (ignored, CodeRabbit uses its own models)
            prompt: Custom prompt (ignored, CodeRabbit has fixed review criteria)
            session_id: Session ID for resumption (not supported by CodeRabbit)
            resume: Whether to resume previous session (not supported)
        
        Yields:
            JSON-formatted output lines from CodeRabbit CLI
        
        Raises:
            RuntimeError: If CodeRabbit CLI fails or returns non-zero exit code
        """
        env = os.environ.copy()
        
        cmd = [
            "coderabbit",
            "review",
            "--json",
            "--plain",
            "--yes"
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=worktree,
            env=env,
            limit=1024 * 1024 * 10
        )
        
        last_error = None
        if process.stdout:
            async for line in read_stream_with_buffer(process.stdout):
                if "not authenticated" in line.lower():
                    last_error = "Not authenticated with CodeRabbit"
                elif "rate limit" in line.lower():
                    last_error = "CodeRabbit rate limit exceeded"
                elif "error" in line.lower() and not last_error:
                    last_error = line[:200]
                
                yield line
        
        exit_code = await process.wait()
        if exit_code != 0:
            if last_error:
                raise RuntimeError(f"CodeRabbit CLI failed: {last_error}")
            else:
                raise RuntimeError(f"CodeRabbit CLI exited with code {exit_code}")
    
    def check_installed(self) -> bool:
        """Check if CodeRabbit CLI is installed and available in PATH.
        
        Returns:
            True if CodeRabbit CLI is installed, False otherwise
        """
        return shutil.which("coderabbit") is not None
    
    def get_install_instructions(self) -> str:
        """Get CodeRabbit CLI installation instructions.
        
        Returns:
            Multi-line string with platform-specific installation instructions
        """
        return """Install CodeRabbit CLI:

macOS and Linux:
  curl -fsSL https://get.coderabbit.ai/install.sh | sh

Windows (WSL):
  Same as Linux instructions above

Alternative (npm):
  npm install -g @coderabbitai/cli

After installation, authenticate with:
  coderabbit login

Verify installation:
  coderabbit --version

For more information:
  https://docs.coderabbit.ai/cli"""
