# Judge Panel: Review Dashboard Multi-Workflow Management Implementations

You are a judge on a panel reviewing two implementations of the Dashboard page for AgentCube's web UI.

---

## 📋 Task Overview

The writers were asked to create a Dashboard page that displays all Agent Cube tasks with:
- Task list display with cards (responsive grid layout)
- Status overview showing active/completed counts
- Auto-refresh polling (5 second interval)
- Navigation to task detail pages
- Loading, error, and empty states

**Time Budget:** 2-3 hours

**Reference Documents:**
- Writer prompt: `.prompts/writer-prompt-04-dashboard.md`
- Architecture spec: `planning/web-ui.md`

---

## 🔍 Review Process

### Step 1: Identify Writer Branches

```bash
# Find the writer branches for task 04-dashboard
git branch -r | grep "04-dashboard"
```

You should see two branches like:
- `origin/writer-<model-a>/04-dashboard`
- `origin/writer-<model-b>/04-dashboard`

### Step 2: Review Each Implementation

For each writer branch, examine:

```bash
# Checkout writer branch
git checkout writer-<model>/04-dashboard

# Review files changed
git diff main --stat
git diff main --name-only

# Review the actual changes
git diff main web-ui/src/pages/Dashboard.tsx
git diff main web-ui/src/components/TaskCard.tsx
git diff main web-ui/src/types/

# Check commit history
git log main..HEAD --oneline

# Examine files created
ls -la web-ui/src/components/
ls -la web-ui/src/pages/
```

### Step 3: Test Functionality

For each implementation, test the dashboard:

```bash
cd web-ui

# Install dependencies (if needed)
npm install

# Check TypeScript compilation
npx tsc --noEmit

# Start dev server
npm run dev
# Visit http://localhost:5173
```

**Manual Testing:**
1. **Initial load:** Dashboard should show loading state, then tasks
2. **Empty state:** Clear state directory - should show "No tasks yet" message
3. **Task display:** Tasks should appear as cards with ID, phase, status badge, progress bar
4. **Status overview:** Verify active/completed counts are correct
5. **Click navigation:** Click card - should navigate to `/tasks/:id`
6. **Auto-refresh:** Open Network tab - verify requests every 5 seconds
7. **Responsive layout:** Resize browser - grid should adapt (1, 2, 3 cols)
8. **Error handling:** Stop backend - should show error message
9. **Browser console:** No errors or warnings

---

## ✅ Evaluation Criteria

Score each criterion on a scale of 0-10, where:
- **0-3**: Does not meet requirements, significant issues
- **4-6**: Partially meets requirements, some issues
- **7-8**: Meets requirements, minor issues
- **9-10**: Exceeds requirements, exemplary

### 1. Correctness (Weight: 30%)

**Does the implementation meet all functional requirements?**

**Dashboard Page:**
- [ ] File exists: `web-ui/src/pages/Dashboard.tsx`
- [ ] Fetches from `GET http://localhost:3030/api/tasks`
- [ ] Displays task cards in responsive grid
- [ ] Shows status overview (active/completed counts)
- [ ] Auto-refresh polling every 5 seconds
- [ ] Cleanup on unmount (no memory leaks)
- [ ] Loading state on initial load
- [ ] Error state when API fails
- [ ] Empty state when no tasks
- [ ] TypeScript types for state and API response

**TaskCard Component:**
- [ ] File exists: `web-ui/src/components/TaskCard.tsx`
- [ ] Props interface with `task: Task`
- [ ] Displays task ID as heading
- [ ] Shows status badge (color-coded)
- [ ] Displays "Phase X/10" text
- [ ] Progress bar (0-100% based on phase)
- [ ] Decision path display (truncated)
- [ ] Click handler navigates to `/tasks/:id`
- [ ] Hover effect (border color change)
- [ ] Uses React Router's `useNavigate()`

