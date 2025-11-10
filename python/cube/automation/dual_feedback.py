"""Dual writer feedback with shared layout."""

import asyncio
from pathlib import Path
from ..core.agent import run_agent
from ..core.dual_layout import get_dual_layout, DualWriterLayout
from ..core.user_config import load_config, get_writer_config
from ..core.parsers.registry import get_parser
from ..core.config import WRITER_LETTERS
from ..automation.stream import format_stream_message
from ..core.output import console

async def send_dual_feedback(
    task_id: str,
    feedback_a_path: Path,
    feedback_b_path: Path,
    session_a: str,
    session_b: str,
    worktree_a: Path,
    worktree_b: Path
) -> None:
    """Send feedback to both writers in parallel with dual layout."""
    
    DualWriterLayout.reset()
    layout = get_dual_layout()
    layout.start()
    
    config = load_config()
    parser = get_parser("cursor-agent")
    
    async def send_to_a():
        wconfig_a = get_writer_config("writer_a")
        feedback_a = feedback_a_path.read_text()
        
        stream = run_agent(worktree_a, wconfig_a.model, feedback_a, session_id=session_a, resume=True)
        
        async for line in stream:
            msg = parser.parse(line)
            if msg:
                formatted = format_stream_message(msg, "Writer A", "green")
                if formatted:
                    if formatted.startswith("[thinking]"):
                        thinking_text = formatted.replace("[thinking]", "").replace("[/thinking]", "")
                        layout.add_thinking("A", thinking_text)
                    else:
                        layout.add_output(formatted)
    
    async def send_to_b():
        wconfig_b = get_writer_config("writer_b")
        feedback_b = feedback_b_path.read_text()
        
        stream = run_agent(worktree_b, wconfig_b.model, feedback_b, session_id=session_b, resume=True)
        
        async for line in stream:
            msg = parser.parse(line)
            if msg:
                formatted = format_stream_message(msg, "Writer B", "blue")
                if formatted:
                    if formatted.startswith("[thinking]"):
                        thinking_text = formatted.replace("[thinking]", "").replace("[/thinking]", "")
                        layout.add_thinking("B", thinking_text)
                    else:
                        layout.add_output(formatted)
    
    await asyncio.gather(send_to_a(), send_to_b())
    
    layout.close()

