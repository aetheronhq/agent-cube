# Writer Task: Decisions UI - Judge Votes and Synthesis

You are implementing the decisions page that displays judge panel votes, synthesis instructions, and decision aggregation results for the AgentCube Web UI.

---

## 🎯 **Your Mission**

Create the decisions visualization layer that:
- Displays individual judge votes with rationales
- Shows decision summary (winner, consensus)
- Visualizes synthesis instructions when applicable
- Distinguishes between panel and peer review decisions
- Handles missing decisions gracefully

**Time Budget:** 2-3 hours

---

## 📖 **Context & Background**

### What You're Building On

The AgentCube workflow already has:
- ✅ `cube.core.decision_files` - Parses decision JSON files
- ✅ Decision format standardized (panel and peer review)
- ✅ Task routing and navigation (Task 01)
- ✅ Backend API base (Task 02)
- ✅ Decisions stored in `~/.cube-py/sessions/{task-id}/decisions.json`

**Your job:** Create a clean UI to visualize these decisions. **DO NOT reparse or reformat decision files!**

### What Comes After

- This is a standalone feature page
- Links from TaskDetail navigation
- May be enhanced later with timeline view or diff viewer (but not now!)

### Architecture Principle: KISS

**Keep It Simple, Stupid:**
- ✅ Read from existing JSON via backend API - no custom parsing
- ✅ Simple card layout - no charts or complex visualizations
- ✅ Static display - no interactive voting
- ✅ Text-based instructions - no diff viewer
- ❌ No over-engineering with graphs
- ❌ No custom decision format

Refer to: `planning/web-ui.md` for architecture details.

---

## ✅ **Requirements & Deliverables**

### 1. Backend: Decision Endpoint

**Create:**
- Add endpoint to `python/cube/ui/routes/tasks.py`
- `/api/tasks/{id}/decisions` that returns parsed decision data

**Acceptance Criteria:**
- [ ] Endpoint reads from session directory
- [ ] Uses `cube.core.decision_files` module (no custom parsing!)
- [ ] Returns both panel and peer review decisions
- [ ] Returns 404 if no decisions found
- [ ] Proper error handling with HTTPException

**Example Implementation:**
```python
from cube.core.decision_files import read_decision_file
from fastapi import HTTPException

@router.get("/tasks/{task_id}/decisions")
async def get_decisions(task_id: str):
    """Get decision data for a task."""
    try:
        decisions = read_decision_file(task_id)
        return {"decisions": decisions}
    except FileNotFoundError:
        raise HTTPException(404, detail="No decisions found for this task")
    except Exception as e:
        raise HTTPException(500, detail=f"Error reading decisions: {str(e)}")
```

### 2. Frontend: TypeScript Types

**Create/Update:**
- Add decision types to `web-ui/src/types/index.ts`

**Required interfaces:**
```typescript
export interface JudgeVote {
  judge: number;               // Judge number (1, 2, 3)
  model: string;               // Model name (e.g., "claude-sonnet-4")
  vote: 'A' | 'B' | 'APPROVE' | 'REQUEST_CHANGES' | 'COMMENT';
  rationale: string;           // Brief explanation
}

export interface SynthesisInfo {
  instructions: string[];      // How to merge the outputs
  bestBits: {
    writerA: string[];         // Best parts from Writer A
    writerB: string[];         // Best parts from Writer B
  };
  compatible: boolean;         // Can outputs be merged?
}

export interface Decision {
  type: 'panel' | 'peer-review';
  judges: JudgeVote[];
  winner?: 'A' | 'B';          // Only for panel decisions
  synthesis?: SynthesisInfo;   // Only if compatible
  timestamp: string;
}
```

**Acceptance Criteria:**
- [ ] All interfaces defined and exported
- [ ] No `any` types
- [ ] Matches backend response structure
- [ ] Used in component props

### 3. Frontend: JudgeVote Component

**Create:**
- `web-ui/src/components/JudgeVote.tsx`

