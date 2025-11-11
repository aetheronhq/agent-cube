# Judge Panel: Review Task Detail View with SSE Streaming Implementations

You are a judge on a panel reviewing two implementations of the Task Detail View with real-time SSE streaming for AgentCube's web UI.

---

## 📋 Task Overview

The writers were asked to create a real-time monitoring interface that:
- Implements SSE streaming endpoint (`/api/tasks/{id}/stream`)
- Creates SSE layout adapter (reuses `BaseThinkingLayout`)
- Builds `useSSE` hook for EventSource connections
- Creates `OutputStream` component for scrolling logs
- Updates `TaskDetail` page with live streaming
- Handles auto-reconnection and memory cleanup

**Time Budget:** 4-6 hours

**Reference Documents:**
- Writer prompt: `.prompts/writer-prompt-05-task-detail-view.md`
- Architecture spec: `planning/web-ui.md` (SSE Streaming Architecture section)

---

## 🔍 Review Process

### Step 1: Identify Writer Branches

```bash
# Find the writer branches for task 05-task-detail-view
git branch -r | grep "05-task-detail-view"
```

You should see two branches like:
- `origin/writer-<model-a>/05-task-detail-view`
- `origin/writer-<model-b>/05-task-detail-view`

### Step 2: Review Each Implementation

For each writer branch, examine:

```bash
# Checkout writer branch
git checkout writer-<model>/05-task-detail-view

# Review files changed
git diff main --stat
git diff main --name-only

# Review the actual changes
git diff main python/cube/ui/sse_layout.py
git diff main python/cube/ui/routes/stream.py
git diff main python/cube/ui/server.py
git diff main web-ui/src/hooks/useSSE.ts
git diff main web-ui/src/components/OutputStream.tsx
git diff main web-ui/src/pages/TaskDetail.tsx

# Check commit history
git log main..HEAD --oneline

# Examine files created
ls -la python/cube/ui/
ls -la python/cube/ui/routes/
ls -la web-ui/src/hooks/
ls -la web-ui/src/components/
```

### Step 3: Test Functionality

For each implementation, test the SSE streaming:

```bash
# Terminal 1: Start backend
cd python
cube ui

# Terminal 2: Test SSE endpoint with curl
curl -N http://localhost:3030/api/tasks/test-task/stream
# Should see heartbeat messages every 30s

# Terminal 3: Start a task
cube writers test-task .prompts/test-prompt.md

# Browser: Open task detail
# http://localhost:5173/tasks/test-task
```

**Manual Testing:**
1. **SSE endpoint (curl):** Verify `data: {...}\n\n` format, heartbeat messages
2. **Connection indicator:** Should show green when connected, red when disconnected
3. **Real-time thinking:** Thinking boxes should update live as agents think
4. **Output stream:** Should show tool calls and output in real-time
5. **Auto-scroll:** Output should auto-scroll to latest message
6. **Timestamps:** Messages should show timestamps
7. **Reconnection:** Stop backend → red indicator → restart → reconnects automatically
8. **Memory cleanup:** Navigate away → check Network tab (connection should close)
9. **Browser console:** No errors or warnings
10. **TypeScript:** No compilation errors

---

## ✅ Evaluation Criteria

Score each criterion on a scale of 0-10, where:
- **0-3**: Does not meet requirements, significant issues
- **4-6**: Partially meets requirements, some issues
- **7-8**: Meets requirements, minor issues
- **9-10**: Exceeds requirements, exemplary

### 1. Correctness (Weight: 30%)

**Does the implementation meet all functional requirements?**

**Backend - SSE Endpoint:**
- [ ] File exists: `python/cube/ui/routes/stream.py`
- [ ] FastAPI router created
- [ ] `GET /api/tasks/{task_id}/stream` endpoint implemented
- [ ] Uses `StreamingResponse` with `text/event-stream` media type
- [ ] Messages in correct format: `data: {JSON}\n\n`
- [ ] Heartbeat sent every 30 seconds
- [ ] CORS headers included (no-cache, keep-alive)
- [ ] Router registered in `server.py`

