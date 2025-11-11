# Web UI Implementation

**Status:** Planning Complete ✅

**Planning Doc:** `../../planning/web-ui.md`

---

## 📋 Phase Organization

### Phase Structure (Dependency-Driven)

This implementation is organized into **4 phases** with **6 tasks** based on dependency analysis.

**See:** `PHASES.md` for complete dependency analysis and phase discovery process.

**Estimated Total Time:**
- **Wall time:** 12-17 hours (with parallelization)
- **Total effort:** 16-23 hours (sum of all tasks)
- **Efficiency gain:** 21-26% from parallelization

---

### Phase 00: Foundation (Parallel) ✅

**Goal:** Establish independent frontend and backend foundations

**Tasks:**
- **01: Project Scaffold** (2-3h) - `phase-00/tasks/01-project-scaffold.md`
- **02: Backend API** (3-4h) - `phase-00/tasks/02-backend-api.md`

**Why parallel?** Zero file overlap (01=frontend, 02=backend)

**Gate:** Both servers run, CORS works, basic endpoints respond

---

### Phase 01: Core Components ⚙️

**Goal:** Build reusable thinking box components

**Tasks:**
- **03: Thinking Boxes** (3-4h) - `phase-01/tasks/03-thinking-boxes.md`

**Dependencies:** Phase 00 complete (needs React structure from Task 01)

**Gate:** Components render with mock data, match CLI aesthetic

---

### Phase 02: Basic Views (Parallel) 📊

**Goal:** Implement non-streaming pages

**Tasks:**
- **04: Dashboard** (2-3h) - `phase-02/tasks/04-dashboard.md`
- **06: Decisions UI** (2-3h) - `phase-02/tasks/06-decisions-ui.md`

**Why parallel?** Different pages, same dependencies, zero conflicts

**Dependencies:** Phase 00 complete (needs routing + API)

**Gate:** Navigation works, API endpoints validated, pages display data

---

### Phase 03: Real-Time Integration ⭐ (Core Feature)

**Goal:** Implement SSE streaming - the heart of AgentCube UI

**Tasks:**
- **05: Task Detail View** (4-6h) - `phase-03/tasks/05-task-detail-view.md`

**Dependencies:** Phase 00, 01, 02 all complete

**Why single task?** Integration point, tightly coupled backend + frontend

**Gate:** End-to-end test passes (run cube writers, watch real-time updates in browser)

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

### Phase Execution Flow

```
Phase 00: Foundation (3-4h wall time)
├─ Task 01: Frontend Scaffold ────┐
└─ Task 02: Backend API ───────────┤ Parallel
                                   ↓
Phase 01: Core Components (3-4h)
└─ Task 03: Thinking Boxes ────────┐ Sequential
                                   ↓
Phase 02: Basic Views (2-3h wall time)
├─ Task 04: Dashboard ─────────────┐
└─ Task 06: Decisions UI ──────────┤ Parallel
                                   ↓
Phase 03: Real-Time Integration (4-6h)
└─ Task 05: Task Detail with SSE ──┐ Sequential, Integration
                                   ↓
                              ✅ Complete
```

**Critical Path:** Phase 00 → Phase 01 → Phase 03 (12-13 hours)  
**Parallel Gains:** Phase 00 (43% gain), Phase 02 (50% gain)

### Path Ownership (Zero Conflicts)

| Phase | Task | Owned Paths |
|-------|------|-------------|
| 00 | 01 | `web-ui/` (entire frontend structure) |
| 00 | 02 | `python/cube/ui/` (entire backend) |
| 01 | 03 | `web-ui/src/components/Thinking*.tsx` |
| 02 | 04 | `web-ui/src/pages/Dashboard.tsx`, `components/TaskCard.tsx` |
| 02 | 06 | `web-ui/src/pages/Decisions.tsx`, `components/Judge*.tsx`, `components/SynthesisView.tsx` |
| 03 | 05 | Backend: `routes/stream.py`, `sse_layout.py`<br>Frontend: `hooks/useSSE.ts`, `pages/TaskDetail.tsx`, `components/OutputStream.tsx` |

**Zero file overlap between parallel tasks** - perfect for dual-writer workflow!

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

