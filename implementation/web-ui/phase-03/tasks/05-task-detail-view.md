# Task 05: Task Detail View with Live Streaming

**Goal:** Implement task detail page with real-time SSE streaming of thinking boxes and output, matching the CLI's live display.

**Time Estimate:** 4-6 hours

---

## 📖 **Context**

**What this builds on:**
- Task 01: Routing and page structure
- Task 02: Backend API (will add `/api/tasks/{id}/stream` SSE endpoint)
- Task 03: DualLayout and TripleLayout components
- Core AgentCube UX is real-time agent monitoring

**Planning docs (Golden Source):**
- `planning/web-ui.md` - SSE streaming, message format, real-time architecture

---

## ✅ **Requirements**

### **1. SSE Streaming Endpoint (Backend)**

**Deliverable:**
- Add `/api/tasks/{id}/stream` endpoint to FastAPI
- Stream thinking and output events
- Adapt existing layout to send SSE messages

**Acceptance criteria:**
- [ ] `routes/stream.py` created in backend
- [ ] SSE endpoint returns `text/event-stream`
- [ ] Streams messages in format: `data: {JSON}\n\n`
- [ ] Intercepts layout calls (thinking and output)
- [ ] Cleans up on client disconnect

### **2. useSSE Hook (Frontend)**

**Deliverable:**
- Custom React hook for SSE connections
- Handles connection, reconnection, cleanup
- Type-safe message parsing

**Acceptance criteria:**
- [ ] `hooks/useSSE.ts` created
- [ ] Returns message stream
- [ ] Auto-reconnects on disconnect
- [ ] Cleans up on unmount
- [ ] Error handling for connection failures

### **3. TaskDetail Page**

**Deliverable:**
- Live task monitoring page
- Shows thinking boxes (dual or triple based on phase)
- Shows output stream below
- Control buttons (start, stop, feedback)

**Acceptance criteria:**
- [ ] `pages/TaskDetail.tsx` updated
- [ ] Fetches task info from `/api/tasks/{id}`
- [ ] Connects to SSE stream
- [ ] Displays DualLayout or TripleLayout based on phase
- [ ] Displays output stream (scrolling log)
- [ ] Auto-scrolls to latest output

### **4. OutputStream Component**

**Deliverable:**
- Scrolling output log component
- Displays tool calls, messages, status
- Color-coded by agent

**Acceptance criteria:**
- [ ] `components/OutputStream.tsx` created
- [ ] Displays messages with timestamps
- [ ] Color codes by agent (green/blue for writers)
- [ ] Auto-scrolls to bottom
- [ ] Monospace font for consistency

---

## 📝 **Implementation Steps**

**Suggested order:**

1. **Backend: SSE Layout Adapter**
   - [ ] Create `python/cube/ui/sse_layout.py`
   - [ ] Inherit from `BaseThinkingLayout`
   - [ ] Override `add_thinking` and `add_output` to queue SSE messages
   - [ ] Use `asyncio.Queue` for message passing

2. **Backend: SSE Endpoint**
   - [ ] Create `python/cube/ui/routes/stream.py`
   - [ ] Implement `/api/tasks/{id}/stream` endpoint
   - [ ] Use `StreamingResponse` from FastAPI
   - [ ] Send SSE formatted messages
   - [ ] Handle client disconnect

3. **Frontend: useSSE Hook**
   - [ ] Create `src/hooks/useSSE.ts`
   - [ ] Use EventSource API
   - [ ] Parse SSE messages
   - [ ] Return messages array and connection status

4. **Frontend: OutputStream Component**
   - [ ] Create `src/components/OutputStream.tsx`
   - [ ] Accept messages array
   - [ ] Render in scrolling div
   - [ ] Auto-scroll with useRef and useEffect

5. **Frontend: TaskDetail Page**
   - [ ] Update `src/pages/TaskDetail.tsx`
   - [ ] Fetch task info on mount
   - [ ] Connect to SSE stream
   - [ ] Separate thinking vs output messages
   - [ ] Render correct layout based on phase

6. **Test Integration**
   - [ ] Start a task: `cube writers test-task test.md`
   - [ ] Open UI: `http://localhost:5173/tasks/test-task`
   - [ ] Verify thinking boxes update in real-time
   - [ ] Verify output stream shows messages

7. **Verify**
   - [ ] Real-time updates work
   - [ ] Reconnects on disconnect
   - [ ] No memory leaks
   - [ ] Clean UI state transitions

8. **Finalize**
   - [ ] Commit backend and frontend changes
   - [ ] Push to branch

---

## 🏗️ **Architecture Constraints**

### **Must Follow**

**Planning docs:**
- SSE message format from `planning/web-ui.md`
- Real-time first principle (no polling)
- Reuse existing layout logic

**Technical constraints:**
- SSE for server→client only (POST for client→server)
- Type-safe message parsing
- Graceful connection handling
- Memory cleanup on unmount

**KISS Principles:**
- ✅ SSE over WebSocket (simpler)
- ✅ Adapter pattern for layout (reuse logic)
- ✅ Single SSE connection per task
- ❌ No complex buffering (EventSource handles it)
- ❌ No message acknowledgment (one-way is sufficient)

---

## 🚫 **Anti-Patterns**

### **❌ DON'T: Use WebSocket for One-Way Streaming**

```python
# Bad: WebSocket is overkill
@app.websocket("/ws/tasks/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    await websocket.accept()
    # Complex bidirectional protocol
```

