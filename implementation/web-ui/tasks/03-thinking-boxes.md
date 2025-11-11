# Task 03: Thinking Boxes Component

**Goal:** Implement dual and triple thinking box layouts that mirror the CLI's Rich Layout visualization.

**Time Estimate:** 3-4 hours

---

## 📖 **Context**

**What this builds on:**
- Task 01: React project structure and styling
- Existing CLI: `base_layout.py`, `dual_layout.py`, `triple_layout.py`
- Core AgentCube UX is seeing AI agents think in real-time

**Planning docs (Golden Source):**
- `planning/web-ui.md` - Component architecture, SSE message format

---

## ✅ **Requirements**

### **1. ThinkingBox Component**

**Deliverable:**
- Individual thinking box component (reusable)
- Shows agent name, recent thinking lines
- Matches CLI aesthetic (dark, monospace)

**Acceptance criteria:**
- [ ] `ThinkingBox.tsx` component created
- [ ] Props: `title`, `lines`, `icon`
- [ ] Displays last 3 lines of thinking
- [ ] Text truncation for long lines (91 chars + "...")
- [ ] Monospace font for consistency with CLI

### **2. DualLayout Component**

**Deliverable:**
- Two thinking boxes side-by-side
- Writer A (green) and Writer B (blue)
- Matches CLI dual writer layout

**Acceptance criteria:**
- [ ] `DualLayout.tsx` component created
- [ ] Props: `writerALines`, `writerBLines`
- [ ] Two `ThinkingBox` components rendered
- [ ] Color coding: Writer A (green), Writer B (blue)
- [ ] Responsive grid (2 columns on desktop)

### **3. TripleLayout Component**

**Deliverable:**
- Three thinking boxes in grid
- Judge 1, Judge 2, Judge 3
- Matches CLI triple judge layout

**Acceptance criteria:**
- [ ] `TripleLayout.tsx` component created
- [ ] Props: `judge1Lines`, `judge2Lines`, `judge3Lines`
- [ ] Three `ThinkingBox` components rendered
- [ ] Icons: ⚖️ for judges, 💭 for writers
- [ ] Responsive grid (3 columns on desktop, stack on smaller screens)

### **4. TypeScript Types**

**Deliverable:**
- Shared types for thinking box data

**Acceptance criteria:**
- [ ] `types/index.ts` defines `ThinkingLine` interface
- [ ] Type for agent metadata (name, color, icon)
- [ ] Type-safe component props

---

## 📝 **Implementation Steps**

**Suggested order:**

1. **Define types**
   - [ ] Create interfaces in `src/types/index.ts`
   - [ ] `ThinkingLine`, `AgentInfo` types
   - [ ] Export for use across components

2. **Create ThinkingBox component**
   - [ ] `src/components/ThinkingBox.tsx`
   - [ ] Accept `title`, `lines`, `icon` props
   - [ ] Render box with border and padding
   - [ ] Display last 3 lines with dim text
   - [ ] Truncate lines >91 chars

3. **Create DualLayout**
   - [ ] `src/components/DualLayout.tsx`
   - [ ] Two-column grid
   - [ ] Pass data to two ThinkingBox instances
   - [ ] Color-code borders (green/blue)

4. **Create TripleLayout**
   - [ ] `src/components/TripleLayout.tsx`
   - [ ] Three-column grid
   - [ ] Pass data to three ThinkingBox instances
   - [ ] Use judge icons and colors

5. **Style components**
   - [ ] Tailwind classes for dark theme
   - [ ] Monospace font (`font-mono`)
   - [ ] Borders, padding, spacing
   - [ ] Responsive breakpoints

6. **Create demo pages**
   - [ ] Temporary demo in Dashboard
   - [ ] Mock thinking data
   - [ ] Verify both layouts render

7. **Verify**
   - [ ] Components render without errors
   - [ ] Text truncation works
   - [ ] Responsive layout works
   - [ ] TypeScript compiles with no errors

8. **Finalize**
   - [ ] Remove demo code
   - [ ] Commit changes
   - [ ] Push to branch

---

## 🏗️ **Architecture Constraints**

### **Must Follow**