**Backend - SSE Layout Adapter:**
- [ ] File exists: `python/cube/ui/sse_layout.py`
- [ ] Inherits from `BaseThinkingLayout`
- [ ] Calls `super()` in `add_thinking()` and `add_output()`
- [ ] Queues messages with `asyncio.Queue`
- [ ] Message format includes type, content, timestamp
- [ ] Reuses parent logic (no duplication)

**Frontend - useSSE Hook:**
- [ ] File exists: `web-ui/src/hooks/useSSE.ts`
- [ ] Returns `{ messages, connected }` state
- [ ] Opens EventSource on mount
- [ ] Closes EventSource on unmount (cleanup)
- [ ] Filters out heartbeat messages
- [ ] Auto-reconnects on error (with delay)
- [ ] Type-safe TypeScript interface

**Frontend - OutputStream Component:**
- [ ] File exists: `web-ui/src/components/OutputStream.tsx`
- [ ] Accepts `messages` array prop
- [ ] Scrolling div with fixed height
- [ ] Auto-scrolls to bottom (useRef + useEffect)
- [ ] Displays timestamps
- [ ] Color-codes by agent
- [ ] Monospace font

**Frontend - TaskDetail Page:**
- [ ] File modified: `web-ui/src/pages/TaskDetail.tsx`
- [ ] Fetches task metadata from API
- [ ] Uses `useSSE` hook to connect to stream
- [ ] Separates thinking vs output messages
- [ ] Groups thinking by agent/box
- [ ] Renders DualLayout or TripleLayout
- [ ] Shows OutputStream below
- [ ] Connection status indicator
- [ ] Loading state while fetching

**Deductions:**
- Missing endpoint: -10 points
- Wrong SSE format: -8 points
- No heartbeat: -3 points
- SSE layout doesn't reuse BaseThinkingLayout: -8 points
- No cleanup (memory leak): -8 points (CRITICAL)
- EventSource not closed on unmount: -8 points (CRITICAL)
- No auto-reconnect: -5 points
- Auto-scroll not working: -4 points
- Connection indicator missing: -3 points

**Score: __/10**

### 2. Code Quality (Weight: 25%)

**Is the code clean, maintainable, and well-structured?**

**Evaluate:**
- Type hints on all Python functions
- TypeScript interfaces (not types)
- Explicit return types on all functions
- No `any` types anywhere
- Proper error handling (try/catch in Python, error states in React)
- Clean, readable code
- Consistent naming conventions
- Proper imports organization
- No unused imports or variables
- No console.log statements
- Descriptive variable names
- Proper component composition
- Docstrings on Python functions

**Red flags:**
- Using `any` types: -3 points per occurrence
- Missing type hints: -2 points per function
- No error handling in SSE endpoint: -4 points
- Duplicating BaseThinkingLayout logic: -8 points
- Inconsistent naming: -2 points
- Messy imports: -1 point
- Console.log statements: -1 point per occurrence
- No docstrings: -2 points

**Score: __/10**

### 3. Architecture Adherence (Weight: 20%)

**Does the implementation follow SSE principles and adapter pattern?**

**Key requirements:**
- ✅ SSE over WebSocket (simpler for one-way streaming)
- ✅ Adapter pattern (reuses BaseThinkingLayout logic)
- ✅ EventSource for frontend (native browser API)
- ✅ Auto-reconnection logic
- ✅ Memory cleanup on unmount
- ✅ Queue-based message passing (asyncio.Queue)
- ❌ No WebSocket implementation
- ❌ No custom buffering logic
- ❌ No reimplementation of layout logic
- ❌ No blocking operations in SSE endpoint

**Evaluate:**
- Proper adapter pattern usage
- SSE format strictly followed
- EventSource used correctly
- Cleanup handled properly
- No over-engineering
- Follows planning doc specifications
- No unnecessary abstractions
- File structure correct

