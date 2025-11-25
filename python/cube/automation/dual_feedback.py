"""Dual writer feedback with shared layout."""

import asyncio
from pathlib import Path
from ..core.agent import run_agent
from ..core.dual_layout import get_dual_layout
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
    """Send feedback to both writers in parallel with dual layout.
    
    Deliver feedback through each writer's configured communication
    channel using their existing sessions. Display progress in a dual
    layout with thinking boxes for each writer.
    
    Args:
        task_id: The task identifier for context
        feedback_a_path: Path to feedback file for Writer A
        feedback_b_path: Path to feedback file for Writer B
        session_a: Session ID for Writer A's existing session
        session_b: Session ID for Writer B's existing session
        worktree_a: Path to Writer A's worktree directory
        worktree_b: Path to Writer B's worktree directory
    """
    
    # Create fresh layout for feedback prompters (closes previous if exists)
    from ..core.dynamic_layout import DynamicLayout
    
    writer_a = get_writer_config("writer_a")
    writer_b = get_writer_config("writer_b")
    boxes = {"prompter_a": f"Prompter A ({writer_a.label})", "prompter_b": f"Prompter B ({writer_b.label})"}
    DynamicLayout.initialize(boxes, lines_per_box=2)
    layout = DynamicLayout
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
                formatted = format_stream_message(msg, "Prompter A", "green")
                if formatted:
                    if formatted.startswith("[thinking]"):
                        thinking_text = formatted.replace("[thinking]", "").replace("[/thinking]", "")
                        layout.add_thinking("prompter_a", thinking_text)
                    elif msg.type == "assistant" and msg.content:
                        layout.add_assistant_message("prompter_a", msg.content, "Prompter A", "green")
                    else:
                        layout.add_output(formatted)
    
    async def send_to_b():
        wconfig_b = get_writer_config("writer_b")
        feedback_b = feedback_b_path.read_text()
        
        stream = run_agent(worktree_b, wconfig_b.model, feedback_b, session_id=session_b, resume=True)
        
        async for line in stream:
            msg = parser.parse(line)
            if msg:
                formatted = format_stream_message(msg, "Prompter B", "blue")
                if formatted:
                    if formatted.startswith("[thinking]"):
                        thinking_text = formatted.replace("[thinking]", "").replace("[/thinking]", "")
                        layout.add_thinking("prompter_b", thinking_text)
                    elif msg.type == "assistant" and msg.content:
                        layout.add_assistant_message("prompter_b", msg.content, "Prompter B", "blue")
                    else:
                        layout.add_output(formatted)
    
    await asyncio.gather(send_to_a(), send_to_b())
    
    layout.close()

