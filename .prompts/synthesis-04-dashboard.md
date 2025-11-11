# Synthesis Prompt: Task 04-Dashboard

**Branch:** `writer-sonnet/04-dashboard`  
**Status:** Winner - Requires API Alignment Fixes  
**Judge Consensus:** 2/3 APPROVED, 1/3 REQUEST_CHANGES  
**Scores:** Writer A: 7.53, Writer B: 7.08

---

## 🎯 What Judges Loved About Your Implementation

Your implementation won because of its **simplicity and adherence to KISS principles**:

**Judge 3 (Score: 9.0/10):**
> "Writer A (Sonnet) is the clear winner. The implementation is simple, clean, and directly follows the architectural guidelines and KISS principles outlined in the prompt. It meets all functional requirements correctly."

**Judge 1 (Score: 8.3/10):**
- ✅ Clean, readable implementation following KISS principles
- ✅ All core requirements met: task list, status overview, auto-refresh, navigation
- ✅ Proper TypeScript types with no 'any' types
- ✅ Correct progress bar calculation and status badge colors
- ✅ TypeScript compiles cleanly with no errors

**Keep these strengths:**
- Simple, straightforward state management
- Clean component structure
- Proper TypeScript typing
- Auto-refresh with proper cleanup

---

## 🚨 Critical Blocker Issue - API Field Mismatch

**Judge 2 identified a blocking issue that affects both implementations:**

> "Both implementations assume the tasks API returns a `phase` field and statuses limited to 'active'/'completed'/'failed', but the backend exposes `current_phase` and workflow status strings like 'in-progress' or 'writers-complete'. As a result the dashboards render 'undefined/10' progress, NaN% bars, and incorrect active/completed counts, so the core functionality requires correction."

**Current Problem:**
Your code expects:
```typescript
interface Task {
  id: string;
  phase: number;              // ❌ Backend returns `current_phase`
  path: string;
  status?: "active" | "completed" | "failed";  // ❌ Backend returns workflow status strings
}
```

But the backend actually returns:
```typescript
{
  id: string;
  current_phase: number;      // ✅ Actual field name
  path: string;
  workflow_status: string;    // ✅ Values like "in-progress", "writers-complete", "judges-complete", etc.
}
```

---

## 🔧 Required Fixes

### 1. Update Type Definitions (`src/types/index.ts`)

**Current (lines 1-6):**
```typescript
export interface Task {
  id: string;
  phase: number;
  path: string;
  status?: "active" | "completed" | "failed";
}
```

**Fix:** Update to match the actual API response:
```typescript
export interface Task {
  id: string;
  current_phase: number;
  path: string;
  workflow_status: string;  // "in-progress", "writers-complete", "judges-complete", "complete", etc.
}
```

### 2. Fix TaskCard Progress Display (`src/components/TaskCard.tsx`)

**Current issue (line 19, 33):**
```typescript
const progressPercentage = (task.phase / 10) * 100;
// ...
<div className="text-sm text-gray-400 mb-2">Phase {task.phase}/10</div>
```

**Fix:** Use `current_phase` instead:
```typescript
const progressPercentage = (task.current_phase / 10) * 100;
// ...
<div className="text-sm text-gray-400 mb-2">Phase {task.current_phase}/10</div>
```

### 3. Fix Status Badge Logic (`src/components/TaskCard.tsx`)

**Current issue (lines 12-17, 29):**
```typescript
const statusColor =
  task.status === "completed"
    ? "bg-blue-600"
    : task.status === "failed"
      ? "bg-red-600"
      : "bg-green-600";
// ...
{task.status || "active"}
```

**Fix:** Map workflow_status to colors and display:
```typescript
const getStatusColor = (workflowStatus: string): string => {
  if (workflowStatus === "complete") return "bg-blue-600";
  if (workflowStatus === "failed" || workflowStatus === "error") return "bg-red-600";
  return "bg-green-600";  // in-progress, writers-complete, judges-complete, etc.
};

const statusColor = getStatusColor(task.workflow_status);
// ...
{task.workflow_status}
```

### 4. Fix Active/Completed Counts (`src/pages/Dashboard.tsx`)

**Current issue (lines 57-58):**
```typescript
const activeTasks = tasks.filter((t) => t.status !== "completed");
const completedTasks = tasks.filter((t) => t.status === "completed");
```

**Fix:** Use workflow_status:
```typescript
const activeTasks = tasks.filter((t) => t.workflow_status !== "complete");
const completedTasks = tasks.filter((t) => t.workflow_status === "complete");
```

---

## 📋 Complete Change Summary

**Files to modify:**
1. `src/types/index.ts` - Update Task interface (lines 1-6)
2. `src/components/TaskCard.tsx` - Update field references and status logic (lines 12-19, 29, 33)
3. `src/pages/Dashboard.tsx` - Update filter logic (lines 57-58)

**What NOT to change:**
- Keep your simple state management approach
- Keep the existing component structure
- Keep the auto-refresh pattern with cleanup
- Keep the loading/error/empty states as-is
- Don't add abort controllers or other complexity (judges appreciated your simplicity)

---

## ✅ Testing & Validation

After making changes, verify:
1. TypeScript compiles with no errors: `npm run build`
2. Progress bars show percentages correctly (not NaN%)
3. Phase display shows "Phase X/10" correctly (not "undefined/10")
4. Active/Completed counts are accurate
5. Status badges display workflow_status strings
6. Status badge colors work (blue for complete, red for failed/error, green for in-progress)

---

## 🚀 When Complete

1. Test your changes locally
2. Verify TypeScript compilation succeeds
3. **Commit your changes:**
   ```bash
   git add src/types/index.ts src/components/TaskCard.tsx src/pages/Dashboard.tsx
   git commit -m "Fix: Align dashboard with backend API fields (current_phase, workflow_status)"
   ```
4. **Push to your branch:**
   ```bash
   git push origin writer-sonnet/04-dashboard
   ```

---

## 💡 Context

Your implementation won because it exemplifies the **KISS principle** that this project values. Judge 3 gave you 10/10 for KISS compliance, while the other implementation scored only 3/10 for over-engineering. Your simple, clean approach is exactly what we need - we just need to fix the API field mapping to make it functional.

The fixes above are surgical and preserve your winning architecture. Make these changes and you'll have a production-ready dashboard that maintains the simplicity judges praised.
