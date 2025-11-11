# Web UI Implementation

**Status:** Planning Complete ✅

**Planning Doc:** `../../planning/web-ui.md`

---

## 📋 Task Breakdown

### Phase Structure

This implementation is organized into **6 parallel-safe tasks** designed for the AgentCube dual-writer workflow.

**Estimated Total Time:** 16-23 hours (2-3 days with dual writers)

---

### Tasks

#### **Task 01: Project Scaffold** (2-3 hours)
- **File:** `tasks/01-project-scaffold.md`
- **Goal:** Set up Vite + React + TypeScript + Tailwind project
- **Deliverables:**
  - Vite project initialized
  - Tailwind CSS configured
  - React Router with 3 routes
  - Dark theme and navigation
- **Dependencies:** None (foundation task)

#### **Task 02: Backend API** (3-4 hours)
- **File:** `tasks/02-backend-api.md`
- **Goal:** FastAPI server wrapping cube.automation modules
- **Deliverables:**
  - FastAPI app with CORS
  - Task management endpoints
  - Workflow control endpoints (start writers, panel)
  - `cube ui` CLI command
- **Dependencies:** None (imports from existing cube modules)

#### **Task 03: Thinking Boxes Component** (3-4 hours)
- **File:** `tasks/03-thinking-boxes.md`
- **Goal:** Dual and triple thinking box layouts
- **Deliverables:**
  - ThinkingBox component (reusable)
  - DualLayout (Writer A + B)
  - TripleLayout (Judge 1, 2, 3)
  - TypeScript types
- **Dependencies:** Task 01 (React structure)

#### **Task 04: Dashboard** (2-3 hours)
- **File:** `tasks/04-dashboard.md`
- **Goal:** Multi-workflow management dashboard
- **Deliverables:**
  - Task list with cards
  - Status overview (active/completed counts)
  - Auto-refresh every 5 seconds
  - Navigation to task detail
- **Dependencies:** Task 01 (routing), Task 02 (API)

#### **Task 05: Task Detail View** (4-6 hours) ⭐ **Core Feature**
- **File:** `tasks/05-task-detail-view.md`
- **Goal:** Real-time SSE streaming of thinking boxes and output
- **Deliverables:**
  - SSE endpoint (`/api/tasks/{id}/stream`)
  - `useSSE` React hook
  - OutputStream component
  - TaskDetail page with live updates
- **Dependencies:** Task 02 (backend), Task 03 (thinking boxes)

#### **Task 06: Decisions UI** (2-3 hours)
- **File:** `tasks/06-decisions-ui.md`
- **Goal:** Display judge votes and synthesis instructions
- **Deliverables:**
  - Decision endpoint
  - JudgeVote component
  - SynthesisView component
  - Decisions page
- **Dependencies:** Task 01 (routing), Task 02 (API)

---

## 📐 Architecture Summary

### Tech Stack
- **Frontend:** React 18 + Vite + TypeScript + Tailwind CSS
- **Backend:** FastAPI (Python async)
- **Real-time:** Server-Sent Events (SSE)
- **State:** Existing JSON state files (no database)

### Key Architectural Decisions

1. **SSE over WebSocket:** Simpler one-way streaming, sufficient for monitoring
2. **Direct Python imports:** Backend wraps `cube.automation`, no logic duplication
3. **Thin UI layer:** All business logic stays in proven Python code
4. **Local-only:** No auth, no deployment complexity, perfect for dev tool
5. **KISS throughout:** Minimal dependencies, simple components, no over-engineering

### File Structure
```
python/cube/ui/              # Backend (FastAPI)
├── server.py
├── sse_layout.py
└── routes/
    ├── tasks.py
    └── stream.py

web-ui/                      # Frontend (React)
├── src/
│   ├── components/          # Reusable UI components
│   ├── pages/               # Route pages
│   ├── hooks/               # React hooks (useSSE)
│   └── types/               # TypeScript types
├── package.json
└── vite.config.ts
```

---

## 🔗 Integration Points

### Backend → Python Modules
- `cube.automation.dual_writers`
- `cube.automation.judge_panel`
- `cube.core.state`
- `cube.core.decision_files`

### Frontend → Backend
- REST API for commands (POST to start workflows)
- SSE for real-time streaming (GET with EventSource)

### Component Hierarchy
```
App
├── Dashboard
│   ├── StatusOverview
│   └── TaskList → TaskCard
├── TaskDetail
│   ├── DualLayout → ThinkingBox (x2)
│   ├── TripleLayout → ThinkingBox (x3)
│   └── OutputStream
└── Decisions
    ├── JudgeVote (x3)
    └── SynthesisView
```

---

## 🚀 Running the UI

Once implemented:

```bash
# Terminal 1: Start UI (backend + frontend)
cube ui

# Or separately:
# Terminal 1: Backend
uvicorn cube.ui.server:app --reload --port 3030

# Terminal 2: Frontend
cd web-ui && npm run dev
```

**Access:** http://localhost:5173

---

## 🎯 Success Criteria

### MVP Features
- ✅ Dashboard lists all tasks with status
- ✅ Real-time thinking boxes (dual and triple)
- ✅ Live output stream
- ✅ Judge decisions display
- ✅ Launch from CLI: `cube ui`

### Quality Gates
- ✅ Follows KISS principle throughout
- ✅ No logic duplication (backend wraps existing modules)
- ✅ Type-safe (TypeScript strict mode)
- ✅ Real-time updates (SSE streaming)
- ✅ Matches CLI aesthetic (dark theme, monospace)

---

## 📝 Implementation Notes

### Task Execution Order

**Parallel Groups:**
- **Group 1 (foundation):** Task 01 + Task 02 can run fully parallel
- **Group 2 (components):** Task 03 + Task 04 depend on Group 1, can run parallel to each other
- **Group 3 (integration):** Task 05 + Task 06 depend on Groups 1 & 2, can run parallel to each other

**Critical Path:** 01 → 03 → 05 (real-time streaming is core feature)

### Path Ownership

Tasks have **clear file ownership** to enable parallel development:
- Task 01: `web-ui/` structure and config
- Task 02: `python/cube/ui/` backend
- Task 03: `web-ui/src/components/Thinking*`
- Task 04: `web-ui/src/components/TaskCard`, `pages/Dashboard`
- Task 05: Both backend SSE and frontend streaming
- Task 06: `web-ui/src/components/Judge*`, `pages/Decisions`

**No overlapping edits** - perfect for dual-writer workflow!

---

## 🎓 Key Learnings from Planning

### What Makes This KISS
- No Redux/Zustand (React Context sufficient)
- No React Query (simple fetch + polling)
- No WebSocket (SSE simpler)
- No database (JSON files work)
- No custom CLI tools (imports existing)

### What Enables Parallel Development
- Clear file ownership per task
- Backend is thin wrapper (no shared logic)
- Components are self-contained
- Pages don't share state

### What Matches CLI UX
- Same thinking box logic (adapted)
- Same message formatting (reused)
- Same phase tracking (state files)
- Dark theme + monospace fonts

---

**Planning completed:** 2025-11-11
**Ready for implementation:** ✅

Use `cube writers` or `cube auto` to execute these tasks!

