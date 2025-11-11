# Web UI Architecture

**Purpose:** Define the architecture for a lightweight React-based web interface for AgentCube that mirrors the CLI's thinking box visualization and adds multi-workflow dashboard capabilities.

**Related Docs:** This is a standalone UI layer over existing `cube.automation` and `cube.core` Python modules.

---

## 🎯 **Principles**

**Core principles for this architecture:**

1. **KISS - Keep It Simple, Stupid**
   - Thin UI layer over robust Python backend
   - No complex state management (React Context sufficient)
   - Direct reuse of `cube.automation` modules (no duplication)
   - Why it matters: UI is display layer only, all logic stays in proven Python code

2. **Real-time First**
   - SSE (Server-Sent Events) for live streaming
   - Thinking boxes update in real-time like CLI
   - No polling, no unnecessary complexity
   - Why it matters: Core AgentCube UX is watching agents think in real-time

3. **Local-Only, Development Tool**
   - No authentication (runs on localhost)
   - No database (uses existing JSON state files)
   - No deployment complexity (single `cube ui` command)
   - Trade-offs: Not production-ready, not multi-user, perfect for local development

---

## 📋 **Requirements**

### **Frontend Stack**

**Must have:**
- React 18+ with TypeScript (strict mode)
- Vite for dev server and build
- Tailwind CSS for styling (minimal custom CSS)
- React Router for navigation
- EventSource API for SSE

**Example (good):**
```typescript
// Simple component, no over-engineering
interface ThinkingBoxProps {
  title: string;
  lines: string[];
}

export function ThinkingBox({ title, lines }: ThinkingBoxProps) {
  return (
    <div className="border border-gray-700 rounded p-4">
      <h3 className="text-sm text-gray-400 mb-2">{title}</h3>
      <div className="space-y-1">
        {lines.map((line, i) => (
          <p key={i} className="text-xs text-gray-300">{line}</p>
        ))}
      </div>
    </div>
  );
}
```

**Example (bad):**
```typescript
// Over-engineered with unnecessary abstractions
class ThinkingBoxManager {
  private state: ThinkingBoxState;
  private renderer: IRenderer;
  private strategy: IDisplayStrategy;
  
  // YAGNI - we don't need this complexity!
}
```

### **Backend Stack**

**Must have:**
- FastAPI (Python async web framework)
- Direct imports from `cube.automation` and `cube.core`
- SSE streaming (no WebSocket complexity)
- CORS enabled for localhost

**Example (good):**
```python
# Direct reuse of existing modules
from cube.automation.dual_writers import launch_dual_writers
from cube.core.state import load_state

@app.post("/api/tasks/{task_id}/writers")
async def start_writers(task_id: str, prompt_file: str):
    # Thin wrapper, delegates to proven code
    await launch_dual_writers(task_id, Path(prompt_file), resume_mode=False)
    return {"status": "started"}
```

**Example (bad):**
```python
# Reimplementing existing logic
@app.post("/api/tasks/{task_id}/writers")
async def start_writers(task_id: str, prompt_file: str):
    # BAD: Duplicating cube.automation logic
    # Read config, setup worktrees, spawn agents...
    # (hundreds of lines duplicating existing code)
```

### **Real-time Streaming**

**Must have:**
- SSE endpoint for each active agent
- Stream thinking, tool calls, and output
- Frontend reconnects on disconnect
- Backend cleans up on client disconnect

**Architecture:**
```
Browser                 FastAPI                cube.automation
  |                        |                         |
  |-- EventSource -------> |                         |
  |                        |-- launch_dual_writers ->|
  |                        |                         |
  |<-- SSE: thinking ------|<-- layout.add_thinking--|
  |<-- SSE: output --------|<-- layout.add_output ---|
  |<-- SSE: tool_call -----|<-- format_stream_msg ---|
```

---

## 🚫 **Anti-Patterns**

### **❌ Don't: Build a Complex State Management System**

**Problem:**
- Redux, Zustand, or complex state trees are overkill
- AgentCube state is already in JSON files
- SSE provides real-time updates

**Example (bad):**
```typescript
// Unnecessary Redux store
const agentSlice = createSlice({
  name: 'agents',
  initialState: { ... },
  reducers: { ... }
});
```

**Instead:**
```typescript
// Simple React Context for UI state only
const UIContext = createContext<{
  selectedTask: string | null;
  setSelectedTask: (id: string) => void;
}>({ ... });
```

### **❌ Don't: Reimplement Python Logic in JavaScript**

**Problem:**
- Duplicates proven code
- Creates maintenance burden
- Introduces bugs

**Instead:**
- Backend is thin FastAPI wrapper
- All logic stays in `cube.automation`
- Frontend is pure display layer

### **❌ Don't: Use WebSocket for One-Way Streaming**

**Problem:**
- WebSocket is bidirectional, overkill here
- More complex connection management
- SSE is simpler and sufficient

**Instead:**
- SSE for server→client streaming
- Regular POST/GET for client→server commands

---

## ✅ **Best Practices**

### **✅ Do: Reuse Existing Layouts**

**Why:**
- `DualWriterLayout` and `TripleLayout` already exist
- Same logic for parsing and formatting
- Consistency with CLI UX

