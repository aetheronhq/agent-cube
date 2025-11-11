# Task 05: Task Detail View with Live Stream

**Goal:** Detailed task page showing thinking boxes, output stream, and controls

## Context

The main view where users monitor a specific workflow. Shows real-time agent activity.

## Requirements

### 1. Task Header

- Task ID and title
- Phase indicator: "Phase 7/10 - SYNTHESIS"
- Progress bar
- Winner badge (if decided)
- Status (Running/Waiting/Complete)

### 2. Thinking Boxes Integration

Use components from Task 03:
- Show dual boxes when writers active
- Show triple boxes when judges active
- Auto-switch based on current phase

### 3. Output Stream

**Terminal-like output:**
```
[Writer A] 📖 src/client.ts
[Writer A]    ✅ 156 lines
[Writer B] 📝 src/types.ts
[Writer B]    ✅ 89 lines
[Judge 1] 💭 Reviewing implementation...
```

**Features:**
- Auto-scroll to bottom
- Color-coded by agent
- Icons for tool types
- Timestamps (optional toggle)
- Search/filter output

### 4. Action Panel

**Buttons:**
- Resume workflow
- Pause (future)
- View decisions
- View logs
- Clean up

**Phase-specific actions:**
- Phase 5: "Run Decide"
- Phase 7: "Skip to PR" (if approved)
- Phase 8+: "Create PR"

### 5. Side Panel (Collapsible)

**Tabs:**
- **Status:** Current phase, completed phases
- **Decisions:** Panel/peer review results
- **Sessions:** Active agent sessions
- **Files:** Generated prompts, decisions

## Deliverables

- [ ] Task detail page at `/task/:id`
- [ ] Real-time SSE integration
- [ ] Thinking boxes update live
- [ ] Output stream scrolls
- [ ] Action buttons work
- [ ] Side panel with tabs
- [ ] Responsive layout
- [ ] Back to dashboard link

## Architecture Constraints

**Streaming:**
```tsx
const { thinking, output, phase } = useWorkflowStream(taskId)

// Auto-updates from SSE
useEffect(() => {
  const es = new EventSource(`/api/workflows/${taskId}/stream`)
  es.onmessage = (e) => {
    const data = JSON.parse(e.data)
    if (data.type === 'thinking') addThought(data.agent, data.text)
    if (data.type === 'tool_call') addOutput(data)
    if (data.type === 'phase') setPhase(data.phase)
  }
  return () => es.close()
}, [taskId])
```

**Performance:**
- ✅ Virtual scroll for output (1000+ lines)
- ✅ Debounce thinking updates
- ✅ Lazy load side panel tabs

## UI Layout

```
┌────────────────────────────────────────────────────────┐
│ ← Dashboard    05-feature-flags-server                 │
│ Phase 7/10 (70%) - SYNTHESIS │ Winner: B │ ⏸ Running  │
├────────────────────────────────────────────────────────┤
│ ┌─ Writer A ──────────┐ ┌─ Writer B ──────────┐       │
│ │ Fixing timeout...   │ │ Adding types...     │       │
│ │ Running tests...    │ │ Updating docs...    │       │
│ └─────────────────────┘ └─────────────────────┘       │
│                                                        │
│ 📤 Output ─────────────────────────────────────────    │
│ [Writer A] 📖 src/timeout.ts                           │
│ [Writer A]    ✅ 45 lines                              │
│ [Writer B] 📝 src/types.ts                             │
│ [Writer B]    ✅ 89 lines                              │
│ ...                                                    │
│                                                        │
│ [Resume] [Decide] [View Decisions]                     │
└────────────────────────────────────────────────────────┘
```

## Acceptance Criteria

1. Shows live thinking boxes
2. Output stream updates in real-time
3. Can execute commands
4. Phase progress accurate
5. Side panel info correct
6. Responsive layout works
7. Back navigation works

## Time Estimate

5-6 hours

