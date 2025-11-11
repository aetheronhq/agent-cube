# Writer Prompt: Task 04 - Dashboard Multi-Workflow Management

**Task ID:** 04-dashboard  
**Complexity:** Medium (2-3 hours)  
**Branch:** `writer-[your-model-slug]/04-dashboard`  
**Generated:** 2025-11-11

---

## 🎯 Your Mission

Build the **Dashboard page** that displays all Agent Cube tasks with status, phase progress, and quick navigation. This is the main entry point for the web UI.

**You are implementing:**
- Task list display with cards
- Status overview (active/completed counts)
- Auto-refresh polling (5s interval)
- Navigation to task detail pages

---

## 📚 Context & Dependencies

### What You're Building On

**Previous tasks (completed):**
- **Task 01:** Page structure and routing (`/`, `/tasks/:id` routes exist)
- **Task 02:** Backend API (`GET /api/tasks` endpoint available at `http://localhost:3030`)

**Key facts:**
- Backend serves task data from state directory (JSON files)
- Tasks have phases 1-10 (writer → synthesis loop)
- Status: `active`, `completed`, or `failed`
- This dashboard is the homepage (`/`)

### Golden Source Documents

**Planning doc:** `planning/web-ui.md`
- Section: "Dashboard Component"
- API Endpoint: `GET /api/tasks` returns `{ tasks: Task[] }`

**Architecture:**
- React + TypeScript + Vite
- TailwindCSS for styling
- React Router for navigation
- Simple component state (no Redux/Zustand needed)

---

## ✅ Requirements Checklist

### 1. Task List Display

**What to build:**
- Grid of task cards (responsive: 1 col mobile, 2 tablet, 3 desktop)
- Each card shows: task ID, phase (X/10), status badge, decision path
- Clickable cards navigate to `/tasks/:id`

**Acceptance criteria:**
- [ ] Fetches from `GET http://localhost:3030/api/tasks`
- [ ] Displays task cards in responsive grid
- [ ] Shows task ID, phase progress (1/10, 5/10, etc.)
- [ ] Click navigates to `/tasks/:id` using React Router
- [ ] Empty state when `tasks.length === 0`

### 2. Status Overview

**What to build:**
- Summary statistics at top of dashboard
- Two cards: "Active Tasks" count, "Completed Tasks" count

**Acceptance criteria:**
- [ ] Calculates counts from tasks array (filter by status)
- [ ] Displays in card format with styling
- [ ] Updates automatically when tasks change

### 3. TaskCard Component

**What to build:**
- Reusable `TaskCard.tsx` component
- Phase progress bar (visual indicator)
- Color-coded status badge

**Acceptance criteria:**
- [ ] `web-ui/src/components/TaskCard.tsx` created
- [ ] Props: `{ task: Task }` (single task object)
- [ ] Phase progress bar (0-100% based on phase/10)
- [ ] Status badge: green=active, blue=completed, red=failed
- [ ] Hover effect (border color change)

### 4. Auto-Refresh Polling

**What to build:**
- Automatic refresh every 5 seconds
- Fetch new data without full page reload

**Acceptance criteria:**
- [ ] `useEffect` with `setInterval` for polling
- [ ] Cleanup interval on component unmount
- [ ] Error handling for network failures
- [ ] No memory leaks

---

## 🏗️ Implementation Plan

**Follow this order:**

### Step 1: Create Type Definitions

**File:** `web-ui/src/types/index.ts` (add to existing or create)

```typescript
export interface Task {
  id: string;
  phase: number;
  path: string;
  status?: 'active' | 'completed' | 'failed';
}

export interface TasksResponse {
  tasks: Task[];
}
```

### Step 2: Create TaskCard Component

**File:** `web-ui/src/components/TaskCard.tsx`

**Requirements:**
- Accept `task: Task` prop
- Display task ID as heading
- Show status badge (color-coded)
- Phase indicator text ("Phase X/10")
- Progress bar (0-100% based on phase)
- Decision path (truncated)
- Click handler to navigate to `/tasks/${task.id}`