**Planning docs:**
- Match CLI aesthetic from `planning/web-ui.md`
- Component hierarchy: ThinkingBox → DualLayout/TripleLayout
- SSE message format (for future integration)

**Technical constraints:**
- TypeScript strict mode (no `any`)
- Functional components with hooks
- Props interface for every component
- Tailwind only (no custom CSS)

**KISS Principles:**
- ✅ Simple component composition
- ✅ Props-based data flow (no complex state)
- ✅ Reusable ThinkingBox (DRY)
- ❌ No animation libraries (CSS transitions sufficient)
- ❌ No virtualization (only 3 lines per box)

---

## 🚫 **Anti-Patterns**

### **❌ DON'T: Over-Engineer with Refs and Animations**

```typescript
// Bad: Unnecessary complexity
const ThinkingBox = ({ lines }: Props) => {
  const ref = useRef<HTMLDivElement>(null);
  const [isAnimating, setIsAnimating] = useState(false);
  
  useEffect(() => {
    // Complex animation logic
    ref.current?.animate(/* ... */);
  }, [lines]);
  
  // Over-engineered
};
```

**Instead:**
```typescript
// Good: Simple and direct
export function ThinkingBox({ title, lines, icon }: ThinkingBoxProps) {
  return (
    <div className="border border-gray-700 rounded-lg p-4">
      <h3 className="text-sm text-gray-400 mb-2">
        {icon} {title}
      </h3>
      <div className="space-y-1 font-mono text-xs">
        {lines.slice(-3).map((line, i) => (
          <p key={i} className="text-gray-300 truncate">
            {line.length > 91 ? line.slice(0, 91) + '...' : line}
          </p>
        ))}
      </div>
    </div>
  );
}
```

### **❌ DON'T: Use Generic UI Libraries**

```typescript
// Bad: Unnecessary dependency
import { Card, CardHeader, CardContent } from '@mui/material';

export function ThinkingBox({ title, lines }: Props) {
  return (
    <Card>
      <CardHeader title={title} />
      <CardContent>...</CardContent>
    </Card>
  );
}
```

**Instead:**
```typescript
// Good: Custom with Tailwind (full control)
export function ThinkingBox({ title, lines }: Props) {
  return (
    <div className="border rounded-lg p-4">
      <h3 className="text-sm mb-2">{title}</h3>
      <div>...</div>
    </div>
  );
}
```

---

## 📂 **Owned Paths**

**This task owns:**
```
web-ui/src/
├── components/
│   ├── ThinkingBox.tsx
│   ├── DualLayout.tsx
│   └── TripleLayout.tsx
└── types/
    └── index.ts
```

**Must NOT modify:**
- Backend code (Task 02)
- Page components (Tasks 04, 05, 06)
- Routing (Task 01)

**Integration:**
- Task 05 (TaskDetail) will use these components
- Task 06 (Decisions) might display judge thinking

---

## 🧪 **Testing Requirements**

**Manual testing:**
- [ ] Dual layout displays two boxes correctly
- [ ] Triple layout displays three boxes correctly
- [ ] Long lines truncate at 91 chars
- [ ] Empty lines array shows empty boxes
- [ ] Responsive layout works (resize browser)
- [ ] Colors match CLI (green/blue for writers)

**Test with mock data:**
```typescript
// In Dashboard.tsx temporarily
const mockWriterA = [
  "Analyzing task requirements...",
  "Reading planning docs...",
  "Starting implementation..."
];

const mockWriterB = [
  "Reviewing architecture...",
  "Setting up types...",
  "Writing tests..."
];

return <DualLayout writerALines={mockWriterA} writerBLines={mockWriterB} />;
```

---

## ✅ **Acceptance Criteria**

**Definition of Done:**

- [ ] `ThinkingBox` component implemented
- [ ] `DualLayout` component implemented
- [ ] `TripleLayout` component implemented
- [ ] TypeScript types defined in `types/index.ts`
- [ ] Components render without errors
- [ ] Text truncation works (>91 chars)
- [ ] Last 3 lines displayed per box
- [ ] Monospace font applied
- [ ] Color coding correct (green/blue for writers, gray for judges)
- [ ] Responsive grid layout
- [ ] TypeScript compiles: `npx tsc --noEmit`
- [ ] Changes committed and pushed

**Quality gates:**
- [ ] Follows KISS (no animations, no refs)
- [ ] Reusable components (DRY)
- [ ] Type-safe props
- [ ] Matches CLI aesthetic

---

## 🔗 **Integration Points**

**Dependencies (requires these first):**
- Task 01: React project structure, Tailwind config

**Dependents (these will use this):**
- Task 05: Task detail view (displays thinking boxes with live data)
- Task 06: Decisions UI (might show judge thinking)

**Integrator task:**
- Task 05 will wire these components to SSE data stream

---

## 📊 **Examples**

### **types/index.ts**

```typescript
export interface ThinkingLine {
  text: string;
  timestamp: string;
}

export interface AgentInfo {
  id: string;
  name: string;
  color: string;
  icon: string;
}

export interface ThinkingBoxProps {
  title: string;
  lines: string[];
  icon: string;
  color?: string;
}
```

### **ThinkingBox.tsx**

```typescript
import { ThinkingBoxProps } from '../types';

export function ThinkingBox({ title, lines, icon, color = 'gray' }: ThinkingBoxProps) {
  const borderColor = `border-${color}-700`;
  const textColor = `text-${color}-400`;
  
  return (
    <div className={`border ${borderColor} rounded-lg p-4 bg-cube-gray`}>
      <h3 className={`text-sm ${textColor} mb-2`}>
        {icon} {title}
      </h3>
      <div className="space-y-1 font-mono text-xs text-gray-300 min-h-[3rem]">
        {lines.slice(-3).map((line, i) => (
          <p key={i} className="truncate">
            {line.length > 91 ? line.slice(0, 91) + '...' : line}
          </p>
        ))}
      </div>
    </div>
  );
}
```

### **DualLayout.tsx**

```typescript
import { ThinkingBox } from './ThinkingBox';

interface DualLayoutProps {
  writerALines: string[];
  writerBLines: string[];
}

export function DualLayout({ writerALines, writerBLines }: DualLayoutProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <ThinkingBox
        title="Writer A"
        lines={writerALines}
        icon="💭"
        color="green"
      />
      <ThinkingBox
        title="Writer B"
        lines={writerBLines}
        icon="💭"
        color="blue"
      />
    </div>
  );
}
```

### **TripleLayout.tsx**

```typescript
import { ThinkingBox } from './ThinkingBox';

interface TripleLayoutProps {
  judge1Lines: string[];
  judge2Lines: string[];
  judge3Lines: string[];
}

export function TripleLayout({ judge1Lines, judge2Lines, judge3Lines }: TripleLayoutProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <ThinkingBox title="Judge 1" lines={judge1Lines} icon="⚖️" />
      <ThinkingBox title="Judge 2" lines={judge2Lines} icon="⚖️" />
      <ThinkingBox title="Judge 3" lines={judge3Lines} icon="⚖️" />
    </div>
  );
}
```

---

## 🎓 **Common Pitfalls**

**Watch out for:**
- ⚠️ Dynamic Tailwind classes don't work (use safelist or static classes)
- ⚠️ Forgetting `min-h` causes boxes to collapse when empty
- ⚠️ Key prop warnings on mapped elements

**If you see [colors not applying], it means [dynamic classes not in bundle] - fix by [using static class names]**

---

## 📝 **Notes**

**Additional context:**
- CLI shows last 3 lines per box (match this)
- CLI truncates at 91 chars (match this)
- Lines ending with punctuation trigger new line in CLI (not needed in UI)

**Nice-to-haves (not required):**
- Subtle fade-in when new line appears
- Auto-scroll to bottom of thinking box

---

**FINAL STEPS - CRITICAL:**

```bash
# Stage changes
git add web-ui/src/components/ web-ui/src/types/

# Commit
git commit -m "feat(ui): implement thinking box components for dual and triple layouts"

# Push
git push origin writer-[your-model-slug]/03-thinking-boxes

# Verify
git status
```

**⚠️ IMPORTANT:** Uncommitted or unpushed changes will NOT be reviewed!

---

**Built with:** Agent Cube v1.0
**Template version:** 1.0
**Last updated:** 2025-11-11

