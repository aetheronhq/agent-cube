"""cursor-agent subprocess management."""

import asyncio
from pathlib import Path
from typing import AsyncGenerator, Optional
import os

async def run_agent(
    worktree: Path,
    model: str,
    prompt: str,
    session_id: Optional[str] = None,
    resume: bool = False
) -> AsyncGenerator[str, None]:
    """Run cursor-agent subprocess and yield JSON output lines."""
    
    env = os.environ.copy()
    env["PATH"] = f"{Path.home() / '.local' / 'bin'}:{env.get('PATH', '')}"
    
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
        env=env
    )
    
    if process.stdout:
        async for line in process.stdout:
            decoded_line = line.decode('utf-8', errors='replace').strip()
            if decoded_line:
                yield decoded_line
    
    await process.wait()

def check_cursor_agent() -> bool:
    """Check if cursor-agent is installed and available."""
    import shutil
    return shutil.which("cursor-agent") is not None

