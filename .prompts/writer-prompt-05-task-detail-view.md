# Writer Prompt: Task 05 - Task Detail View with Live Streaming

**Task ID:** 05-task-detail-view  
**Complexity:** High (4-6 hours)  
**Branch:** `writer-[your-model-slug]/05-task-detail-view`  
**Generated:** 2025-11-11

---

## 🎯 Your Mission

Build the **Task Detail View** with **real-time SSE streaming** of thinking boxes and output, matching the CLI's live display. This is the core monitoring interface for Agent Cube.

**You are implementing:**
- Backend: SSE streaming endpoint (`/api/tasks/{id}/stream`)
- Backend: SSE layout adapter (reuses existing layout logic)
- Frontend: `useSSE` hook for EventSource connections
- Frontend: `OutputStream` component for scrolling logs
- Frontend: `TaskDetail` page with live updates

**Time Budget:** 4-6 hours

---

## 📚 Context & Dependencies

### What You're Building On

**Previous tasks (completed):**
- **Task 01:** Page routing (`/tasks/:id` route exists)
- **Task 02:** Backend API (base server at `http://localhost:3030`)
- **Task 03:** `DualLayout` and `TripleLayout` components (thinking boxes)
- **Task 04:** Dashboard (links to task detail pages)

**Key facts:**
- Agent Cube's core UX is **real-time agent monitoring**
- CLI already has live thinking boxes + output streaming
- Your job: Bring that live experience to the web UI
- SSE (Server-Sent Events) is simpler than WebSocket for one-way streaming

### Golden Source Documents

**Planning doc:** `planning/web-ui.md`
- Section: "SSE Streaming Architecture"
- Message format: `data: {JSON}\n\n`
- Endpoint: `/api/tasks/{id}/stream`

**Architecture Principles:**
- ✅ **SSE over WebSocket** (simpler, one-way is sufficient)
- ✅ **Adapter pattern** for layout (reuse existing logic)
- ✅ **Auto-reconnect** on disconnect
- ✅ **Memory cleanup** on unmount
- ❌ No complex buffering (EventSource handles it)
- ❌ No message acknowledgment (one-way streaming)

---

## ✅ Requirements Checklist

### 1. SSE Streaming Endpoint (Backend)

**What to build:**
- Add `routes/stream.py` to FastAPI backend
- Implement `/api/tasks/{id}/stream` endpoint
- Stream thinking and output events in real-time
- Use `StreamingResponse` with `text/event-stream` media type

**Acceptance criteria:**
- [ ] `python/cube/ui/routes/stream.py` created
- [ ] SSE endpoint returns `text/event-stream` media type
- [ ] Streams messages in format: `data: {JSON}\n\n`
- [ ] Includes CORS headers (keep-alive, no-cache)
- [ ] Sends heartbeat every 30s to keep connection alive
- [ ] Cleans up on client disconnect

**Example endpoint:**
```python
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio
import json

router = APIRouter()

@router.get("/tasks/{task_id}/stream")
async def stream_task(task_id: str):
    async def event_generator():
        queue = asyncio.Queue()
        
        # TODO: Wire up to actual task execution
        # For now, send heartbeat
        while True:
            try:
                msg = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield f"data: {json.dumps(msg)}\n\n"
            except asyncio.TimeoutError:
                yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
```

### 2. SSE Layout Adapter (Backend)

**What to build:**
- Create `python/cube/ui/sse_layout.py`
- Extend `BaseThinkingLayout` (from `cube.core.base_layout`)
- Override `add_thinking()` and `add_output()` to queue SSE messages
- Use `asyncio.Queue` for message passing

**Acceptance criteria:**
- [ ] `python/cube/ui/sse_layout.py` created
- [ ] Inherits from `BaseThinkingLayout`
- [ ] Reuses parent logic (calls `super()`)
- [ ] Queues messages with `asyncio.create_task()`
- [ ] Message format matches SSE spec

**Example adapter:**
```python
import asyncio
import json
from datetime import datetime
from cube.core.base_layout import BaseThinkingLayout

class SSELayout(BaseThinkingLayout):
    def __init__(self, boxes: dict, queue: asyncio.Queue):
        super().__init__(boxes)
        self.queue = queue
    
    def add_thinking(self, box_id: str, text: str) -> None:
        # Reuse parent logic
        super().add_thinking(box_id, text)
        
        # Queue SSE message
        asyncio.create_task(self.queue.put({
            "type": "thinking",
            "box": box_id,
            "text": text,
            "timestamp": datetime.utcnow().isoformat()
        }))
    
    def add_output(self, line: str) -> None:
        super().add_output(line)
        
        asyncio.create_task(self.queue.put({
            "type": "output",
            "content": line,
            "timestamp": datetime.utcnow().isoformat()
        }))
```