**Display Requirements:**
- Card layout with colored vote badge
- Shows judge number and model
- Displays rationale text
- Color coding:
  - A = green
  - B = blue
  - APPROVE = green
  - REQUEST_CHANGES = red
  - COMMENT = yellow

**Acceptance Criteria:**
- [ ] Component created with proper TypeScript props
- [ ] Displays all vote information
- [ ] Color-coded vote badges
- [ ] Responsive card layout
- [ ] Dark theme styling with Tailwind

**Example Implementation:**
```typescript
import { JudgeVote as JudgeVoteType } from '../types';

interface JudgeVoteProps {
  vote: JudgeVoteType;
}

export function JudgeVote({ vote }: JudgeVoteProps) {
  const voteColorMap: Record<string, string> = {
    'A': 'bg-green-600 text-white',
    'B': 'bg-blue-600 text-white',
    'APPROVE': 'bg-green-600 text-white',
    'REQUEST_CHANGES': 'bg-red-600 text-white',
    'COMMENT': 'bg-yellow-600 text-black'
  };
  
  const voteColor = voteColorMap[vote.vote] || 'bg-gray-600 text-white';

  return (
    <div className="border border-gray-700 rounded-lg p-4 bg-gray-900">
      <div className="flex justify-between items-start mb-2">
        <div>
          <h3 className="font-semibold text-gray-100">Judge {vote.judge}</h3>
          <p className="text-xs text-gray-400">{vote.model}</p>
        </div>
        <span className={`px-2 py-1 rounded text-xs font-bold ${voteColor}`}>
          {vote.vote}
        </span>
      </div>
      <p className="text-sm text-gray-300 mt-2">{vote.rationale}</p>
    </div>
  );
}
```

### 4. Frontend: SynthesisView Component

**Create:**
- `web-ui/src/components/SynthesisView.tsx`

**Display Requirements:**
- Shows compatibility status
- Lists synthesis instructions
- Shows best bits from each writer
- Two-column layout for best bits comparison
- Clean, readable typography

**Acceptance Criteria:**
- [ ] Component created with proper TypeScript props
- [ ] Displays synthesis instructions clearly
- [ ] Shows best bits side-by-side
- [ ] Compatible status indicator
- [ ] Responsive layout

**Example Implementation:**
```typescript
import { SynthesisInfo } from '../types';

interface SynthesisViewProps {
  synthesis: SynthesisInfo;
}

export function SynthesisView({ synthesis }: SynthesisViewProps) {
  return (
    <div className="border border-gray-700 rounded-lg p-6 bg-gray-900">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-100 mb-2">Synthesis Instructions</h3>
        <div className="flex items-center gap-2 mb-4">
          <span className="text-sm text-gray-400">Compatible:</span>
          <span className={`px-2 py-1 rounded text-xs font-bold ${
            synthesis.compatible ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
          }`}>
            {synthesis.compatible ? '✅ Yes' : '❌ No'}
          </span>
        </div>
      </div>

      <div className="mb-6">
        <h4 className="text-sm font-semibold text-gray-300 mb-3">How to Merge:</h4>
        <ul className="list-disc list-inside space-y-2 text-sm text-gray-400">
          {synthesis.instructions.map((instruction, i) => (
            <li key={i}>{instruction}</li>
          ))}
        </ul>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h4 className="text-sm font-semibold mb-3 text-green-400">
            💎 Best Bits: Writer A
          </h4>
          <ul className="list-disc list-inside space-y-1 text-xs text-gray-400">
            {synthesis.bestBits.writerA.map((bit, i) => (
              <li key={i}>{bit}</li>
            ))}
          </ul>
        </div>
        <div>
          <h4 className="text-sm font-semibold mb-3 text-blue-400">
            💎 Best Bits: Writer B
          </h4>
          <ul className="list-disc list-inside space-y-1 text-xs text-gray-400">
            {synthesis.bestBits.writerB.map((bit, i) => (
              <li key={i}>{bit}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
```

