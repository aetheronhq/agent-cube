"""Dual writer feedback with shared layout."""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List

from ..automation.stream import format_stream_message
from ..core.agent import run_agent
from ..core.parsers.registry import get_parser
from ..core.user_config import get_writer_config


@dataclass
class FeedbackInfo:
    writer_key: str
    feedback_path: Path
    session_id: str
    worktree: Path


async def send_dual_feedback(task_id: str, feedbacks: List[FeedbackInfo]) -> None:
    """Send feedback to both writers in parallel with dual layout.

    Deliver feedback through each writer's configured communication
    channel using their existing sessions. Display progress in a dual
    layout with thinking boxes for each writer.

    Args:
        task_id: The task identifier for context
        feedbacks: List of FeedbackInfo objects, each containing:
            - writer_key: Writer identifier (e.g., "writer_a")
            - feedback_path: Path to the feedback markdown file
            - session_id: Session ID for the writer's existing session
            - worktree: Path to the writer's worktree directory
    """

    # Create fresh layout for feedback prompters (closes previous if exists)
    from ..core.dynamic_layout import DynamicLayout

    boxes = {}
    for fb in feedbacks:
        wconfig = get_writer_config(fb.writer_key)
        boxes[f"prompter_{fb.writer_key}"] = f"Prompter {wconfig.label}"

    DynamicLayout.initialize(boxes, lines_per_box=2, task_name=task_id)
    layout = DynamicLayout
    layout.start()

    parser = get_parser("cursor-agent")

    # Create log files for web UI
    logs_dir = Path.home() / ".cube" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    timestamp = int(datetime.now().timestamp())

    async def send_to_writer(feedback_info: FeedbackInfo):
        wconfig = get_writer_config(feedback_info.writer_key)
        feedback = feedback_info.feedback_path.read_text()

        log_file = logs_dir / f"synth-{wconfig.name}-{task_id}-{timestamp}.json"

        stream = run_agent(
            feedback_info.worktree, wconfig.model, feedback, session_id=feedback_info.session_id, resume=True
        )

        with open(log_file, "w") as f:
            async for line in stream:
                f.write(line + "\n")
                f.flush()

                msg = parser.parse(line)
                if msg:
                    if msg.type == "system" and msg.subtype == "init":
                        msg.resumed = True
                    formatted = format_stream_message(msg, f"Prompter {wconfig.label}", wconfig.color)
                    if formatted:
                        if formatted.startswith("[thinking]"):
                            thinking_text = formatted.replace("[thinking]", "").replace("[/thinking]", "")
                            layout.add_thinking(f"prompter_{feedback_info.writer_key}", thinking_text)
                        elif msg.type == "assistant" and msg.content:
                            layout.add_assistant_message(
                                f"prompter_{feedback_info.writer_key}",
                                msg.content,
                                f"Prompter {wconfig.label}",
                                wconfig.color,
                            )
                        else:
                            layout.add_output(formatted)

    await asyncio.gather(*(send_to_writer(fb) for fb in feedbacks))

    layout.close()