**Critical violations:**
- Using WebSocket instead of SSE: -10 points
- Reimplementing BaseThinkingLayout logic: -10 points
- Blocking operations in event generator: -8 points
- Wrong SSE message format: -8 points
- No memory cleanup: -8 points
- Not using adapter pattern: -8 points

**Score: __/10**

### 4. SSE Implementation & Streaming (Weight: 15%)

**Is the SSE streaming implemented correctly?**

**Check:**
- Correct SSE message format: `data: {JSON}\n\n`
- Content-Type: `text/event-stream`
- CORS headers present
- Heartbeat keeps connection alive
- Messages stream in real-time
- Connection doesn't close prematurely
- Queue-based message passing (non-blocking)
- Async generator function
- Cleanup on client disconnect
- EventSource reconnection logic

**Test cases:**
- Open stream with curl - should see heartbeats
- Start task - should see thinking and output messages
- Connection stays open for duration
- Backend restart - frontend reconnects
- Navigate away - connection closes

**Deductions:**
- Wrong SSE format: -8 points
- No heartbeat: -3 points
- Connection closes immediately: -8 points
- Blocking operations: -6 points
- No CORS headers: -4 points
- No reconnection logic: -5 points
- Messages not received: -8 points

**Score: __/10**

### 5. State Management & Side Effects (Weight: 5%)

**Are state and side effects handled correctly?**

**Check:**
- `useState` for messages, connected state
- `useEffect` with proper dependency array
- Cleanup function returns from useEffect
- EventSource closed on unmount
- No memory leaks
- State updates don't cause infinite loops
- Loading states handled
- Error states handled
- Message filtering (no heartbeats in UI)

**Test cases:**
- Component mounts - EventSource opens
- Component unmounts - EventSource closes
- Messages received - state updates
- Error occurs - reconnection triggered
- Navigate away - no memory leak warnings

**Deductions:**
- No cleanup function: -5 points (CRITICAL)
- Memory leak detected: -5 points
- Missing dependency in useEffect: -3 points
- No error handling: -3 points
- Infinite loops: -5 points

**Score: __/10**

### 6. Testing & Verification (Weight: 5%)

**Has the implementation been properly tested?**

**Evidence of testing:**
- TypeScript compiles cleanly: `npx tsc --noEmit`
- Python type checks pass (if using mypy)
- SSE endpoint tested with curl
- Task detail page renders without errors
- Real-time updates verified
- Auto-scroll verified
- Reconnection tested
- Memory cleanup verified (Network tab)
- Browser console clean (no errors or warnings)
- Integration test passed (CLI → UI)
- Commit messages indicate testing
- Changes pushed to remote branch

**Deductions:**
- TypeScript compilation errors: -3 points per error
- SSE endpoint doesn't work: -5 points
- Page doesn't render: -5 points
- Real-time updates broken: -5 points
- Auto-scroll broken: -3 points
- Memory leak: -5 points
- Console errors: -2 points
- Not tested with actual task: -3 points
- Not pushed to remote: -5 points (CRITICAL)

**Score: __/10**

---

## 📊 Scoring Rubric

Calculate the weighted total score:

```
Total Score = (Correctness × 0.30) + 
              (Code Quality × 0.25) + 
              (Architecture × 0.20) + 
              (SSE Implementation × 0.15) + 
              (State Management × 0.05) + 
              (Testing × 0.05)
```

**Grade Interpretation:**

| Score | Grade | Recommendation |
|-------|-------|----------------|
| 9.0 - 10.0 | A+ | APPROVED - Exceptional implementation |
| 8.0 - 8.9 | A | APPROVED - Strong implementation |
| 7.0 - 7.9 | B+ | APPROVED - Good implementation |
| 6.0 - 6.9 | B | REQUEST_CHANGES - Acceptable with minor fixes |
| 5.0 - 5.9 | C | REQUEST_CHANGES - Needs improvements |
| 4.0 - 4.9 | D | REQUEST_CHANGES - Significant issues |
| 0.0 - 3.9 | F | REJECTED - Does not meet requirements |