### 3. useSSE Hook (Frontend)

**What to build:**
- Custom React hook for SSE connections
- Manages EventSource lifecycle
- Auto-reconnects on disconnect
- Type-safe message parsing

**Acceptance criteria:**
- [ ] `web-ui/src/hooks/useSSE.ts` created
- [ ] Returns `{ messages, connected }` state
- [ ] Opens EventSource on mount
- [ ] Closes EventSource on unmount
- [ ] Auto-reconnects on error (3s delay)
- [ ] Filters out heartbeat messages
- [ ] Type-safe TypeScript interface

**Example hook:**
```typescript
import { useState, useEffect } from 'react';

interface SSEMessage {
  type: string;
  box?: string;
  agent?: string;
  content?: string;
  text?: string;
  timestamp: string;
}

export function useSSE(url: string) {
  const [messages, setMessages] = useState<SSEMessage[]>([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const eventSource = new EventSource(url);

    eventSource.onopen = () => {
      setConnected(true);
    };

    eventSource.onmessage = (event) => {
      const msg: SSEMessage = JSON.parse(event.data);
      if (msg.type !== 'heartbeat') {
        setMessages((prev) => [...prev, msg]);
      }
    };

    eventSource.onerror = () => {
      setConnected(false);
      eventSource.close();
      
      // Reconnect after 3 seconds
      setTimeout(() => {
        window.location.reload();
      }, 3000);
    };

    return () => {
      eventSource.close();
    };
  }, [url]);

  return { messages, connected };
}
```

### 4. OutputStream Component (Frontend)

**What to build:**
- Scrolling output log component
- Displays messages with timestamps
- Color-coded by agent
- Auto-scrolls to bottom

**Acceptance criteria:**
- [ ] `web-ui/src/components/OutputStream.tsx` created
- [ ] Accepts `messages` array prop
- [ ] Displays in scrolling div (fixed height)
- [ ] Color codes by agent (green/blue for writers)
- [ ] Monospace font for consistency
- [ ] Auto-scrolls to latest (useRef + useEffect)
- [ ] Timestamp formatting

**Example component:**
```typescript
import { useEffect, useRef } from 'react';

interface OutputStreamProps {
  messages: Array<{ agent?: string; content?: string; timestamp: string }>;
}

export function OutputStream({ messages }: OutputStreamProps) {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="border border-gray-700 rounded-lg p-4 bg-cube-gray h-96 overflow-y-auto font-mono text-xs">
      {messages.map((msg, i) => (
        <div key={i} className="mb-1 text-gray-300">
          <span className="text-gray-500">[{new Date(msg.timestamp).toLocaleTimeString()}]</span>
          {msg.agent && <span className="text-green-400"> [{msg.agent}]</span>}
          {' '}{msg.content}
        </div>
      ))}
      <div ref={endRef} />
    </div>
  );
}
```

### 5. TaskDetail Page (Frontend)

**What to build:**
- Full task monitoring page
- Fetches task metadata from `/api/tasks/{id}`
- Connects to SSE stream
- Shows DualLayout or TripleLayout based on phase
- Shows OutputStream below

**Acceptance criteria:**
- [ ] `web-ui/src/pages/TaskDetail.tsx` updated
- [ ] Fetches task info on mount
- [ ] Uses `useSSE` hook for streaming
- [ ] Separates thinking vs output messages
- [ ] Groups thinking by agent (writer-a, writer-b, judges)
- [ ] Renders correct layout (Dual for phase 1-2, Triple for 3-10)
- [ ] Shows connection status indicator
- [ ] Auto-scrolls output stream

