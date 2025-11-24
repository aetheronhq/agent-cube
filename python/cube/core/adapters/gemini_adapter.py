"""Gemini CLI adapter."""

import asyncio
from pathlib import Path
from typing import AsyncGenerator, Optional
import os
import shutil

from ..cli_adapter import CLIAdapter, run_subprocess_streaming

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
            "--no-sandbox"
        ]
        
        if resume and session_id:
            cmd.extend(["--resume", session_id])
        elif resume:
            cmd.extend(["--resume", "latest"])
        
        cmd.extend(["-p", prompt])
        
        worktree.mkdir(parents=True, exist_ok=True)
        
        last_error = None
        line_count = 0
        
        try:
            async for line in run_subprocess_streaming(cmd, worktree, "gemini", env):
                line_count += 1
                
                if "not logged in" in line.lower() or "authentication" in line.lower():
                    last_error = "Authentication required"
                elif line.startswith('{"type":"error"') or line.startswith('Error:'):
                    last_error = line[:200]
                
                yield line
        
        except RuntimeError as e:
            if last_error == "Authentication required":
                raise RuntimeError("gemini CLI not logged in. Run: gemini (choose 'Login with Google')")
            elif last_error:
                raise RuntimeError(f"gemini failed: {last_error}")
            else:
                raise
        
        if line_count == 0:
            raise RuntimeError("gemini CLI produced no output. Run: gemini")
    
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