---

## 🎯 Anti-Pattern Detection

**CRITICAL: Check for these anti-patterns that should result in REQUEST_CHANGES or REJECTED:**

### ❌ Anti-Pattern 1: Using WebSocket Instead of SSE

```python
# BAD - WebSocket is overkill for one-way streaming
@app.websocket("/ws/tasks/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    await websocket.accept()
    while True:
        await websocket.send_json({"type": "thinking", ...})
```

**Why wrong:** WebSocket adds complexity (bidirectional protocol, ping/pong, manual reconnection). SSE is simpler for one-way streaming and has built-in reconnection.

**✅ Good:**
```python
@app.get("/api/tasks/{task_id}/stream")
async def stream_task(task_id: str):
    async def event_generator():
        queue = asyncio.Queue()
        while True:
            try:
                msg = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield f"data: {json.dumps(msg)}\n\n"
            except asyncio.TimeoutError:
                yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

**Impact:** REJECTED - Fundamental architecture violation

### ❌ Anti-Pattern 2: Reimplementing Layout Logic

```python
# BAD - Duplicating BaseThinkingLayout logic
class SSELayout:
    def add_thinking(self, box_id, text):
        if box_id not in self.buffers:
            self.buffers[box_id] = []
        self.buffers[box_id].append(text)
        if text.endswith('.'):
            # 100+ lines of complex flushing logic...
```

**Why wrong:** Duplicates tested logic from `BaseThinkingLayout`. Violates DRY principle and adapter pattern.

**✅ Good:**
```python
# Adapter pattern reuses logic
class SSELayout(BaseThinkingLayout):
    def __init__(self, boxes: dict, queue: asyncio.Queue):
        super().__init__(boxes)
        self.queue = queue
    
    def add_thinking(self, box_id: str, text: str):
        super().add_thinking(box_id, text)  # ✅ Reuse parent logic
        asyncio.create_task(self.queue.put({
            "type": "thinking",
            "box": box_id,
            "text": text
        }))
```

**Impact:** REJECTED - Violates adapter pattern requirement

### ❌ Anti-Pattern 3: Wrong SSE Format

```python
# BAD - Wrong SSE format
async def event_generator():
    while True:
        msg = await queue.get()
        yield json.dumps(msg)  # Missing "data: " prefix and "\n\n"
```

**Why wrong:** EventSource expects specific format: `data: {JSON}\n\n`. Wrong format causes silent failures.

**✅ Good:**
```python
async def event_generator():
    while True:
        msg = await queue.get()
        yield f"data: {json.dumps(msg)}\n\n"  # ✅ Correct format
```

**Impact:** REQUEST_CHANGES - SSE won't work without correct format

### ❌ Anti-Pattern 4: Memory Leak (No Cleanup)

```typescript
// BAD - Memory leak!
export function useSSE(url: string) {
  const [messages, setMessages] = useState<SSEMessage[]>([]);
  
  useEffect(() => {
    const eventSource = new EventSource(url);
    eventSource.onmessage = (event) => {
      setMessages(prev => [...prev, JSON.parse(event.data)]);
    };
    // No cleanup! Connection stays open after unmount
  }, [url]);
}
```

**Why wrong:** EventSource connection never closes, causing memory leaks and hanging connections.

**✅ Good:**
```typescript
export function useSSE(url: string) {
  const [messages, setMessages] = useState<SSEMessage[]>([]);
  
  useEffect(() => {
    const eventSource = new EventSource(url);
    eventSource.onmessage = (event) => {
      setMessages(prev => [...prev, JSON.parse(event.data)]);
    };
    
    return () => {
      eventSource.close();  // ✅ Cleanup
    };
  }, [url]);
}
```

**Impact:** REQUEST_CHANGES - Memory leaks are critical bugs

### ❌ Anti-Pattern 5: Blocking Operations in Event Loop

```python
# BAD - Synchronous operation in async function
async def event_generator():
    while True:
        # Blocking file I/O!
        with open(f'logs/{task_id}.log') as f:
            line = f.readline()
        yield f"data: {json.dumps({'content': line})}\n\n"
