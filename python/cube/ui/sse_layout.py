"""SSE Layout Adapter for streaming thinking and output to web UI."""

import asyncio
import json
from datetime import datetime
from typing import Dict

from cube.core.base_layout import BaseThinkingLayout


class SSELayout(BaseThinkingLayout):
    """Layout adapter that streams thinking and output via SSE."""
    
    def __init__(self, boxes: Dict[str, str], queue: asyncio.Queue):
        """
        Initialize SSE layout adapter.
        
        Args:
            boxes: dict of {box_id: title} e.g. {"writer_a": "Writer A"}
            queue: asyncio.Queue for streaming messages
        """
        super().__init__(boxes)
        self.queue = queue
    
    def add_thinking(self, box_id: str, text: str) -> None:
        """Add thinking text to a specific box and queue SSE message."""
        super().add_thinking(box_id, text)
        
        asyncio.create_task(self.queue.put({
            "type": "thinking",
            "box": box_id,
            "text": text,
            "timestamp": datetime.utcnow().isoformat()
        }))
    
    def add_output(self, line: str) -> None:
        """Add output line and queue SSE message."""
        super().add_output(line)
        
        asyncio.create_task(self.queue.put({
            "type": "output",
            "content": line,
            "timestamp": datetime.utcnow().isoformat()
        }))