### 5. Frontend: Decisions Page

**Update:**
- `web-ui/src/pages/Decisions.tsx`

**Display Requirements:**
- Fetches decisions from API endpoint
- Shows decision summary (type, winner, timestamp)
- Displays judge votes in responsive grid
- Shows synthesis view if applicable
- Handles loading and error states
- Empty state message if no decisions

**Acceptance Criteria:**
- [ ] Page fetches from `/api/tasks/{id}/decisions`
- [ ] Shows decision summary
- [ ] Renders JudgeVote components in grid
- [ ] Conditionally shows SynthesisView
- [ ] Loading state while fetching
- [ ] Error handling for 404 and network errors
- [ ] Empty state for tasks without decisions

**Example Implementation:**
```typescript
import { useParams } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { JudgeVote } from '../components/JudgeVote';
import { SynthesisView } from '../components/SynthesisView';
import { Decision } from '../types';

export function Decisions() {
  const { id } = useParams<{ id: string }>();
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`http://localhost:3030/api/tasks/${id}/decisions`)
      .then(res => {
        if (!res.ok) {
          if (res.status === 404) {
            throw new Error('No decisions found for this task');
          }
          throw new Error('Failed to fetch decisions');
        }
        return res.json();
      })
      .then(data => {
        setDecisions(data.decisions || []);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-gray-400">Loading decisions...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-400 mb-2">⚠️ {error}</div>
        <p className="text-gray-500 text-sm">
          Run the judge panel first: <code className="bg-gray-800 px-2 py-1 rounded">cube panel {id}</code>
        </p>
      </div>
    );
  }

  if (decisions.length === 0) {
    return (
      <div className="text-center py-12 text-gray-400">
        <p className="mb-2">No decisions yet</p>
        <p className="text-sm text-gray-500">
          Run: <code className="bg-gray-800 px-2 py-1 rounded">cube panel {id}</code>
        </p>
      </div>
    );
  }

  const latestDecision = decisions[decisions.length - 1];

  return (
    <div className="space-y-6 p-6">
      <h1 className="text-2xl font-bold text-gray-100">Decisions: {id}</h1>

      {/* Decision Summary */}
      <div className="border border-gray-700 rounded-lg p-4 bg-gray-900">
        <h2 className="text-lg font-semibold text-gray-100 mb-3">Decision Summary</h2>
        <div className="text-sm text-gray-300 space-y-1">
          <p>
            <span className="text-gray-500">Type:</span>{' '}
            <span className="font-semibold">{latestDecision.type}</span>
          </p>
          {latestDecision.winner && (
            <p>
              <span className="text-gray-500">Winner:</span>{' '}
              <span className="font-semibold text-green-400">
                Writer {latestDecision.winner}
              </span>
            </p>
          )}
          <p>
            <span className="text-gray-500">Timestamp:</span>{' '}
            {new Date(latestDecision.timestamp).toLocaleString()}
          </p>
        </div>
      </div>

      {/* Judge Votes */}
      <div>
        <h2 className="text-lg font-semibold text-gray-100 mb-3">Judge Votes</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {latestDecision.judges.map((vote) => (
            <JudgeVote key={vote.judge} vote={vote} />
          ))}
        </div>
      </div>

      {/* Synthesis View */}
      {latestDecision.synthesis && (
        <div>
          <h2 className="text-lg font-semibold text-gray-100 mb-3">Synthesis</h2>
          <SynthesisView synthesis={latestDecision.synthesis} />
        </div>
      )}
    </div>
  );
}
```

---

## 📋 **Implementation Steps**

Follow these steps in order:

### Step 1: Backend - Add Decision Endpoint

**Location:** `python/cube/ui/routes/tasks.py`

```bash
cd /Users/jacob/dev/agent-cube/python
```

**Tasks:**
- [ ] Import `read_decision_file` from `cube.core.decision_files`
- [ ] Add `@router.get("/tasks/{task_id}/decisions")` endpoint
- [ ] Handle FileNotFoundError with 404 response
- [ ] Return decision data as JSON
- [ ] Test with curl

**Test:**
```bash
# Start server
cube ui