```

**Why wrong:** Blocks the entire event loop, causing all requests to hang.

**✅ Good:**
```python
async def event_generator():
    queue = asyncio.Queue()
    while True:
        msg = await queue.get()  # ✅ Non-blocking
        yield f"data: {json.dumps(msg)}\n\n"
```

**Impact:** REQUEST_CHANGES - Breaks concurrency

### ❌ Anti-Pattern 6: No Auto-Reconnection

```typescript
// BAD - No reconnection logic
eventSource.onerror = () => {
  setConnected(false);
  eventSource.close();
  // Just closes, never reconnects!
};
```

**Why wrong:** User must manually refresh page after network blip or server restart.

**✅ Good:**
```typescript
eventSource.onerror = () => {
  setConnected(false);
  eventSource.close();
  
  // Reconnect after 3 seconds
  setTimeout(() => {
    window.location.reload();  // Or implement custom reconnect logic
  }, 3000);
};
```

**Impact:** REQUEST_CHANGES - Poor UX without auto-reconnect

### ❌ Anti-Pattern 7: Missing Heartbeat

```python
# BAD - No heartbeat, connection times out
async def event_generator():
    queue = asyncio.Queue()
    while True:
        msg = await queue.get()  # Will timeout after 60s of inactivity
        yield f"data: {json.dumps(msg)}\n\n"
```

**Why wrong:** SSE connections timeout after period of inactivity (typically 60s).

**✅ Good:**
```python
async def event_generator():
    queue = asyncio.Queue()
    while True:
        try:
            msg = await asyncio.wait_for(queue.get(), timeout=30.0)
            yield f"data: {json.dumps(msg)}\n\n"
        except asyncio.TimeoutError:
            # Heartbeat every 30s
            yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
