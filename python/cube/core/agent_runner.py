"""Helper for running agents with consistent output handling."""

import json
from pathlib import Path
from typing import Callable, Optional, Union

from ..automation.stream import format_stream_message
from .agent import run_agent
from .parsers.registry import get_parser


async def run_agent_with_layout(
    cwd: Union[str, Path],
    model: str,
    prompt: str,
    layout,
    label: str,
    color: str,
    box_id: Optional[str] = None,
    session_id: Optional[str] = None,
    resume: bool = False,
    cli_name: str = "cursor-agent",
    stop_when_exists: Optional[Path] = None,
    capture_session_callback: Optional[Callable[[str], None]] = None,
) -> None:
    """Run an agent and pipe output to a layout.

    Args:
        cwd: Working directory
        model: Model name
        prompt: Agent prompt
        layout: SingleAgentLayout or DynamicLayout
        label: Display label for the agent
        color: Color for output
        box_id: Box ID for DynamicLayout (None for SingleAgentLayout)
        session_id: Optional session ID for resuming
        resume: Whether to resume existing session
        cli_name: CLI adapter name
        stop_when_exists: Stop early when this file exists
        capture_session_callback: Optional callback to receive session_id when captured
    """
    parser = get_parser(cli_name)
    stream = run_agent(cwd, model, prompt, session_id=session_id, resume=resume)

    is_dynamic = box_id is not None
    session_captured = False

    async for line in stream:
        # Capture session ID from first line if callback provided
        if capture_session_callback and not session_captured:
            try:
                data = json.loads(line)
                if "session_id" in data:
                    capture_session_callback(data["session_id"])
                    session_captured = True
            except (json.JSONDecodeError, TypeError):
                pass

        msg = parser.parse(line)
        if msg:
            if msg.type == "system" and msg.subtype == "init":
                msg.resumed = resume
            formatted = format_stream_message(msg, label, color)
            if formatted:
                if formatted.startswith("[thinking]"):
                    thinking_text = formatted.replace("[thinking]", "").replace("[/thinking]", "")
                    if is_dynamic:
                        layout.add_thinking(box_id, thinking_text)
                    else:
                        layout.add_thinking(thinking_text)
                elif msg.type == "assistant" and msg.content:
                    if is_dynamic:
                        layout.add_assistant_message(box_id, msg.content, label, color)
                    else:
                        layout.add_assistant_message(msg.content, label, color)
                else:
                    layout.add_output(formatted)

        if stop_when_exists and stop_when_exists.exists():
            break
