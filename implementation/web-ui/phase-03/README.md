# Phase 03: Real-Time Integration

**Goal:** Implement core SSE streaming feature - the heart of AgentCube UI

**Parallelization:** ❌ Single task (integration point)

---

## 📋 Tasks

### Task 05: Task Detail View with SSE (4-6h)
- **File:** `tasks/05-task-detail-view.md`
- **Owner:** Full-stack specialist (touches backend + frontend)
- **Paths:**
  - Backend: `python/cube/ui/sse_layout.py`, `python/cube/ui/routes/stream.py`
  - Frontend: `web-ui/src/hooks/useSSE.ts`, `web-ui/src/components/OutputStream.tsx`, `web-ui/src/pages/TaskDetail.tsx`
- **Deliverables:**
  - SSE streaming endpoint (`/api/tasks/{id}/stream`)
  - SSELayout adapter (backend)
  - useSSE hook (frontend)
  - OutputStream component (frontend)
  - TaskDetail page with live updates

---

## ✅ Phase Gate

**Phase 03 complete when:**
- [ ] SSE endpoint streams events in correct format
- [ ] Frontend connects via EventSource
- [ ] Thinking boxes update in real-time
- [ ] Output stream shows tool calls and messages
- [ ] Auto-reconnects on disconnect
- [ ] Memory cleanup on unmount
- [ ] **END-TO-END TEST PASSES** (see below)

**End-to-End Test:**
```bash
# Terminal 1: Start UI
cube ui

# Terminal 2: Start a real task
cube writers test-task implementation/web-ui/phase-00/tasks/01-project-scaffold.md

# Browser: Open http://localhost:5173/tasks/test-task

# Verify in real-time:
# ✅ Thinking boxes update as agents think
# ✅ Output stream shows:
#    - "📖 reading file..."
#    - "📝 writing to..."
#    - "🔧 running command..."
# ✅ Connection status shows "Connected"
# ✅ If you kill backend, shows "Disconnected" and reconnects
# ✅ Auto-scrolls to latest output

# This is the CORE AgentCube UX - watching agents work in real-time
```

**Verify SSE directly:**
```bash
# Test SSE endpoint with curl
curl -N http://localhost:3030/api/tasks/test-task/stream

# Should see streaming events:
# data: {"type":"thinking","box":"writer-a","text":"Reading task..."}
#
# data: {"type":"output","agent":"Writer A","content":"📖 ..."}
#
```

---

## 🔗 Dependencies

**Requires:**
- ✅ Phase 00 complete (Task 02 for backend API structure)
- ✅ Phase 01 complete (Task 03 for thinking box components)
- ⚠️ Phase 02 complete (validates API and routing work)

**Enables:**
- ✅ Complete Web UI (this is the final integration)

---

## ⏱️ Estimated Time

**Wall time:** 4-6 hours  
**Total effort:** 4-6 hours  
**Efficiency gain:** 0% (single task, integration point)

---

## 🎯 Why This Phase?

**Rationale:**
- Integration point (combines backend + frontend + components)
- Most complex feature (real-time streaming)
- Core AgentCube UX (watching agents think)
- Highest risk (touches both sides of stack)

**Why single task?**
- SSE endpoint and frontend hook are tightly coupled
- Backend SSELayout and frontend useSSE must work together
- Splitting would require complex coordination
- Better to have one person/pair handle both sides

**Why last phase?**
- Most complex, highest risk
- Depends on everything else working
- If this fails, previous phases help debug
- Validates entire stack end-to-end

**Critical for:**
- This IS the AgentCube UI
- Without real-time streaming, it's just a static dashboard
- Core value: watching AI agents think in real-time
- Everything else supports this feature

---

## 🚨 Common Issues & Solutions

### Issue: SSE closes immediately
**Cause:** Wrong message format  
**Solution:** Must be `data: {JSON}\n\n` (two newlines!)

### Issue: CORS error on SSE
**Cause:** Missing CORS headers on streaming response  
**Solution:** Add headers to StreamingResponse:
```python
headers={
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Access-Control-Allow-Origin": "http://localhost:5173"
}
```

### Issue: Memory leak in frontend
**Cause:** EventSource not closed on unmount  
**Solution:** Return cleanup in useEffect:
```typescript
return () => {
  eventSource.close();
};
```

### Issue: Thinking boxes not updating
**Cause:** SSELayout not intercepting add_thinking calls  
**Solution:** Verify SSELayout overrides BaseThinkingLayout correctly

---

## 🎓 Testing Strategy

### Unit Tests
- Backend: SSELayout queues messages correctly
- Frontend: useSSE parses messages correctly

### Integration Tests
- SSE endpoint streams to curl
- Frontend connects and receives messages

### End-to-End Test (Manual)
1. Start `cube ui`
2. Start `cube writers test-task test.md`
3. Watch browser update in real-time
4. Kill backend, verify reconnect
5. Check memory (no leaks after unmount)

**If end-to-end test passes → Phase complete → Web UI complete!**

