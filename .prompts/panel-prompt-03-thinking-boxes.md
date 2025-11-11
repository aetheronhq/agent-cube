# Judge Panel: Review Thinking Boxes Component Implementations

You are a judge on a panel reviewing two implementations of the Thinking Box components for AgentCube's web UI.

---

## 📋 Task Overview

The writers were asked to create React components that visualize AI agent reasoning in real-time, mirroring the CLI's Rich Layout visualization:
- **ThinkingBox** - Reusable component for individual agent thinking
- **DualLayout** - Side-by-side layout for two writers
- **TripleLayout** - Three-column layout for judges
- TypeScript type definitions

**Time Budget:** 3-4 hours

**Reference Documents:**
- Writer prompt: `.prompts/writer-prompt-03-thinking-boxes.md`
- Architecture spec: `planning/web-ui.md`
- CLI reference: `python/cube/core/base_layout.py`, `dual_layout.py`, `triple_layout.py`

---

## 🔍 Review Process

### Step 1: Identify Writer Branches

```bash
# Find the writer branches for task 03-thinking-boxes
git branch -r | grep "03-thinking-boxes"
```

You should see two branches like:
- `origin/writer-codex/03-thinking-boxes`
- `origin/writer-sonnet/03-thinking-boxes`

### Step 2: Review Each Implementation

For each writer branch, examine:

```bash
# Checkout writer branch
git checkout writer-<model>/03-thinking-boxes

# Review files changed
git diff main --stat
git diff main --name-only

# Review the actual changes
git diff main web-ui/src/components/
git diff main web-ui/src/types/

# Check commit history
git log main..HEAD --oneline

# Examine files created
ls -la web-ui/src/components/
ls -la web-ui/src/types/
```

### Step 3: Test Functionality

For each implementation, test the components:

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
1. Add test code to Dashboard.tsx with mock data
2. Check that ThinkingBox renders with icon, title, and lines
3. Verify line truncation at 91 characters
4. Test empty arrays (boxes should not collapse)
5. Check DualLayout responsive behavior (resize browser)
6. Check TripleLayout responsive behavior
7. Verify colors: green (Writer A), blue (Writer B), gray (Judges)
8. Verify icons: 💭 (writers), ⚖️ (judges)
9. Check browser console for errors

---

## ✅ Evaluation Criteria

Score each criterion on a scale of 0-10, where:
- **0-3**: Does not meet requirements, significant issues
- **4-6**: Partially meets requirements, some issues
- **7-8**: Meets requirements, minor issues
- **9-10**: Exceeds requirements, exemplary

### 1. Correctness (Weight: 30%)

**Does the implementation meet all functional requirements?**

**ThinkingBox Component:**
- [ ] File exists: `web-ui/src/components/ThinkingBox.tsx`
- [ ] Props interface defined with required fields (title, lines, icon, color)
- [ ] Displays icon and title in header
- [ ] Shows last 3 lines from lines array
- [ ] Truncates lines longer than 91 characters with "..."
- [ ] Uses monospace font (`font-mono` or similar)
- [ ] Has minimum height to prevent collapse when empty
- [ ] Dark background with colored border
- [ ] Exported as named function (not default export)

**DualLayout Component:**
- [ ] File exists: `web-ui/src/components/DualLayout.tsx`
- [ ] Props interface with writerALines and writerBLines
- [ ] Renders two ThinkingBox instances side-by-side
- [ ] Writer A uses green color and 💭 icon
- [ ] Writer B uses blue color and 💭 icon
- [ ] Uses grid layout with 2 columns (desktop)
- [ ] Stacks on mobile (responsive)
- [ ] Exported as named function

**TripleLayout Component:**
- [ ] File exists: `web-ui/src/components/TripleLayout.tsx`
- [ ] Props interface with judge1Lines, judge2Lines, judge3Lines
- [ ] Renders three ThinkingBox instances
- [ ] All judges use ⚖️ icon and gray color
- [ ] Uses grid layout with 3 columns (desktop)
- [ ] Stacks on mobile (responsive)
- [ ] Exported as named function

**Types:**
- [ ] File exists: `web-ui/src/types/index.ts`
- [ ] Interfaces exported for component props
- [ ] No `any` types used

**Deductions:**
- Missing component: -10 points
- Missing required prop: -2 points per prop
- Wrong export format: -1 point per file
- Line truncation not working: -4 points
- Empty boxes collapse: -3 points
- Colors incorrect: -3 points
- Icons missing or wrong: -2 points
- Not responsive: -4 points