**Type Definitions:**
- [ ] File exists or modified: `web-ui/src/types/index.ts`
- [ ] `Task` interface with id, phase, path, status
- [ ] `TasksResponse` interface with tasks array
- [ ] No `any` types used

**Deductions:**
- Missing component: -10 points
- Auto-refresh not working: -5 points
- Missing state (loading/error/empty): -3 points per state
- Navigation broken: -5 points
- No cleanup (memory leak): -5 points
- Status counts incorrect: -3 points
- Progress bar incorrect: -3 points
- Not responsive: -4 points

**Score: __/10**

### 2. Code Quality (Weight: 25%)

**Is the code clean, maintainable, and well-structured?**

**Evaluate:**
- TypeScript interfaces (not types) for props and data
- Type annotations on all functions
- Explicit return types (`JSX.Element` for components)
- No `any` types anywhere
- Clean component structure
- Proper error handling (try/catch in fetch)
- Consistent naming conventions (PascalCase for components)
- Proper imports organization
- No unused imports or variables
- No console.log statements
- No commented-out code
- Descriptive variable names
- Component composition (TaskCard reused)

**Red flags:**
- Using `any` types: -3 points per occurrence
- Missing return type annotations: -2 points per function
- No error handling in fetch: -4 points
- Inconsistent naming: -2 points
- Unused imports: -1 point per file
- Console.log statements: -1 point per occurrence
- Commented-out code: -2 points
- Poor variable names: -2 points

**Score: __/10**

### 3. Architecture Adherence (Weight: 20%)

**Does the implementation follow KISS principles and specifications?**

**Key requirements:**
- ✅ Simple state management (useState, no Redux/Zustand)
- ✅ Native fetch API (no axios or React Query)
- ✅ Tailwind CSS only (no custom CSS files)
- ✅ React Router for navigation (useNavigate)
- ✅ Component composition (TaskCard reusable)
- ✅ Functional components only
- ❌ No external data fetching libraries
- ❌ No UI component libraries (MUI, Chakra, etc.)
- ❌ No animation libraries
- ❌ No over-engineering (pagination, filtering, sorting)

**Evaluate:**
- Follows KISS principles
- Minimal state management
- Proper component composition
- Uses Tailwind utility classes correctly
- No over-engineering
- No unnecessary abstractions
- Matches planning doc specifications
- File structure correct

**Critical violations:**
- Adding data fetching library (React Query, SWR): -8 points
- Adding UI component library: -8 points
- Custom CSS instead of Tailwind: -5 points
- Over-engineering with pagination/filtering/sorting: -5 points
- Wrong directory structure: -3 points
- Not using React Router: -5 points

**Score: __/10**

### 4. State Management & Side Effects (Weight: 15%)

**Are state and side effects handled correctly?**

**Check:**
- `useState` for tasks, loading, error
- `useEffect` with proper dependency array
- `setInterval` for polling
- Cleanup function returns from useEffect
- No memory leaks (interval cleared on unmount)
- Error boundaries or error handling in fetch
- Loading state set correctly
- State updates don't cause unnecessary re-renders

**Test cases:**
- Component mounts - initial fetch happens
- Component unmounts - interval is cleared
- API fails - error state is set
- API succeeds - tasks state is updated
- Auto-refresh - fetch happens every 5 seconds
- Navigate away - no memory leak warnings

**Deductions:**
- No cleanup function: -5 points (CRITICAL)
- Memory leak detected: -5 points
- Missing dependency in useEffect: -3 points
- No error handling: -4 points
- Incorrect loading state management: -3 points
- State updates cause infinite loops: -5 points

**Score: __/10**

### 5. Styling & Responsiveness (Weight: 5%)

**Is the UI properly styled and responsive?**

**Check:**
- Responsive grid layout (1, 2, 3 columns)
- Correct breakpoints (`md:`, `lg:`)
- TaskCard styling (dark background, borders)
- Status badges color-coded correctly
  - Active: green (`bg-green-600`)
  - Completed: blue (`bg-blue-600`)
  - Failed: red (`bg-red-600`)