**Example structure:**
```typescript
import { useNavigate } from 'react-router-dom';
import { Task } from '../types';

interface TaskCardProps {
  task: Task;
}

export function TaskCard({ task }: TaskCardProps) {
  const navigate = useNavigate();
  
  const statusColor = task.status === 'completed' ? 'bg-blue-600' : 
                      task.status === 'failed' ? 'bg-red-600' : 'bg-green-600';
  
  return (
    <div
      onClick={() => navigate(`/tasks/${task.id}`)}
      className="border border-gray-700 rounded-lg p-4 hover:border-gray-500 cursor-pointer transition-colors bg-cube-gray"
    >
      {/* Task ID and status badge */}
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-semibold text-white">{task.id}</h3>
        <span className={`text-xs px-2 py-1 rounded ${statusColor}`}>
          {task.status || 'active'}
        </span>
      </div>
      
      {/* Phase indicator */}
      <div className="text-sm text-gray-400 mb-2">
        Phase {task.phase}/10
      </div>
      
      {/* Progress bar */}
      <div className="w-full bg-gray-700 rounded-full h-2">
        <div
          className="bg-blue-500 h-2 rounded-full"
          style={{ width: `${(task.phase / 10) * 100}%` }}
        />
      </div>
      
      {/* Decision path */}
      <div className="mt-2 text-xs text-gray-500 truncate">
        {task.path}
      </div>
    </div>
  );
}
```

### Step 3: Implement Dashboard Page

**File:** `web-ui/src/pages/Dashboard.tsx`

**Requirements:**
- State: `tasks` array, `loading` boolean, `error` string
- Fetch on mount and every 5 seconds
- Display loading state initially
- Display error state if fetch fails
- Display empty state if no tasks
- Display status overview cards (active/completed counts)
- Display task grid using TaskCard components

**Example structure:**
```typescript
import { useState, useEffect } from 'react';
import { TaskCard } from '../components/TaskCard';
import { Task, TasksResponse } from '../types';

export function Dashboard() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const res = await fetch('http://localhost:3030/api/tasks');
        if (!res.ok) throw new Error('Failed to fetch tasks');
        const data: TasksResponse = await res.json();
        setTasks(data.tasks);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
    const interval = setInterval(fetchTasks, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="text-center py-12">Loading tasks...</div>;
  }

  if (error) {
    return (
      <div className="text-center py-12 text-red-400">
        Error: {error}
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className="text-center py-12 text-gray-400">
        <p className="text-lg mb-2">No tasks yet</p>
        <p className="text-sm">Start a task with: cube auto &lt;task-file&gt;</p>
      </div>
    );
  }

  const activeTasks = tasks.filter(t => t.status !== 'completed');
  const completedTasks = tasks.filter(t => t.status === 'completed');

  return (
    <div>
      {/* Status overview */}
      <div className="mb-8 grid grid-cols-2 gap-4">
        <div className="border border-gray-700 rounded-lg p-4 bg-cube-gray">
          <div className="text-2xl font-bold text-green-500">{activeTasks.length}</div>
          <div className="text-sm text-gray-400">Active Tasks</div>
        </div>
        <div className="border border-gray-700 rounded-lg p-4 bg-cube-gray">
          <div className="text-2xl font-bold text-blue-500">{completedTasks.length}</div>
          <div className="text-sm text-gray-400">Completed Tasks</div>
        </div>
      </div>

      {/* Task grid */}
      <h2 className="text-xl font-bold mb-4">All Tasks</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {tasks.map(task => (
          <TaskCard key={task.id} task={task} />
        ))}
      </div>
    </div>
  );
}
```

### Step 4: Verify TypeScript

```bash
cd web-ui
npx tsc --noEmit
```

**Must pass with no errors!**

### Step 5: Manual Testing

**Test scenarios:**

1. **Empty state:**
   - Clear state directory or use fresh install
   - Dashboard should show "No tasks yet" message

2. **Active tasks:**
   - Run: `cube writers 01-test test.md`
   - Dashboard should show 1 active task
   - Card should display task ID, phase, progress bar

3. **Click navigation:**
   - Click on task card
   - Should navigate to `/tasks/:id` (detail page)

4. **Auto-refresh:**
   - Open browser dev tools → Network tab
   - Watch for requests to `/api/tasks` every 5 seconds
   - Start a new task → should appear on dashboard within 5s

