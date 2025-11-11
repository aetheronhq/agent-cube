# Task 06: Decisions UI - Judge Votes and Synthesis

**Goal:** Implement decisions page that displays judge votes, synthesis instructions, and decision aggregation results.

**Time Estimate:** 2-3 hours

---

## 📖 **Context**

**What this builds on:**
- Task 01: Routing and page structure
- Task 02: Backend API (will add `/api/tasks/{id}/decisions` endpoint)
- Existing decision files (`decisions.json` from `cube.core.decision_files`)

**Planning docs (Golden Source):**
- `planning/web-ui.md` - Component architecture
- Existing: `python/cube/core/decision_files.py` - Decision JSON format

---

## ✅ **Requirements**

### **1. Decision Endpoint (Backend)**

**Deliverable:**
- Add `/api/tasks/{id}/decisions` endpoint
- Return parsed decision data from JSON files

**Acceptance criteria:**
- [ ] Endpoint reads from session directory
- [ ] Returns panel decisions and peer review decisions
- [ ] Parses JSON using `cube.core.decision_files`
- [ ] Returns 404 if no decisions found

### **2. Decisions Page**

**Deliverable:**
- Display judge votes (A or B)
- Show synthesis instructions
- Display decision summary (winner, consensus)

**Acceptance criteria:**
- [ ] `pages/Decisions.tsx` updated
- [ ] Fetches from `/api/tasks/{id}/decisions`
- [ ] Shows each judge's vote
- [ ] Shows majority decision
- [ ] Shows synthesis instructions if applicable
- [ ] Distinguishes panel vs peer review

### **3. JudgeVote Component**

**Deliverable:**
- Card showing individual judge vote
- Shows vote (A/B/APPROVE/REQUEST_CHANGES)
- Shows brief rationale

**Acceptance criteria:**
- [ ] `components/JudgeVote.tsx` created
- [ ] Displays judge number and model
- [ ] Shows vote with color coding
- [ ] Shows rationale text
- [ ] Responsive card layout

### **4. SynthesisView Component**

**Deliverable:**
- Display synthesis instructions
- Show best bits from each writer
- Display compatibility assessment

**Acceptance criteria:**
- [ ] `components/SynthesisView.tsx` created
- [ ] Shows synthesis instructions
- [ ] Lists best bits by writer
- [ ] Shows compatibility notes
- [ ] Collapsible sections for readability

---

## 📝 **Implementation Steps**

**Suggested order:**

1. **Backend: Decision Endpoint**
   - [ ] Add to `routes/tasks.py`
   - [ ] Import from `cube.core.decision_files`
   - [ ] Implement `/api/tasks/{id}/decisions`
   - [ ] Parse and return JSON data

2. **Frontend: Type Definitions**
   - [ ] Add decision types to `types/index.ts`
   - [ ] `JudgeVote`, `Decision`, `SynthesisInfo` interfaces

3. **Frontend: JudgeVote Component**
   - [ ] Create `components/JudgeVote.tsx`
   - [ ] Card layout with vote badge
   - [ ] Color coding: A=green, B=blue, APPROVE=green, REQUEST_CHANGES=red

4. **Frontend: SynthesisView Component**
   - [ ] Create `components/SynthesisView.tsx`
   - [ ] Display instructions and best bits
   - [ ] Collapsible sections

5. **Frontend: Decisions Page**
   - [ ] Update `pages/Decisions.tsx`
   - [ ] Fetch decision data
   - [ ] Display judges in grid
   - [ ] Show decision summary
   - [ ] Conditionally show synthesis

6. **Test Integration**
   - [ ] Run task through panel: `cube panel test-task panel-prompt.md`
   - [ ] Open UI: `http://localhost:5173/tasks/test-task/decisions`
   - [ ] Verify votes display
   - [ ] Verify synthesis shows if applicable

7. **Verify**
   - [ ] All judge votes visible
   - [ ] Synthesis instructions readable
   - [ ] No errors for tasks without decisions
   - [ ] TypeScript compiles

8. **Finalize**
   - [ ] Commit changes
   - [ ] Push to branch

---

## 🏗️ **Architecture Constraints**

### **Must Follow**

**Planning docs:**
- Use existing decision file format
- Direct import from `cube.core.decision_files`

**Technical constraints:**
- Type-safe decision parsing
- Handle missing decisions gracefully
- Show both panel and peer review decisions

**KISS Principles:**
- ✅ Read from existing JSON files (no custom format)
- ✅ Simple card layout (no complex visualization)
- ✅ Static display (no interactive voting)
- ❌ No charts/graphs (text is sufficient)
- ❌ No diff viewer (just show instructions)

---

## 🚫 **Anti-Patterns**