- Progress bar shows correct percentage
- Hover effects on cards
- Consistent spacing and padding
- Text contrast is readable
- Status overview cards styled appropriately
- No custom CSS files

**Visual check:**
- Cards look good on mobile, tablet, desktop
- Colors apply correctly
- Layout is clean and organized
- No visual glitches or overlaps
- Grid adapts properly to screen size

**Deductions:**
- Not responsive: -5 points
- Wrong colors: -3 points
- Poor text contrast: -2 points
- Inconsistent styling: -2 points
- Custom CSS files used: -4 points
- Progress bar incorrect: -2 points

**Score: __/10**

### 6. Testing & Verification (Weight: 5%)

**Has the implementation been properly tested?**

**Evidence of testing:**
- TypeScript compiles cleanly: `npx tsc --noEmit`
- Dashboard renders without errors
- All states tested (loading, error, empty, populated)
- Auto-refresh verified (Network tab)
- Navigation tested (click cards)
- Responsive behavior verified
- Browser console clean (no errors or warnings)
- Commit messages indicate testing
- Changes pushed to remote branch

**Deductions:**
- TypeScript compilation errors: -3 points per error
- Dashboard doesn't render: -5 points
- States not tested: -2 points per state
- Auto-refresh broken: -4 points
- Navigation broken: -4 points
- Console errors: -2 points
- Not pushed to remote: -5 points (CRITICAL)

**Score: __/10**

---

## 📊 Scoring Rubric

Calculate the weighted total score:

```
Total Score = (Correctness × 0.30) + 
              (Code Quality × 0.25) + 
              (Architecture × 0.20) + 
              (State Management × 0.15) + 
              (Styling × 0.05) + 
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

### ❌ Anti-Pattern 1: Memory Leak (No Cleanup)

```typescript
// BAD: No cleanup function
useEffect(() => {
  const interval = setInterval(fetchTasks, 5000);
  // Missing cleanup!
}, []);
```

**✅ Good:**
```typescript
// Cleanup interval on unmount
useEffect(() => {
  const interval = setInterval(fetchTasks, 5000);
  return () => clearInterval(interval);  // ✅
}, []);
```

**Impact:** REQUEST_CHANGES - Memory leaks are critical bugs

### ❌ Anti-Pattern 2: Over-Engineering with Libraries

```typescript
// BAD: Adding React Query unnecessarily
import { useQuery } from '@tanstack/react-query';

function Dashboard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['tasks'],
    queryFn: fetchTasks,
    refetchInterval: 5000,
  });
}
```

**✅ Good:**
```typescript
// Simple fetch with native APIs
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

**Impact:** REQUEST_CHANGES - Violates KISS principle

### ❌ Anti-Pattern 3: Missing Error Handling

```typescript
// BAD: No try/catch or error state
const fetchTasks = async () => {
  const res = await fetch('http://localhost:3030/api/tasks');
  const data = await res.json();
  setTasks(data.tasks);  // Crashes if network fails!
};
```

**✅ Good:**
```typescript
// Proper error handling
const fetchTasks = async () => {
  try {
    const res = await fetch('http://localhost:3030/api/tasks');
    if (!res.ok) throw new Error('Failed to fetch tasks');
    const data = await res.json();
    setTasks(data.tasks);
    setError(null);
  } catch (err) {
    setError(err instanceof Error ? err.message : 'Unknown error');
  } finally {
    setLoading(false);
  }
};
```

**Impact:** REQUEST_CHANGES - Must handle network failures gracefully

### ❌ Anti-Pattern 4: Complex State Management

```typescript
// BAD: Over-engineering
const [tasks, setTasks] = useState<Task[]>([]);
const [filter, setFilter] = useState('all');
const [sort, setSort] = useState<SortOrder>('asc');
const [page, setPage] = useState(1);
const [searchQuery, setSearchQuery] = useState('');
const [perPage, setPerPage] = useState(10);
```

