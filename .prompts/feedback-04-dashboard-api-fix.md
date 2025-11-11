# Feedback: Fix API Field Mismatch

**Issue:** Judge 2's blocker - Dashboard expects different field names than the backend returns

## The Problem

The backend returns different field names than your code expects:
- ❌ Your code uses: `task.phase` 
- ✅ Backend returns: `task.current_phase`
- ❌ Your code uses: `task.status`
- ✅ Backend returns: `task.workflow_status`

**Backend workflow_status values:**
- `"in-progress"` - Task is running
- `"writers-complete"` - Writers finished
- `"judges-complete"` - Judges finished  
- `"complete"` - Fully complete
- `"failed"` / `"error"` - Failed

## Required Fixes

### 1. Update Type Interface (`src/types/index.ts`)

**Change lines 1-6 from:**
```typescript
export interface Task {
  id: string;
  phase: number;
  path: string;
  status?: "active" | "completed" | "failed";
}
```

**To:**
```typescript
export interface Task {
  id: string;
  current_phase: number;
  path: string;
  workflow_status: string;
}
```

### 2. Fix TaskCard Component (`src/components/TaskCard.tsx`)

**Find and replace:**
- `task.phase` → `task.current_phase` (appears in 2 places)
- `task.status === "completed"` → `task.workflow_status === "complete"`
- `task.status || "active"` → `task.workflow_status`

**Update status color logic (around line 12-17):**
```typescript
const getStatusColor = (workflowStatus: string): string => {
  if (workflowStatus === "complete") return "bg-blue-600";
  if (workflowStatus === "failed" || workflowStatus === "error") return "bg-red-600";
  return "bg-green-600";
};

const statusColor = getStatusColor(task.workflow_status);
```

### 3. Fix Dashboard Filters (`src/pages/Dashboard.tsx`)

**Change lines 57-58 from:**
```typescript
const activeTasks = tasks.filter((t) => t.status !== "completed");
const completedTasks = tasks.filter((t) => t.status === "completed");
```

**To:**
```typescript
const activeTasks = tasks.filter((t) => t.workflow_status !== "complete");
const completedTasks = tasks.filter((t) => t.workflow_status === "complete");
```

## Summary

These are simple field name changes. The logic is correct, just needs to match the actual API response format.

See `.prompts/synthesis-04-dashboard.md` for full context.

