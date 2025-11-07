"""Gemini CLI adapter."""

import asyncio
from pathlib import Path
from typing import AsyncGenerator, Optional
import os
import shutil

from ..cli_adapter import CLIAdapter, read_stream_with_buffer

class GeminiAdapter(CLIAdapter):
    """Adapter for gemini CLI (https://github.com/google-gemini/gemini-cli)."""
    
    async def run(
        self,
        worktree: Path,
        model: str,
        prompt: str,
        session_id: Optional[str] = None,
        resume: bool = False
    ) -> AsyncGenerator[str, None]:
        """Run gemini CLI and yield JSON output lines."""
        
        from ..gemini_config import ensure_trusted_folders
        ensure_trusted_folders()
        
        env = os.environ.copy()
        env["PATH"] = f"{Path.home() / '.local' / 'bin'}:{env.get('PATH', '')}"
        
        cmd = [
            "gemini",
            "-m", model,
            "--output-format", "stream-json",
            "--approval-mode", "yolo",
            "--no-sandbox",
            "-p", prompt
        ]
        
        worktree.mkdir(parents=True, exist_ok=True)
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=worktree,
            env=env,
            limit=1024 * 1024 * 10
        )
        
        if process.stdout:
            async for line in read_stream_with_buffer(process.stdout):
                yield line
        
        exit_code = await process.wait()
        
        if exit_code != 0:
            raise RuntimeError(f"gemini CLI exited with code {exit_code}")
    
    def check_installed(self) -> bool:
        """Check if gemini CLI is installed."""
        return shutil.which("gemini") is not None
    
    def get_install_instructions(self) -> str:
        """Get installation instructions."""
        return """Install gemini CLI:
  npm install -g @google/gemini-cli

After installation, authenticate with:
  gemini
  (Choose: Login with Google)

Documentation: https://github.com/google-gemini/gemini-cli"""