# In another terminal
curl http://localhost:3030/api/tasks/test-task/decisions
# Expected: 404 if no decisions, or decision JSON if they exist
```

### Step 2: Frontend - Define TypeScript Types

**Location:** `web-ui/src/types/index.ts`

```bash
cd /Users/jacob/dev/agent-cube/web-ui
```

**Tasks:**
- [ ] Add `JudgeVote` interface
- [ ] Add `SynthesisInfo` interface
- [ ] Add `Decision` interface
- [ ] Export all interfaces
- [ ] Verify with: `npx tsc --noEmit`

### Step 3: Frontend - Create JudgeVote Component

**Location:** `web-ui/src/components/JudgeVote.tsx`

**Tasks:**
- [ ] Create file with functional component
- [ ] Define props interface using types
- [ ] Implement card layout with Tailwind
- [ ] Add vote color coding
- [ ] Display judge info and rationale
- [ ] Test with mock data in Dashboard temporarily

### Step 4: Frontend - Create SynthesisView Component

**Location:** `web-ui/src/components/SynthesisView.tsx`

**Tasks:**
- [ ] Create file with functional component
- [ ] Define props interface using types
- [ ] Implement layout with Tailwind
- [ ] Add compatible status indicator
- [ ] Show instructions list
- [ ] Show best bits in two columns
- [ ] Test with mock data

### Step 5: Frontend - Update Decisions Page

**Location:** `web-ui/src/pages/Decisions.tsx`

**Tasks:**
- [ ] Import components and types
- [ ] Add useState for decisions, loading, error
- [ ] Add useEffect to fetch from API
- [ ] Implement loading state
- [ ] Implement error state
- [ ] Implement empty state
- [ ] Render decision summary
- [ ] Render judge votes in grid
- [ ] Conditionally render synthesis

### Step 6: Integration Test

```bash
# Terminal 1: Start backend
cd /Users/jacob/dev/agent-cube/python
cube ui

# Terminal 2: Run panel on a test task
cube panel test-task panel-prompt.md

# After completion, open browser
# Navigate to: http://localhost:5173/tasks/test-task/decisions
```

**Verify:**
- [ ] Page loads without errors
- [ ] Judge votes display correctly
- [ ] Vote colors match vote type
- [ ] Synthesis shows if applicable
- [ ] No console errors
- [ ] Responsive layout works

### Step 7: Verify TypeScript

```bash
cd /Users/jacob/dev/agent-cube/web-ui
npx tsc --noEmit
```

**Must pass with zero errors.**

### Step 8: Clean Up

- [ ] Remove any test code
- [ ] Remove console.log statements
- [ ] Verify all imports are used
- [ ] Check for commented-out code

---

## 🚧 **Constraints & Guidelines**

### MUST Follow

**Architecture:**
- ✅ Use `cube.core.decision_files` module (no custom parsing!)
- ✅ Functional components with TypeScript
- ✅ Props interfaces for all components
- ✅ Tailwind CSS only (no custom CSS files)
- ✅ Simple card-based layout

**KISS Principles:**
- ✅ Text-based display (no charts/graphs)
- ✅ Static visualization (no interactive elements)
- ✅ Direct API calls (no complex state management)
- ❌ No diff viewer (save for future)
- ❌ No timeline view (save for future)
- ❌ No vote visualization libraries

**Code Quality:**
- Use TypeScript interfaces, not types
- Export functions with `export function`, not `export default`
- No inline styles
- No commented-out code
- Clear, descriptive variable names
- Proper error handling (try/catch, HTTPException)

### File Ownership

**You MUST create/modify:**
```
python/cube/ui/routes/
└── tasks.py                   (ADD endpoint)

