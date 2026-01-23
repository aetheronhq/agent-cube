"""Cursor Agent CLI adapter."""

import os
import shutil
from pathlib import Path
from typing import AsyncGenerator, Optional

from .base import CLIAdapter, run_subprocess_streaming


class CursorAdapter(CLIAdapter):
    """Adapter for cursor-agent CLI."""

    def check_logged_in(self) -> bool:
        """Check if cursor-agent is logged in."""
        config_file = Path.home() / ".cursor" / "cli-config.json"
        return config_file.exists()

    async def run(
        self, worktree: Path, model: str, prompt: str, session_id: Optional[str] = None, resume: bool = False
    ) -> AsyncGenerator[str, None]:
        """Run cursor-agent and yield JSON output lines."""

        if not self.check_logged_in():
            raise RuntimeError("cursor-agent is not logged in. " "Run: cursor-agent login")

        env = os.environ.copy()
        env["PATH"] = f"{Path.home() / '.local' / 'bin'}:{env.get('PATH', '')}"

        if "CURSOR_API_KEY" in env:
            del env["CURSOR_API_KEY"]

        cmd = ["cursor-agent", "--force", "--output-format", "stream-json", "--stream-partial-output", "--model", model]

        if resume and session_id:
            cmd.extend(["--resume", session_id])

        # Use -- to signal end of options, so prompts starting with - aren't parsed as flags
        cmd.extend(["--", prompt])

        last_error = None
        line_count = 0

        from ..master_log import get_master_log

        try:
            async for line in run_subprocess_streaming(cmd, worktree, "cursor-agent", env):
                line_count += 1

                # Log every line to master log
                master_log = get_master_log()
                if master_log:
                    master_log.write_raw_line(f"cursor-{model}", line)

                # Detect specific error types - only in error lines, not regular content
                is_error_line = line.startswith('{"type":"error"') or line.startswith("Error:")

                if "RetriableError" in line or (is_error_line and "unavailable" in line.lower()):
                    last_error = f"Transient error: {line[:150]}"
                elif is_error_line and ("rate limit" in line.lower() or "capacity" in line.lower()):
                    last_error = f"Rate limit: {line[:150]}"
                elif "ConnectError" in line or "ECONNRESET" in line:
                    last_error = "Network connection error"
                elif is_error_line and ("not logged in" in line.lower() or "authentication" in line.lower()):
                    last_error = "Authentication required"
                elif is_error_line:
                    last_error = line[:200]

                yield line

        except RuntimeError:
            # Pass through transient errors for retry logic
            if last_error and last_error.startswith("Transient error:"):
                raise RuntimeError(last_error)
            elif last_error and last_error.startswith("Rate limit:"):
                raise RuntimeError(last_error)
            elif last_error == "Network connection error":
                raise RuntimeError("cursor-agent network error (try again)")
            elif last_error == "Authentication required":
                raise RuntimeError("cursor-agent not logged in. Run: cursor-agent login")
            elif last_error:
                raise RuntimeError(f"cursor-agent failed: {last_error}")
            else:
                raise

        if line_count == 0:
            raise RuntimeError("cursor-agent produced no output (API may be unavailable)")

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
