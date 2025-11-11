# Agent Cube Web UI

**Goal:** Lightweight React SPA to manage multiple autonomous workflows in parallel

## Overview

A web interface that wraps the existing `cube-py` CLI to provide:
- Visual workflow monitoring (multiple tasks simultaneously)
- Real-time thinking boxes (like terminal Rich Layout)
- Progress tracking and phase visualization
- Command execution interface
- Decision review and approval UI

## Architecture Principles

### **1. Thin Client**
- UI calls existing `cube-py` CLI (no reimplementation)
- Python handles all logic (workflows, agents, decisions)
- UI is pure visualization + command execution

### **2. Real-time Updates**
- WebSocket or SSE for streaming agent output
- Live thinking boxes (React components)
- Progress bars for phases

### **3. Multi-workflow Management**
- Dashboard showing all active tasks
- Drill-down to individual task details
- Side-by-side comparison of writers

## Technical Stack

**Frontend:**
- React 18+ (hooks, suspense)
- Vite (fast dev server, HMR)
- TailwindCSS (styling)
- Zustand (state management)
- React Query (server state)

**Backend Options:**

**Option A: CLI Wrapper (Simplest)**
```python
# Tiny FastAPI server
@app.post("/api/auto/{task_id}")
async def run_auto(task_id: str):
    proc = subprocess.Popen(["cube", "auto", task_id], stdout=PIPE)
    return StreamingResponse(stream_output(proc))
```

**Option B: Direct Python (Better)**
```python
# Import cube modules directly
from cube.commands.orchestrate import orchestrate_auto_command

@app.post("/api/auto/{task_id}")
async def run_auto(task_id: str):
    await orchestrate_auto_command(task_file, 1)
```

**Recommendation:** Option B (direct imports, better integration)

## UI Components

### **Dashboard View**
```
┌─────────────────────────────────────────────┐
│ Agent Cube - Active Workflows               │
├─────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────┐ │
│ │ 05-feature-flags                         │ │
│ │ Phase 7/10 (70%) │ SYNTHESIS │ Writer B │ │
│ │ ███████░░░                               │ │
│ └─────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────┐ │
│ │ 04-exemplar                              │ │
│ │ Phase 4/10 (40%) │ Panel Running        │ │
│ │ ████░░░░░░                               │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ [+ New Workflow]                            │
└─────────────────────────────────────────────┘
```

### **Task Detail View**
```
┌─────────────────────────────────────────────┐
│ 05-feature-flags-server                     │
│ Phase 7/10 (70%) - SYNTHESIS                │
├─────────────────────────────────────────────┤
│ ┌─ Writer A Thinking ─────────────────────┐ │
│ │ Addressing synthesis feedback...         │ │
│ │ Fixing circuit breaker timeout...        │ │
│ │ Running tests...                         │ │
│ └──────────────────────────────────────────┘ │
│ ┌─ Writer B Thinking ─────────────────────┐ │
│ │ Implementing type-safe registry...       │ │
│ │ Adding JSDoc comments...                 │ │
│ │ Validating against spec...               │ │
│ └──────────────────────────────────────────┘ │
│                                             │
│ 📖 Output:                                  │
│ [Writer A] 📖 src/circuit-breaker.ts        │
│ [Writer A]    ✅ 89 lines                   │
│ [Writer B] 📝 src/registry.ts               │
│ [Writer B]    ✅ 156 lines                  │
│                                             │
│ [Pause] [Continue] [Restart Phase]          │
└─────────────────────────────────────────────┘
```

### **Decisions View**
```
┌─────────────────────────────────────────────┐
│ Panel Decisions - 05-feature-flags          │
├─────────────────────────────────────────────┤
│ Judge 1: APPROVED → Winner B (7.8 vs 9.2)   │
│ Judge 2: REQUEST_CHANGES → Winner B         │
│   • Circuit breaker timeout missing         │
│   • Type safety issues                      │
│ Judge 3: APPROVED → Winner B                │
│                                             │
│ Consensus: APPROVED (2/3)                   │
│ Winner: Writer B (Codex)                    │
│ Next: SYNTHESIS                             │
│                                             │
│ [View Judge 1 Details] [View Judge 2]       │
└─────────────────────────────────────────────┘
```

## API Endpoints

```python
# Workflow management
POST   /api/workflows              # Start new workflow
GET    /api/workflows              # List all active
GET    /api/workflows/{task_id}    # Get status
DELETE /api/workflows/{task_id}    # Clean up

# Real-time streaming
GET    /api/workflows/{task_id}/stream  # SSE stream

# Commands
POST   /api/workflows/{task_id}/resume/{agent}
POST   /api/workflows/{task_id}/decide
GET    /api/workflows/{task_id}/logs/{agent}

# Decisions
GET    /api/decisions/{task_id}/panel
GET    /api/decisions/{task_id}/peer-review
```

## File Structure