**Score: __/10**

### 2. Code Quality (Weight: 25%)

**Is the code clean, maintainable, and well-structured?**

**Evaluate:**
- TypeScript interfaces (not types) for props
- Type annotations on all functions
- Explicit return types (`JSX.Element` for components)
- No `any` types anywhere
- Clean, readable code structure
- Consistent naming conventions (PascalCase for components)
- Proper imports organization
- No unused imports or variables
- No console.log statements
- No commented-out code
- Descriptive variable names
- Component composition (ThinkingBox reused in layouts)

**Red flags:**
- Using `any` types: -3 points per occurrence
- Missing return type annotations: -2 points per function
- Inconsistent naming: -2 points
- Unused imports: -1 point per file
- Console.log statements: -1 point per occurrence
- Commented-out code: -2 points
- Poor variable names: -2 points

**Score: __/10**

### 3. Architecture Adherence (Weight: 20%)

**Does the implementation follow KISS principles and specifications?**

**Key requirements:**
- ✅ Functional components only (no class components)
- ✅ Props-based data flow (no complex state)
- ✅ Tailwind CSS only (no custom CSS files)
- ✅ ThinkingBox is reusable component
- ✅ Named exports (not default exports)
- ✅ Component composition pattern
- ❌ No refs (unless absolutely necessary)
- ❌ No animation libraries
- ❌ No external UI libraries (MUI, Ant Design, etc.)
- ❌ No state management libraries

**Evaluate:**
- Follows KISS principles
- Simple component structure
- Proper component composition
- Uses Tailwind utility classes correctly
- No over-engineering
- No unnecessary abstractions
- Matches CLI aesthetic
- File structure matches specification

**Critical violations:**
- Using UI component library: -8 points
- Custom CSS files instead of Tailwind: -5 points
- Unnecessary refs or state: -4 points
- Default exports instead of named: -2 points
- Over-engineered abstractions: -3 points
- Wrong directory structure: -3 points

**Score: __/10**

### 4. Styling & Visual Fidelity (Weight: 15%)

**Does the implementation match the CLI aesthetic and specifications?**

**Check:**
- Dark background (bg-gray-900 or similar)
- Colored borders (green for Writer A, blue for Writer B, gray for judges)
- Monospace font applied to thinking text
- Proper spacing and padding
- Rounded corners on boxes
- Minimum height prevents collapse
- Icons display correctly (💭 and ⚖️)
- Text contrast is readable
- Responsive grid layout works
- Equal width columns with gaps
- Consistent styling across components

**Visual check:**
- Boxes have dark background
- Text is readable (good contrast)
- Colors apply correctly
- Layout is clean and organized
- No visual glitches or overlaps
- Mobile layout stacks properly

**Deductions:**
- Wrong colors: -4 points
- No monospace font: -3 points
- Poor text contrast: -2 points
- Boxes collapse when empty: -4 points
- Inconsistent styling: -2 points
- Responsive layout broken: -4 points
- Icons missing or wrong: -2 points

**Score: __/10**

### 5. TypeScript Configuration (Weight: 5%)

**Is TypeScript properly configured and used?**

**Check:**
- TypeScript compilation succeeds: `npx tsc --noEmit`
- No TypeScript errors
- Interfaces defined for all props
- No `any` types
- Proper type imports
- Return types on all functions
- Type safety maintained throughout

**Deductions:**
- TypeScript compilation errors: -3 points per error
- Using `any` types: -2 points per occurrence
- Missing type definitions: -2 points
- No return types on functions: -1 point per function

**Score: __/10**

### 6. Testing & Verification (Weight: 5%)

**Has the implementation been properly tested?**

**Evidence of testing:**
- Components render without errors
- TypeScript compiles cleanly
- Responsive behavior verified
- Edge cases tested (empty arrays, long lines)
- Browser console clean (no errors or warnings)
- Commit messages indicate testing
- Changes pushed to remote branch
- Test code removed before commit

**Deductions:**
- Components don't render: -5 points
- TypeScript errors: -4 points
- Not tested with different screen sizes: -2 points
- Console errors: -2 points
- Test code left in files: -3 points
- Not pushed to remote: -5 points (CRITICAL)

**Score: __/10**

---

## 📊 Scoring Rubric

Calculate the weighted total score:

```
Total Score = (Correctness × 0.30) + 
              (Code Quality × 0.25) + 
              (Architecture × 0.20) + 
              (Styling × 0.15) + 
              (TypeScript Config × 0.05) + 
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

### ❌ Anti-Pattern 1: Dynamic Tailwind Classes

```typescript
// BAD: Dynamic class names don't work with Tailwind
const borderColor = `border-${color}-700`;
return <div className={borderColor}>...</div>;
```

**✅ Good:**
```typescript
const borderClass = color === 'green' ? 'border-green-700' : 
                   color === 'blue' ? 'border-blue-700' : 
                   'border-gray-700';
return <div className={borderClass}>...</div>;
```

**Impact:** REQUEST_CHANGES if colors don't work due to dynamic classes

### ❌ Anti-Pattern 2: Over-Engineering with Refs

```typescript
// BAD: Unnecessary refs and effects
const ref = useRef<HTMLDivElement>(null);
useEffect(() => {
  ref.current?.scrollTo({ top: 0, behavior: 'smooth' });
}, [lines]);

return <div ref={ref}>...</div>;
```

**✅ Good:**
```typescript
// Simple rendering, no refs needed
return <div>{displayLines.map(...)}</div>;
```

**Impact:** REQUEST_CHANGES - Violates KISS principle

### ❌ Anti-Pattern 3: Using UI Component Libraries

```typescript
// BAD: External UI library
import { Box, Typography } from '@mui/material';

return (
  <Box>
    <Typography>{title}</Typography>
  </Box>
);
```

**✅ Good:**
```typescript
// Custom components with Tailwind
return (
  <div className="border rounded-lg p-4">
    <h3 className="text-sm">{title}</h3>
  </div>
);
```

**Impact:** REQUEST_CHANGES - Must use Tailwind only

### ❌ Anti-Pattern 4: No Empty State Handling

```typescript
// BAD: Boxes collapse when empty
<div className="space-y-1">
  {lines.slice(-3).map((line, i) => (
    <p key={i}>{line}</p>
  ))}
</div>
```

**✅ Good:**
```typescript
// Maintains height when empty
<div className="space-y-1 min-h-[3rem]">
  {lines.slice(-3).map((line, i) => (
    <p key={i}>{line}</p>
  ))}
</div>
```

**Impact:** REQUEST_CHANGES - Layout jumps are jarring UX

### ❌ Anti-Pattern 5: Missing Type Definitions

```typescript
// BAD: No props interface
export function ThinkingBox({ title, lines, icon, color }) {
  return <div>...</div>;
}
```

**✅ Good:**
```typescript
interface ThinkingBoxProps {
  title: string;
  lines: string[];
  icon: string;
  color?: string;
}

