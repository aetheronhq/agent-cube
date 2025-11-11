from __future__ import annotations

import asyncio
import json
from collections import deque
from contextlib import suppress
from datetime import datetime, timezone
from threading import Lock
from typing import Any, AsyncGenerator, Deque, Dict, Iterable, Set

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from cube.core.dual_layout import DualWriterLayout
from cube.core.triple_layout import TripleJudgeLayout

from ..sse_layout import SSELayout

HEARTBEAT_INTERVAL = 30.0
HISTORY_LIMIT = 500
STREAM_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}

WRITER_BOXES = {
    "writer_a": "Writer A",
    "writer_b": "Writer B",
}

JUDGE_BOXES = {
    "judge_1": "Judge 1",
    "judge_2": "Judge 2",
    "judge_3": "Judge 3",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _format_sse(event: Dict[str, Any]) -> str:
    return f"data: {json.dumps(event, separators=(',', ':'))}\n\n"


class TaskStreamState:
    """Holds streaming state for a single task."""

    def __init__(self, task_id: str):
        self.task_id = task_id
        self.queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()
        self.history: Deque[Dict[str, Any]] = deque(maxlen=HISTORY_LIMIT)
        self.subscribers: Set[asyncio.Queue[Dict[str, Any]]] = set()
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.get_event_loop()
        self._loop = loop
        self._broadcast_task = self._loop.create_task(self._broadcast_loop())
        self._layouts: Dict[str, SSELayout] = {}

    async def _broadcast_loop(self) -> None:
        try:
            while True:
                message = await self.queue.get()
                self.history.append(message)
                stale: list[asyncio.Queue[Dict[str, Any]]] = []
                for subscriber in list(self.subscribers):
                    try:
                        await subscriber.put(message)
                    except asyncio.CancelledError:
                        stale.append(subscriber)
                for subscriber in stale:
                    self.subscribers.discard(subscriber)
        except asyncio.CancelledError:
            pass

    def add_subscriber(self) -> asyncio.Queue[Dict[str, Any]]:
        queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()
        self.subscribers.add(queue)
        return queue

    def remove_subscriber(self, queue: asyncio.Queue[Dict[str, Any]]) -> None:
        self.subscribers.discard(queue)

    def get_history(self) -> Iterable[Dict[str, Any]]:
        return list(self.history)

    def ensure_writers_layout(self) -> None:
        if "writers" in self._layouts:
            return
        DualWriterLayout.reset()
        layout = SSELayout(self.task_id, WRITER_BOXES, self.queue)
        DualWriterLayout._instance = layout  # type: ignore[attr-defined]
        self._layouts["writers"] = layout

    def release_writers_layout(self) -> None:
        if "writers" not in self._layouts:
            return
        DualWriterLayout.reset()
        self._layouts.pop("writers", None)

    def ensure_judges_layout(self) -> None:
        if "judges" in self._layouts:
            return
        TripleJudgeLayout.reset()
        layout = SSELayout(self.task_id, JUDGE_BOXES, self.queue)
        TripleJudgeLayout._instance = layout  # type: ignore[attr-defined]
        self._layouts["judges"] = layout

    def release_judges_layout(self) -> None:
        if "judges" not in self._layouts:
            return
        TripleJudgeLayout.reset()
        self._layouts.pop("judges", None)

    def publish_status(self, status: str, **payload: Any) -> None:
        message = {
            "type": "status",
            "status": status,
            "taskId": self.task_id,
            "timestamp": _now_iso(),
            **payload,
        }
        self._loop.create_task(self.queue.put(message))

    async def close(self) -> None:
        for queue in list(self.subscribers):
            self.subscribers.discard(queue)
        for key, layout in list(self._layouts.items()):
            layout.close()
            self._layouts.pop(key, None)
        self._broadcast_task.cancel()
        with suppress(asyncio.CancelledError):
            await self._broadcast_task


class TaskStreamRegistry:
    """Registry of active task SSE streams."""

    def __init__(self) -> None:
        self._streams: Dict[str, TaskStreamState] = {}
        self._lock = Lock()

    def ensure(self, task_id: str) -> TaskStreamState:
        with self._lock:
            state = self._streams.get(task_id)
            if state is None:
                state = TaskStreamState(task_id)
                self._streams[task_id] = state
            return state

    async def cleanup(self, task_id: str) -> None:
        with self._lock:
            state = self._streams.pop(task_id, None)
        if state:
            await state.close()


task_stream_registry = TaskStreamRegistry()

router = APIRouter(prefix="/tasks", tags=["stream"])


@router.get("/{task_id}/stream")
async def stream_task(task_id: str) -> StreamingResponse:
    state = task_stream_registry.ensure(task_id)
    subscriber_queue = state.add_subscriber()
    history = state.get_history()

    async def event_stream() -> AsyncGenerator[str, None]:
        try:
            for item in history:
                yield _format_sse(item)

            while True:
                try:
                    message = await asyncio.wait_for(
                        subscriber_queue.get(), timeout=HEARTBEAT_INTERVAL
                    )
                    yield _format_sse(message)
                except asyncio.TimeoutError:
                    heartbeat = {
                        "type": "heartbeat",
                        "taskId": task_id,
                        "timestamp": _now_iso(),
                    }
                    yield _format_sse(heartbeat)
        except asyncio.CancelledError:
            raise
        finally:
            state.remove_subscriber(subscriber_queue)

    return StreamingResponse(event_stream(), media_type="text/event-stream", headers=STREAM_HEADERS)


__all__ = ["router", "task_stream_registry", "TaskStreamRegistry", "TaskStreamState"]