web-ui/src/
├── components/
│   ├── JudgeVote.tsx          (CREATE)
│   └── SynthesisView.tsx      (CREATE)
├── pages/
│   └── Decisions.tsx          (UPDATE)
└── types/
    └── index.ts               (UPDATE)
```

**You MUST NOT modify:**
- `cube.core.decision_files` module (just import it!)
- Decision file format
- Other pages/components unrelated to decisions
- Backend routing configuration

**Temporary modifications OK (remove before commit):**
- Dashboard.tsx for component testing

---

## ❌ **Anti-Patterns - DON'T DO THESE!**

### ❌ 1. Don't Reparse Decision Files

**BAD:**
```python
@router.get("/tasks/{task_id}/decisions")
async def get_decisions(task_id: str):
    # DON'T: Custom parsing logic
    session_dir = Path.home() / ".cube-py" / "sessions" / task_id
    with open(session_dir / "decisions.json") as f:
        data = json.load(f)
        # Manual parsing of decision structure...
```

**GOOD:**
```python
from cube.core.decision_files import read_decision_file

@router.get("/tasks/{task_id}/decisions")
async def get_decisions(task_id: str):
    # DO: Use existing module
    decisions = read_decision_file(task_id)
    return {"decisions": decisions}
```

**Why:** DRY principle. The parsing logic already exists and is tested.

### ❌ 2. Don't Over-Engineer Visualization

**BAD:**
```typescript
import { PieChart, BarChart } from 'recharts';

export function Decisions() {
  const chartData = votes.map(v => ({
    name: `Judge ${v.judge}`,
    value: v.vote === 'A' ? 1 : 0
  }));
  
  return <PieChart data={chartData} />; // Overkill!
}
```

**GOOD:**
```typescript
export function Decisions() {
  return (
    <div className="grid grid-cols-3 gap-4">
      {votes.map(vote => (
        <JudgeVote key={vote.judge} vote={vote} />
      ))}
    </div>
  );
}
```

**Why:** KISS principle. Text cards are sufficient and faster to implement.

### ❌ 3. Don't Skip Error Handling

**BAD:**
```typescript
useEffect(() => {
  fetch(`/api/tasks/${id}/decisions`)
    .then(res => res.json())
    .then(data => setDecisions(data.decisions));
}, [id]);
```

**GOOD:**
```typescript
useEffect(() => {
  fetch(`/api/tasks/${id}/decisions`)
    .then(res => {
      if (!res.ok) throw new Error('Failed to fetch');
      return res.json();
    })
    .then(data => {
      setDecisions(data.decisions || []);
      setLoading(false);
    })
    .catch(err => {
      setError(err.message);
      setLoading(false);
    });
}, [id]);
```

**Why:** Handle 404, network errors, and empty responses gracefully.

### ❌ 4. Don't Use Dynamic Tailwind Classes

**BAD:**
```typescript
const color = vote.vote === 'A' ? 'green' : 'blue';
return <span className={`bg-${color}-600`}>...</span>; // Doesn't work!
```

**GOOD:**
```typescript
const colorMap: Record<string, string> = {
  'A': 'bg-green-600',
  'B': 'bg-blue-600'
};
return <span className={colorMap[vote.vote]}>...</span>;
```

**Why:** Tailwind purges unused classes. Use static class names.

---

## 🎯 **Success Criteria**

### Definition of Done

All of these must be true:

**Backend:**
- [ ] Decision endpoint added to `tasks.py`
- [ ] Uses `cube.core.decision_files.read_decision_file`
- [ ] Returns proper JSON response
- [ ] Returns 404 for missing decisions
- [ ] Tested with curl

**Frontend:**
- [ ] TypeScript types defined in `types/index.ts`
- [ ] `JudgeVote.tsx` component created
- [ ] `SynthesisView.tsx` component created
- [ ] `Decisions.tsx` page updated
- [ ] All components use TypeScript props
- [ ] No `any` types

**Functionality:**
- [ ] Page fetches decisions from API
- [ ] Shows decision summary correctly
- [ ] Judge votes display with correct colors
- [ ] Synthesis shows when present
- [ ] Loading state works
- [ ] Error state works
- [ ] Empty state shows helpful message
- [ ] Responsive layout (works on mobile)

**Code Quality:**
- [ ] TypeScript compiles: `npx tsc --noEmit` passes
- [ ] No unused imports
- [ ] No console.log statements
- [ ] No commented-out code
- [ ] Follows KISS principles

**Testing:**
- [ ] Manually tested with real decision data
- [ ] Tested with no decisions (empty state)
- [ ] Tested with 404 (error state)
- [ ] Responsive layout verified

---

## 🚨 **CRITICAL: Git Workflow**

### Before Starting

```bash
# Ensure you're on main and up to date
git checkout main
git pull origin main

