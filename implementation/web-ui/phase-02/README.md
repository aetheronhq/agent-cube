# Phase 02: Basic Views

**Goal:** Implement non-streaming pages that validate routing and API

**Parallelization:** ✅ Both tasks can run in parallel (different pages)

---

## 📋 Tasks

### Task 04: Dashboard (2-3h)
- **File:** `tasks/04-dashboard.md`
- **Owner:** Frontend specialist A
- **Paths:** `web-ui/src/pages/Dashboard.tsx`, `web-ui/src/components/TaskCard.tsx`
- **Deliverables:**
  - Dashboard page with task list
  - TaskCard component
  - Status overview (active/completed counts)
  - Auto-refresh every 5 seconds

### Task 06: Decisions UI (2-3h)
- **File:** `tasks/06-decisions-ui.md`
- **Owner:** Frontend specialist B
- **Paths:** `web-ui/src/pages/Decisions.tsx`, `web-ui/src/components/JudgeVote.tsx`, `web-ui/src/components/SynthesisView.tsx`
- **Deliverables:**
  - Decisions page
  - JudgeVote component
  - SynthesisView component
  - Decision endpoint in backend

---

## ✅ Phase Gate

**Phase 02 complete when:**
- [ ] Dashboard lists all tasks from API
- [ ] Clicking task card navigates to task detail page
- [ ] Task counts display correctly (active vs completed)
- [ ] Auto-refresh polls API every 5 seconds
- [ ] Decisions page displays judge votes
- [ ] Synthesis instructions show when applicable
- [ ] Navigation between pages works
- [ ] All API endpoints respond correctly

**Verify:**
```bash
# Terminal 1: Ensure backend and frontend running
cube ui

# Terminal 2: Create test data
cube writers test-task test.md
# Wait for completion
cube panel test-task panel-prompt.md
cube decide test-task

# Browser tests:
# 1. Visit http://localhost:5173
#    → Should see "test-task" in list
# 2. Click task card
#    → Should navigate to /tasks/test-task
# 3. Navigate to /tasks/test-task/decisions
#    → Should see judge votes

# Check auto-refresh (Network tab)
# → Should see /api/tasks requests every 5 seconds
```

---

## 🔗 Dependencies

**Requires:**
- ✅ Phase 00 complete (Tasks 01 & 02 for routing and API)

**Enables:**
- Phase 03: Validates API and routing work before complex SSE

---

## ⏱️ Estimated Time

**Wall time:** 2-3 hours (parallel execution)  
**Total effort:** 4-6 hours (sum of both tasks)  
**Efficiency gain:** 50% from parallelization

---

## 🎯 Why This Phase?

**Rationale:**
- Both tasks have same dependencies (Phase 00)
- Different file ownership (zero conflicts)
- Simple API calls (no SSE complexity yet)
- Validates basics before integration

**Critical for:**
- Proves routing works
- Proves API endpoints work
- Builds confidence before Phase 03
- Creates navigation structure

**Why before Phase 03?**
- Phase 03 is complex integration (SSE streaming)
- Better to validate simple cases first
- If these fail, Phase 03 won't work
- Risk management: simple → complex

**Parallel execution strategy:**
- Assign Task 04 to one writer pair
- Assign Task 06 to another writer pair
- Both can work simultaneously
- No coordination needed (different pages/components)