### **❌ DON'T: Build Complex Visualization**

```typescript
// Bad: Over-engineering with charts
import { PieChart, Pie } from 'recharts';

function Decisions() {
  return (
    <PieChart width={400} height={400}>
      <Pie data={voteData} /* ... */ />
    </PieChart>
  );
}
```

**Instead:**
```typescript
// Good: Simple text display
function Decisions() {
  return (
    <div className="grid grid-cols-3 gap-4">
      {judges.map(judge => (
        <JudgeVote key={judge.id} vote={judge.vote} />
      ))}
    </div>
  );
}
```

### **❌ DON'T: Reparse Decision Files**

```python
# Bad: Reimplementing parsing logic
@app.get("/api/tasks/{task_id}/decisions")
async def get_decisions(task_id: str):
    # BAD: Custom parsing
    with open(f"{sessions_dir}/{task_id}/decisions.json") as f:
        data = json.load(f)
        # Manual parsing...
```

**Instead:**
```python
# Good: Use existing module
from cube.core.decision_files import read_decision_file

@app.get("/api/tasks/{task_id}/decisions")
async def get_decisions(task_id: str):
    decisions = read_decision_file(task_id)
    return decisions
```

---

## 📂 **Owned Paths**

**This task owns:**
```
python/cube/ui/routes/
└── tasks.py  (add decision endpoint)

web-ui/src/
├── components/
│   ├── JudgeVote.tsx
│   └── SynthesisView.tsx
├── pages/
│   └── Decisions.tsx
└── types/
    └── index.ts  (add decision types)
```

**Must NOT modify:**
- Decision file format (defined in `cube.core`)
- Other pages/components
- Backend modules (just import)

**Integration:**
- Reads from `cube.core.decision_files`
- Linked from TaskDetail page (via navigation)

---

## 🧪 **Testing Requirements**

**Manual testing:**
- [ ] Run task with panel: `cube panel test-task prompt.md`
- [ ] Wait for panel completion
- [ ] Run aggregation: `cube decide test-task`
- [ ] Open UI: `http://localhost:5173/tasks/test-task/decisions`
- [ ] Verify judge votes display
- [ ] Verify synthesis shows if present

**Test scenarios:**
- No decisions yet → show "No decisions" message
- Panel decisions only → show panel results
- Peer review decisions → show both panel and peer

---

## ✅ **Acceptance Criteria**

**Definition of Done:**

- [ ] `/api/tasks/{id}/decisions` endpoint implemented
- [ ] `JudgeVote` component created
- [ ] `SynthesisView` component created
- [ ] Decisions page displays judge votes
- [ ] Shows decision summary (winner, consensus)
- [ ] Shows synthesis instructions when applicable
- [ ] Handles missing decisions gracefully
- [ ] TypeScript types for decisions
- [ ] TypeScript compiles: `npx tsc --noEmit`
- [ ] Changes committed and pushed

**Quality gates:**
- [ ] Follows KISS (simple text display)
- [ ] Reuses decision parsing (no duplication)
- [ ] Clean error states

---

## 🔗 **Integration Points**

**Dependencies (requires these first):**
- Task 01: Routing
- Task 02: Backend API base

**Dependents (these will use this):**
- None (standalone feature)

**Integrator task:**
- Links from TaskDetail navigation

---

## 📊 **Examples**

### **types/index.ts additions**

```typescript
export interface JudgeVote {
  judge: number;
  model: string;
  vote: 'A' | 'B' | 'APPROVE' | 'REQUEST_CHANGES' | 'COMMENT';
  rationale: string;
}

export interface SynthesisInfo {
  instructions: string[];
  bestBits: {
    writerA: string[];
    writerB: string[];
  };
  compatible: boolean;
}

export interface Decision {
  type: 'panel' | 'peer-review';
  judges: JudgeVote[];
  winner?: 'A' | 'B';
  synthesis?: SynthesisInfo;
  timestamp: string;
}
```

### **Backend: Decision Endpoint**

```python
from cube.core.decision_files import read_decision_file
from fastapi import HTTPException

@router.get("/tasks/{task_id}/decisions")
async def get_decisions(task_id: str):
    try:
        decisions = read_decision_file(task_id)
        return {"decisions": decisions}
    except FileNotFoundError:
        raise HTTPException(404, "No decisions found for this task")
```

### **components/JudgeVote.tsx**