# Create your feature branch
# Replace [your-model-slug] with your actual model identifier
git checkout -b writer-[your-model-slug]/06-decisions-ui
```

### After Completing

**⚠️ MANDATORY - DO NOT SKIP ⚠️**

```bash
# Navigate to project root
cd /Users/jacob/dev/agent-cube

# Stage your changes
git add python/cube/ui/routes/tasks.py
git add web-ui/src/components/JudgeVote.tsx
git add web-ui/src/components/SynthesisView.tsx
git add web-ui/src/pages/Decisions.tsx
git add web-ui/src/types/index.ts

# Verify staged files
git status

# Commit with clear message
git commit -m "feat(ui): implement decisions UI for judge votes and synthesis

- Add /api/tasks/{id}/decisions endpoint using cube.core.decision_files
- Create JudgeVote component with color-coded vote badges
- Create SynthesisView component for merge instructions
- Update Decisions page to fetch and display decision data
- Add TypeScript interfaces for Decision, JudgeVote, SynthesisInfo
- Implement loading, error, and empty states
- Add responsive grid layout for judge votes
- Show decision summary with winner and timestamp
- Conditionally display synthesis when available

Refs: task 06-decisions-ui"

# Push to remote
git push origin writer-[your-model-slug]/06-decisions-ui

