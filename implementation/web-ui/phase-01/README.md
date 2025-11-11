# Phase 01: Core Components

**Goal:** Build reusable thinking box components that mirror CLI aesthetic

**Parallelization:** ❌ Single task (no parallel opportunity)

---

## 📋 Tasks

### Task 03: Thinking Boxes (3-4h)
- **File:** `tasks/03-thinking-boxes.md`
- **Owner:** Frontend specialist
- **Paths:** `web-ui/src/components/Thinking*.tsx`, `web-ui/src/types/`
- **Deliverables:**
  - ThinkingBox component (reusable)
  - DualLayout component (Writer A + B)
  - TripleLayout component (Judge 1, 2, 3)
  - TypeScript types for thinking data

---

## ✅ Phase Gate

**Phase 01 complete when:**
- [ ] `<ThinkingBox>` component renders correctly
- [ ] `<DualLayout>` displays two boxes side-by-side
- [ ] `<TripleLayout>` displays three boxes in grid
- [ ] Mock thinking data displays properly
- [ ] Text truncation works (>91 chars)
- [ ] Colors match CLI (green/blue for writers, gray for judges)
- [ ] Monospace font applied
- [ ] Responsive layout works

**Verify:**
```bash
# In Dashboard.tsx (temporarily add):
const mockData = ["Line 1...", "Line 2...", "Line 3..."];
return <DualLayout writerALines={mockData} writerBLines={mockData} />;

# Then visit http://localhost:5173
# Should see two thinking boxes with mock data
```

---

## 🔗 Dependencies

**Requires:**
- ✅ Phase 00 complete (Task 01 for React structure)

**Enables:**
- Phase 03: Task Detail View (needs these components for real-time display)

---

## ⏱️ Estimated Time

**Wall time:** 3-4 hours  
**Total effort:** 3-4 hours  
**Efficiency gain:** 0% (single task, no parallelization)

---

## 🎯 Why This Phase?

**Rationale:**
- Thinking boxes are foundation for Phase 03
- Component layer before page layer (clean architecture)
- Single task focuses effort on matching CLI aesthetic
- Creates reusable primitives

**Critical for:**
- Task Detail View (Phase 03) depends on these components
- Establishes visual consistency with CLI
- Provides building blocks for real-time display

**Why not parallel with Phase 02?**
- Could work technically (different files)
- But Phase 02 needs to validate API endpoints work
- Cleaner to complete component layer first
- Phase 02 can proceed faster knowing components ready

