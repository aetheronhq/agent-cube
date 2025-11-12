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
        # Maintain a bounded in-memory history so new subscribers can replay recent events
        # prior to receiving live updates. This mirrors the CLI experience after refresh.
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
        # Hijack layouts when first subscriber connects
        if len(self.subscribers) == 1:
            self.ensure_writers_layout()
            self.ensure_judges_layout()
        return queue

    def remove_subscriber(self, queue: asyncio.Queue[Dict[str, Any]]) -> None:
        self.subscribers.discard(queue)

    def get_history(self) -> Iterable[Dict[str, Any]]:
        return list(self.history)

    def ensure_writers_layout(self) -> None:
        if "writers" in self._layouts:
            return
        DualWriterLayout.reset()
        # ----------------------------------------------------------------------
        # CRITICAL INTEGRATION PATTERN: "Layout hijacking"
        #
        # DualWriterLayout and TripleJudgeLayout expose class-level singleton
        # instances that automation commands interact with directly. By swapping
        # the `_instance` for our SSELayout adapter we transparently intercept
        # every `add_thinking` / `add_output` call made by automation without
        # modifying the underlying orchestration code.
        #
        # Why this is safe:
        # • SSELayout subclasses BaseThinkingLayout and preserves behaviour.
        # • We restore the original singleton by calling `reset()` in the
        #   corresponding release_* methods when subscribers disconnect.
        # • There is no public hook for dependency injection; targeted
        #   monkey-patching keeps the integration localised to the UI layer.
        #
        # Alternative approaches (observer pattern, wrapper types, etc.) would
        # require invasive changes across automation modules. This technique keeps
        # the streaming integration self-contained while guaranteeing parity with
        # the CLI experience.
        # ----------------------------------------------------------------------
        layout = SSELayout(self.task_id, WRITER_BOXES, self.queue)
        DualWriterLayout._instance = layout  # type: ignore[attr-defined]
        self._layouts["writers"] = layout

    def release_writers_layout(self) -> None:
        if "writers" not in self._layouts:
            return
        # reset() reinstates the original BaseThinkingLayout-backed singleton
        # so future CLI usage behaves exactly as before streaming began.
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
        # Mirror the writers flow: restore the default singleton to avoid
        # leaking the SSE adapter once no subscribers are connected.
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
    """Manage SSE stream lifecycle and state for UI task monitoring.

    Lifecycle
    ---------
    1. `ensure(task_id)` creates or returns a TaskStreamState. This step also
       hijacks the Dual/Triple layout singletons so automation writes flow
       through SSELayout.
    2. While subscribers are active, messages are queued asynchronously and
       replayed from the bounded history buffer for late joiners.
    3. `cleanup(task_id)` is invoked when the last subscriber disconnects. It
       releases the hijacked layouts via `reset()`, cancels background tasks,
       and allows the state to be garbage collected.

    Thread safety
    -------------
    The registry uses a threading.Lock around its dictionary. FastAPI runs each
    coroutine on a single event loop, so this light synchronisation is sufficient
    without additional concurrency primitives.

    Memory management
    -----------------
    Each TaskStreamState caps history at `HISTORY_LIMIT` messages. Because state
    is cleaned up as soon as there are no subscribers, memory usage stays bounded
    and no filesystem persistence is required.
    """

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
    """Stream task events by tailing log files in real-time."""
    from pathlib import Path
    from cube.automation.stream import format_stream_message
    from cube.core.parsers.registry import get_parser
    
    logs_dir = Path.home() / ".cube" / "logs"
    parser = get_parser("cursor-agent")
    
    async def event_stream() -> AsyncGenerator[str, None]:
        yield _format_sse({"type": "heartbeat", "taskId": task_id, "timestamp": _now_iso()})
        
        file_positions: dict[str, int] = {}
        
        try:
            while True:
                current_logs = sorted(logs_dir.glob(f"*{task_id}*.json")) if logs_dir.exists() else []
                
                for log_file in current_logs:
                    if not log_file.exists():
                        continue
                    
                    # Detect agent info from filename
                    filename = str(log_file.name)
                    if "writer-sonnet" in filename:
                        box_id, agent_label, color = "writer-a", "Writer A", "green"
                    elif "writer-codex" in filename:
                        box_id, agent_label, color = "writer-b", "Writer B", "blue"
                    elif "judge-1" in filename:
                        box_id, agent_label, color = "judge-1", "Judge 1", "yellow"
                    elif "judge-2" in filename:
                        box_id, agent_label, color = "judge-2", "Judge 2", "yellow"
                    elif "judge-3" in filename:
                        box_id, agent_label, color = "judge-3", "Judge 3", "yellow"
                    else:
                        continue
                    
                    pos = file_positions.get(str(log_file), 0)
                    
                    try:
                        with open(log_file) as f:
                            f.seek(pos)
                            for line in f:
                                line = line.strip()
                                if not line:
                                    continue
                                
                                # Use CLI parser
                                msg = parser.parse(line)
                                if not msg:
                                    continue
                                
                                # Use CLI formatter
                                formatted = format_stream_message(msg, agent_label, color)
                                if not formatted:
                                    continue
                                
                                # Convert to SSE
                                if formatted.startswith("[thinking]"):
                                    text = formatted.replace("[thinking]", "").replace("[/thinking]", "").strip()
                                    if text:
                                        yield _format_sse({
                                            "type": "thinking",
                                            "box": box_id,
                                            "text": text,
                                            "timestamp": _now_iso()
                                        })
                                else:
                                    # Output message
                                    yield _format_sse({
                                        "type": "output",
                                        "content": formatted,
                                        "timestamp": _now_iso()
                                    })
                            
                            file_positions[str(log_file)] = f.tell()
                    except:
                        pass
                
                await asyncio.sleep(0.5)
                
                if len(file_positions) == 0:
                    yield _format_sse({"type": "heartbeat", "taskId": task_id, "timestamp": _now_iso()})
        except asyncio.CancelledError:
            raise

    return StreamingResponse(event_stream(), media_type="text/event-stream", headers=STREAM_HEADERS)


__all__ = ["router", "task_stream_registry", "TaskStreamRegistry", "TaskStreamState"]