```typescript
import { JudgeVote as JudgeVoteType } from '../types';

interface JudgeVoteProps {
  vote: JudgeVoteType;
}

export function JudgeVote({ vote }: JudgeVoteProps) {
  const voteColor = {
    'A': 'bg-green-600',
    'B': 'bg-blue-600',
    'APPROVE': 'bg-green-600',
    'REQUEST_CHANGES': 'bg-red-600',
    'COMMENT': 'bg-yellow-600'
  }[vote.vote] || 'bg-gray-600';

  return (
    <div className="border border-gray-700 rounded-lg p-4 bg-cube-gray">
      <div className="flex justify-between items-start mb-2">
        <div>
          <h3 className="font-semibold">Judge {vote.judge}</h3>
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

### **components/SynthesisView.tsx**

```typescript
import { SynthesisInfo } from '../types';

interface SynthesisViewProps {
  synthesis: SynthesisInfo;
}

export function SynthesisView({ synthesis }: SynthesisViewProps) {
  return (
    <div className="border border-gray-700 rounded-lg p-4 bg-cube-gray">
      <h3 className="font-semibold mb-3">Synthesis Instructions</h3>
      
      <div className="mb-4">
        <h4 className="text-sm text-gray-400 mb-2">Compatible: {synthesis.compatible ? '✅ Yes' : '❌ No'}</h4>
      </div>

      <div className="mb-4">
        <h4 className="text-sm font-semibold mb-2">Instructions</h4>
        <ul className="list-disc list-inside space-y-1 text-sm text-gray-300">
          {synthesis.instructions.map((instruction, i) => (
            <li key={i}>{instruction}</li>
          ))}
        </ul>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <h4 className="text-sm font-semibold mb-2 text-green-400">Best Bits: Writer A</h4>
          <ul className="list-disc list-inside space-y-1 text-xs text-gray-300">
            {synthesis.bestBits.writerA.map((bit, i) => (
              <li key={i}>{bit}</li>
            ))}
          </ul>
        </div>
        <div>
          <h4 className="text-sm font-semibold mb-2 text-blue-400">Best Bits: Writer B</h4>
          <ul className="list-disc list-inside space-y-1 text-xs text-gray-300">
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

### **pages/Decisions.tsx**

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

  useEffect(() => {
    fetch(`http://localhost:3030/api/tasks/${id}/decisions`)
      .then(res => res.json())
      .then(data => {
        setDecisions(data.decisions || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [id]);

  if (loading) return <div>Loading decisions...</div>;
  if (decisions.length === 0) {
    return (
      <div className="text-center py-12 text-gray-400">
        No decisions yet. Run the judge panel first.
      </div>
    );
  }

  const latestDecision = decisions[decisions.length - 1];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Decisions: {id}</h1>

      <div className="border border-gray-700 rounded-lg p-4 bg-cube-gray">
        <h2 className="text-lg font-semibold mb-2">Decision Summary</h2>
        <div className="text-sm text-gray-300">
          <p>Type: <span className="font-semibold">{latestDecision.type}</span></p>
          {latestDecision.winner && (
            <p>Winner: <span className="font-semibold text-green-400">Writer {latestDecision.winner}</span></p>
          )}
          <p>Timestamp: {new Date(latestDecision.timestamp).toLocaleString()}</p>
        </div>
      </div>

      <div>
        <h2 className="text-lg font-semibold mb-3">Judge Votes</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {latestDecision.judges.map((vote) => (
            <JudgeVote key={vote.judge} vote={vote} />
          ))}
        </div>
      </div>

      {latestDecision.synthesis && (
        <div>
          <h2 className="text-lg font-semibold mb-3">Synthesis</h2>
          <SynthesisView synthesis={latestDecision.synthesis} />
        </div>
      )}
    </div>
  );
}
```

---

## 🎓 **Common Pitfalls**

**Watch out for:**
- ⚠️ Missing decision files (handle 404 gracefully)
- ⚠️ Different formats for panel vs peer review
- ⚠️ JSON parsing errors (use try/catch)

**If you see [empty page], it means [decision file not found or wrong format] - fix by [checking session directory and decision_files module]**

---

## 📝 **Notes**

**Additional context:**
- Decision files are in `~/.cube-py/sessions/{task-id}/decisions.json`
- Format defined by `cube.core.decision_files`
- Both panel and peer review use same format with different `type` field

**Nice-to-haves (not required):**
- Timeline view showing decision history
- Diff view for synthesis changes
- Export decisions as markdown

---

**FINAL STEPS - CRITICAL:**

```bash
# Stage changes
git add python/cube/ui/routes/ web-ui/src/

# Commit
git commit -m "feat(ui): implement decisions UI for judge votes and synthesis"

# Push
git push origin writer-[your-model-slug]/06-decisions-ui

# Verify
git status
```

**⚠️ IMPORTANT:** Uncommitted or unpushed changes will NOT be reviewed!

---

**Built with:** Agent Cube v1.0
**Template version:** 1.0
**Last updated:** 2025-11-11