**✅ Good:**
```typescript
// Minimal state for MVP
const [tasks, setTasks] = useState<Task[]>([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);
```

**Impact:** REQUEST_CHANGES - MVP doesn't need filtering/sorting/pagination

### ❌ Anti-Pattern 5: Missing Type Definitions

```typescript
// BAD: No interfaces, using any
function TaskCard({ task }: any) {
  return <div>{task.id}</div>;
}
```

**✅ Good:**
```typescript
// Proper TypeScript types
interface Task {
  id: string;
  phase: number;
  path: string;
  status?: 'active' | 'completed' | 'failed';
}

interface TaskCardProps {
  task: Task;
}

export function TaskCard({ task }: TaskCardProps): JSX.Element {
  return <div>{task.id}</div>;
}
```

**Impact:** REQUEST_CHANGES if >30% of code lacks types

### ❌ Anti-Pattern 6: Incorrect Progress Bar Calculation

```typescript
// BAD: Wrong percentage calculation
<div style={{ width: `${task.phase}%` }} />  // Phase 8 = 8%, not 80%!
```

**✅ Good:**
```typescript
// Correct: phase/10 * 100
<div style={{ width: `${(task.phase / 10) * 100}%` }} />
```

**Impact:** REQUEST_CHANGES - Progress bar should show 0-100%

### ❌ Anti-Pattern 7: Missing States (Loading/Error/Empty)

```typescript
// BAD: Only shows tasks, no other states
function Dashboard() {
  const [tasks, setTasks] = useState<Task[]>([]);
  
  return (
    <div>
      {tasks.map(task => <TaskCard task={task} />)}
    </div>
  );
}
```

**✅ Good:**
```typescript
// All states handled
if (loading) return <div>Loading tasks...</div>;
if (error) return <div>Error: {error}</div>;
if (tasks.length === 0) return <div>No tasks yet</div>;

return <div>{tasks.map(...)}</div>;
```

**Impact:** REQUEST_CHANGES - Must handle all UI states

### ❌ Anti-Pattern 8: Not Using React Router

```typescript
// BAD: Using window.location or <a> tags
<div onClick={() => window.location.href = `/tasks/${task.id}`}>
```

**✅ Good:**
```typescript
// Use React Router's useNavigate
const navigate = useNavigate();

<div onClick={() => navigate(`/tasks/${task.id}`)}>
```

**Impact:** REQUEST_CHANGES - Must use React Router for navigation

---

## 📝 Decision Template

After reviewing both implementations, provide your decision using this exact JSON format:

```json
{
  "task_id": "04-dashboard",
  "judge_id": "judge-<your-model>",
  "timestamp": "2025-11-11T<time>Z",
  "reviews": {
    "writer_a": {
      "branch": "writer-<model-a>/04-dashboard",
      "scores": {
        "correctness": 0.0,
        "code_quality": 0.0,
        "architecture": 0.0,
        "state_management": 0.0,
        "styling": 0.0,
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
      "branch": "writer-<model-b>/04-dashboard",
      "scores": {
        "correctness": 0.0,
        "code_quality": 0.0,
        "architecture": 0.0,
        "state_management": 0.0,
        "styling": 0.0,
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

- Review ALL changed files
- Test functionality (run dev server, test all states)
- Check for TypeScript errors
- Verify auto-refresh in Network tab
- Test responsive behavior at different screen sizes
- Click cards to verify navigation
- Test error scenarios (stop backend)

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
- Dashboard works without errors
- Auto-refresh works correctly
- Minor issues can be addressed in follow-up

**REQUEST_CHANGES:**
- Total score 4.0 - 6.9
- Some requirements not met
- Fixable issues identified
- Core functionality present but needs improvement
- TypeScript errors or missing features

**REJECTED:**
- Total score < 4.0
- Critical requirements missing
- Memory leaks or major bugs
- Dashboard doesn't work
- Would require complete rewrite

---

## 🔗 Reference Files

Review these files to understand the requirements:

```bash
# Writer prompt
cat .prompts/writer-prompt-04-dashboard.md