5. **Error handling:**
   - Stop backend server
   - Dashboard should show error message
   - Restart backend → should recover on next poll

### Step 6: Code Quality Check

- [ ] No `console.log()` statements
- [ ] No TypeScript errors: `npx tsc --noEmit`
- [ ] No ESLint warnings: `npm run lint`
- [ ] Clean browser console (no errors/warnings)

---

## 🚫 Critical Anti-Patterns

### ❌ DON'T: Over-Engineer with External Libraries

```typescript
// BAD - Don't add React Query
import { useQuery } from '@tanstack/react-query';

function Dashboard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['tasks'],
    queryFn: fetchTasks,
    refetchInterval: 5000,
  });
}
```

**Why wrong:** Adds unnecessary dependency. Simple fetch + interval is sufficient for MVP.

**Do this instead:**
```typescript
// GOOD - Simple fetch with useEffect
function Dashboard() {
  const [tasks, setTasks] = useState<Task[]>([]);
  
  useEffect(() => {
    const fetchTasks = async () => {
      const res = await fetch('http://localhost:3030/api/tasks');
      const data = await res.json();
      setTasks(data.tasks);
    };
    
    fetchTasks();
    const interval = setInterval(fetchTasks, 5000);
    return () => clearInterval(interval);
  }, []);
}
```

### ❌ DON'T: Complex State Management

```typescript
// BAD - Over-engineering
const [tasks, setTasks] = useState<Task[]>([]);
const [filter, setFilter] = useState<string>('all');
const [sort, setSort] = useState<SortOrder>('asc');
const [page, setPage] = useState(1);
const [searchQuery, setSearchQuery] = useState('');
```

**Why wrong:** MVP doesn't need filtering, sorting, pagination, or search.

**Do this instead:**
```typescript
// GOOD - Minimal state
const [tasks, setTasks] = useState<Task[]>([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);
```

### ❌ DON'T: Forget Cleanup

```typescript
// BAD - Memory leak!
useEffect(() => {
  const interval = setInterval(fetchTasks, 5000);
  // No cleanup - interval keeps running after unmount!
}, []);
```

**Do this instead:**
```typescript
// GOOD - Cleanup on unmount
useEffect(() => {
  const interval = setInterval(fetchTasks, 5000);
  return () => clearInterval(interval);  // ✅ Cleanup
}, []);
```

---

## 🎨 Styling Guidelines

**Color scheme (from Tailwind config):**
- Background: `bg-cube-gray` (dark gray)
- Borders: `border-gray-700`
- Text primary: `text-white`
- Text secondary: `text-gray-400`
- Active status: `text-green-500` / `bg-green-600`
- Completed status: `text-blue-500` / `bg-blue-600`
- Failed status: `text-red-400` / `bg-red-600`

**Layout:**
- Page padding: `p-6` or `p-8`
- Card spacing: `gap-4`
- Grid breakpoints: 1 col (mobile), 2 cols (`md:`), 3 cols (`lg:`)

---

## ⚠️ Common Pitfalls & Solutions

| Problem | Solution |
|---------|----------|
| CORS errors when fetching | Backend must set CORS headers for `http://localhost:5173` |
| Empty dashboard (no tasks) | Check if backend is running AND if state directory has task folders |
| Auto-refresh not working | Verify interval is set and cleanup returns function |
| Memory leak warning | Make sure `clearInterval` is called in cleanup |
| Cards not clickable | Use `cursor-pointer` class and `onClick` with `useNavigate()` |

---

## 🧪 Testing Checklist

**Before committing, verify:**

- [ ] Dashboard loads without errors
- [ ] Task cards display with correct data
- [ ] Status badges show correct colors
- [ ] Phase progress bar shows correct percentage
- [ ] Click on card navigates to `/tasks/:id`
- [ ] Status counts (active/completed) are accurate
- [ ] Auto-refresh works (check Network tab every 5s)
- [ ] Empty state shows when no tasks
- [ ] Loading state shows on initial load
- [ ] Error state shows when API fails
- [ ] TypeScript compiles: `npx tsc --noEmit`
- [ ] No console errors or warnings

---

## ✅ Definition of Done

