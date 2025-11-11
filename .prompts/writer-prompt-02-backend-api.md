# Writer Task: Backend API for AgentCube Web UI

You are implementing the FastAPI backend that wraps AgentCube's existing automation modules and provides REST endpoints for the web UI.

---

## 🎯 **Your Mission**

Create a thin FastAPI wrapper layer that:
- Exposes task management endpoints
- Wraps existing `cube.automation` and `cube.core` modules
- Provides workflow control (dual writers, judge panel)
- Runs locally with CORS for the React frontend
- Launches via `cube ui` command

**Time Budget:** 3-4 hours

---

## 📖 **Context & Background**

### What You're Building On

The AgentCube Python codebase already has:
- ✅ `cube.automation.dual_writers` - Launches writer agents
- ✅ `cube.automation.judge_panel` - Launches judge panel
- ✅ `cube.core.state` - Manages task state in JSON files
- ✅ `cube.core.config` - Loads configuration
- ✅ All workflow logic already works perfectly

**Your job:** Create a thin REST API layer that delegates to these proven modules. **DO NOT reimplement any logic!**

### What Comes After

- Task 05 (Task Detail View) will consume your endpoints
- Task 06 (Decisions UI) will call your workflow endpoints
- Task 05 will also add SSE streaming (you create the foundation here)

### Architecture Principle: KISS

**Keep It Simple, Stupid:**
- ✅ Direct imports from `cube.automation` - no duplication
- ✅ File-based state (existing JSON files) - no database
- ✅ Background tasks for long operations - no blocking
- ✅ CORS for localhost only - no auth complexity
- ❌ No custom state management
- ❌ No business logic in API layer

Refer to: `planning/web-ui.md` for full architecture details.

---

## ✅ **Requirements & Deliverables**

### 1. FastAPI Server Setup

**Create:**
- `python/cube/ui/server.py` - Main FastAPI application
- CORS middleware configured for `http://localhost:5173`
- Health check endpoint

**Acceptance Criteria:**
- [ ] FastAPI app created and importable
- [ ] CORS allows requests from React dev server (localhost:5173)
- [ ] Server runs on `http://localhost:3030`
- [ ] `GET /health` returns `{"status": "ok"}`

**Example:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AgentCube UI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}
```

### 2. Task Management Endpoints

**Create:**
- `python/cube/ui/routes/__init__.py`
- `python/cube/ui/routes/tasks.py`

**Endpoints to implement:**

| Method | Path | Purpose | Returns |
|--------|------|---------|---------|
| GET | `/api/tasks` | List all tasks | Array of task summaries |
| GET | `/api/tasks/{id}` | Get task detail | Full task state |
| GET | `/api/tasks/{id}/logs` | Get agent logs | Log entries |

**Acceptance Criteria:**
- [ ] `GET /api/tasks` returns list of tasks from state directory
- [ ] `GET /api/tasks/{id}` uses `load_state()` from `cube.core.state`
- [ ] `GET /api/tasks/{id}/logs` reads agent log files
- [ ] All endpoints return JSON
- [ ] Proper HTTP status codes (200, 404, 500)
- [ ] Error responses are JSON formatted

**Implementation Guide:**
```python
from fastapi import APIRouter, HTTPException
from pathlib import Path
from cube.core.state import load_state, get_sessions_dir

router = APIRouter()

@router.get("/tasks")
async def list_tasks():
    """List all tasks from state files."""
    sessions_dir = get_sessions_dir()
    tasks = []
    
    for state_file in sessions_dir.glob("*/state.json"):
        state = load_state(state_file.parent.name)
        if state:
            tasks.append({
                "id": state_file.parent.name,
                "phase": state.current_phase,
                "path": state.decision_path,
                "status": "active"  # Derive from state
            })
    
    return {"tasks": tasks}

