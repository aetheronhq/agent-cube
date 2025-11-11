"""SSE streaming endpoints for real-time task monitoring."""

import asyncio
import json
import logging
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from cube.core.state import load_state

router = APIRouter(tags=["streaming"])

logger = logging.getLogger(__name__)


@router.get("/tasks/{task_id}/stream")
async def stream_task(task_id: str) -> StreamingResponse:
    """
    Stream task execution events via Server-Sent Events (SSE).
    
    Streams thinking and output messages in real-time for the given task.
    Sends heartbeat every 30s to keep connection alive.
    """
    state = load_state(task_id)
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{task_id}' not found"
        )
    
    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events."""
        queue: asyncio.Queue = asyncio.Queue()
        
        # TODO: Wire up to actual task execution queue
        # For now, send initial status and heartbeat
        
        yield f"data: {json.dumps({'type': 'connected', 'task_id': task_id, 'timestamp': state.updated_at or ''})}\n\n"
        
        while True:
            try:
                msg = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield f"data: {json.dumps(msg)}\n\n"
            except asyncio.TimeoutError:
                yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
            except asyncio.CancelledError:
                logger.info("SSE stream cancelled for task %s", task_id)
                break
            except Exception as e:
                logger.error("Error in SSE stream for task %s: %s", task_id, e)
                break
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )
