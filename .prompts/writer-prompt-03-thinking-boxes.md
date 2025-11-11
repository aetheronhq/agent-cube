# Writer Prompt: Thinking Boxes Component

**Task ID:** 03-thinking-boxes
**Workflow:** Dual-Writer with Triple-Judge Panel
**Time Estimate:** 3-4 hours

---

## 🎯 Your Mission

Implement the **thinking box components** that visualize AI agent reasoning in real-time. These components mirror the CLI's Rich Layout visualization and are core to the Agent Cube UX.

You will create:
1. **ThinkingBox** - Reusable component for individual agent thinking
2. **DualLayout** - Side-by-side layout for two writers
3. **TripleLayout** - Three-column layout for judges

---

## 📚 Context

### What You're Building On

**Existing work:**
- Task 01 completed: React + Vite project with Tailwind CSS configured
- Project structure: `web-ui/src/` with pages and components folders
- CLI implementation: `python/cube/core/base_layout.py`, `dual_layout.py`, `triple_layout.py`

**Why this matters:**
The core Agent Cube UX is watching AI agents think in real-time. The CLI shows thinking text streaming into boxes. Your job is to recreate this in React.

### Reference Materials

**GOLDEN SOURCE - Read these first:**
- `planning/web-ui.md` - Component architecture, SSE message format
- `implementation/web-ui/phase-02/` - Component phase documentation
- CLI code in `python/cube/core/` for layout behavior

**Key insights from CLI:**
- Shows last 3 lines of thinking per agent
- Truncates lines at 91 characters
- Uses monospace font and dark theme
- Color codes: green for Writer A, blue for Writer B
- Icons: 💭 for writers, ⚖️ for judges

---

## ✅ Requirements Checklist

### 1. ThinkingBox Component

Create a reusable component that displays agent thinking.

**Required props:**
- `title: string` - Agent name (e.g., "Writer A", "Judge 1")
- `lines: string[]` - Array of thinking text lines
- `icon: string` - Emoji icon (💭 or ⚖️)
- `color?: string` - Border/text color (optional, defaults to gray)

**Display rules:**
- Show only the last 3 lines from `lines` array
- Truncate lines longer than 91 characters with "..."
- Use monospace font (`font-mono` in Tailwind)
- Dark background with colored border
- Minimum height to prevent collapse when empty

**Deliverable:**
- [ ] File created: `web-ui/src/components/ThinkingBox.tsx`
- [ ] Props interface defined
- [ ] Displays icon and title
- [ ] Shows last 3 lines with proper truncation
- [ ] Styled with Tailwind classes

### 2. DualLayout Component

Create a two-column layout for dual writers.

**Required props:**
- `writerALines: string[]` - Thinking lines for Writer A
- `writerBLines: string[]` - Thinking lines for Writer B

**Display rules:**
- Two ThinkingBox components side-by-side
- Writer A: green color, 💭 icon
- Writer B: blue color, 💭 icon
- Responsive: 2 columns on desktop, stack on mobile
- Equal width columns with gap between

**Deliverable:**
- [ ] File created: `web-ui/src/components/DualLayout.tsx`
- [ ] Props interface defined
- [ ] Two ThinkingBox instances rendered
- [ ] Grid layout with responsive breakpoints
- [ ] Correct colors and icons

### 3. TripleLayout Component

Create a three-column layout for judges.

**Required props:**
- `judge1Lines: string[]` - Thinking lines for Judge 1
- `judge2Lines: string[]` - Thinking lines for Judge 2
- `judge3Lines: string[]` - Thinking lines for Judge 3

**Display rules:**
- Three ThinkingBox components in a row
- All use ⚖️ icon and gray color scheme
- Responsive: 3 columns on desktop, stack on mobile
- Equal width columns with gaps

**Deliverable:**
- [ ] File created: `web-ui/src/components/TripleLayout.tsx`
- [ ] Props interface defined
- [ ] Three ThinkingBox instances rendered
- [ ] Grid layout with responsive breakpoints
- [ ] Judge styling and icons

### 4. TypeScript Types

Define shared types for type safety.

**Required types:**
- `ThinkingLine` - Individual thinking line (text, timestamp)
- `AgentInfo` - Agent metadata (id, name, color, icon)
- `ThinkingBoxProps` - Props for ThinkingBox component
- Additional interfaces as needed

**Deliverable:**
- [ ] File created: `web-ui/src/types/index.ts`
- [ ] All interfaces exported
- [ ] Used in component props
- [ ] No `any` types (TypeScript strict mode)

---

## 🛠️ Implementation Steps

Follow these steps in order:

### Step 1: Create Types

```bash
# Create types directory if it doesn't exist
mkdir -p web-ui/src/types
```

Create `web-ui/src/types/index.ts` with:
- `ThinkingLine` interface
- `AgentInfo` interface
- `ThinkingBoxProps` interface
- Any other needed types

### Step 2: Implement ThinkingBox

Create `web-ui/src/components/ThinkingBox.tsx`:

**Requirements:**
- Import types from `../types`
- Define props interface extending `ThinkingBoxProps`
- Return a `div` with Tailwind classes for:
  - Dark background (`bg-gray-900` or similar)
  - Colored border (use static classes, NOT dynamic)
  - Rounded corners (`rounded-lg`)
  - Padding (`p-4`)
- Header section with icon and title
- Content section with last 3 lines
- Text truncation logic for lines > 91 chars

**Example structure:**
```typescript
export function ThinkingBox({ title, lines, icon, color = 'gray' }: ThinkingBoxProps) {
  // Get last 3 lines
  const displayLines = lines.slice(-3);
  
  return (
    <div className="border rounded-lg p-4 bg-gray-900 min-h-[8rem]">
      <h3 className="text-sm text-gray-400 mb-2">
        {icon} {title}
      </h3>
      <div className="space-y-1 font-mono text-xs text-gray-300">
        {displayLines.map((line, i) => (
          <p key={i} className="truncate">
            {line.length > 91 ? line.slice(0, 91) + '...' : line}
          </p>
        ))}
      </div>
    </div>
  );
}
```

### Step 3: Implement DualLayout

Create `web-ui/src/components/DualLayout.tsx`:

**Requirements:**
- Import `ThinkingBox` from `./ThinkingBox`
- Define props interface
- Use CSS Grid with 2 columns on medium+ screens
- Pass correct props to ThinkingBox instances
- Writer A: green border/text
- Writer B: blue border/text

**Example structure:**
```typescript
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

### Step 4: Implement TripleLayout

Create `web-ui/src/components/TripleLayout.tsx`:

**Requirements:**
- Import `ThinkingBox` from `./ThinkingBox`
- Define props interface
- Use CSS Grid with 3 columns on medium+ screens
- Pass correct props to ThinkingBox instances
- All judges: ⚖️ icon, gray color

**Example structure:**
```typescript
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

### Step 5: Manual Testing

Add temporary test code to `web-ui/src/pages/Dashboard.tsx`:

```typescript
import { DualLayout } from '../components/DualLayout';
import { TripleLayout } from '../components/TripleLayout';

// Inside Dashboard component
const mockWriterA = [
  "Analyzing task requirements from planning docs...",
  "Identifying key components to implement...",
  "Starting with type definitions..."
];

const mockWriterB = [
  "Reading through existing code structure...",
  "Understanding integration points...",
  "Planning component architecture..."
];

const mockJudge1 = [
  "Evaluating implementation approach...",
  "Checking against requirements..."
];

return (
  <div className="space-y-8">
    <h2>Dual Writer Layout Test</h2>
    <DualLayout writerALines={mockWriterA} writerBLines={mockWriterB} />
    
    <h2>Triple Judge Layout Test</h2>
    <TripleLayout 
      judge1Lines={mockJudge1} 
      judge2Lines={[]} 
      judge3Lines={[]} 
    />
  </div>
);
```