export function ThinkingBox({ title, lines, icon, color = 'gray' }: ThinkingBoxProps): JSX.Element {
  return <div>...</div>;
}
```

**Impact:** REQUEST_CHANGES if >30% of props lack types

### ❌ Anti-Pattern 6: Custom CSS Files

```css
/* BAD: custom.css */
.thinking-box {
  background-color: #1a1a1a;
  border: 1px solid #444;
  padding: 16px;
}
```

**✅ Good:**
```typescript
// Tailwind utility classes
<div className="bg-gray-900 border border-gray-700 p-4">
```

**Impact:** REQUEST_CHANGES - Must use Tailwind only

### ❌ Anti-Pattern 7: Wrong Export Format

```typescript
// BAD: Default exports
export default function ThinkingBox() { ... }
```

**✅ Good:**
```typescript
// Named exports
export function ThinkingBox() { ... }
```

**Impact:** Minor deduction, but should be corrected

### ❌ Anti-Pattern 8: No Line Truncation

```typescript
// BAD: No truncation logic
{lines.slice(-3).map((line, i) => (
  <p key={i}>{line}</p>  // Long lines break layout!
))}
```

**✅ Good:**
```typescript
// Truncate at 91 characters
{lines.slice(-3).map((line, i) => (
  <p key={i} className="truncate">
    {line.length > 91 ? line.slice(0, 91) + '...' : line}
  </p>
))}
```

**Impact:** REQUEST_CHANGES - Critical for UX

---

## 📝 Decision Template

After reviewing both implementations, provide your decision using this exact JSON format:

```json
{
  "task_id": "03-thinking-boxes",
  "judge_id": "judge-<your-model>",
  "timestamp": "2025-11-11T<time>Z",
  "reviews": {
    "writer_a": {
      "branch": "writer-<model-a>/03-thinking-boxes",
      "scores": {
        "correctness": 0.0,
        "code_quality": 0.0,
        "architecture": 0.0,
        "styling": 0.0,
        "typescript_config": 0.0,
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
      "branch": "writer-<model-b>/03-thinking-boxes",
      "scores": {
        "correctness": 0.0,
        "code_quality": 0.0,
        "architecture": 0.0,
        "styling": 0.0,
        "typescript_config": 0.0,
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
- Test functionality (run dev server, add test data)
- Check for TypeScript errors
- Verify responsive behavior at different screen sizes
- Examine component structure and composition
- Test edge cases (empty arrays, long lines)

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
- Components render without errors
- TypeScript compiles cleanly
- Minor issues can be addressed in follow-up

**REQUEST_CHANGES:**
- Total score 4.0 - 6.9
- Some requirements not met
- Fixable issues identified
- Core structure present but needs improvement
- TypeScript errors or missing features

**REJECTED:**
- Total score < 4.0
- Critical requirements missing
- Fundamental architecture violations
- Components don't render or have major bugs
- Would require complete rewrite

---

## 🔗 Reference Files

Review these files to understand the requirements:

```bash
# Writer prompt
cat .prompts/writer-prompt-03-thinking-boxes.md

# Architecture spec
cat planning/web-ui.md

# CLI reference (for behavior)
cat python/cube/core/base_layout.py
cat python/cube/core/dual_layout.py
cat python/cube/core/triple_layout.py
```

---

## ✅ Judge Checklist

Before submitting your review:

- [ ] Reviewed both writer branches completely
- [ ] Checked all 4 expected files created (ThinkingBox, DualLayout, TripleLayout, types)
- [ ] Tested TypeScript compilation for both (`npx tsc --noEmit`)
- [ ] Manually tested components with mock data
- [ ] Verified line truncation at 91 characters
- [ ] Tested empty arrays (boxes don't collapse)
- [ ] Checked responsive behavior (desktop and mobile)
- [ ] Verified colors: green (Writer A), blue (Writer B), gray (Judges)
- [ ] Verified icons: 💭 (writers), ⚖️ (judges)
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
.prompts/decisions/judge-<your-model>-03-thinking-boxes-decision.json
```

Your review will be aggregated with other judges to make the final decision.

---

## 📋 Quick Reference: What Good Looks Like

### ✅ Excellent Implementation Checklist

**Files Created:**
- [ ] `web-ui/src/components/ThinkingBox.tsx`
- [ ] `web-ui/src/components/DualLayout.tsx`
- [ ] `web-ui/src/components/TripleLayout.tsx`
- [ ] `web-ui/src/types/index.ts`

**ThinkingBox Component:**
- [ ] Props: title, lines, icon, color (optional)
- [ ] Shows last 3 lines only
- [ ] Truncates at 91 characters
- [ ] Monospace font
- [ ] Dark background with colored border
- [ ] Minimum height (no collapse)
- [ ] Named export

**DualLayout Component:**
- [ ] Two ThinkingBox instances
- [ ] Grid layout (2 columns on desktop)
- [ ] Responsive (stacks on mobile)
- [ ] Writer A: green, 💭
- [ ] Writer B: blue, 💭

**TripleLayout Component:**
- [ ] Three ThinkingBox instances
- [ ] Grid layout (3 columns on desktop)
- [ ] Responsive (stacks on mobile)
- [ ] All judges: gray, ⚖️

**TypeScript:**
- [ ] Interfaces for all props
- [ ] No `any` types
- [ ] Explicit return types
- [ ] Compiles with no errors

**Code Quality:**
- [ ] Clean, readable code
- [ ] No unused imports
- [ ] No console.log statements
- [ ] Follows KISS principles
- [ ] Component composition pattern

**Testing:**
- [ ] Components render without errors
- [ ] Responsive behavior works
- [ ] Edge cases handled (empty arrays, long lines)
- [ ] Committed and pushed to remote

---

## 🔍 Comparison Focus Areas

When comparing the two implementations, pay special attention to:

1. **Component Design:**
   - Which approach is cleaner and more maintainable?
   - Better component composition?
   - More reusable architecture?

2. **TypeScript Usage:**
   - Better type definitions?
   - More type-safe?
   - Clearer interfaces?

3. **Styling Approach:**
   - Better use of Tailwind?
   - More consistent styling?
   - Better color handling?

4. **Edge Case Handling:**
   - Better handling of empty arrays?
   - Better line truncation?
   - More robust responsive behavior?

5. **Code Clarity:**
   - More readable code?
   - Better variable names?
   - Clearer structure?

---

**Remember:** Your role is to ensure quality, catch issues, and help select the best implementation. Be thorough, fair, and constructive in your review.

Good luck! 🎯
