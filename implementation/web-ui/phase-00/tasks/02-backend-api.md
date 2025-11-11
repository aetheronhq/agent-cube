# Task 02: Backend API

**Goal:** Create FastAPI server that wraps cube.automation modules and provides REST endpoints for the web UI.

**Time Estimate:** 3-4 hours

---

## 📖 **Context**

**What this builds on:**
- Existing `cube.automation` and `cube.core` modules
- Thin wrapper layer (no logic duplication)
- Foundation for tasks 05 and 06 (SSE streaming)

**Planning docs (Golden Source):**
- `planning/web-ui.md` - API endpoints, backend stack, integration points

---

## ✅ **Requirements**

### **1. FastAPI Server Setup**

**Deliverable:**
- FastAPI application in `python/cube/ui/server.py`
- CORS middleware for localhost
- Basic health check endpoint

**Acceptance criteria:**
- [ ] FastAPI app created and importable
- [ ] CORS configured for `http://localhost:5173`
- [ ] Server runs on `http://localhost:3030`
- [ ] `GET /health` returns `{"status": "ok"}`

### **2. Task Management Endpoints**

**Deliverable:**
- List tasks (from state files)
- Get task detail and status
- Get task logs

**Acceptance criteria:**
- [ ] `GET /api/tasks` returns list of tasks from state directory
- [ ] `GET /api/tasks/{id}` returns task state (uses `load_state`)
- [ ] `GET /api/tasks/{id}/logs` returns agent logs
- [ ] All endpoints return JSON with proper error handling

### **3. Workflow Control Endpoints**

**Deliverable:**
- Start dual writers
- Start judge panel
- Send feedback to writer

