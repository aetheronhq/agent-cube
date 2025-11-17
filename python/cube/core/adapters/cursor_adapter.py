"""Cursor Agent CLI adapter."""

import asyncio
from pathlib import Path
from typing import AsyncGenerator, Optional
import os
import shutil

from ..cli_adapter import CLIAdapter, read_stream_with_buffer

class CursorAdapter(CLIAdapter):
    """Adapter for cursor-agent CLI."""
    
    async def run(
        self,
        worktree: Path,
        model: str,
        prompt: str,
        session_id: Optional[str] = None,
        resume: bool = False
    ) -> AsyncGenerator[str, None]:
        """Run cursor-agent and yield JSON output lines."""
        
        env = os.environ.copy()
        env["PATH"] = f"{Path.home() / '.local' / 'bin'}:{env.get('PATH', '')}"
        
        if "CURSOR_API_KEY" in env:
            del env["CURSOR_API_KEY"]
        
        cmd = [
            "cursor-agent",
            "--print",
            "--force",
            "--output-format", "stream-json",
            "--stream-partial-output",
            "--model", model
        ]
        
        if resume and session_id:
            cmd.extend(["--resume", session_id])
        
        cmd.append(prompt)
        
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
                if "ConnectError" in line or "ECONNRESET" in line:
                    last_error = "Network connection error"
                elif "error" in line.lower() and not last_error:
                    last_error = line[:200]
                yield line
        
        exit_code = await process.wait()
        
        if exit_code != 0:
            if last_error == "Network connection error":
                raise RuntimeError(f"cursor-agent network error (try again)")
            elif last_error:
                raise RuntimeError(f"cursor-agent failed: {last_error}")
            else:
                raise RuntimeError(f"cursor-agent exited with code {exit_code}")
    
    def check_installed(self) -> bool:
        """Check if cursor-agent is installed."""
        env_path = os.environ.get("PATH", "")
        home = Path.home()
        local_bin = home / ".local" / "bin"
        
        if str(local_bin) not in env_path:
            os.environ["PATH"] = f"{local_bin}:{env_path}"
        
        return shutil.which("cursor-agent") is not None
    
    def get_install_instructions(self) -> str:
        """Get installation instructions."""
        return """Install cursor-agent:
  npm install -g @cursor/cli

Or add to your PATH if already installed:
  export PATH="$HOME/.local/bin:$PATH"

After installation, authenticate with:
  cursor-agent login"""
    
    async def check_authenticated(self) -> bool:
        """Cursor doesn't require separate authentication check."""
        return True