**Test cases:**
- [ ] Both layouts render without errors
- [ ] Long lines truncate at 91 characters
- [ ] Empty arrays show empty boxes (don't collapse)
- [ ] Responsive layout works (resize browser)
- [ ] Colors match specification
- [ ] Icons display correctly

### Step 6: Verify TypeScript

```bash
cd web-ui
npx tsc --noEmit
```

**Must pass with zero errors.**

### Step 7: Clean Up

- [ ] Remove test code from Dashboard.tsx
- [ ] Ensure no console.log statements
- [ ] Verify imports are correct
- [ ] Check for unused imports

---

## 🚧 Constraints & Guidelines

### MUST Follow

**Architecture:**
- ✅ Functional components only (no class components)
- ✅ TypeScript strict mode (no `any` types)
- ✅ Props interfaces for every component
- ✅ Tailwind CSS only (no custom CSS files)
- ✅ Component composition (ThinkingBox is reusable)

**KISS Principles:**
- ✅ Simple props-based data flow
- ✅ No complex state management (props only)
- ✅ No refs unless absolutely necessary
- ❌ No animation libraries (CSS transitions if needed)
- ❌ No virtualization (only 3 lines per box)
- ❌ No external UI libraries (MUI, Ant Design, etc.)

**Code Quality:**
- Use TypeScript interfaces, not types
- Export functions with `export function`, not `export default`
- No inline styles
- No commented-out code
- Clear, descriptive variable names

### File Ownership

**You MUST create/modify:**
```
web-ui/src/
├── components/
│   ├── ThinkingBox.tsx       (CREATE)
│   ├── DualLayout.tsx        (CREATE)
│   └── TripleLayout.tsx      (CREATE)
└── types/
    └── index.ts              (CREATE)
```

**You MUST NOT modify:**
- Backend code (`python/`)
- Routing configuration
- Vite/build configuration
- Other task components

**Temporary modifications OK (remove before commit):**
- `Dashboard.tsx` for testing

---

## ❌ Anti-Patterns

### DON'T: Dynamic Tailwind Classes

**❌ Bad:**
```typescript
const borderColor = `border-${color}-700`; // Doesn't work!
return <div className={borderColor}>...</div>;
```

**✅ Good:**
```typescript
const borderClass = color === 'green' ? 'border-green-700' : 
                   color === 'blue' ? 'border-blue-700' : 
                   'border-gray-700';
return <div className={borderClass}>...</div>;
```

**Why:** Tailwind purges unused classes at build time. Dynamic strings aren't detected.

### DON'T: Over-Engineer with Refs

**❌ Bad:**
```typescript
const ref = useRef<HTMLDivElement>(null);
useEffect(() => {
  ref.current?.scrollTo({ top: 0, behavior: 'smooth' });
}, [lines]);
```

**✅ Good:**
```typescript
// Just render the data, no refs needed
return <div>{displayLines.map(...)}</div>;
```

**Why:** KISS principle. Refs add complexity. Simple rendering is sufficient.

### DON'T: Use UI Component Libraries

**❌ Bad:**
```typescript
import { Card, CardContent } from '@mui/material';
```

**✅ Good:**
```typescript
// Custom components with Tailwind
<div className="border rounded-lg p-4">...</div>
```

**Why:** Full control over styling, no extra dependencies, matches CLI aesthetic.

### DON'T: Forget Empty State Handling

**❌ Bad:**
```typescript
<div className="space-y-1">
  {lines.slice(-3).map(...)} // Collapses when empty!
</div>
```

**✅ Good:**
```typescript
<div className="space-y-1 min-h-[3rem]">
  {lines.slice(-3).map(...)}
</div>
```

**Why:** Empty boxes should maintain height for consistent layout.

---

## 🎯 Success Criteria

### Definition of Done

All of these must be true:

**Code:**
- [ ] `ThinkingBox.tsx` created with all required props
- [ ] `DualLayout.tsx` created with correct layout
- [ ] `TripleLayout.tsx` created with correct layout
- [ ] `types/index.ts` created with all interfaces
- [ ] All components export functions (not default exports)
- [ ] TypeScript compiles: `npx tsc --noEmit` passes

**Functionality:**
- [ ] Components render without errors
- [ ] Last 3 lines displayed per box
- [ ] Lines >91 chars truncate with "..."
- [ ] Empty arrays show empty (not collapsed) boxes
- [ ] Monospace font applied to thinking text
- [ ] Color coding correct: green (Writer A), blue (Writer B), gray (Judges)
- [ ] Icons correct: 💭 (writers), ⚖️ (judges)

**Responsive Design:**
- [ ] DualLayout: 2 columns on desktop, stacks on mobile
- [ ] TripleLayout: 3 columns on desktop, stacks on mobile
- [ ] No horizontal scroll on any screen size
- [ ] Consistent spacing between boxes

**Code Quality:**
- [ ] No TypeScript `any` types
- [ ] No unused imports
- [ ] No console.log statements
- [ ] No commented-out code
- [ ] Follows KISS principles (no over-engineering)

**Testing:**
- [ ] Manually tested with mock data
- [ ] All test cases pass (see Step 5)
- [ ] Test code removed before commit

---

## 🚨 CRITICAL: Git Workflow

### Before Starting

```bash
# Ensure you're on main and up to date
git checkout main
git pull origin main

# Create your feature branch
git checkout -b writer-[your-name]/03-thinking-boxes
```

### After Completing

**⚠️ MANDATORY - DO NOT SKIP ⚠️**

```bash
# Navigate to project root
cd /Users/jacob/dev/agent-cube

# Stage your changes
git add web-ui/src/components/ThinkingBox.tsx
git add web-ui/src/components/DualLayout.tsx
git add web-ui/src/components/TripleLayout.tsx
git add web-ui/src/types/index.ts

# Verify staged files
git status

# Commit with clear message
git commit -m "feat(ui): implement thinking box components for dual and triple layouts

- Add ThinkingBox component with props for title, lines, icon, color
- Add DualLayout for side-by-side writer visualization
- Add TripleLayout for three-judge panel
- Define TypeScript interfaces in types/index.ts
- Implement line truncation at 91 chars
- Add responsive grid layouts
- Match CLI aesthetic with monospace font and dark theme"

# Push to remote
git push origin writer-[your-name]/03-thinking-boxes

# Verify push succeeded
git log -1
git branch -vv
```

**If you don't commit and push, your work will NOT be reviewed!**

---

## 📋 Pre-Submission Checklist

Before marking this task complete, verify:

- [ ] All 4 files created in correct locations
- [ ] TypeScript compiles with no errors
- [ ] Manual testing completed with mock data
- [ ] Test code removed from Dashboard
- [ ] No console warnings in browser
- [ ] Responsive layout works (tested at different screen sizes)
- [ ] Colors and icons match specifications
- [ ] Line truncation works correctly
- [ ] Empty arrays handled gracefully
- [ ] Code follows KISS principles
- [ ] Git commit created with descriptive message
- [ ] Changes pushed to feature branch
- [ ] Branch name correct: `writer-[your-name]/03-thinking-boxes`

---

## 🆘 Troubleshooting

### Issue: Colors not applying

**Symptom:** Border colors stay gray regardless of prop

**Cause:** Dynamic Tailwind classes purged from bundle

**Fix:** Use static class names with conditional logic:
```typescript
const borderClass = color === 'green' ? 'border-green-700' : 'border-gray-700';
```

### Issue: TypeScript errors on imports

**Symptom:** "Cannot find module '../types'"

**Cause:** Types file not created or wrong path

**Fix:** 
1. Ensure `web-ui/src/types/index.ts` exists
2. Check import path: `import { ThinkingBoxProps } from '../types'`
3. Run `npx tsc --noEmit` to see exact error

### Issue: Boxes collapse when empty

**Symptom:** Layout jumps when lines array is empty

**Cause:** No minimum height set

**Fix:** Add `min-h-[3rem]` or similar to content div

### Issue: Icons not displaying

**Symptom:** Emoji icons show as boxes or question marks

**Cause:** Font doesn't support emoji

**Fix:** Ensure system emoji font is available, or use text alternatives temporarily

---

## 📞 Integration Notes

**For Task 05 (Task Detail View):**
- You will consume these components
- Props will come from SSE event data
- See `planning/web-ui.md` for SSE message format

**For Task 06 (Decisions UI):**
- May use TripleLayout to show judge thinking
- Integration details TBD

---

## 📚 Reference: CLI Behavior

The CLI shows thinking like this:

```
╭──────────────── Writer A ────────────────╮  ╭──────────────── Writer B ────────────────╮
│ 💭                                        │  │ 💭                                        │
│ Analyzing task requirements...           │  │ Reading existing code...                  │
│ Setting up project structure...          │  │ Understanding architecture...             │
│ Creating component files...              │  │ Planning implementation...                │
╰──────────────────────────────────────────╯  ╰──────────────────────────────────────────╯
```

Your React components should recreate this visual pattern with:
- Dark background
- Colored borders
- Icon + title header
- Last 3 lines of monospace text
- Truncation at 91 characters

---

## ✅ Final Reminder

**Your deliverables:**
1. Four new files in `web-ui/src/`
2. Working components that render correctly
3. TypeScript compilation with no errors
4. Git commit + push to feature branch

**Time estimate:** 3-4 hours

**Next task:** Task 04 will create the panel orchestration UI

**Questions?** Refer to:
- `planning/web-ui.md` for architecture
- `implementation/web-ui/phase-02/` for component specs
- CLI code in `python/cube/core/` for behavior

---

**Good luck! Keep it simple, follow KISS, and commit your work!** 🚀
