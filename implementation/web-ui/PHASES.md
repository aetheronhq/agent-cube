# Web UI Phase Organization

**Methodology:** AgentCube dependency-driven phase discovery

**Date:** 2025-11-11

---

## 🔍 **Dependency Analysis**

### **Step 1: List Tasks with Dependencies**

| Task | Depends On | Why |
|------|-----------|-----|
| 01: Project Scaffold | None | Foundation - Vite project setup |
| 02: Backend API | None | Foundation - imports existing cube modules |
| 03: Thinking Boxes | Task 01 | Needs React components structure |
| 04: Dashboard | Task 01, 02 | Needs routing (01) and API endpoints (02) |
| 05: Task Detail (SSE) | Task 02, 03 | Needs API base (02) and thinking components (03) |
| 06: Decisions UI | Task 01, 02 | Needs routing (01) and API endpoints (02) |

### **Step 2: Build Dependency Graph**

```
01 (Frontend Scaffold)
  ├─→ 03 (Thinking Boxes)
  │     └─→ 05 (Task Detail - SSE) ←─┐
  ├─→ 04 (Dashboard)                  │
  └─→ 06 (Decisions UI)               │
                                      │
02 (Backend API)                      │
  ├─→ 04 (Dashboard)                  │
  ├─→ 05 (Task Detail - SSE) ←────────┘
  └─→ 06 (Decisions UI)
```

### **Step 3: Identify Parallelization Opportunities**

**Can run in parallel:**
- Tasks 01 & 02 (independent foundations)
- Tasks 04 & 06 (same dependencies, different files)
- Tasks 03 alone (depends on 01 only)
- Task 05 is integration point (depends on multiple)

### **Step 4: Critical Path Analysis**

**Critical Path:** 01 → 03 → 05 (Real-time streaming)

**Why Task 05 is critical:**
- Core AgentCube UX (watching agents think)
- Most complex (backend + frontend integration)
- Touches both SSE endpoint and React components
- Integration point for thinking boxes

---

## 📊 **Phase Structure (Discovered)**

### **Phase 00: Foundation** (Parallel)

**Goal:** Establish independent foundations

**Tasks:**
- ✅ **Task 01:** Project Scaffold (2-3h)
- ✅ **Task 02:** Backend API (3-4h)

**Why parallel?**
- Zero file overlap
- 01 = frontend only (`web-ui/`)
- 02 = backend only (`python/cube/ui/`)
- No shared dependencies

**Gate:** 
- [ ] Vite dev server runs
- [ ] FastAPI server runs
- [ ] Both can be started independently

**Estimated:** 3-4 hours wall time (parallel) / 5-7 hours total effort

---

### **Phase 01: Core Components** (Sequential to Phase 00)

**Goal:** Build reusable UI components

**Tasks:**
- ✅ **Task 03:** Thinking Boxes (3-4h)

**Why sequential?**
- Depends on Task 01 (React structure, Tailwind)
- No parallel opportunity (only one task)

**Why separate phase?**
- Thinking boxes are foundation for Phase 02
- Clean separation of component layer

**Gate:**
- [ ] ThinkingBox component renders
- [ ] DualLayout and TripleLayout work
- [ ] Components match CLI aesthetic

**Estimated:** 3-4 hours

---

### **Phase 02: Basic Views** (Parallel, depends on Phase 00)

**Goal:** Implement non-streaming pages

**Tasks:**
- ✅ **Task 04:** Dashboard (2-3h)
- ✅ **Task 06:** Decisions UI (2-3h)

**Why parallel?**
- Both depend on Phase 00 (Tasks 01 & 02)
- Different file ownership:
  - Task 04: `Dashboard.tsx`, `TaskCard.tsx`
  - Task 06: `Decisions.tsx`, `JudgeVote.tsx`, `SynthesisView.tsx`
- No shared components
- Simple API calls (no SSE complexity)