# Verify push succeeded
git log -1
git branch -vv
```

**If you don't commit and push, your work will NOT be reviewed!**

**Verify your commit is on the remote:**
```bash
git log origin/$(git branch --show-current) -1 --oneline
# Should show your commit message
```

---

## 📋 **Pre-Submission Checklist**

Before marking this task complete, verify:

**Backend:**
- [ ] Decision endpoint added and tested
- [ ] Uses `cube.core.decision_files` (no custom parsing)
- [ ] Proper error handling (404, 500)
- [ ] Returns correct JSON structure

**Frontend:**
- [ ] All 3 components created (JudgeVote, SynthesisView, updated Decisions)
- [ ] TypeScript types defined
- [ ] TypeScript compiles with no errors
- [ ] All states handled (loading, error, empty, data)
- [ ] Responsive layout works
- [ ] Color coding correct

**Testing:**
- [ ] Tested with real decision data
- [ ] Tested empty state
- [ ] Tested error state
- [ ] No console warnings/errors
- [ ] Works on mobile viewport

**Code Quality:**
- [ ] No `any` types
- [ ] No unused imports
- [ ] No console.log statements
- [ ] No commented-out code
- [ ] Follows KISS principles

**Git:**
- [ ] Changes committed with descriptive message
- [ ] Changes pushed to feature branch
- [ ] Branch name correct: `writer-[your-model-slug]/06-decisions-ui`
- [ ] Verified commit on remote

---

## 🆘 **Troubleshooting**

### Issue: Backend can't find decision files

**Symptom:** 404 errors even when decisions exist

**Cause:** Wrong path or module import

**Fix:**
1. Verify import: `from cube.core.decision_files import read_decision_file`
2. Check session directory exists: `~/.cube-py/sessions/{task-id}/`
3. Ensure decision file exists: `decisions.json` in session directory

### Issue: TypeScript errors on decision types

**Symptom:** "Property 'winner' does not exist on type 'Decision'"

**Cause:** Optional properties not marked correctly

**Fix:** Use optional properties: `winner?: 'A' | 'B'`

### Issue: Colors not showing correctly

**Symptom:** All vote badges are gray

**Cause:** Dynamic class names not working

**Fix:** Use object/map with static class names:
```typescript
const colorMap: Record<string, string> = {
  'A': 'bg-green-600',
  'B': 'bg-blue-600'
};
```

### Issue: Synthesis not showing

**Symptom:** Synthesis section never renders

**Cause:** Checking wrong property or undefined

**Fix:**
```typescript
{latestDecision.synthesis && (
  <SynthesisView synthesis={latestDecision.synthesis} />
)}
```

### Issue: Empty state not showing

**Symptom:** Blank page when no decisions

**Cause:** Not handling empty array

**Fix:**
```typescript
if (decisions.length === 0) {
  return <div>No decisions yet</div>;
}
```

---

## 📞 **Integration Notes**

**Depends on:**
- Task 01: Routing (to navigate to decisions page)
- Task 02: Backend API (server infrastructure)
- Existing: `cube.core.decision_files` module

**Used by:**
- Task Detail View (links to decisions page)

**Future enhancements (NOT in this task):**
- Timeline view showing decision history
- Diff viewer for synthesis changes
- Export decisions as markdown

---

## 📚 **Reference: Decision File Format**

Understanding the data structure (DO NOT reparse, just reference):

```json
{
  "type": "panel",
  "timestamp": "2025-11-11T10:30:00Z",
  "winner": "A",
  "judges": [
    {
      "judge": 1,
      "model": "claude-sonnet-4",
      "vote": "A",
      "rationale": "Implementation is more complete and follows best practices"
    },
    {
      "judge": 2,
      "model": "gpt-4-turbo",
      "vote": "A",
      "rationale": "Better error handling and type safety"
    },
    {
      "judge": 3,
      "model": "claude-opus",
      "vote": "B",
      "rationale": "Simpler approach, easier to maintain"
    }
  ],
  "synthesis": {
    "compatible": true,
    "instructions": [
      "Use Writer A's component structure",
      "Incorporate Writer B's simplified error handling",
      "Merge both approaches to styling"
    ],
    "bestBits": {
      "writerA": [
        "Type safety with strict interfaces",
        "Comprehensive error boundaries",
        "Loading state management"
      ],
      "writerB": [
        "Cleaner component composition",
        "Simpler prop structure"
      ]
    }
  }
}
```

---

## 📖 **Key Concepts**

### Panel vs Peer Review

**Panel Decision:**
- Type: `"panel"`
- Has `winner` field (A or B)
- May have `synthesis` if compatible
- Votes are A or B

**Peer Review Decision:**
- Type: `"peer-review"`
- No `winner` field
- Votes are APPROVE, REQUEST_CHANGES, or COMMENT
- May have feedback/comments

Your UI should distinguish between these types.

### Synthesis

Only present when:
- Panel decision
- Judges voted for different writers BUT
- Outputs are compatible for merging

Shows how to combine best parts of both outputs.

---

## ✅ **Final Reminder**

**Your deliverables:**
1. Backend endpoint in `tasks.py`
2. Two new components: `JudgeVote.tsx`, `SynthesisView.tsx`
3. Updated `Decisions.tsx` page
4. Updated `types/index.ts` with decision interfaces
5. All TypeScript compiles without errors
6. Git commit + push to feature branch

**Time estimate:** 2-3 hours

**Next steps:**
- This is a standalone feature
- May integrate with Task Detail navigation
- Could be enhanced with timeline view (future work)

**Questions?** Refer to:
- `planning/web-ui.md` for architecture
- `python/cube/core/decision_files.py` for data format
- Existing components for styling patterns

---

**Remember:** Keep it simple. Use existing modules. No over-engineering. And **COMMIT YOUR WORK!** 🚀

Good luck! 🎯
