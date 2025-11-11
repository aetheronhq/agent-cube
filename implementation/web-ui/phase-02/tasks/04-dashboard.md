# Task 04: Dashboard - Multi-Workflow Management

**Goal:** Create dashboard page that lists all tasks with status, phase progress, and quick actions.

**Time Estimate:** 2-3 hours

---

## 📖 **Context**

**What this builds on:**
- Task 01: Page structure and routing
- Task 02: Backend API (`/api/tasks` endpoint)
- Existing state management (JSON files)

**Planning docs (Golden Source):**
- `planning/web-ui.md` - Dashboard component, API endpoints

---

## ✅ **Requirements**

### **1. Task List Display**

**Deliverable:**
- Grid of task cards
- Each card shows: task ID, phase, status, decision path
- Click to navigate to task detail

**Acceptance criteria:**
- [ ] Fetches tasks from `GET /api/tasks`
- [ ] Displays task cards in grid layout
- [ ] Shows task ID, current phase (X/10), status
- [ ] Click navigates to `/tasks/:id`
- [ ] Empty state when no tasks

### **2. Status Overview**

**Deliverable:**
- Summary stats at top of dashboard
- Active tasks count, completed count

**Acceptance criteria:**
- [ ] Counts active vs completed tasks
- [ ] Displays stats in card format
- [ ] Updates when tasks change

### **3. Task Card Component**

**Deliverable:**
- Reusable card component for task display
- Shows phase progress bar
- Color-coded status (active=green, completed=blue)

**Acceptance criteria:**
- [ ] `TaskCard.tsx` component created
- [ ] Props: `id`, `phase`, `status`, `path`
- [ ] Phase progress indicator (1/10, 5/10, etc.)
- [ ] Status badge with color
- [ ] Hover effect for interactivity

### **4. Auto-Refresh**

**Deliverable:**
- Dashboard polls for updates every 5 seconds

**Acceptance criteria:**
- [ ] `useEffect` with interval for polling
- [ ] Cleanup on unmount
- [ ] Error handling for failed fetches

---

## 📝 **Implementation Steps**

**Suggested order:**

1. **Create TaskCard component**
   - [ ] `src/components/TaskCard.tsx`
   - [ ] Accept task props
   - [ ] Render card with styling
   - [ ] Add onClick to navigate

2. **Update Dashboard page**
   - [ ] `src/pages/Dashboard.tsx`
   - [ ] useState for tasks array
   - [ ] useEffect to fetch from API
   - [ ] Display loading state

3. **Implement API fetch**
   - [ ] Create `src/utils/api.ts` (optional helper)
   - [ ] Fetch function with error handling
   - [ ] Parse response JSON

4. **Add status overview**
   - [ ] Calculate stats from tasks array
   - [ ] Display in summary cards
   - [ ] Position at top of dashboard

5. **Implement auto-refresh**
   - [ ] setInterval in useEffect
   - [ ] Clear interval on unmount
   - [ ] Handle fetch errors gracefully

6. **Add empty state**
   - [ ] Conditional render when tasks.length === 0
   - [ ] Helpful message and styling

7. **Verify**
   - [ ] Dashboard loads and displays tasks
   - [ ] Click on card navigates to detail page
   - [ ] Auto-refresh works (watch network tab)
   - [ ] Empty state shows when no tasks

8. **Finalize**
   - [ ] Clean up console logs
   - [ ] Commit changes
   - [ ] Push to branch

---

## 🏗️ **Architecture Constraints**

### **Must Follow**

**Planning docs:**
- Use `/api/tasks` endpoint from `planning/web-ui.md`
- Dashboard is entry point (from component hierarchy)

**Technical constraints:**
- TypeScript strict mode
- Type-safe API responses
- Error boundaries for failed fetches
- Loading states for async operations

**KISS Principles:**
- ✅ Simple polling (no complex state sync)
- ✅ Direct fetch API (no axios/react-query overhead for MVP)
- ✅ Component state (no global state needed)
- ❌ No infinite scroll (simple list is sufficient)
- ❌ No real-time WebSocket (polling is simpler)

---

## 🚫 **Anti-Patterns**

### **❌ DON'T: Over-Engineer with React Query**

```typescript
// Bad: Unnecessary dependency for MVP
import { useQuery } from '@tanstack/react-query';

function Dashboard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['tasks'],
    queryFn: fetchTasks,
    refetchInterval: 5000,
  });
  // Over-engineered for simple polling
}
```

**Instead:**
```typescript
// Good: Simple fetch with interval
function Dashboard() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTasks = async () => {
      const res = await fetch('http://localhost:3030/api/tasks');
      const data = await res.json();
      setTasks(data.tasks);
      setLoading(false);
    };

    fetchTasks();
    const interval = setInterval(fetchTasks, 5000);
    return () => clearInterval(interval);
  }, []);

  // Simple and clear
}
```

