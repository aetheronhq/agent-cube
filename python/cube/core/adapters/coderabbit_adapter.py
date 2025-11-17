"""CodeRabbit CLI adapter."""

import asyncio
import os
import shutil
from pathlib import Path
from typing import AsyncGenerator, Optional

from ..cli_adapter import CLIAdapter, read_stream_with_buffer


class CodeRabbitAdapter(CLIAdapter):
    """Adapter for running CodeRabbit CLI reviews."""

    async def run(
        self,
        worktree: Path,
        model: str,
        prompt: str,
        session_id: Optional[str] = None,
        resume: bool = False,
    ) -> AsyncGenerator[str, None]:
        """Run CodeRabbit review and yield plain text output lines.

        The CodeRabbit CLI outputs plain text reviews, not JSON. It manages its
        own models, prompts, and sessions, so the related parameters are
        accepted for interface compatibility but ignored.

        Args:
            worktree: Path to the repository being reviewed.
            model: Unused; CodeRabbit controls model selection internally.
            prompt: Unused; CodeRabbit applies its own review criteria.
            session_id: Unused; session resume is not supported.
            resume: Unused flag indicating session resume requests.

        Yields:
            Plain text lines from CodeRabbit CLI review output.

        Raises:
            RuntimeError: If the CodeRabbit CLI exits with a non-zero status.
        """
        env = os.environ.copy()

        cmd = [
            "coderabbit",
            "review",
            "--plain",
            "--type",
            "all",
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=worktree,
            env=env,
            limit=1024 * 1024 * 10,
        )

        last_error: Optional[str] = None
        if process.stdout:
            async for line in read_stream_with_buffer(process.stdout):
                lower_line = line.lower()
                if "not authenticated" in lower_line:
                    last_error = "Not authenticated with CodeRabbit"
                elif "rate limit" in lower_line:
                    last_error = "CodeRabbit rate limit exceeded"
                elif "error" in lower_line and not last_error:
                    last_error = line[:200]
                yield line

        exit_code = await process.wait()
        if exit_code != 0:
            if last_error:
                raise RuntimeError(f"CodeRabbit CLI failed: {last_error}")
            raise RuntimeError(f"CodeRabbit CLI exited with code {exit_code}")

    def check_installed(self) -> bool:
        """Return True if the CodeRabbit CLI is available on PATH."""
        return shutil.which("coderabbit") is not None

    def get_install_instructions(self) -> str:
        """Return installation instructions for the CodeRabbit CLI."""
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

Documentation:
  https://docs.coderabbit.ai/cli"""
    
    async def check_authenticated(self) -> bool:
        """Check if CodeRabbit CLI is authenticated.
        
        Returns:
            True if authenticated, False if authentication required.
        """
        try:
            process = await asyncio.create_subprocess_exec(
                "coderabbit", "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.wait()
            return process.returncode == 0
        except Exception:
            return False
