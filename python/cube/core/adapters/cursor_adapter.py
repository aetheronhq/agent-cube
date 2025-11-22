"""Cursor Agent CLI adapter."""

import asyncio
from pathlib import Path
from typing import AsyncGenerator, Optional
import os
import shutil

from ..cli_adapter import CLIAdapter, read_stream_with_buffer

class CursorAdapter(CLIAdapter):
    """Adapter for cursor-agent CLI."""
    
    def check_logged_in(self) -> bool:
        """Check if cursor-agent is logged in."""
        config_file = Path.home() / ".cursor" / "cli-config.json"
        return config_file.exists()
    
    async def run(
        self,
        worktree: Path,
        model: str,
        prompt: str,
        session_id: Optional[str] = None,
        resume: bool = False
    ) -> AsyncGenerator[str, None]:
        """Run cursor-agent and yield JSON output lines."""
        
        if not self.check_logged_in():
            raise RuntimeError(
                "cursor-agent is not logged in. "
                "Run: cursor-agent login"
            )
        
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
        line_count = 0
        first_line_timeout = 30
        
        if process.stdout:
            from ..cli_adapter import monitor_process_health
            
            health_monitor = asyncio.create_task(
                monitor_process_health(process, "cursor-agent", check_interval=5.0)
            )
            
            stream_iter = read_stream_with_buffer(process.stdout)
            
            try:
                first_line = await asyncio.wait_for(
                    anext(stream_iter),
                    timeout=first_line_timeout
                )
                line_count += 1
                
                if "not logged in" in first_line.lower() or "authentication" in first_line.lower():
                    last_error = "Authentication required"
                elif "ConnectError" in first_line or "ECONNRESET" in first_line:
                    last_error = "Network connection error"
                elif "error" in first_line.lower():
                    last_error = first_line[:200]
                
                yield first_line
                
            except asyncio.TimeoutError:
                health_monitor.cancel()
                process.kill()
                await process.wait()
                raise RuntimeError(
                    "cursor-agent timed out waiting for output. "
                    "This usually means you're not logged in. "
                    "Run: cursor-agent login"
                )
            except StopAsyncIteration:
                health_monitor.cancel()
                pass
            
            try:
                async for line in stream_iter:
                    line_count += 1
                    
                    if "not logged in" in line.lower() or "authentication" in line.lower():
                        last_error = "Authentication required"
                    elif "ConnectError" in line or "ECONNRESET" in line:
                        last_error = "Network connection error"
                    elif "error" in line.lower() and not last_error:
                        last_error = line[:200]
                    
                    yield line
            except StopAsyncIteration:
                pass
            finally:
                health_monitor.cancel()
                try:
                    await health_monitor
                except (asyncio.CancelledError, RuntimeError):
                    pass
        
        exit_code = await process.wait()
        
        if exit_code != 0:
            if last_error == "Authentication required":
                raise RuntimeError(
                    "cursor-agent authentication required. "
                    "Run: cursor-agent login"
                )
            elif last_error == "Network connection error":
                raise RuntimeError("cursor-agent network error (try again)")
            elif last_error:
                raise RuntimeError(f"cursor-agent failed: {last_error}")
            else:
                raise RuntimeError(f"cursor-agent exited with code {exit_code}")
        
        if line_count == 0:
            raise RuntimeError(
                "cursor-agent produced no output. "
                "This usually means you're not logged in. "
                "Run: cursor-agent login"
            )
    
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