```
packages/web-ui/
├── src/
│   ├── components/
│   │   ├── Dashboard.tsx
│   │   ├── TaskDetail.tsx
│   │   ├── ThinkingBox.tsx        # Dual/triple boxes
│   │   ├── OutputStream.tsx       # Tool calls, messages
│   │   ├── DecisionCard.tsx       # Judge decisions
│   │   └── PhaseProgress.tsx      # Visual phase tracker
│   ├── hooks/
│   │   ├── useWorkflowStream.ts   # SSE hook
│   │   ├── useWorkflowStatus.ts   # React Query
│   │   └── useDecisions.ts        # Load decisions
│   ├── api/
│   │   └── client.ts              # API client
│   └── App.tsx
├── server/
│   ├── main.py                    # FastAPI server
│   ├── routers/
│   │   ├── workflows.py
│   │   └── decisions.py
│   └── streaming.py               # SSE implementation
├── package.json
├── vite.config.ts
└── tailwind.config.js
```

## Agent Tasks Breakdown

### **Phase 1: Foundation**

**Task 01: Project Scaffold**
- Set up Vite + React + TypeScript
- Configure TailwindCSS
- Basic routing (dashboard, task detail)
- Build pipeline
- **Deliverable:** `npm run dev` shows empty dashboard

**Task 02: FastAPI Backend**
- Lightweight FastAPI server
- Import `cube.commands` modules
- Basic endpoints: `/workflows`, `/workflows/{id}/status`
- CORS configuration
- **Deliverable:** API responds to requests, returns mock data

### **Phase 2: Core Visualization**

**Task 03: Real-time Stream Integration**
- SSE endpoint streaming agent output
- React hook `useWorkflowStream`
- Parse JSON stream (same as terminal)
- Display tool calls and messages
- **Deliverable:** See live agent output in browser

**Task 04: Thinking Boxes Component**
- React component matching Rich Layout
- Dual boxes for writers
- Triple boxes for judges
- Real-time updates from stream
- **Deliverable:** Thinking boxes update live

### **Phase 3: Workflow Management**

**Task 05: Dashboard & Status Display**
- List all active workflows
- Phase progress visualization
- Start new workflow form
- Navigate to task details
- **Deliverable:** Dashboard shows active tasks, can drill down

**Task 06: Command Execution Interface**
- Buttons for resume, decide, clean
- Form inputs for messages
- Execute Python commands
- Show results
- **Deliverable:** Can control workflows from UI

### **Phase 4: Polish**

**Task 07: Decision Review UI**
- Display judge decisions (panel + peer)
- Show scores, blockers, recommendations
- Aggregate view with winner highlighting
- **Deliverable:** Beautiful decision cards

**Task 08: Multi-workflow Parallel View**
- Side-by-side task comparison
- Grid layout for 2-4 tasks
- Synchronized scrolling
- **Deliverable:** Monitor multiple tasks at once

## Non-functional Requirements

**Performance:**
- Initial load: <2s
- Stream latency: <100ms
- UI responsive at 60fps

**Reliability:**
- Handle disconnects gracefully
- Reconnect to existing workflows
- Don't lose state on refresh

**Security:**
- Localhost only (no auth needed)
- Or simple token auth for network access

## Implementation Notes

### **Streaming Strategy**

```python
# SSE endpoint
@app.get("/api/workflows/{task_id}/stream")
async def stream_workflow(task_id: str):
    async def generate():
        # Run orchestrate_auto in background
        # Yield JSON events as they happen
        # Format: data: {type: "thinking", agent: "A", text: "..."}
        
    return StreamingResponse(generate(), media_type="text/event-stream")
```

### **State Sync**

```python
# UI polls for status
useQuery(['workflow', taskId], async () => {
  const res = await fetch(`/api/workflows/${taskId}/status`)
  return res.json()  // { current_phase, winner, decisions: {...} }
}, { refetchInterval: 2000 })
```

### **Thinking Boxes**

```tsx
// Match terminal Rich Layout
<div className="space-y-2">
  <ThinkingBox title="Writer A" color="green">
    {writerAThoughts.slice(-3).map(t => <p>{t}</p>)}
  </ThinkingBox>
  <ThinkingBox title="Writer B" color="blue">
    {writerBThoughts.slice(-3).map(t => <p>{t}</p>)}
  </ThinkingBox>
</div>

// Auto-scroll output below
<OutputPane messages={messages} />
```

## Success Criteria

**MVP (Tasks 01-04):**
- ✅ Can start workflow from UI
- ✅ See real-time thinking boxes
- ✅ View tool calls and output
- ✅ Monitor one workflow end-to-end

**Full Feature (Tasks 05-08):**
- ✅ Dashboard with all active tasks
- ✅ Control workflows (resume, decide, clean)
- ✅ Beautiful decision visualization
- ✅ Manage 4+ parallel workflows

## Deployment

**Development:**
```bash
cd packages/web-ui
npm run dev          # Frontend on :5173
npm run server       # Backend on :8000
```

**Production:**
```bash
npm run build        # Static bundle
python server/main.py --host 0.0.0.0  # Serves built files + API
```

Single binary deployment option later.

## Future Enhancements

- PR preview links
- Cost tracking per workflow
- Model performance analytics
- Judge agreement heatmaps
- Workflow templates
- Saved prompts library

---

**This UI makes Agent Cube accessible to non-technical users!** 🎨✨

