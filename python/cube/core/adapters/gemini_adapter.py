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
        
        last_error = None
        line_count = 0
        first_line_timeout = 30
        
        if process.stdout:
            stream_iter = read_stream_with_buffer(process.stdout)
            
            try:
                first_line = await asyncio.wait_for(
                    anext(stream_iter),
                    timeout=first_line_timeout
                )
                line_count += 1
                
                if "not logged in" in first_line.lower() or "authentication" in first_line.lower():
                    last_error = "Authentication required"
                elif "error" in first_line.lower():
                    last_error = first_line[:200]
                
                yield first_line
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise RuntimeError(
                    "gemini CLI timed out waiting for output. "
                    "This usually means you're not logged in. "
                    "Run: gemini (then choose 'Login with Google')"
                )
            except StopAsyncIteration:
                pass
            
            try:
                async for line in stream_iter:
                    line_count += 1
                    
                    if "not logged in" in line.lower() or "authentication" in line.lower():
                        last_error = "Authentication required"
                    elif "error" in line.lower() and not last_error:
                        last_error = line[:200]
                    
                    yield line
            except StopAsyncIteration:
                pass
        
        exit_code = await process.wait()
        
        if exit_code != 0:
            if last_error == "Authentication required":
                raise RuntimeError(
                    "gemini CLI authentication required. "
                    "Run: gemini (then choose 'Login with Google')"
                )
            elif last_error:
                raise RuntimeError(f"gemini failed: {last_error}")
            else:
                raise RuntimeError(f"gemini CLI exited with code {exit_code}")
        
        if line_count == 0:
            raise RuntimeError(
                "gemini CLI produced no output. "
                "This usually means you're not logged in. "
                "Run: gemini (then choose 'Login with Google')"
            )
    
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