### **❌ DON'T: Complex State Management**

```typescript
// Bad: Over-engineering
const [tasks, setTasks] = useState<Task[]>([]);
const [filter, setFilter] = useState<string>('all');
const [sort, setSort] = useState<SortOrder>('asc');
const [page, setPage] = useState(1);
// Too much for MVP!
```

**Instead:**
```typescript
// Good: Minimal state
const [tasks, setTasks] = useState<Task[]>([]);
const [loading, setLoading] = useState(true);
```

---

## 📂 **Owned Paths**

**This task owns:**
```
web-ui/src/
├── pages/
│   └── Dashboard.tsx
├── components/
│   └── TaskCard.tsx
└── types/
    └── index.ts  (add Task interface)
```

**Must NOT modify:**
- Backend API (Task 02)
- Thinking boxes (Task 03)
- Task detail page (Task 05)

**Integration:**
- Calls `GET /api/tasks` from Task 02
- Links to TaskDetail page (Task 05)

---

## 🧪 **Testing Requirements**

**Manual testing:**
- [ ] Dashboard loads without errors
- [ ] Task cards display correctly
- [ ] Click on card navigates to `/tasks/:id`
- [ ] Status counts are correct
- [ ] Auto-refresh works (check Network tab every 5s)
- [ ] Empty state shows when no tasks

**Test scenarios:**
- Start with no tasks → empty state
- Run `cube writers 01-test test.md` → task appears
- Click task card → navigates to detail page

---

## ✅ **Acceptance Criteria**

**Definition of Done:**

- [ ] Dashboard page implemented
- [ ] TaskCard component created
- [ ] Fetches tasks from API
- [ ] Displays task list in grid
- [ ] Status overview shows counts
- [ ] Click on card navigates to detail
- [ ] Auto-refresh every 5 seconds
- [ ] Empty state when no tasks
- [ ] Loading state on initial load
- [ ] Error handling for failed fetches
- [ ] TypeScript compiles: `npx tsc --noEmit`
- [ ] Changes committed and pushed

**Quality gates:**
- [ ] Follows KISS (simple polling, no complex state)
- [ ] Type-safe API responses
- [ ] Clean console (no errors/warnings)

---

## 🔗 **Integration Points**

**Dependencies (requires these first):**
- Task 01: Page structure, routing
- Task 02: Backend API (`/api/tasks`)

**Dependents (these will use this):**
- Task 05: Dashboard links to TaskDetail

**Integrator task:**
- None (self-contained page)

---

## 📊 **Examples**

### **types/index.ts additions**

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

### **TaskCard.tsx**

```typescript
import { useNavigate } from 'react-router-dom';
import { Task } from '../types';

interface TaskCardProps {
  task: Task;
}

export function TaskCard({ task }: TaskCardProps) {
  const navigate = useNavigate();
  
  const statusColor = task.status === 'completed' ? 'bg-blue-600' : 'bg-green-600';
  
  return (
    <div
      onClick={() => navigate(`/tasks/${task.id}`)}
      className="border border-gray-700 rounded-lg p-4 hover:border-gray-500 cursor-pointer transition-colors bg-cube-gray"
    >
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-semibold text-white">{task.id}</h3>
        <span className={`text-xs px-2 py-1 rounded ${statusColor}`}>
          {task.status || 'active'}
        </span>
      </div>
      
      <div className="text-sm text-gray-400 mb-2">
        Phase {task.phase}/10
      </div>
      
      <div className="w-full bg-gray-700 rounded-full h-2">
        <div
          className="bg-blue-500 h-2 rounded-full"
          style={{ width: `${(task.phase / 10) * 100}%` }}
        />
      </div>
      
      <div className="mt-2 text-xs text-gray-500 truncate">
        {task.path}
      </div>
    </div>
  );
}
```

### **Dashboard.tsx**

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

---

## 🎓 **Common Pitfalls**

**Watch out for:**
- ⚠️ Memory leaks (clear interval on unmount)
- ⚠️ CORS errors (backend must allow localhost:5173)
- ⚠️ API not running (handle connection errors)

**If you see [empty dashboard], it means [no tasks in state dir or API not running] - fix by [running a task or checking backend]**

---

**FINAL STEPS - CRITICAL:**

```bash
# Stage changes
git add web-ui/src/pages/Dashboard.tsx web-ui/src/components/TaskCard.tsx web-ui/src/types/

# Commit
git commit -m "feat(ui): implement dashboard with task list and status overview"

# Push
git push origin writer-[your-model-slug]/04-dashboard

# Verify
git status
```

**⚠️ IMPORTANT:** Uncommitted or unpushed changes will NOT be reviewed!

---

**Built with:** Agent Cube v1.0
**Template version:** 1.0
**Last updated:** 2025-11-11