**Example:**
```python
# Backend: Intercept layout calls and stream to SSE
class SSELayout:
    def __init__(self, sse_queue: asyncio.Queue):
        self.queue = sse_queue
    
    def add_thinking(self, box_id: str, text: str):
        await self.queue.put({
            "type": "thinking",
            "box": box_id,
            "text": text
        })
```

### **✅ Do: Use Existing State Files**

**Why:**
- `cube.core.state` already manages workflow state
- No need for database
- File-based is simple and works

**Example:**
```python
@app.get("/api/tasks/{task_id}/status")
async def get_status(task_id: str):
    state = load_state(task_id)
    return state.dict() if state else {"error": "not found"}
```

### **✅ Do: Make UI Launchable from CLI**

**Why:**
- Consistent with AgentCube UX
- Single entry point: `cube ui`
- Auto-opens browser

**Example:**
```python
# In cube.commands.ui
def ui_command(port: int = 3030):
    import uvicorn
    import webbrowser
    
    webbrowser.open(f"http://localhost:{port}")
    uvicorn.run("cube.ui.server:app", host="127.0.0.1", port=port)
```

---

## 🔗 **Integration Points**

**This connects with:**

- **`cube.automation`:** Direct imports of `launch_dual_writers`, `launch_judge_panel`, etc.
- **`cube.core.state`:** Read/write workflow state from JSON files
- **`cube.core.config`:** Load models, worktrees, session directories
- **`cube.core.parsers`:** Reuse stream message parsing

**No new planning docs needed** - UI follows existing architecture exactly.

---

## 📐 **Technical Specifications**

### **API Endpoints**

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/tasks` | List all tasks (from state files) |
| GET | `/api/tasks/{id}` | Get task detail and status |
| POST | `/api/tasks/{id}/writers` | Start dual writers |
| POST | `/api/tasks/{id}/panel` | Start judge panel |
| POST | `/api/tasks/{id}/feedback` | Send feedback to writer |
| GET | `/api/tasks/{id}/stream` | SSE stream for task |
| GET | `/api/tasks/{id}/logs` | Get agent logs |

### **Frontend Routes**

| Route | Component | Purpose |
|-------|-----------|---------|
| `/` | Dashboard | List all tasks, status overview |
| `/tasks/:id` | TaskDetail | Live task monitoring with thinking boxes |
| `/tasks/:id/decisions` | Decisions | Judge decisions and synthesis |

### **SSE Message Format**

```typescript
interface SSEMessage {
  type: 'thinking' | 'output' | 'tool_call' | 'status';
  agent?: string;        // "writer-a", "judge-1", etc.
  box?: string;          // For thinking: which box
  content: string;       // The actual message
  timestamp: string;     // ISO 8601
}
```

### **Component Hierarchy**

```
App
├── Dashboard
│   ├── TaskList
│   └── StatusOverview
├── TaskDetail
│   ├── ThinkingBoxes (dual or triple)
│   ├── OutputStream
│   └── ControlPanel
└── Decisions
    ├── JudgeVotes
    └── SynthesisView
```

---

## 📂 **File Structure**

```
python/cube/ui/
├── __init__.py
├── server.py              # FastAPI app
├── routes/
│   ├── __init__.py
│   ├── tasks.py           # Task CRUD endpoints
│   └── stream.py          # SSE streaming
└── sse_layout.py          # SSE adapter for layouts

web-ui/
├── src/
│   ├── main.tsx           # React entry
│   ├── App.tsx            # Router setup
│   ├── components/
│   │   ├── ThinkingBox.tsx
│   │   ├── DualLayout.tsx
│   │   ├── TripleLayout.tsx
│   │   ├── OutputStream.tsx
│   │   └── TaskCard.tsx
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── TaskDetail.tsx
│   │   └── Decisions.tsx
│   ├── hooks/
│   │   └── useSSE.ts      # SSE connection hook
│   └── types/
│       └── index.ts       # TypeScript types
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js

python/cube/commands/ui.py  # CLI: cube ui
```

---

## ❓ **Open Questions / TBD**

### **Auto-refresh vs Manual Control**
- **Status:** Decided
- **Decision:** Auto-refresh on SSE updates, no polling
- **Rationale:** Real-time is core to AgentCube UX

### **Historical Task Viewing**
- **Status:** Phase 2 (not in initial 6 tasks)
- **Default:** Show only active tasks initially
- **Future:** Add completed task archive view

---

## 📚 **References**

**External:**
- [FastAPI Server-Sent Events](https://fastapi.tiangolo.com/advanced/custom-response/#using-streamingresponse-with-file-like-objects)
- [React EventSource / SSE](https://developer.mozilla.org/en-US/docs/Web/API/EventSource)
- [Vite + React + TypeScript Template](https://vitejs.dev/guide/#scaffolding-your-first-vite-project)

**Internal:**
- Existing: `python/cube/core/base_layout.py` - Thinking box logic
- Existing: `python/cube/automation/stream.py` - Message formatting
- Existing: `python/cube/core/state.py` - State management

**Examples:**
- CLI thinking boxes are the reference implementation
- UI should feel like "CLI in the browser"

---

## ✏️ **Revision History**

| Date | Change | Reason |
|------|--------|--------|
| 2025-11-11 | Initial version | Created during AgentCube UI planning |

---

**NOTE:** This is a living document. Update as you learn from implementation!