**Acceptance criteria:**
- [ ] `POST /api/tasks/{id}/writers` calls `launch_dual_writers`
- [ ] `POST /api/tasks/{id}/panel` calls `launch_judge_panel`
- [ ] `POST /api/tasks/{id}/feedback` calls feedback function
- [ ] Endpoints return immediately (don't block on async tasks)
- [ ] Background tasks tracked and logged

### **4. CLI Integration**

**Deliverable:**
- `cube ui` command to launch server + open browser

**Acceptance criteria:**
- [ ] `python/cube/commands/ui.py` created
- [ ] `cube ui` command registered in `cli.py`
- [ ] Command starts FastAPI server with uvicorn
- [ ] Browser auto-opens to `http://localhost:3030`
- [ ] Graceful shutdown on Ctrl+C

---

## 📝 **Implementation Steps**

**Suggested order:**

1. **Create server module**
   - [ ] Create `python/cube/ui/__init__.py`
   - [ ] Create `python/cube/ui/server.py`
   - [ ] Install FastAPI and uvicorn: `pip install fastapi uvicorn[standard]`

2. **Basic FastAPI app**
   - [ ] Define app with CORS middleware
   - [ ] Add health check endpoint
   - [ ] Test: `uvicorn cube.ui.server:app --reload`

3. **Task endpoints**
   - [ ] Create `python/cube/ui/routes/__init__.py`
   - [ ] Create `python/cube/ui/routes/tasks.py`
   - [ ] Import `load_state`, `get_sessions_dir` from `cube.core`
   - [ ] Implement list/detail endpoints
   - [ ] Implement logs endpoint

4. **Workflow endpoints**
   - [ ] Import `launch_dual_writers`, `launch_judge_panel` from `cube.automation`
   - [ ] Implement async POST endpoints
   - [ ] Use `BackgroundTasks` to run workflows
   - [ ] Add error handling and validation

5. **CLI command**
   - [ ] Create `python/cube/commands/ui.py`
   - [ ] Implement `ui_command(port: int)`
   - [ ] Use `webbrowser.open()` for auto-launch
   - [ ] Register in `cli.py`

6. **Verify**
   - [ ] Test each endpoint with curl or httpie
   - [ ] Test `cube ui` command
   - [ ] Verify CORS headers present
   - [ ] Check error responses

7. **Finalize**
   - [ ] Update `requirements.txt`
   - [ ] Commit changes
   - [ ] Push to branch

---

## 🏗️ **Architecture Constraints**

### **Must Follow**

**Planning docs:**
- Use FastAPI (from `planning/web-ui.md`)
- Direct imports from `cube.automation` (no duplication)
- Thin wrapper pattern (backend does minimal logic)

**Technical constraints:**
- Python 3.10+ async/await
- Type hints on all functions
- Pydantic models for request/response validation
- Proper HTTP status codes

**KISS Principles:**
- ✅ Direct delegation to existing modules
- ✅ No custom state management (use existing JSON files)
- ✅ No database (file-based state is sufficient)
- ❌ No JWT/auth (local-only tool)
- ❌ No complex middleware (just CORS)

---

## 🚫 **Anti-Patterns**

### **❌ DON'T: Reimplement Workflow Logic**

```python
# Bad: Duplicating cube.automation code
@app.post("/api/tasks/{task_id}/writers")
async def start_writers(task_id: str, prompt_file: str):
    # BAD: Copying logic from launch_dual_writers
    config = load_config()
    writer_a = config.writers.writer_a
    writer_b = config.writers.writer_b
    # ... (100+ lines of duplicated code)
```

**Instead:**
```python
# Good: Thin wrapper
@app.post("/api/tasks/{task_id}/writers")
async def start_writers(task_id: str, request: WriterRequest, bg: BackgroundTasks):
    bg.add_task(
        launch_dual_writers,
        task_id,
        Path(request.prompt_file),
        resume_mode=False
    )
    return {"status": "started", "task_id": task_id}
```

### **❌ DON'T: Block on Long-Running Tasks**

```python
# Bad: Blocking the request
@app.post("/api/tasks/{task_id}/writers")
async def start_writers(task_id: str, prompt_file: str):
    await launch_dual_writers(task_id, Path(prompt_file))  # Blocks for minutes!
    return {"status": "completed"}
```

**Instead:**
```python
# Good: Background task
@app.post("/api/tasks/{task_id}/writers")
async def start_writers(task_id: str, request: WriterRequest, bg: BackgroundTasks):
    bg.add_task(launch_dual_writers, task_id, Path(request.prompt_file))
    return {"status": "started"}  # Returns immediately
```

---

## 📂 **Owned Paths**

**This task owns:**
```
python/cube/ui/
├── __init__.py
├── server.py              # FastAPI app
└── routes/
    ├── __init__.py
    └── tasks.py           # Task CRUD endpoints

python/cube/commands/ui.py  # CLI: cube ui
python/cube/cli.py          # Add ui command registration
```

**Must NOT modify:**
- `cube.automation` modules (just import)
- `cube.core` modules (just import)
- Frontend code (Task 01)

**Integration:**
- Imports from `cube.automation.dual_writers`, `cube.automation.judge_panel`
- Imports from `cube.core.state`, `cube.core.config`
- Task 05 will add SSE streaming endpoint

---

## 🧪 **Testing Requirements**

**Manual testing:**
- [ ] `cube ui` starts server and opens browser
- [ ] `GET /health` returns 200
- [ ] `GET /api/tasks` returns task list
- [ ] `POST /api/tasks/test/writers` accepts request (test with dummy task)
- [ ] CORS headers present in responses
- [ ] Server logs show requests

**Test with curl:**
```bash
# Health check
curl http://localhost:3030/health

# List tasks
curl http://localhost:3030/api/tasks

# Get task detail
curl http://localhost:3030/api/tasks/01-my-task

# Start writers (will fail without valid task, but endpoint should accept)
curl -X POST http://localhost:3030/api/tasks/01-test/writers \
  -H "Content-Type: application/json" \
  -d '{"prompt_file": "test.md"}'
```

---

## ✅ **Acceptance Criteria**

**Definition of Done:**

- [ ] FastAPI server created in `python/cube/ui/`
- [ ] CORS configured for localhost:5173
- [ ] Health check endpoint works
- [ ] Task list/detail endpoints work
- [ ] Workflow control endpoints accept requests
- [ ] Background tasks don't block requests
- [ ] `cube ui` command implemented
- [ ] Server auto-opens browser
- [ ] Type hints on all functions
- [ ] Error handling on all endpoints
- [ ] `requirements.txt` updated
- [ ] Changes committed and pushed

**Quality gates:**
- [ ] Follows KISS (thin wrapper, no duplication)
- [ ] No blocking on long operations
- [ ] Proper HTTP status codes
- [ ] JSON error responses

---

## 🔗 **Integration Points**

**Dependencies (requires these first):**
- None (imports from existing cube modules)

**Dependents (these will use this):**
- Task 05: Task detail (calls API endpoints)
- Task 06: Decisions UI (calls decision endpoints)
- Task 05: SSE streaming (will add `/api/tasks/{id}/stream`)

**Integrator task:**
- None (self-contained backend)

---

## 📊 **Examples**

### **server.py**

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

from .routes import tasks
app.include_router(tasks.router, prefix="/api")
```

### **routes/tasks.py**

```python
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pathlib import Path
from pydantic import BaseModel
from cube.core.state import load_state, get_sessions_dir
from cube.automation.dual_writers import launch_dual_writers

router = APIRouter()

class WriterRequest(BaseModel):
    prompt_file: str

@router.get("/tasks")
async def list_tasks():
    sessions_dir = get_sessions_dir()
    tasks = []
    for state_file in sessions_dir.glob("*/state.json"):
        state = load_state(state_file.parent.name)
        if state:
            tasks.append({
                "id": state_file.parent.name,
                "phase": state.current_phase,
                "path": state.decision_path
            })
    return {"tasks": tasks}

@router.post("/tasks/{task_id}/writers")
async def start_writers(task_id: str, request: WriterRequest, bg: BackgroundTasks):
    prompt_path = Path(request.prompt_file)
    if not prompt_path.exists():
        raise HTTPException(404, f"Prompt file not found: {request.prompt_file}")
    
    bg.add_task(launch_dual_writers, task_id, prompt_path, resume_mode=False)
    return {"status": "started", "task_id": task_id}
```

### **commands/ui.py**

```python
import webbrowser
import uvicorn

def ui_command(port: int = 3030):
    """Launch AgentCube web UI."""
    url = f"http://localhost:{port}"
    webbrowser.open(url)
    
    uvicorn.run(
        "cube.ui.server:app",
        host="127.0.0.1",
        port=port,
        log_level="info"
    )
```

---

## 🎓 **Common Pitfalls**

**Watch out for:**
- ⚠️ CORS errors (must allow localhost:5173)
- ⚠️ Blocking on async operations (use BackgroundTasks)
- ⚠️ Missing type hints (causes mypy errors)

**If you see [CORS error], it means [middleware not configured] - fix by [adding CORSMiddleware]**

---

**FINAL STEPS - CRITICAL:**

```bash
# Update requirements
echo "fastapi>=0.104.0" >> python/requirements.txt
echo "uvicorn[standard]>=0.24.0" >> python/requirements.txt

# Stage changes
git add python/cube/ui/ python/cube/commands/ui.py python/cube/cli.py python/requirements.txt

# Commit
git commit -m "feat(ui): add FastAPI backend with task management endpoints"

# Push
git push origin writer-[your-model-slug]/02-backend-api

# Verify
git status
```

**⚠️ IMPORTANT:** Uncommitted or unpushed changes will NOT be reviewed!

---

**Built with:** Agent Cube v1.0
**Template version:** 1.0
**Last updated:** 2025-11-11

