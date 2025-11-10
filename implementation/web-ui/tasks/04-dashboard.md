# Task 04: Dashboard & Workflow Management

**Goal:** Main dashboard showing all active workflows with controls

## Context

Central hub for managing multiple autonomous workflows in parallel.

## Requirements

### 1. Active Workflows List

**Display for each task:**
- Task ID and title
- Current phase (7/10)
- Progress bar
- Path (SYNTHESIS/FEEDBACK/MERGE)
- Winner (if decided)
- Status (Running/Complete/Error)

### 2. Workflow Cards

```tsx
<WorkflowCard
  taskId="05-feature-flags"
  phase={7}
  totalPhases={10}
  path="SYNTHESIS"
  winner="B"
  status="running"
  onClick={() => navigate(`/task/05-feature-flags`)}
/>
```

### 3. Start Workflow Form

- File upload or path input
- "Start Autonomous Workflow" button
- Shows progress immediately after start

### 4. Quick Actions

Per workflow card:
- [View Details] - Navigate to task page
- [Decide] - Run cube decide
- [Resume] - Quick resume from checkpoint
- [Clean] - Remove task

### 5. Filters & Search

- Filter by status (running/complete/error)
- Filter by path (SYNTHESIS/FEEDBACK/MERGE)
- Search by task ID
- Sort by phase progress

## Deliverables

- [ ] Dashboard shows all active workflows
- [ ] Workflow cards with phase progress
- [ ] Start new workflow form
- [ ] Navigate to task details
- [ ] Quick actions on each card
- [ ] Real-time updates (polling or SSE)
- [ ] Filters and search work
- [ ] Responsive layout

## Architecture Constraints

**Data Loading:**
```tsx
const { data: workflows } = useQuery(
  ['workflows'],
  () => api.getWorkflows(),
  { refetchInterval: 2000 }  // Poll every 2s
)
```

**State Management:**
- ✅ React Query for server state
- ✅ URL state for filters
- ❌ No Zustand yet (not needed)

**Layout:**
- ✅ Grid layout (responsive)
- ✅ 1 column mobile, 2-3 desktop
- ✅ Cards are clickable
- ❌ No infinite scroll (paginate if >20)

## UI Design

```
┌────────────────────────────────────────────┐
│ 🎲 Agent Cube       [+ New Workflow] [⚙️]  │
├────────────────────────────────────────────┤
│                                            │
│ Active Workflows (3)                       │
│                                            │
│ ┌──────────────────┐ ┌──────────────────┐ │
│ │ 05-feature-flags │ │ 04-exemplar      │ │
│ │ Phase 7/10 (70%) │ │ Phase 4/10 (40%) │ │
│ │ ███████░░░       │ │ ████░░░░░░       │ │
│ │ SYNTHESIS        │ │ Panel Running    │ │
│ │ Winner: B        │ │ --               │ │
│ │                  │ │                  │ │
│ │ [Details] [✓]    │ │ [Details]        │ │
│ └──────────────────┘ └──────────────────┘ │
│                                            │
│ [Filter: All] [Search...]                  │
└────────────────────────────────────────────┘
```

## Acceptance Criteria

1. Shows all active workflows from state
2. Real-time updates every 2s
3. Can start new workflow
4. Navigate to task details
5. Quick actions work
6. Filters work
7. Responsive on mobile
8. Loading states shown

## API Integration

```typescript
// GET /api/workflows
interface Workflow {
  task_id: string
  current_phase: number
  path: string
  winner?: string
  status: 'running' | 'complete' | 'error'
}

// POST /api/workflows
interface StartWorkflowRequest {
  task_file: string
}
```

## Time Estimate

4-5 hours

