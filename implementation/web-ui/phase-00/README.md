# Phase 00: Foundation

**Goal:** Establish independent frontend and backend foundations

**Parallelization:** ✅ Both tasks can run in parallel (zero file overlap)

---

## 📋 Tasks

### Task 01: Project Scaffold (2-3h)
- **File:** `tasks/01-project-scaffold.md`
- **Owner:** Frontend specialist
- **Paths:** `web-ui/` directory
- **Deliverables:**
  - Vite + React + TypeScript + Tailwind project
  - React Router with 3 routes
  - Dark theme and navigation
  - Directory structure

### Task 02: Backend API (3-4h)
- **File:** `tasks/02-backend-api.md`
- **Owner:** Backend specialist
- **Paths:** `python/cube/ui/` directory
- **Deliverables:**
  - FastAPI server with CORS
  - Task management endpoints
  - Workflow control endpoints
  - `cube ui` CLI command

---

## ✅ Phase Gate

**Phase 00 complete when:**
- [ ] `npm run dev` in `web-ui/` works (port 5173)
- [ ] `cube ui` launches FastAPI (port 3030)
- [ ] CORS configured (frontend can call backend)
- [ ] `GET /health` endpoint responds
- [ ] `GET /api/tasks` endpoint responds (even if empty)
- [ ] Basic routes render in frontend (even if blank)

**Verify:**
```bash
# Terminal 1
cd web-ui && npm run dev

# Terminal 2
cube ui

# Terminal 3
curl http://localhost:3030/health
curl http://localhost:3030/api/tasks

# Browser
open http://localhost:5173
# Navigate to /, /tasks/test, /tasks/test/decisions
```

---

## 🔗 Dependencies

**Requires:** None (foundation phase)

**Enables:**
- Phase 01 (needs Task 01 for React structure)
- Phase 02 (needs both tasks for API + routing)
- Phase 03 (needs both tasks for integration)

---

## ⏱️ Estimated Time

**Wall time:** 3-4 hours (parallel execution)  
**Total effort:** 5-7 hours (sum of both tasks)  
**Efficiency gain:** 43% from parallelization

---

## 🎯 Why This Phase?

**Rationale:**
- Completely independent foundations
- No shared files or dependencies
- Different skillsets (frontend vs backend)
- Maximum parallelization opportunity

**Critical for:**
- All subsequent phases depend on this foundation
- Validates that both frontend and backend can run
- Establishes CORS and basic connectivity

