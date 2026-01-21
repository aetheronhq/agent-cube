"""Agent execution with pluggable CLI adapters (ports and adapters pattern)."""

import asyncio
from pathlib import Path
from typing import AsyncGenerator, Optional

from .adapters.registry import get_adapter
from .output import console
from .user_config import load_config

# Errors that should trigger auto-retry (transient failures)
RETRYABLE_ERRORS = [
    "network error",
    "exited with code 1",
    "rate limit",
    "capacity",
    "connection",
    "timeout",
    "unavailable",
    "retriable",
    "transient",
]


def _is_retryable_error(error_msg: str) -> bool:
    """Check if an error message indicates a retryable transient failure."""
    error_lower = error_msg.lower()
    return any(pattern in error_lower for pattern in RETRYABLE_ERRORS)


async def run_agent(
    worktree: Path,
    model: str,
    prompt: str,
    session_id: Optional[str] = None,
    resume: bool = False,
    max_retries: int = 1,
) -> AsyncGenerator[str, None]:
    """Run agent using appropriate CLI adapter with auto-retry for transient failures.

    Uses config to determine which CLI tool to use for each model.
    Supports: cursor-agent, gemini, and future CLI tools via adapters.

    Args:
        worktree: Working directory for the agent
        model: Model name to use
        prompt: Prompt to send to the agent
        session_id: Optional session ID for resuming
        resume: Whether this is a resume operation
        max_retries: Number of retries for transient failures (default: 1)
    """
    config = load_config()
    cli_name = config.cli_tools.get(model, "cursor-agent")
    adapter = get_adapter(cli_name)

    last_error: Optional[Exception] = None

    for attempt in range(max_retries + 1):
        try:
            async for line in adapter.run(worktree, model, prompt, session_id, resume):  # type: ignore[attr-defined]
                yield line
            return  # Success - exit the retry loop
        except RuntimeError as e:
            error_msg = str(e)
            last_error = e

            if attempt < max_retries and _is_retryable_error(error_msg):
                console.print(f"[yellow]⚠️  Retrying after transient error: {error_msg[:80]}...[/yellow]")
                await asyncio.sleep(2)  # Brief pause before retry
                continue
            else:
                raise

    # Should not reach here, but just in case
    if last_error:
        raise last_error


def check_cursor_agent() -> bool:
    """Check if cursor-agent is installed (legacy function)."""
    from .adapters.cursor import CursorAdapter

    return CursorAdapter().check_installed()


def run_async(coro):
    """Run async code with proper cleanup to avoid 'Event loop is closed' warnings.

    This is a replacement for asyncio.run() that properly handles:
    - Cancelling pending tasks
    - Closing subprocess transports
    - Shutting down async generators

    Args:
        coro: The coroutine to run

    Returns:
        The result of the coroutine
    """
    import gc
    import sys
    import warnings

    # Suppress asyncio cleanup warnings upfront
    warnings.filterwarnings("ignore", message=".*Event loop is closed.*")
    warnings.filterwarnings("ignore", message=".*was destroyed but it is pending.*")

    # Install quiet unraisablehook early to catch all cleanup errors
    original_unraisablehook = getattr(sys, "unraisablehook", None)

    def quiet_unraisablehook(unraisable):
        msg = str(unraisable.exc_value) if unraisable.exc_value else ""
        if "Event loop is closed" in msg or "pending" in msg.lower():
            return  # Silently ignore async cleanup noise
        if original_unraisablehook:
            original_unraisablehook(unraisable)

    sys.unraisablehook = quiet_unraisablehook

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        return loop.run_until_complete(coro)
    finally:
        try:
            # Cancel all pending tasks
            pending = asyncio.all_tasks(loop)
            for task in pending:
                task.cancel()

            # Let cancelled tasks complete
            if pending:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))

            # Shutdown async generators
            loop.run_until_complete(loop.shutdown_asyncgens())

            # Shutdown default executor (Python 3.9+)
            loop.run_until_complete(loop.shutdown_default_executor())

            # Force garbage collection while loop is still open
            gc.collect()
        except Exception:
            pass  # Best effort cleanup

        # Close the loop
        loop.close()