**Instead:**
```python
# Good: Simple SSE
@app.get("/api/tasks/{task_id}/stream")
async def stream_task(task_id: str):
    async def event_generator():
        queue = asyncio.Queue()
        # Stream messages
        while True:
            msg = await queue.get()
            yield f"data: {json.dumps(msg)}\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

### **❌ DON'T: Reimplement Layout Logic**

```python
# Bad: Duplicating layout code
class SSELayout:
    def add_thinking(self, box_id, text):
        # BAD: Reimplementing BaseThinkingLayout logic
        self.buffers[box_id].append(text)
        if text.endswith('.'):
            # Complex logic duplicated...
```

**Instead:**
```python
# Good: Adapt existing layout
class SSELayout(BaseThinkingLayout):
    def __init__(self, queue: asyncio.Queue):
        super().__init__(boxes)
        self.queue = queue
    
    def add_thinking(self, box_id: str, text: str):
        super().add_thinking(box_id, text)  # Reuse logic
        asyncio.create_task(self.queue.put({
            "type": "thinking",
            "box": box_id,
            "text": text
        }))
```

---

## 📂 **Owned Paths**

**This task owns:**
```
python/cube/ui/
├── sse_layout.py          # SSE adapter for layouts
└── routes/
    └── stream.py          # SSE streaming endpoint

web-ui/src/
├── hooks/
│   └── useSSE.ts          # SSE connection hook
├── components/
│   └── OutputStream.tsx   # Output log component
└── pages/
    └── TaskDetail.tsx     # Task monitoring page
```

**Must NOT modify:**
- Core automation modules (just import)
- Thinking box components (Task 03)
- Dashboard (Task 04)

**Integration:**
- Uses DualLayout/TripleLayout from Task 03
- Linked from Dashboard (Task 04)
- Backend imports from `cube.automation`

---

## 🧪 **Testing Requirements**

**Manual testing:**
- [ ] Start dual writers: `cube writers test-task test.md`
- [ ] Open UI: `http://localhost:5173/tasks/test-task`
- [ ] Verify thinking boxes update in real-time
- [ ] Verify output stream shows tool calls
- [ ] Disconnect backend, verify reconnect
- [ ] Check Network tab for SSE connection

**Test SSE endpoint:**
```bash
# With curl (should stream events)
curl -N http://localhost:3030/api/tasks/test-task/stream

# Should see:
# data: {"type":"thinking","box":"writer-a","text":"..."}
#
# data: {"type":"output","agent":"Writer A","content":"..."}
```

---

## ✅ **Acceptance Criteria**

**Definition of Done:**

- [ ] SSE endpoint `/api/tasks/{id}/stream` implemented
- [ ] `SSELayout` adapter created
- [ ] `useSSE` hook implemented
- [ ] `OutputStream` component created
- [ ] `TaskDetail` page updated with SSE integration
- [ ] Real-time thinking boxes work
- [ ] Real-time output stream works
- [ ] Auto-scroll to latest output
- [ ] Reconnects on disconnect
- [ ] Memory cleanup on unmount
- [ ] TypeScript compiles: `npx tsc --noEmit`
- [ ] Backend and frontend committed and pushed

**Quality gates:**
- [ ] Follows KISS (SSE, not WebSocket)
- [ ] Reuses layout logic (adapter pattern)
- [ ] No memory leaks
- [ ] Clean error handling

---

## 🔗 **Integration Points**

**Dependencies (requires these first):**
- Task 02: Backend API base
- Task 03: Thinking box components

**Dependents (these will use this):**
- None (core monitoring feature)

**Integrator task:**
- This task bridges backend and frontend for real-time streaming

---

## 📊 **Examples**

### **SSE Message Format**

```typescript
interface SSEMessage {
  type: 'thinking' | 'output' | 'status';
  agent?: string;        // "Writer A", "Judge 1"
  box?: string;          // "writer-a", "judge-1"
  content: string;
  timestamp: string;
}
```

### **sse_layout.py**

```python
import asyncio
import json
from ..core.base_layout import BaseThinkingLayout

class SSELayout(BaseThinkingLayout):
    def __init__(self, boxes: dict, queue: asyncio.Queue):
        super().__init__(boxes)
        self.queue = queue
    
    def add_thinking(self, box_id: str, text: str) -> None:
        super().add_thinking(box_id, text)
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

### **routes/stream.py**

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

### **hooks/useSSE.ts**

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

### **components/OutputStream.tsx**

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

### **pages/TaskDetail.tsx**

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

## 🎓 **Common Pitfalls**

**Watch out for:**
- ⚠️ CORS errors (backend must send correct headers for SSE)
- ⚠️ Memory leaks (close EventSource on unmount)
- ⚠️ SSE format errors (must be `data: {JSON}\n\n`)

**If you see [connection closes immediately], it means [SSE format wrong] - fix by [checking yield format in backend]**

---

## 📝 **Notes**

**Additional context:**
- SSE connections have ~100 concurrent limit (sufficient for local dev)
- EventSource API is well-supported in modern browsers
- Auto-reconnect is built into EventSource

**Nice-to-haves (not required):**
- Pause/resume stream
- Download output as text file
- Search/filter output

---

**FINAL STEPS - CRITICAL:**

```bash
# Stage changes (both backend and frontend)
git add python/cube/ui/ web-ui/src/

# Commit
git commit -m "feat(ui): implement task detail view with SSE live streaming"

# Push
git push origin writer-[your-model-slug]/05-task-detail-view

# Verify
git status
```

**⚠️ IMPORTANT:** Uncommitted or unpushed changes will NOT be reviewed!

---

**Built with:** Agent Cube v1.0
**Template version:** 1.0
**Last updated:** 2025-11-11

