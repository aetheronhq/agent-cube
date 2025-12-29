"""Claude Code CLI adapter."""

import asyncio
from pathlib import Path
from typing import AsyncGenerator, Optional
import os
import shutil

from .base import CLIAdapter, run_subprocess_streaming


class ClaudeCodeAdapter(CLIAdapter):
    """Adapter for Claude Code CLI (https://github.com/anthropics/claude-code).
    
    Claude Code output format (verified via claude --help):
    - Uses -p/--print for non-interactive mode
    - Uses --output-format stream-json for JSON streaming (requires --verbose)
    - Uses --model for model selection (e.g., 'sonnet', 'opus', or full model name)
    - Supports --resume and --continue for session management
    """
    
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
        env["PATH"] = f"{Path.home() / '.local' / 'bin'}:{env.get('PATH', '')}"
        
        cmd = [
            "claude",
            "-p",
            "--output-format", "stream-json",
            "--verbose",
            "--model", model,
        ]
        
        if resume and session_id:
            cmd.extend(["--resume", session_id])
        elif resume:
            cmd.append("--continue")
        
        cmd.append(prompt)
        
        worktree.mkdir(parents=True, exist_ok=True)
        
        last_error = None
        line_count = 0
        
        from ..master_log import get_master_log
        
        try:
            async for line in run_subprocess_streaming(cmd, worktree, "claude-code", env):
                line_count += 1
                
                master_log = get_master_log()
                if master_log:
                    master_log.write_raw_line(f"claude-{model}", line)
                
                if "not logged in" in line.lower() or "authentication" in line.lower():
                    last_error = "Authentication required"
                elif "setup-token" in line.lower() or "auth" in line.lower():
                    if "error" in line.lower() or "fail" in line.lower():
                        last_error = "Authentication required"
                elif line.startswith('{"type":"error"') or line.startswith('Error:'):
                    last_error = line[:200]
                
                yield line
        
        except RuntimeError as e:
            if last_error == "Authentication required":
                raise RuntimeError(
                    "Claude Code CLI not authenticated. Run: claude setup-token\n"
                    "Requires a Claude subscription (Pro/Team/Enterprise)."
                )
            elif last_error:
                raise RuntimeError(f"claude-code failed: {last_error}")
            else:
                raise
        
        if line_count == 0:
            raise RuntimeError(
                "Claude Code CLI produced no output. "
                "Ensure you are authenticated: claude setup-token"
            )
    
    def check_installed(self) -> bool:
        """Check if claude CLI is installed."""
        return shutil.which("claude") is not None
    
    def get_install_instructions(self) -> str:
        """Get installation instructions."""
        return """Install Claude Code CLI:
  npm install -g @anthropic-ai/claude-code

After installation, authenticate with:
  claude setup-token

Requires Claude subscription (Pro, Team, or Enterprise).
Documentation: https://docs.anthropic.com/en/docs/claude-code"""
