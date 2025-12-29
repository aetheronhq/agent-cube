from __future__ import annotations

import asyncio
import re
from datetime import datetime, timezone
from typing import Any, Dict

from cube.core.base_layout import BaseThinkingLayout

_MARKUP_PATTERN = re.compile(r"\[/?[^\]]+\]")


def _strip_markup(value: str) -> str:
    """Remove Rich-style markup tags from a string."""
    if not value:
        return ""
    return _MARKUP_PATTERN.sub("", value).strip()


def _timestamp() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


class SSELayout(BaseThinkingLayout):
    """Adapter layout that broadcasts thinking/output updates over SSE queues."""

    def __init__(self, task_id: str, boxes: Dict[str, str], queue: asyncio.Queue[Dict[str, Any]]):
        super().__init__(boxes)
        self.task_id = task_id
        self.queue = queue
        self._agent_labels = set(boxes.values())

    def start(self) -> None:
        """Override start to skip Rich live rendering in SSE context."""
        with self.lock:
            self.started = True

    def _update(self) -> None:
        """Disable Rich UI updates for SSE layout."""
        return

    def add_thinking(self, box_id: str, text: str) -> None:
        super().add_thinking(box_id, text)
        cleaned = _strip_markup(text)
        if not cleaned:
            return
        payload = {
            "type": "thinking",
            "taskId": self.task_id,
            "box": box_id.replace("_", "-"),
            "agent": self.boxes.get(box_id),
            "text": cleaned,
            "timestamp": _timestamp(),
        }
        asyncio.create_task(self.queue.put(payload))

    def add_output(self, line: str) -> None:
        super().add_output(line)
        cleaned = _strip_markup(line)
        if not cleaned:
            return
        agent = None
        content = cleaned
        for label in self._agent_labels:
            if cleaned.startswith(label):
                agent = label
                content = cleaned[len(label):].lstrip()
                break
        payload = {
            "type": "output",
            "taskId": self.task_id,
            "content": content,
            "timestamp": _timestamp(),
        }
        if agent:
            payload["agent"] = agent
        asyncio.create_task(self.queue.put(payload))
