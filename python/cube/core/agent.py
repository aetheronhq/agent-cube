"""Agent execution with pluggable CLI adapters (ports and adapters pattern)."""

from pathlib import Path
from typing import AsyncGenerator, Optional

from .adapters.registry import get_adapter
from .user_config import load_config

async def run_agent(
    worktree: Path,
    model: str,
    prompt: str,
    session_id: Optional[str] = None,
    resume: bool = False
) -> AsyncGenerator[str, None]:
    """Run agent using appropriate CLI adapter.
    
    Uses config to determine which CLI tool to use for each model.
    Supports: cursor-agent, gemini, and future CLI tools via adapters.
    """
    
    config = load_config()
    cli_name = config.cli_tools.get(model, "cursor-agent")
    
    adapter = get_adapter(cli_name)
    
    async for line in adapter.run(worktree, model, prompt, session_id, resume):
        yield line

def check_cursor_agent() -> bool:
    """Check if cursor-agent is installed (legacy function)."""
    from .adapters.cursor_adapter import CursorAdapter
    return CursorAdapter().check_installed()