**You're done when:**

1. **Code complete:**
   - [ ] `TaskCard.tsx` component created
   - [ ] `Dashboard.tsx` page implemented
   - [ ] Type definitions added to `types/index.ts`
   - [ ] All requirements met (see checklist above)

2. **Quality checks pass:**
   - [ ] TypeScript compiles: `npx tsc --noEmit`
   - [ ] ESLint clean: `npm run lint`
   - [ ] No console errors in browser

3. **Manual testing passed:**
   - [ ] Empty state works
   - [ ] Task cards display correctly
   - [ ] Navigation works
   - [ ] Auto-refresh works
   - [ ] Error handling works

4. **Code committed and pushed:**
   - [ ] Changes staged
   - [ ] Commit message follows convention
   - [ ] Pushed to branch

---

## 🚀 Final Steps - CRITICAL

**⚠️ DO NOT SKIP THIS SECTION**

### 1. Stage Your Changes

```bash
cd /Users/jacob/dev/agent-cube
git add web-ui/src/pages/Dashboard.tsx
git add web-ui/src/components/TaskCard.tsx
git add web-ui/src/types/
```

### 2. Commit with Conventional Message

```bash
git commit -m "feat(ui): implement dashboard with task list and status overview

- Add TaskCard component with phase progress and status badge
- Implement Dashboard page with task grid and status overview
- Add auto-refresh polling every 5 seconds
- Add loading, error, and empty states
- Type-safe API integration with backend"
```

### 3. Push to Remote Branch

```bash
git push origin writer-[your-model-slug]/04-dashboard
```

### 4. Verify Push Succeeded

```bash
git status
# Should say: "Your branch is up to date with 'origin/writer-[your-model-slug]/04-dashboard'"
```

### 5. Report Completion

**In your final message, include:**
- ✅ All requirements completed
- ✅ Tests passed (manual verification)
- ✅ Committed to: `writer-[your-model-slug]/04-dashboard`
- ✅ Pushed to remote
- Summary of what was built

---

## 📁 File Structure

**Your changes should create/modify:**

```
web-ui/
├── src/
│   ├── components/
│   │   └── TaskCard.tsx          # NEW - Task card component
│   ├── pages/
│   │   └── Dashboard.tsx         # MODIFIED - Dashboard page
│   └── types/
│       └── index.ts              # MODIFIED - Add Task types
```

**Do NOT modify:**
- Backend API files (Task 02 owns these)
- Thinking boxes component (Task 03)
- Task detail page (Task 05 will create this)
- Routing setup (Task 01 owns this)

---

## 🔗 Integration Points

**Your code interacts with:**

1. **Backend API (Task 02):**
   - Endpoint: `GET http://localhost:3030/api/tasks`
   - Response: `{ tasks: Task[] }`

2. **Routing (Task 01):**
   - Navigate to: `/tasks/:id` (using React Router's `useNavigate`)

3. **Future Task Detail Page (Task 05):**
   - Your dashboard links to it
   - Task 05 will implement `/tasks/:id` route

---

## 📖 Reference Material

**Planning doc:** `/Users/jacob/dev/agent-cube/planning/web-ui.md`
- Look for "Dashboard Component" section
- API endpoint specifications

**Existing code to reference:**
- `web-ui/src/App.tsx` - See routing setup
- `web-ui/tailwind.config.js` - See color scheme

---

## 💡 Tips for Success

1. **Start simple:** Get basic task list working first, then add polish
2. **Test incrementally:** Check each piece (fetch, display, navigation) before moving on
3. **Use TypeScript:** Let the compiler catch mistakes early
4. **Watch the console:** Browser console will show fetch errors and warnings
5. **Check Network tab:** Verify API calls are happening every 5s
6. **Read error messages:** They usually tell you exactly what's wrong

---

**Good luck! You've got this! 🚀**

**Questions during implementation?**
- Check planning doc: `planning/web-ui.md`
- Review Task 02 for API details
- Look at example code in this prompt

**Remember:** Commit and push when done! Uncommitted work won't be reviewed.

---

**Generated by:** Agent Cube v1.0  
**Template:** Dual-Writer Workflow  
**Date:** 2025-11-11