**Why before Task 05?**
- Validates API endpoints work
- Tests routing works
- Builds confidence before complex SSE integration

**Gate:**
- [ ] Dashboard lists tasks
- [ ] Navigation between pages works
- [ ] Decisions page shows judge votes
- [ ] All API endpoints responding

**Estimated:** 2-3 hours wall time (parallel) / 4-6 hours total effort

---

### **Phase 03: Real-Time Integration** (Sequential, depends on Phase 01 & 02)

**Goal:** Implement core SSE streaming feature

**Tasks:**
- ✅ **Task 05:** Task Detail View with SSE (4-6h)

**Why sequential?**
- Depends on Task 02 (backend API structure)
- Depends on Task 03 (thinking box components)
- Most complex integration
- Touches both backend and frontend
- Core feature that ties everything together

**Why separate phase?**
- Integration point (combines previous work)
- Most likely to reveal issues
- Highest risk/complexity
- Real-time streaming is THE core UX

**Why only one task?**
- SSE endpoint and frontend hook are tightly coupled
- Backend SSELayout and frontend useSSE must work together
- Better to have one person/pair handle both sides

**Gate:**
- [ ] SSE endpoint streams messages
- [ ] Frontend receives and displays thinking in real-time
- [ ] Output stream shows tool calls
- [ ] Reconnection works
- [ ] End-to-end: Run `cube writers` → UI updates live

**Estimated:** 4-6 hours

---

## 📈 **Phase Progression Summary**

```
Phase 00: Foundation (Parallel)
├─ Task 01: Frontend Scaffold
└─ Task 02: Backend API
      ↓ (both complete)

Phase 01: Core Components
└─ Task 03: Thinking Boxes
      ↓ (components ready)

Phase 02: Basic Views (Parallel)
├─ Task 04: Dashboard
└─ Task 06: Decisions UI
      ↓ (views work, API validated)

Phase 03: Real-Time Integration
└─ Task 05: Task Detail with SSE
      ↓ (complete system)

✅ Web UI Complete
```

**Total Time:**
- **Wall time:** 12-17 hours (with parallelization)
- **Total effort:** 16-23 hours (sum of all tasks)
- **Efficiency gain:** 21-26% from parallelization

---

## 🎯 **Why This Phase Structure?**

### **Design Principles Applied**

1. **Maximize Parallelization (P2) without threatening Quality (P1)**
   - Phase 00: 2 parallel tasks (zero overlap)
   - Phase 02: 2 parallel tasks (different pages)
   - Phases 01 & 03: Sequential (dependencies require it)

2. **Clear Gates Between Phases**
   - Phase 00: Both servers run
   - Phase 01: Components render
   - Phase 02: Pages navigate, API responds
   - Phase 03: Real-time streaming works end-to-end

3. **Risk Management**
   - Simple tasks early (01, 02)
   - Complex integration last (05)
   - Validate basics before advanced features

4. **Integration Points Explicit**
   - Phase 03 is THE integration phase
   - Combines backend (02), components (03), routing (01)
   - Single task handles both sides of SSE

### **Alternative Considered: Why Not Parallel 03, 04, 06?**

**Rejected because:**
- Task 03 (Thinking Boxes) is a dependency for Task 05
- Better to complete components before starting views
- Separating Phase 01 from Phase 02 creates cleaner gate
- Allows validation of component layer before page layer

**Could work but:**
- More complex mental model
- Harder to validate progress
- No significant time savings (03 is solo anyway)

---

## 🔄 **Iteration Notes**

### **First Pass** (before this document)
- Had 6 tasks in flat structure
- No explicit phases
- Parallelization implied but not explicit

### **Second Pass** (this document)
- Analyzed dependencies deeply
- Discovered 4 natural phases
- Made parallelization explicit
- Identified integration point (Phase 03)

### **Key Insights**
- Task 05 is integration point (like Integrator in v2)
- Phases 00 and 02 enable parallelization
- Phase 01 is small but necessary (component foundation)
- Phase 03 is high-risk, high-value (core feature)