```

**Impact:** REQUEST_CHANGES - Connection will drop in production

### ❌ Anti-Pattern 8: Missing CORS Headers

```python
# BAD - No CORS headers
return StreamingResponse(
    event_generator(),
    media_type="text/event-stream"
)
```

**Why wrong:** EventSource from `localhost:5173` to `localhost:3030` requires CORS headers.

**✅ Good:**
```python
return StreamingResponse(
    event_generator(),
    media_type="text/event-stream",
    headers={
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",  # Disable nginx buffering
    }
)
```

**Impact:** REQUEST_CHANGES - CORS errors will block streaming

---

## 📝 Decision Template

After reviewing both implementations, provide your decision using this exact JSON format:

```json
{
  "task_id": "05-task-detail-view",
  "judge_id": "judge-<your-model>",
  "timestamp": "2025-11-11T<time>Z",
  "reviews": {
    "writer_a": {
      "branch": "writer-<model-a>/05-task-detail-view",
      "scores": {
        "correctness": 0.0,
        "code_quality": 0.0,
        "architecture": 0.0,
        "sse_implementation": 0.0,
        "state_management": 0.0,
        "testing": 0.0,
        "total": 0.0
      },
      "strengths": [
        "List 2-4 key strengths"
      ],
      "weaknesses": [
        "List 2-4 key weaknesses or concerns"
      ],
      "critical_issues": [
        "List any blocking issues (empty if none)"
      ],
      "recommendation": "APPROVED | REQUEST_CHANGES | REJECTED",
      "summary": "2-3 sentence summary of the implementation"
    },
    "writer_b": {
      "branch": "writer-<model-b>/05-task-detail-view",
      "scores": {
        "correctness": 0.0,
        "code_quality": 0.0,
        "architecture": 0.0,
        "sse_implementation": 0.0,
        "state_management": 0.0,
        "testing": 0.0,
        "total": 0.0
      },
      "strengths": [
        "List 2-4 key strengths"
      ],
      "weaknesses": [
        "List 2-4 key weaknesses or concerns"
      ],
      "critical_issues": [
        "List any blocking issues (empty if none)"
      ],
      "recommendation": "APPROVED | REQUEST_CHANGES | REJECTED",
      "summary": "2-3 sentence summary of the implementation"
    }
  },
  "comparison": {
    "better_implementation": "writer_a | writer_b | tie",
    "rationale": "2-3 sentences explaining why one is better (or why it's a tie)",
    "key_differences": [
      "List 2-3 significant differences between implementations"
    ]
  },
  "panel_recommendation": {
    "final_decision": "APPROVED | REQUEST_CHANGES | REJECTED",
    "selected_writer": "writer_a | writer_b | none",
    "confidence": "high | medium | low",
    "reasoning": "Detailed explanation of final decision (3-5 sentences)",
    "next_steps": [
      "List specific actions to take (merge, request fixes, reject, etc.)"
    ]
  }
}
```

---

## 🎯 Judging Guidelines

### Objectivity

- Focus on technical merit, not style preferences
- Use the scoring rubric consistently
- Cite specific code examples for critiques
- Be fair and balanced in evaluation

### Thoroughness

- Review ALL changed files (backend and frontend)
- Test SSE endpoint with curl
- Test functionality in browser (run dev server)
- Check for memory leaks (Network tab)
- Verify TypeScript compilation
- Test reconnection logic
- Verify integration with existing components

### Constructive Feedback

- Highlight both strengths and weaknesses
- Provide specific, actionable feedback
- Suggest improvements for REQUEST_CHANGES
- Acknowledge good practices when present

### Decision Criteria

**APPROVED:**
- Total score ≥ 7.0
- No critical issues
- All core requirements met
- SSE streaming works correctly
- No memory leaks
- Minor issues can be addressed in follow-up

**REQUEST_CHANGES:**
- Total score 4.0 - 6.9
- Some requirements not met
- Fixable issues identified
- Core functionality present but needs improvement
- Memory leaks or SSE format issues

**REJECTED:**
- Total score < 4.0
- Critical requirements missing
- Wrong architecture (WebSocket, no adapter pattern)
- Reimplemented layout logic
- Would require complete rewrite

---

## 🔗 Reference Files

Review these files to understand the requirements:

```bash
# Writer prompt
cat .prompts/writer-prompt-05-task-detail-view.md

# Architecture spec (SSE section)
cat planning/web-ui.md

# Existing layout logic (should be reused)
cat python/cube/core/base_layout.py

# Existing thinking components (Task 03)
cat web-ui/src/components/DualLayout.tsx
cat web-ui/src/components/TripleLayout.tsx

