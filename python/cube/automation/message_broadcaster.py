"""Centralized message broadcasting to CLI and SSE."""

from datetime import datetime
from typing import Optional, Any, Dict


class MessageBroadcaster:
    """Broadcasts messages to both CLI layout and SSE streams."""
    
    def __init__(self, task_id: str, layout: Any, sse_state: Optional[Any] = None):
        self.task_id = task_id
        self.layout = layout
        self.sse_state = sse_state
    
    async def broadcast_thinking(self, box_id: str, text: str) -> None:
        """Broadcast thinking to CLI and SSE."""
        # CLI display
        self.layout.add_thinking(box_id, text)
        
        # SSE stream
        if self.sse_state:
            await self.sse_state.queue.put({
                "type": "thinking",
                "box": self._normalize_box_id(box_id),
                "text": text,
                "timestamp": datetime.now().isoformat()
            })
    
    async def broadcast_output(self, line: str, agent_label: Optional[str] = None) -> None:
        """Broadcast output to CLI and SSE."""
        # CLI display
        self.layout.add_output(line)
        
        # SSE stream
        if self.sse_state:
            payload: Dict[str, Any] = {
                "type": "output",
                "content": line,
                "timestamp": datetime.now().isoformat()
            }
            if agent_label:
                payload["agent"] = agent_label
            
            await self.sse_state.queue.put(payload)
    
    @staticmethod
    def _normalize_box_id(box_id: str) -> str:
        """Normalize box ID for SSE (writer_a -> writer-a, judge number -> judge-N)."""
        if isinstance(box_id, str):
            return box_id.replace("_", "-")
        # box_id is a number (judge)
        return f"judge-{box_id}"


def create_broadcaster(task_id: str, layout: Any) -> MessageBroadcaster:
    """Create broadcaster with optional SSE integration."""
    try:
        from ..ui.routes.stream import task_stream_registry
        sse_state = task_stream_registry.ensure(task_id)
    except ImportError:
        sse_state = None
    
    return MessageBroadcaster(task_id, layout, sse_state)

