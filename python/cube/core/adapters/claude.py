"""Claude Code CLI adapter."""

import os
import shutil
from pathlib import Path
from typing import AsyncGenerator, Optional

from .base import CLIAdapter, run_subprocess_streaming


class ClaudeAdapter(CLIAdapter):
    """Adapter for Claude Code CLI."""

    def check_logged_in(self) -> bool:
        """Check if claude is logged in (has valid auth)."""
        # Claude stores auth in ~/.claude/ - check for config
        config_dir = Path.home() / ".claude"
        return config_dir.exists() and any(config_dir.iterdir())

    async def run(
        self, worktree: Path, model: str, prompt: str, session_id: Optional[str] = None, resume: bool = False
    ) -> AsyncGenerator[str, None]:
        """Run claude and yield JSON output lines."""

        if not self.check_installed():
            raise RuntimeError("claude is not installed. " + self.get_install_instructions())

        env = os.environ.copy()

        # Build command
        cmd = [
            "claude",
            "-p",  # Print mode (non-interactive)
            "--verbose",  # Required for stream-json
            "--output-format",
            "stream-json",
            "--include-partial-messages",  # Include thinking
            "--model",
            model,
        ]

        if resume and session_id:
            cmd.extend(["--resume", session_id])

        # Add prompt at the end
        cmd.append(prompt)

        last_error = None
        line_count = 0

        from ..master_log import get_master_log

        try:
            async for line in run_subprocess_streaming(cmd, worktree, "claude", env):
                line_count += 1

                # Log every line to master log
                master_log = get_master_log()
                if master_log:
                    master_log.write_raw_line(f"claude-{model}", line)

                # Detect specific error types - only in error lines, not regular content
                is_error_line = line.startswith('{"type":"error"') or line.startswith("Error:")

                if is_error_line and ("rate limit" in line.lower() or "capacity" in line.lower()):
                    last_error = f"Rate limit: {line[:150]}"
                elif is_error_line and "overloaded" in line.lower():
                    last_error = f"Overloaded: {line[:150]}"
                elif "ConnectError" in line or "ECONNRESET" in line:
                    last_error = "Network connection error"
                elif is_error_line and ("not logged in" in line.lower() or "authentication" in line.lower()):
                    last_error = "Authentication required"
                elif is_error_line and "api key" in line.lower() and "invalid" in line.lower():
                    last_error = "Invalid API key"
                elif is_error_line:
                    last_error = line[:200]

                yield line

        except RuntimeError:
            # Pass through errors for retry logic
            if last_error and ("Rate limit:" in last_error or "Overloaded:" in last_error):
                raise RuntimeError(last_error)
            elif last_error == "Network connection error":
                raise RuntimeError("claude network error (try again)")
            elif last_error == "Authentication required":
                raise RuntimeError("claude not authenticated. Run: claude login")
            elif last_error == "Invalid API key":
                raise RuntimeError("claude API key invalid")
            elif last_error:
                raise RuntimeError(f"claude failed: {last_error}")
            else:
                raise

        if line_count == 0:
            raise RuntimeError("claude produced no output (API may be unavailable)")

    def check_installed(self) -> bool:
        """Check if claude is installed."""
        return shutil.which("claude") is not None

    def get_install_instructions(self) -> str:
        """Get installation instructions."""
        return """Install Claude Code CLI:
  npm install -g @anthropic-ai/claude-code

After installation, authenticate with:
  claude login

Or set ANTHROPIC_API_KEY environment variable."""
