"""Gemini CLI adapter."""

import asyncio
from pathlib import Path
from typing import AsyncGenerator, Optional
import os
import shutil

from .base import CLIAdapter, run_subprocess_streaming

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
            "--debug"  # Capture ALL output for timeout heartbeat
        ]
        
        if resume and session_id:
            cmd.extend(["--resume", session_id])
        elif resume:
            cmd.extend(["--resume", "latest"])
        
        cmd.extend(["-p", prompt])
        
        worktree.mkdir(parents=True, exist_ok=True)
        
        last_error = None
        line_count = 0
        json_started = False
        
        from ..master_log import get_master_log
        
        try:
            async for line in run_subprocess_streaming(cmd, worktree, "gemini", env):
                line_count += 1
                
                # Log every line to master log (including debug)
                master_log = get_master_log()
                if master_log:
                    master_log.write_raw_line(f"gemini-{model}", line)
                
                # Check for errors in any output
                if "not logged in" in line.lower() or "authentication" in line.lower():
                    last_error = "Authentication required"
                elif line.startswith('{"type":"error"') or line.startswith('Error:'):
                    last_error = line[:200]
                
                # Yield JSON lines; for non-JSON, yield if it looks meaningful
                if line.startswith('{'):
                    json_started = True
                    yield line
                elif json_started:
                    yield line  # After JSON starts, yield everything
                elif line.strip() and not line.startswith('[debug]'):
                    # Non-JSON preamble - yield so parser can wrap it as log message
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