# Check how layout is used
cat python/cube/automation/dual_writers.py
```

---

## ✅ Judge Checklist

Before submitting your review:

- [ ] Reviewed both writer branches completely
- [ ] Checked all expected files (backend and frontend)
- [ ] Tested SSE endpoint with curl
- [ ] Verified SSE message format: `data: {...}\n\n`
- [ ] Verified heartbeat every 30 seconds
- [ ] Verified CORS headers present
- [ ] Tested TypeScript compilation for both (`npx tsc --noEmit`)
- [ ] Ran dev server and tested functionality
- [ ] Verified real-time thinking boxes update
- [ ] Verified output stream displays messages
- [ ] Verified auto-scroll works
- [ ] Verified connection indicator accurate
- [ ] Tested reconnection (stop/start backend)
- [ ] Checked memory cleanup (Network tab on unmount)
- [ ] Verified no console errors
- [ ] Checked adapter pattern usage (no duplicate logic)
- [ ] Scored all 6 criteria for both writers
- [ ] Calculated weighted total scores
- [ ] Identified strengths and weaknesses
- [ ] Listed critical issues (if any)
- [ ] Made clear recommendation for each
- [ ] Compared implementations fairly
- [ ] Provided final panel decision
- [ ] Included reasoning and next steps
- [ ] Used exact JSON format

---

## 🚀 Submit Your Review

Save your decision JSON to:
```
.prompts/decisions/judge-<your-model>-05-task-detail-view-decision.json
```

Your review will be aggregated with other judges to make the final decision.

---

## 📋 Quick Reference: What Good Looks Like

### ✅ Excellent Implementation Checklist

**Backend Files:**
- [ ] `python/cube/ui/sse_layout.py` (new)
  - [ ] Inherits from BaseThinkingLayout
  - [ ] Calls super() in all methods
  - [ ] Queues messages to asyncio.Queue
  - [ ] No duplicated logic

- [ ] `python/cube/ui/routes/stream.py` (new)
  - [ ] SSE endpoint with StreamingResponse
  - [ ] Correct format: `data: {...}\n\n`
  - [ ] Heartbeat every 30s
  - [ ] CORS headers
  - [ ] Async generator function

- [ ] `python/cube/ui/server.py` (modified)
  - [ ] Router registered

**Frontend Files:**
- [ ] `web-ui/src/hooks/useSSE.ts` (new)
  - [ ] Returns messages and connected state
  - [ ] Opens EventSource on mount
  - [ ] Closes EventSource on unmount
  - [ ] Filters heartbeats
  - [ ] Auto-reconnects on error

- [ ] `web-ui/src/components/OutputStream.tsx` (new)
  - [ ] Scrolling div with fixed height
  - [ ] Auto-scroll with useRef
  - [ ] Timestamps displayed
  - [ ] Color-coded by agent
  - [ ] Monospace font

- [ ] `web-ui/src/pages/TaskDetail.tsx` (modified)
  - [ ] Uses useSSE hook
  - [ ] Separates thinking vs output
  - [ ] Groups by agent
  - [ ] Shows connection indicator
  - [ ] Renders appropriate layout

**Testing:**
- [ ] SSE endpoint works with curl
- [ ] Real-time updates work in browser
- [ ] Auto-scroll works
- [ ] Reconnection works
- [ ] No memory leaks
- [ ] TypeScript compiles
- [ ] No console errors
- [ ] Committed and pushed

---

## 🔍 Comparison Focus Areas

When comparing the two implementations, pay special attention to:

1. **SSE Implementation:**
   - Correct message format?
   - Heartbeat implemented?
   - CORS headers present?
   - Non-blocking operations?

2. **Adapter Pattern:**
   - Properly inherits from BaseThinkingLayout?
   - Calls super() to reuse logic?
   - No duplicated code?
   - Clean integration?

3. **Memory Management:**
   - EventSource closed on unmount?
   - No memory leaks?
   - Proper cleanup?
   - Resources released?

4. **Real-Time UX:**
   - Live updates smooth?
   - Auto-scroll works well?
   - Connection indicator accurate?
   - Auto-reconnection seamless?

5. **Code Quality:**
   - Type-safe TypeScript?
   - Proper error handling?
   - Clean, readable code?
   - Good architecture?

6. **Integration:**
   - Works with existing components?
   - Follows project patterns?
   - Proper file structure?
   - Complete implementation?

---

## 🧪 Testing Commands

**Test SSE endpoint:**
```bash
# Should see heartbeat messages every 30s
curl -N http://localhost:3030/api/tasks/test-task/stream
```

**Test TypeScript:**
```bash
cd web-ui
npx tsc --noEmit
```

**Test integration:**
```bash
# Terminal 1
cd python
cube ui

# Terminal 2
cube writers test-task .prompts/test-prompt.md

# Browser
open http://localhost:5173/tasks/test-task
```

**Check memory leaks:**
1. Open browser DevTools → Network tab
2. Filter by "EventSource"
3. Should see SSE connection
4. Navigate away from page
5. Connection should close (status should update)

---

**Remember:** This is the most complex task in the workflow. Real-time monitoring is the core UX of Agent Cube. Be thorough in testing SSE format, memory cleanup, and reconnection logic.

Good luck! 🎯