@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """Get detailed task state."""
    state = load_state(task_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    return state.dict()

@router.get("/tasks/{task_id}/logs")
async def get_task_logs(task_id: str):
    """Get agent logs for a task."""
    sessions_dir = get_sessions_dir()
    log_dir = sessions_dir / task_id / "logs"
    
    if not log_dir.exists():
        raise HTTPException(status_code=404, detail="Logs not found")
    
    logs = []
    for log_file in sorted(log_dir.glob("*.log")):
        logs.append({
            "file": log_file.name,
            "content": log_file.read_text()
        })
    
    return {"logs": logs}
```

### 3. Workflow Control Endpoints

**Endpoints to implement:**

| Method | Path | Purpose | Action |
|--------|------|---------|--------|
| POST | `/api/tasks/{id}/writers` | Start dual writers | Calls `launch_dual_writers` |
| POST | `/api/tasks/{id}/panel` | Start judge panel | Calls `launch_judge_panel` |
| POST | `/api/tasks/{id}/feedback` | Send writer feedback | Calls feedback function |

**Acceptance Criteria:**
- [ ] `POST /api/tasks/{id}/writers` delegates to `launch_dual_writers`
- [ ] `POST /api/tasks/{id}/panel` delegates to `launch_judge_panel`
- [ ] `POST /api/tasks/{id}/feedback` sends feedback to writer
- [ ] Endpoints return immediately (use `BackgroundTasks`)
- [ ] Background tasks are logged
- [ ] Request validation with Pydantic models

**CRITICAL: Use Background Tasks!**

Long-running operations (launching writers/panel) take minutes. **Never block the HTTP request!**

```python
from fastapi import BackgroundTasks
from pydantic import BaseModel
from cube.automation.dual_writers import launch_dual_writers
from cube.automation.judge_panel import launch_judge_panel

class WriterRequest(BaseModel):
    prompt_file: str

class FeedbackRequest(BaseModel):
    writer: str  # "writer-a" or "writer-b"
    feedback: str

@router.post("/tasks/{task_id}/writers")
async def start_writers(
    task_id: str, 
    request: WriterRequest, 
    background_tasks: BackgroundTasks
):
    """Start dual writers for a task."""
    prompt_path = Path(request.prompt_file)
    
    if not prompt_path.exists():
        raise HTTPException(404, f"Prompt file not found: {request.prompt_file}")
    
    # Launch in background - returns immediately
    background_tasks.add_task(
        launch_dual_writers,
        task_id,
        prompt_path,
        resume_mode=False
    )
    
    return {
        "status": "started",
        "task_id": task_id,
        "message": "Dual writers launching in background"
    }

@router.post("/tasks/{task_id}/panel")
async def start_panel(task_id: str, background_tasks: BackgroundTasks):
    """Start judge panel for a task."""
    # Launch in background
    background_tasks.add_task(launch_judge_panel, task_id, resume_mode=False)
    
    return {
        "status": "started",
        "task_id": task_id,
        "message": "Judge panel launching in background"
    }
```

### 4. CLI Integration

**Create:**
- `python/cube/commands/ui.py` - New command module

**Acceptance Criteria:**
- [ ] `cube ui` command implemented
- [ ] Starts FastAPI server with uvicorn
- [ ] Auto-opens browser to `http://localhost:3030`
- [ ] Accepts `--port` argument (default 3030)
- [ ] Graceful shutdown on Ctrl+C
- [ ] Command registered in `python/cube/cli.py`

**Implementation:**
```python
# python/cube/commands/ui.py
"""Launch AgentCube web UI."""

import webbrowser
import uvicorn
from typing import Optional


def ui_command(port: int = 3030):
    """
    Launch the AgentCube web UI.
    
    Args:
        port: Port to run server on (default 3030)
    """
    url = f"http://localhost:{port}"
    
    print(f"🚀 Starting AgentCube UI server on {url}")
    print("📊 Dashboard will open in your browser...")
    print("Press Ctrl+C to stop")
    
    # Open browser after short delay
    webbrowser.open(url)
    
    # Start server (blocking)
    uvicorn.run(
        "cube.ui.server:app",
        host="127.0.0.1",
        port=port,
        log_level="info"
    )
```

**Then register in `python/cube/cli.py`:**
```python
# Add import
from cube.commands.ui import ui_command

# Add to CLI group
@cli.command()
@click.option("--port", default=3030, help="Port to run UI server on")
def ui(port: int):
    """Launch AgentCube web UI."""
    ui_command(port)
```

---

## 📋 **Implementation Steps**

Follow these steps in order:

### Step 1: Install Dependencies

```bash
cd /Users/jacob/dev/agent-cube/python
pip install fastapi uvicorn[standard]
```

Update `requirements.txt`:
```bash
echo "fastapi>=0.104.0" >> requirements.txt
echo "uvicorn[standard]>=0.24.0" >> requirements.txt
```

### Step 2: Create Module Structure

```bash
cd /Users/jacob/dev/agent-cube/python/cube
mkdir -p ui/routes
touch ui/__init__.py
touch ui/routes/__init__.py
```

### Step 3: Implement Server Core

Create `python/cube/ui/server.py`:
- [ ] FastAPI app instance
- [ ] CORS middleware
- [ ] Health check endpoint
- [ ] Include task router

### Step 4: Implement Task Endpoints

Create `python/cube/ui/routes/tasks.py`:
- [ ] Router instance
- [ ] Pydantic models for requests
- [ ] GET /tasks - list tasks
- [ ] GET /tasks/{id} - get task detail
- [ ] GET /tasks/{id}/logs - get logs

### Step 5: Implement Workflow Endpoints

In `python/cube/ui/routes/tasks.py`:
- [ ] POST /tasks/{id}/writers
- [ ] POST /tasks/{id}/panel
- [ ] POST /tasks/{id}/feedback
- [ ] Use BackgroundTasks for all

### Step 6: Create CLI Command

Create `python/cube/commands/ui.py`:
- [ ] Import uvicorn and webbrowser
- [ ] Implement ui_command function
- [ ] Open browser to localhost:3030
- [ ] Start uvicorn server

Register in `python/cube/cli.py`:
- [ ] Import ui_command
- [ ] Add @cli.command() for ui

### Step 7: Test Manually

```bash
# Test server directly
cd /Users/jacob/dev/agent-cube/python
uvicorn cube.ui.server:app --reload

# In another terminal, test endpoints
curl http://localhost:3030/health
curl http://localhost:3030/api/tasks

# Test CLI command
cube ui
```

### Step 8: Verify Everything Works

- [ ] Server starts without errors
- [ ] Health endpoint returns 200
- [ ] Task list endpoint works
- [ ] CORS headers present in responses
- [ ] `cube ui` opens browser
- [ ] No blocking on workflow endpoints

---

## 🚫 **Anti-Patterns - DON'T DO THESE!**

### ❌ 1. Don't Reimplement Workflow Logic

**BAD:**
```python
@router.post("/tasks/{task_id}/writers")
async def start_writers(task_id: str, prompt_file: str):
    # DON'T: Copy logic from cube.automation
    config = load_config()
    writer_a_model = config.writers.writer_a
    writer_b_model = config.writers.writer_b
    
    # Setting up worktrees...
    # Spawning agents...
    # Managing state...
    # (100+ lines of duplicated code)
```

**GOOD:**
```python
@router.post("/tasks/{task_id}/writers")
async def start_writers(task_id: str, request: WriterRequest, bg: BackgroundTasks):
    # DO: Delegate to existing function
    bg.add_task(launch_dual_writers, task_id, Path(request.prompt_file))
    return {"status": "started"}
```

### ❌ 2. Don't Block on Long Operations

**BAD:**
```python
@router.post("/tasks/{task_id}/writers")
async def start_writers(task_id: str, prompt_file: str):
    # DON'T: Wait for completion (takes minutes!)
    await launch_dual_writers(task_id, Path(prompt_file))
    return {"status": "completed"}  # Client times out!
```

**GOOD:**
```python
@router.post("/tasks/{task_id}/writers")
async def start_writers(task_id: str, request: WriterRequest, bg: BackgroundTasks):
    # DO: Return immediately
    bg.add_task(launch_dual_writers, task_id, Path(request.prompt_file))
    return {"status": "started"}  # Returns in milliseconds
```

### ❌ 3. Don't Skip Error Handling

**BAD:**
```python
@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    state = load_state(task_id)
    return state.dict()  # Crashes if state is None!
```

**GOOD:**
```python
@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    state = load_state(task_id)
    if not state:
        raise HTTPException(404, f"Task {task_id} not found")
    return state.dict()
```

### ❌ 4. Don't Forget Type Hints

**BAD:**
```python
def ui_command(port=3030):  # No type hints!
    pass
```

**GOOD:**
```python
def ui_command(port: int = 3030) -> None:
    """Launch UI server."""
    pass
```

---

## 📂 **File Structure You're Creating**

```
python/cube/ui/
├── __init__.py              # Empty or minimal exports
├── server.py                # FastAPI app + middleware
└── routes/
    ├── __init__.py          # Empty
    └── tasks.py             # All task/workflow endpoints

python/cube/commands/ui.py   # CLI: cube ui command

python/cube/cli.py           # Updated: register ui command
python/requirements.txt      # Updated: add fastapi, uvicorn
```

**Files you'll modify:**
- `python/cube/cli.py` - Add ui command
- `python/requirements.txt` - Add dependencies

**Files you'll create:**
- `python/cube/ui/__init__.py`
- `python/cube/ui/server.py`
- `python/cube/ui/routes/__init__.py`
- `python/cube/ui/routes/tasks.py`
- `python/cube/commands/ui.py`

---

## 🧪 **Testing Checklist**

Before committing, verify:

### Manual Tests

```bash
# 1. Start server
cube ui

# 2. In another terminal, test endpoints
curl http://localhost:3030/health
# Expected: {"status": "ok"}

curl http://localhost:3030/api/tasks
# Expected: {"tasks": [...]}

curl http://localhost:3030/api/tasks/some-task-id
# Expected: 404 if task doesn't exist, or task JSON if it does

# 3. Test CORS headers
curl -H "Origin: http://localhost:5173" -I http://localhost:3030/health
# Expected: Should see Access-Control-Allow-Origin header

# 4. Test workflow endpoint (will fail without valid task, but should accept)
curl -X POST http://localhost:3030/api/tasks/test/writers \
  -H "Content-Type: application/json" \
  -d '{"prompt_file": "test.md"}'
# Expected: 404 for missing file (correct behavior)
```

### Quality Checks

- [ ] All functions have type hints
- [ ] All endpoints return JSON
- [ ] Error responses have proper status codes
- [ ] No print statements (use logging)
- [ ] CORS headers present
- [ ] Background tasks don't block
- [ ] Browser opens when running `cube ui`

---

## ✅ **Success Criteria**

Your implementation is complete when:

**Functionality:**
- [ ] FastAPI server runs without errors
- [ ] `GET /health` returns 200 OK
- [ ] `GET /api/tasks` lists tasks from state files
- [ ] `GET /api/tasks/{id}` returns task detail
- [ ] `GET /api/tasks/{id}/logs` returns logs
- [ ] `POST /api/tasks/{id}/writers` accepts requests
- [ ] `POST /api/tasks/{id}/panel` accepts requests
- [ ] `cube ui` command launches server + browser

**Code Quality:**
- [ ] Type hints on all functions
- [ ] Pydantic models for request validation
- [ ] Proper error handling (try/except, HTTPException)
- [ ] No duplicated logic from cube.automation
- [ ] Background tasks used for long operations
- [ ] CORS configured correctly

**Documentation:**
- [ ] Docstrings on public functions
- [ ] requirements.txt updated

---

## 🎯 **Final Quality Checklist**

Before committing, ask yourself:

1. **Is this a thin wrapper?**
   - ✅ Direct imports from cube.automation
   - ✅ No business logic in API layer
   - ❌ No duplicated workflow code

2. **Does it follow KISS?**
   - ✅ Simple, straightforward code
   - ✅ No premature abstractions
   - ❌ No unnecessary complexity

3. **Are long operations non-blocking?**
   - ✅ BackgroundTasks for writers/panel
   - ✅ Endpoints return immediately
   - ❌ No await on long operations

4. **Is error handling complete?**
   - ✅ HTTPException for errors
   - ✅ 404 for missing resources
   - ✅ 500 for server errors

---

## 🚨 **FINAL STEPS - CRITICAL**

### YOU MUST COMMIT AND PUSH YOUR CHANGES!

After completing all implementation and tests:

```bash
# 1. Check what you've changed
git status

# 2. Stage your changes
git add python/cube/ui/
git add python/cube/commands/ui.py
git add python/cube/cli.py
git add python/requirements.txt

# 3. Commit with descriptive message
git commit -m "feat(ui): add FastAPI backend with task management endpoints

- Created FastAPI server in cube.ui.server
- Implemented task list/detail/logs endpoints
- Added workflow control endpoints (writers, panel, feedback)
- Created 'cube ui' CLI command with browser auto-launch
- Used BackgroundTasks for non-blocking workflow operations
- Configured CORS for React dev server
- Added fastapi and uvicorn dependencies

Refs: task 02-backend-api"

# 4. Push to your writer branch
git push origin HEAD

# 5. VERIFY push succeeded
git log origin/HEAD..HEAD
# Should show NO unpushed commits (empty output)
```

### ⚠️ **CRITICAL VERIFICATION**

After pushing:

```bash
# Confirm your commit is on remote
git log origin/$(git branch --show-current) -1 --oneline

# Should show your latest commit message
```

**If push fails or shows unpushed commits:**
- Resolve any conflicts
- Push again
- **Do NOT leave unpushed commits!**

---

## 🔗 **Integration Context**

**This task integrates with:**

- **Imports from:**
  - `cube.automation.dual_writers` - Writer orchestration
  - `cube.automation.judge_panel` - Judge orchestration
  - `cube.core.state` - Task state management
  - `cube.core.config` - Configuration loading

- **Used by (future tasks):**
  - Task 05: Task Detail View (calls your endpoints)
  - Task 06: Decisions UI (calls workflow endpoints)

**Future enhancement:**
- Task 05 will add SSE streaming endpoint (`/api/tasks/{id}/stream`)

---

## 📚 **Reference Documentation**

**Key files to reference:**
- `planning/web-ui.md` - Complete architecture spec
- `python/cube/automation/dual_writers.py` - Writer function signatures
- `python/cube/core/state.py` - State management functions

**External docs:**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [Uvicorn Server](https://www.uvicorn.org/)

---

## 💡 **Implementation Tips**

1. **Start simple:** Get health endpoint working first
2. **Test incrementally:** Don't implement everything then test
3. **Use existing functions:** Import from cube.core and cube.automation
4. **Type everything:** mypy will catch bugs early
5. **Log requests:** Helps with debugging
6. **Background tasks:** Always use for writers/panel
7. **Error handling:** Every endpoint needs try/except or HTTPException

---

## ❓ **Troubleshooting**

**"CORS error in browser"**
→ Check CORSMiddleware configuration, ensure localhost:5173 is in allow_origins

**"Server won't start"**
→ Check port 3030 isn't already in use: `lsof -i :3030`

**"Import errors from cube.automation"**
→ Ensure you're in the python/ directory, cube package is installed

**"BackgroundTasks not working"**
→ Check function signature: `async def endpoint(bg: BackgroundTasks)`

**"Task endpoints return empty list"**
→ Check get_sessions_dir() path, verify state files exist

---

## 🎉 **You're Done When...**

✅ Server starts with `cube ui`
✅ Browser opens automatically
✅ All endpoints tested with curl
✅ CORS headers present
✅ Type hints everywhere
✅ Error handling complete
✅ Changes committed
✅ **Changes pushed to remote branch**

---

**Remember:** This is a thin wrapper. Keep it simple. Delegate to existing code. Don't reinvent the wheel!

Good luck! 🚀
