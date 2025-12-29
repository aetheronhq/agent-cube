"""Claude Code CLI adapter."""

import asyncio
from pathlib import Path
from typing import AsyncGenerator, Optional
import os
import shutil

from .base import CLIAdapter, run_subprocess_streaming
from ..master_log import get_master_log

class ClaudeCodeAdapter(CLIAdapter):
    """Adapter for Claude Code CLI (https://github.com/anthropics/claude-code)."""

    async def run(
        self,
        worktree: Path,
        model: str,
        prompt: str,
        session_id: Optional[str] = None,
        resume: bool = False
    ) -> AsyncGenerator[str, None]:
        """Run Claude Code CLI and yield JSON output lines."""
        env = os.environ.copy()

        cmd = [
            "claude",
            "--model", model,
            "--print",
            "--output-format", "stream-json",
            "--tools", "",  # Disable tools for now
        ]

        if resume and session_id:
            cmd.extend(["--resume", session_id])
        
        cmd.append(prompt)

        worktree.mkdir(parents=True, exist_ok=True)

        last_error = None
        line_count = 0
        
        try:
            async for line in run_subprocess_streaming(cmd, worktree, "claude-code", env):
                line_count += 1

                master_log = get_master_log()
                if master_log:
                    master_log.write_raw_line(f"claude-code-{model}", line)

                if "auth" in line.lower() or "authenticate" in line.lower():
                    last_error = "Authentication required. Please run `claude auth`."
                elif line.startswith('{"error"'):
                    last_error = line[:200]
                
                yield line

        except RuntimeError as e:
            if last_error:
                raise RuntimeError(f"claude-code failed: {last_error}")
            else:
                raise

        if line_count == 0:
            raise RuntimeError("Claude Code CLI produced no output. Is it installed and authenticated? Run: claude auth")

    def check_installed(self) -> bool:
        """Check if claude CLI is installed."""
        return shutil.which("claude") is not None

    def get_install_instructions(self) -> str:
        """Get installation instructions."""
        return """Install Claude Code CLI:
  npm install -g @anthropic-ai/claude-code

After installation, authenticate with:
  claude auth

Documentation: https://github.com/anthropics/claude-code"""
