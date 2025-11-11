# Task 02: Backend API Layer

**Goal:** Lightweight FastAPI server that wraps cube-py Python modules

## Context

Creates the backend that the React UI calls. Exposes existing `cube` functionality via REST API + SSE.

## Requirements

### 1. FastAPI Server

Create `packages/web-ui/server/main.py`:
- FastAPI application
- CORS for localhost:5173
- Serve static files (built React app)
- Run on port 8000

### 2. Core Endpoints

```python
GET    /api/workflows              # List active (from state files)
POST   /api/workflows              # Start new (calls orchestrate_auto)
GET    /api/workflows/{id}          # Get status
DELETE /api/workflows/{id}          # Clean up

GET    /api/workflows/{id}/decisions/panel
GET    /api/workflows/{id}/decisions/peer
POST   /api/workflows/{id}/resume/{agent}
```

### 3. Streaming Endpoint

```python
GET /api/workflows/{id}/stream  # SSE streaming agent output

# Yields:
# data: {"type":"thinking","agent":"A","text":"Analyzing..."}
# data: {"type":"tool_call","agent":"B","tool":"read","path":"file.ts"}
# data: {"type":"phase","phase":6,"name":"Synthesis"}
```

### 4. Direct Python Integration

**Import cube modules:**
```python
from cube.commands.orchestrate import orchestrate_auto_command
from cube.core.state import load_state
from cube.core.decision_parser import parse_all_decisions
```

**Don't shell out** - use Python directly!

## Deliverables

- [ ] FastAPI server in `packages/web-ui/server/`
- [ ] All REST endpoints implemented
- [ ] SSE streaming working
- [ ] Direct Python imports (no subprocess)
- [ ] CORS configured for dev
- [ ] Error handling with proper status codes
- [ ] API documentation (FastAPI auto-docs)
- [ ] `python server/main.py` starts server

## Architecture Constraints

**Integration:**
- ✅ Import cube-py modules directly
- ✅ Use existing functions (orchestrate_auto_command, load_state, etc.)
- ✅ Share code with CLI (don't duplicate logic)
- ❌ Don't shell out to `cube` command
- ❌ Don't reimplement orchestration

**API Design:**
- ✅ RESTful endpoints
- ✅ SSE for real-time (not WebSocket - simpler)
- ✅ JSON responses
- ✅ Proper HTTP status codes

**Error Handling:**
- 200: Success
- 400: Bad request (invalid task_id)
- 404: Task not found
- 500: Internal error (with message)

## Example Implementation

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from cube.commands.orchestrate import orchestrate_auto_command
from cube.core.state import load_state
import asyncio

app = FastAPI()

@app.post("/api/workflows")
async def start_workflow(task_file: str):
    task_id = extract_task_id(task_file)
    
    # Run in background
    asyncio.create_task(
        orchestrate_auto_command(task_file, 1)
    )
    
    return {"task_id": task_id, "status": "started"}

@app.get("/api/workflows/{task_id}")
async def get_status(task_id: str):
    state = load_state(task_id)
    if not state:
        raise HTTPException(404, "Task not found")
    
    return {
        "task_id": task_id,
        "current_phase": state.current_phase,
        "path": state.path,
        "winner": state.winner
    }

@app.get("/api/workflows/{task_id}/stream")
async def stream_workflow(task_id: str):
    async def generate():
        # Hook into agent output stream
        # Parse and yield SSE events
        ...
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```

## Acceptance Criteria

1. Server starts on port 8000
2. Can start workflow via POST
3. Status endpoint returns state
4. SSE stream yields agent events
5. No subprocess calls (direct Python)
6. FastAPI docs at `/docs` work
7. CORS allows localhost:5173
8. Error responses are clear

## Dependencies

```
fastapi==0.108.0
uvicorn[standard]==0.25.0
python-multipart==0.0.6
```

Plus: `cube-py` (local package)

## Time Estimate

3-4 hours