**Example page:**
```typescript
import { useParams } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { useSSE } from '../hooks/useSSE';
import { DualLayout } from '../components/DualLayout';
import { TripleLayout } from '../components/TripleLayout';
import { OutputStream } from '../components/OutputStream';

export function TaskDetail() {
  const { id } = useParams<{ id: string }>();
  const [task, setTask] = useState<any>(null);
  const { messages, connected } = useSSE(`http://localhost:3030/api/tasks/${id}/stream`);

  useEffect(() => {
    fetch(`http://localhost:3030/api/tasks/${id}`)
      .then(res => res.json())
      .then(setTask);
  }, [id]);

  if (!task) return <div>Loading...</div>;

  // Separate thinking from output
  const thinkingMessages = messages.filter(m => m.type === 'thinking');
  const outputMessages = messages.filter(m => m.type === 'output');

  // Group by agent
  const writerALines = thinkingMessages
    .filter(m => m.box === 'writer-a')
    .map(m => m.text || '');
  const writerBLines = thinkingMessages
    .filter(m => m.box === 'writer-b')
    .map(m => m.text || '');

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">{id}</h1>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-sm text-gray-400">
            {connected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      <DualLayout writerALines={writerALines} writerBLines={writerBLines} />

      <div>
        <h2 className="text-lg font-semibold mb-2">Output Stream</h2>
        <OutputStream messages={outputMessages} />
      </div>
    </div>
  );
}
```

---

## 📋 Implementation Steps

**Follow this order:**

### Step 1: Backend - SSE Layout Adapter

**File:** `python/cube/ui/sse_layout.py`

- [ ] Import `BaseThinkingLayout` from `cube.core.base_layout`
- [ ] Create `SSELayout` class that inherits from `BaseThinkingLayout`
- [ ] Add `__init__` that accepts `boxes` dict and `queue`
- [ ] Override `add_thinking()` - call `super()` then queue message
- [ ] Override `add_output()` - call `super()` then queue message
- [ ] Use ISO timestamp format
- [ ] Message format: `{"type": "thinking"|"output", ...}`

### Step 2: Backend - SSE Endpoint

**File:** `python/cube/ui/routes/stream.py`

- [ ] Create FastAPI router
- [ ] Implement `GET /tasks/{task_id}/stream` endpoint
- [ ] Use `StreamingResponse` with `text/event-stream`
- [ ] Async generator function for events
- [ ] Queue-based message passing
- [ ] Heartbeat every 30s (timeout on queue.get)
- [ ] SSE format: `f"data: {json.dumps(msg)}\n\n"`
- [ ] CORS headers (no-cache, keep-alive)

**Register router in `python/cube/ui/server.py`:**
```python
from cube.ui.routes import stream

app.include_router(stream.router, prefix="/api")
```

### Step 3: Frontend - useSSE Hook

**File:** `web-ui/src/hooks/useSSE.ts`

- [ ] Create `SSEMessage` interface
- [ ] Create `useSSE(url: string)` function
- [ ] State: `messages` array, `connected` boolean
- [ ] useEffect to manage EventSource
- [ ] Open connection on mount
- [ ] Parse messages (JSON.parse)
- [ ] Filter heartbeats
- [ ] Handle errors and reconnect
- [ ] Close on unmount (cleanup function)

### Step 4: Frontend - OutputStream Component

**File:** `web-ui/src/components/OutputStream.tsx`

- [ ] Create `OutputStreamProps` interface
- [ ] Accept `messages` prop
- [ ] Render in scrolling div (h-96, overflow-y-auto)
- [ ] Map over messages with timestamps
- [ ] Color code agents (text-green-400, text-blue-400)
- [ ] Monospace font (font-mono)
- [ ] Auto-scroll with useRef + useEffect
- [ ] Empty state (no messages yet)

### Step 5: Frontend - TaskDetail Page

**File:** `web-ui/src/pages/TaskDetail.tsx`

- [ ] Get `id` from `useParams()`
- [ ] Fetch task metadata from `/api/tasks/{id}`
- [ ] Connect to SSE with `useSSE()` hook
- [ ] Filter messages by type (thinking vs output)
- [ ] Group thinking messages by box (writer-a, writer-b, judges)
- [ ] Render DualLayout or TripleLayout based on phase
- [ ] Render OutputStream below
- [ ] Show connection status indicator
- [ ] Loading state while fetching task

### Step 6: Test Integration

**Manual testing:**

```bash
# Terminal 1: Start backend
cd python
cube ui

# Terminal 2: Start a task
cube writers test-task test.md