# Architecture spec
cat planning/web-ui.md

# Check existing routing (Task 01)
cat web-ui/src/App.tsx

# Check Tailwind config for colors
cat web-ui/tailwind.config.js
```

---

## ✅ Judge Checklist

Before submitting your review:

- [ ] Reviewed both writer branches completely
- [ ] Checked all expected files (Dashboard.tsx, TaskCard.tsx, types)
- [ ] Tested TypeScript compilation for both (`npx tsc --noEmit`)
- [ ] Ran dev server and tested functionality
- [ ] Verified loading state on initial load
- [ ] Verified error state (stopped backend)
- [ ] Verified empty state (cleared state directory)
- [ ] Verified populated state with task cards
- [ ] Tested navigation (clicked cards)
- [ ] Verified auto-refresh in Network tab (every 5s)
- [ ] Tested responsive layout (mobile, tablet, desktop)
- [ ] Verified status badges color-coded correctly
- [ ] Verified progress bars show correct percentage
- [ ] Verified status counts are accurate
- [ ] Checked browser console for errors
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
.prompts/decisions/judge-<your-model>-04-dashboard-decision.json
```

Your review will be aggregated with other judges to make the final decision.

---

## 📋 Quick Reference: What Good Looks Like

### ✅ Excellent Implementation Checklist

**Files Created/Modified:**
- [ ] `web-ui/src/pages/Dashboard.tsx` (modified or created)
- [ ] `web-ui/src/components/TaskCard.tsx` (new)
- [ ] `web-ui/src/types/index.ts` (modified)

**Dashboard Component:**
- [ ] State: tasks, loading, error
- [ ] Fetches from `GET http://localhost:3030/api/tasks`
- [ ] Auto-refresh every 5 seconds
- [ ] Cleanup on unmount
- [ ] Loading state shown initially
- [ ] Error state when fetch fails
- [ ] Empty state when no tasks
- [ ] Status overview (active/completed counts)
- [ ] Responsive grid layout (1, 2, 3 cols)
- [ ] Named export

**TaskCard Component:**
- [ ] Props: `{ task: Task }`
- [ ] Task ID displayed
- [ ] Status badge (color-coded)
- [ ] Phase text (X/10)
- [ ] Progress bar (0-100%)
- [ ] Decision path (truncated)
- [ ] Click navigates with `useNavigate()`
- [ ] Hover effect
- [ ] Named export

**TypeScript:**
- [ ] Interfaces for Task, TasksResponse, TaskCardProps
- [ ] No `any` types
- [ ] Explicit return types
- [ ] Compiles with no errors

**Code Quality:**
- [ ] Clean, readable code
- [ ] Proper error handling
- [ ] No console.log statements
- [ ] No memory leaks
- [ ] Follows KISS principles
- [ ] Component composition

**Testing:**
- [ ] All states work (loading, error, empty, populated)
- [ ] Auto-refresh verified
- [ ] Navigation works
- [ ] Responsive behavior correct
- [ ] Committed and pushed to remote

---

## 🔍 Comparison Focus Areas

When comparing the two implementations, pay special attention to:

1. **State Management:**
   - Which handles cleanup better?
   - Better error handling?
   - More robust loading states?

2. **Component Design:**
   - Cleaner component structure?
   - Better component composition?
   - More reusable code?

3. **TypeScript Usage:**
   - Better type definitions?
   - More type-safe?
   - Clearer interfaces?

4. **Auto-Refresh Implementation:**
   - Correct interval usage?
   - Proper cleanup?
   - No memory leaks?

5. **UI/UX Quality:**
   - Better responsive design?
   - Better visual design?
   - More intuitive interface?

6. **Edge Case Handling:**
   - Handles all states correctly?
   - Better error messages?
   - More robust overall?

---

**Remember:** Your role is to ensure quality, catch issues, and help select the best implementation. Be thorough, fair, and constructive in your review.

Good luck! 🎯
