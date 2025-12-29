"""Dual writer feedback with shared layout."""

import asyncio
from datetime import datetime
from pathlib import Path
from ..core.agent import run_agent
from ..core.user_config import load_config
from ..core.parsers.registry import get_parser
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
    
    # Create fresh layout for feedback prompters (closes previous if exists)
    from ..core.dynamic_layout import DynamicLayout
    
    config = load_config()
    writers = [config.writers[key] for key in config.writer_order]
    boxes = {}
    for idx, w in enumerate(writers):
        letter = chr(ord('a') + idx)
        boxes[f"prompter_{letter}"] = f"Prompter {letter.upper()} ({w.label})"
    DynamicLayout.initialize(boxes, lines_per_box=2)
    layout = DynamicLayout
    layout.start()
    
    parser = get_parser("cursor-agent")
    
    # Create log files for web UI
    logs_dir = Path.home() / ".cube" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    timestamp = int(datetime.now().timestamp())
    
    # Get writers from config (first two for backwards compatibility)
    wconfig_a = writers[0] if len(writers) > 0 else None
    wconfig_b = writers[1] if len(writers) > 1 else None
    
    if not wconfig_a or not wconfig_b:
        raise RuntimeError("At least 2 writers must be configured for dual feedback")
    
    log_file_a = logs_dir / f"synth-{wconfig_a.name}-{task_id}-{timestamp}.json"
    log_file_b = logs_dir / f"synth-{wconfig_b.name}-{task_id}-{timestamp}.json"
    
    async def send_to_a():
        feedback_a = feedback_a_path.read_text()
        
        stream = run_agent(worktree_a, wconfig_a.model, feedback_a, session_id=session_a, resume=True)
        
        with open(log_file_a, 'w') as f:
            async for line in stream:
                f.write(line + '\n')
                f.flush()
                
                msg = parser.parse(line)
                if msg:
                    formatted = format_stream_message(msg, f"Prompter A ({wconfig_a.label})", wconfig_a.color)
                    if formatted:
                        if formatted.startswith("[thinking]"):
                            thinking_text = formatted.replace("[thinking]", "").replace("[/thinking]", "")
                            layout.add_thinking("prompter_a", thinking_text)
                        elif msg.type == "assistant" and msg.content:
                            layout.add_assistant_message("prompter_a", msg.content, f"Prompter A ({wconfig_a.label})", wconfig_a.color)
                        else:
                            layout.add_output(formatted)
    
    async def send_to_b():
        feedback_b = feedback_b_path.read_text()
        
        stream = run_agent(worktree_b, wconfig_b.model, feedback_b, session_id=session_b, resume=True)
        
        with open(log_file_b, 'w') as f:
            async for line in stream:
                f.write(line + '\n')
                f.flush()
                
                msg = parser.parse(line)
                if msg:
                    formatted = format_stream_message(msg, f"Prompter B ({wconfig_b.label})", wconfig_b.color)
                    if formatted:
                        if formatted.startswith("[thinking]"):
                            thinking_text = formatted.replace("[thinking]", "").replace("[/thinking]", "")
                            layout.add_thinking("prompter_b", thinking_text)
                        elif msg.type == "assistant" and msg.content:
                            layout.add_assistant_message("prompter_b", msg.content, f"Prompter B ({wconfig_b.label})", wconfig_b.color)
                        else:
                            layout.add_output(formatted)
    
    await asyncio.gather(send_to_a(), send_to_b())
    
    layout.close()