# Browser: Open task detail
http://localhost:5173/tasks/test-task
```

**Verify:**
- [ ] Thinking boxes update in real-time
- [ ] Output stream shows messages
- [ ] Connection indicator shows green
- [ ] Auto-scrolls to latest output
- [ ] Reconnects on disconnect

### Step 7: Test with curl

```bash
# Test SSE endpoint directly
curl -N http://localhost:3030/api/tasks/test-task/stream

# Should see:
# data: {"type":"heartbeat"}
#
# (Every 30 seconds)
```

### Step 8: Quality Checks

```bash
# Frontend TypeScript
cd web-ui
npx tsc --noEmit

# Backend (if using mypy)
cd python
mypy cube/ui/

# No console errors in browser
```

---

## 🚫 Critical Anti-Patterns

### ❌ DON'T: Use WebSocket Instead of SSE

```python
# BAD - WebSocket is overkill for one-way streaming
@app.websocket("/ws/tasks/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    await websocket.accept()
    # Complex bidirectional protocol
    while True:
        await websocket.send_json({"type": "thinking", ...})
```

**Why wrong:** WebSocket adds complexity (bidirectional, ping/pong, reconnection logic). SSE is simpler for one-way streaming and has built-in reconnection.

**Do this instead:**
```python
# GOOD - Simple SSE
@app.get("/api/tasks/{task_id}/stream")
async def stream_task(task_id: str):
    async def event_generator():
        queue = asyncio.Queue()
        while True:
            msg = await queue.get()
            yield f"data: {json.dumps(msg)}\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

### ❌ DON'T: Reimplement Layout Logic

```python
# BAD - Duplicating BaseThinkingLayout logic
class SSELayout:
    def add_thinking(self, box_id, text):
        # Reimplementing buffer management
        if box_id not in self.buffers:
            self.buffers[box_id] = []
        self.buffers[box_id].append(text)
        if text.endswith('.'):
            # Complex flushing logic...
```

**Why wrong:** Duplicates 100+ lines of tested logic from `BaseThinkingLayout`. Violates DRY principle.

**Do this instead:**
```python
# GOOD - Adapter pattern reuses logic
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

### ❌ DON'T: Forget SSE Format

```python
# BAD - Wrong SSE format
async def event_generator():
    while True:
        msg = await queue.get()
        yield json.dumps(msg)  # Missing "data: " prefix and "\n\n"
```

**Why wrong:** EventSource expects specific format: `data: {JSON}\n\n`. Wrong format causes silent failures.

**Do this instead:**
```python
# GOOD - Correct SSE format
async def event_generator():
    while True:
        msg = await queue.get()
        yield f"data: {json.dumps(msg)}\n\n"  # ✅ Correct format
```

### ❌ DON'T: Memory Leaks in EventSource

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

**Do this instead:**
```typescript
// GOOD - Cleanup on unmount
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

### ❌ DON'T: Block the Event Loop

```python
# BAD - Synchronous operation in async function
async def event_generator():
    while True:
        # Blocking file I/O!
        with open(f'logs/{task_id}.log') as f:
            line = f.readline()
        yield f"data: {json.dumps({'content': line})}\n\n"
```

**Do this instead:**
```python
# GOOD - Use async queue
async def event_generator():
    queue = asyncio.Queue()
    while True:
        msg = await queue.get()  # ✅ Non-blocking
        yield f"data: {json.dumps(msg)}\n\n"
```

---

## 🧪 Testing Checklist

**Before committing, verify:**

### Backend Tests

- [ ] SSE endpoint returns 200 OK
- [ ] Content-Type is `text/event-stream`
- [ ] Messages have correct format: `data: {...}\n\n`
- [ ] Heartbeat sent every 30s
- [ ] CORS headers present
- [ ] No Python errors in console

**Test with curl:**
```bash
curl -N http://localhost:3030/api/tasks/test-task/stream
# Should see heartbeat messages
```

### Frontend Tests

- [ ] Task detail page loads
- [ ] Connection indicator shows green when connected
- [ ] Thinking boxes update in real-time
- [ ] Output stream shows messages
- [ ] Auto-scrolls to latest output
- [ ] Timestamps display correctly
- [ ] No TypeScript errors: `npx tsc --noEmit`
- [ ] No console errors in browser

### Integration Tests

- [ ] Start task via CLI
- [ ] Open task detail in browser
- [ ] Verify thinking boxes stream live
- [ ] Verify output stream shows tool calls
- [ ] Stop backend → connection indicator turns red
- [ ] Restart backend → reconnects automatically
- [ ] Check Network tab for SSE connection

### Quality Tests

- [ ] TypeScript compiles: `npx tsc --noEmit`
- [ ] ESLint clean: `npm run lint`
- [ ] No memory leaks (close and reopen page multiple times)
- [ ] Connection closes on unmount (check Network tab)

---

## ⚠️ Common Pitfalls & Solutions

| Problem | Cause | Solution |
|---------|-------|----------|
| SSE connection closes immediately | Wrong SSE format | Ensure `data: {JSON}\n\n` format exactly |
| CORS errors | Missing headers | Add CORS headers in StreamingResponse |
| Memory leak | EventSource not closed | Add cleanup in useEffect return |
| No messages received | Wrong URL | Check SSE URL matches backend endpoint |
| Thinking boxes don't update | Messages not filtered correctly | Verify `type === 'thinking'` filter |
| Output not scrolling | Auto-scroll not working | Check useRef and scrollIntoView |

---

## 🎨 Styling Guidelines

**OutputStream component:**
- Background: `bg-cube-gray`
- Border: `border-gray-700`
- Height: `h-96` (fixed height for scrolling)
- Font: `font-mono text-xs`
- Text: `text-gray-300`
- Timestamps: `text-gray-500`
- Agents: `text-green-400` (Writer A), `text-blue-400` (Writer B)

**Connection indicator:**
- Connected: `bg-green-500` dot
- Disconnected: `bg-red-500` dot
- Size: `w-2 h-2 rounded-full`

---

## ✅ Definition of Done

**You're done when:**

### Functionality Complete
- [ ] SSE endpoint implemented and streaming
- [ ] SSE layout adapter reuses BaseThinkingLayout
- [ ] useSSE hook manages connections
- [ ] OutputStream component displays logs
- [ ] TaskDetail page shows live updates
- [ ] Auto-scroll works
- [ ] Connection status indicator works
- [ ] Reconnects on disconnect

### Code Quality
- [ ] TypeScript compiles: `npx tsc --noEmit`
- [ ] ESLint clean: `npm run lint`
- [ ] Type hints on all Python functions
- [ ] No console errors
- [ ] No memory leaks

### Testing Passed
- [ ] Manual tests passed (see checklist)
- [ ] SSE endpoint tested with curl
- [ ] Integration test passed (CLI → UI)
- [ ] Reconnection tested

### Documented
- [ ] SSE message format documented
- [ ] Code has clear comments
- [ ] No TODO comments left

---

## 🚀 Final Steps - CRITICAL

**⚠️ DO NOT SKIP THIS SECTION**

### 1. Check What Changed

```bash
cd /Users/jacob/dev/agent-cube
git status
```

### 2. Stage Your Changes

```bash
# Backend
git add python/cube/ui/sse_layout.py
git add python/cube/ui/routes/stream.py
git add python/cube/ui/server.py

# Frontend
git add web-ui/src/hooks/useSSE.ts
git add web-ui/src/components/OutputStream.tsx
git add web-ui/src/pages/TaskDetail.tsx
git add web-ui/src/types/
```

### 3. Commit with Conventional Message

```bash
git commit -m "feat(ui): implement task detail view with SSE live streaming

Backend:
- Created SSELayout adapter that reuses BaseThinkingLayout logic
- Implemented /api/tasks/{id}/stream SSE endpoint
- Added message queuing with asyncio.Queue
- Configured CORS headers for EventSource

Frontend:
- Created useSSE hook for EventSource connection management
- Implemented OutputStream component with auto-scroll
- Updated TaskDetail page with real-time thinking boxes
- Separated thinking vs output message streams
- Added connection status indicator
- Auto-reconnection on disconnect

Tests:
- Manual testing with CLI integration
- SSE endpoint tested with curl
- Verified memory cleanup on unmount
- Verified auto-reconnection

Refs: task 05-task-detail-view"
```

### 4. Push to Remote Branch

```bash
git push origin writer-[your-model-slug]/05-task-detail-view
```

### 5. Verify Push Succeeded

```bash
# Should show branch is up to date with origin
git status

# Should show your commit on remote
git log origin/$(git branch --show-current) -1 --oneline
```

### 6. CRITICAL VERIFICATION

**After pushing, verify:**

```bash
# Check for unpushed commits (should be empty)
git log origin/HEAD..HEAD

# If you see commits, push again!
git push origin HEAD
```

### ⚠️ **If push fails:**
- Resolve any conflicts
- Push again
- **Do NOT leave unpushed commits!**
- Uncommitted or unpushed work will NOT be reviewed!

---

## 📁 File Structure

**Your changes should create/modify:**

```
python/cube/ui/
├── sse_layout.py               # NEW - SSE adapter for BaseThinkingLayout
├── server.py                   # MODIFIED - Register stream router
└── routes/
    └── stream.py               # NEW - SSE streaming endpoint

web-ui/src/
├── hooks/
│   └── useSSE.ts               # NEW - SSE connection hook
├── components/
│   └── OutputStream.tsx        # NEW - Scrolling log component
├── pages/
│   └── TaskDetail.tsx          # MODIFIED - Add SSE integration
└── types/
    └── index.ts                # MODIFIED - Add SSEMessage type
```

**Do NOT modify:**
- Core automation modules (just import)
- Thinking box components (Task 03 created these)
- Dashboard (Task 04 owns this)
- Base layout logic (reuse via adapter)

---

## 🔗 Integration Points

**Your code integrates with:**

1. **Backend API (Task 02):**
   - Existing server at `http://localhost:3030`
   - Add new SSE endpoint to router

2. **Thinking Boxes (Task 03):**
   - Import `DualLayout` and `TripleLayout`
   - Pass thinking lines as props

3. **Dashboard (Task 04):**
   - Dashboard links to `/tasks/:id`
   - Your TaskDetail page renders at that route

4. **Core Automation:**
   - Import `BaseThinkingLayout` from `cube.core.base_layout`
   - Reuse existing layout logic via inheritance

---

## 📖 Reference Material

**Planning docs:**
- `/Users/jacob/dev/agent-cube/planning/web-ui.md`
  - Look for "SSE Streaming Architecture" section
  - Message format specification
  - Real-time architecture principles

**Code references:**
- `python/cube/core/base_layout.py` - Layout logic to reuse
- `python/cube/automation/dual_writers.py` - See how layout is used
- `web-ui/src/components/DualLayout.tsx` - Thinking box component

**External docs:**
- [Server-Sent Events (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [FastAPI StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- [EventSource API](https://developer.mozilla.org/en-US/docs/Web/API/EventSource)

---

## 💡 Tips for Success

1. **Start with backend:** Get SSE endpoint working with curl before frontend
2. **Test SSE format:** Wrong format = silent failures. Test with curl first.
3. **Use adapter pattern:** Don't reimplement layout logic, inherit it
4. **Test reconnection:** Stop/start backend to verify auto-reconnect
5. **Check Network tab:** See SSE connection and messages in browser DevTools
6. **Memory cleanup:** Always close EventSource in useEffect cleanup
7. **Type everything:** TypeScript will catch message format mistakes
8. **Small iterations:** Test each piece (backend, hook, component, page) separately

---

## 🎉 You're Done When...

✅ SSE endpoint streams events with curl  
✅ Frontend connects and receives messages  
✅ Thinking boxes update in real-time  
✅ Output stream shows tool calls  
✅ Auto-scroll works  
✅ Connection indicator accurate  
✅ Reconnects on disconnect  
✅ No memory leaks  
✅ TypeScript compiles  
✅ Changes committed  
✅ **Changes pushed to remote branch**

---

## ❓ Troubleshooting

**"SSE connection closes immediately"**
→ Check SSE format: Must be `data: {JSON}\n\n` exactly

**"CORS error on EventSource"**
→ Ensure StreamingResponse includes CORS headers

**"Messages not received"**
→ Check Network tab in DevTools, verify SSE connection is open

**"Thinking boxes don't update"**
→ Check message filtering: `msg.type === 'thinking'`

**"Memory leak warning"**
→ Ensure EventSource.close() in useEffect cleanup

**"Auto-scroll not working"**
→ Check useRef is attached to div at bottom of list

**"Backend crashes on stream"**
→ Check async/await usage, ensure queue operations are non-blocking

---

**Good luck! This is the most complex task in the workflow. Take your time, test incrementally, and follow the anti-patterns guide closely! 🚀**

**Remember:** The power of Agent Cube is real-time monitoring. Make it smooth and responsive!

---

**Generated by:** Agent Cube v1.0  
**Template:** Dual-Writer Workflow  
**Date:** 2025-11-11