---

## 📋 **Updated Task Files**

All task files will be updated with phase information:
- Header: `**Phase:** 00` (or 01, 02, 03)
- Dependencies: Clear links to previous phase gates
- Integration notes: What this enables for later phases

---

## ✅ **Phase Gates (Checklist)**

### **Phase 00 Complete When:**
- [ ] `npm run dev` in web-ui/ works (port 5173)
- [ ] `cube ui` launches FastAPI (port 3030)
- [ ] CORS configured (frontend can call backend)
- [ ] Health check endpoint responds
- [ ] Basic routes render (even if empty)

### **Phase 01 Complete When:**
- [ ] `<ThinkingBox>` component renders
- [ ] `<DualLayout>` shows two boxes
- [ ] `<TripleLayout>` shows three boxes
- [ ] Mock data displays correctly
- [ ] Text truncation works

### **Phase 02 Complete When:**
- [ ] Dashboard lists tasks from API
- [ ] Clicking task navigates to detail page
- [ ] Decisions page displays judge votes
- [ ] All navigation links work
- [ ] Auto-refresh polls API

### **Phase 03 Complete When:**
- [ ] SSE endpoint streams events
- [ ] Frontend connects via EventSource
- [ ] Thinking boxes update in real-time
- [ ] Output stream shows messages
- [ ] Reconnection works
- [ ] **END-TO-END TEST PASSES:**
  ```bash
  # Terminal 1
  cube ui
  
  # Terminal 2
  cube writers test-task test.md
  
  # Browser: Watch real-time updates
  ```

---

## 🚀 **Execution Strategy**

### **For Dual-Writer Workflow:**

```bash
# Phase 00 (both in parallel)
cube writers 01-project-scaffold implementation/web-ui/phase-00/tasks/01-project-scaffold.md
cube writers 02-backend-api implementation/web-ui/phase-00/tasks/02-backend-api.md

# Wait for both, validate Phase 00 gate

# Phase 01 (sequential, no parallel option)
cube writers 03-thinking-boxes implementation/web-ui/phase-01/tasks/03-thinking-boxes.md

# Wait, validate Phase 01 gate

# Phase 02 (both in parallel)
cube writers 04-dashboard implementation/web-ui/phase-02/tasks/04-dashboard.md
cube writers 06-decisions-ui implementation/web-ui/phase-02/tasks/06-decisions-ui.md

# Wait for both, validate Phase 02 gate

# Phase 03 (sequential, integration)
cube writers 05-task-detail-view implementation/web-ui/phase-03/tasks/05-task-detail-view.md

# Validate Phase 03 gate → DONE
```

### **For Autonomous Workflow:**

```bash
# Let orchestrator handle phases
cube auto implementation/web-ui/phase-00/tasks/01-project-scaffold.md
# Continue through phases...
```

---

## 📊 **Dependency Matrix**

|          | 01 | 02 | 03 | 04 | 05 | 06 |
|----------|----|----|----|----|----|----|
| **01**   | -  | ❌ | ❌ | ❌ | ❌ | ❌ |
| **02**   | ❌ | -  | ❌ | ❌ | ❌ | ❌ |
| **03**   | ✅ | ❌ | -  | ❌ | ❌ | ❌ |
| **04**   | ✅ | ✅ | ❌ | -  | ❌ | ❌ |
| **05**   | ❌ | ✅ | ✅ | ❌ | -  | ❌ |
| **06**   | ✅ | ✅ | ❌ | ❌ | ❌ | -  |

Legend:
- ✅ = Depends on
- ❌ = Independent

**Critical Path:** 01 → 03 → 05 (12-13 hours)
**Parallel Paths:** 02 (3-4h), 04+06 (4-6h parallel)

---

**Phases discovered through dependency analysis ✅**

**Ready for execution with proper phase gates ✅**

