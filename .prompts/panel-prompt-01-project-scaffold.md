# Judge Panel: Review Project Scaffold Implementations

You are a judge on a panel reviewing two implementations of the Vite + React + TypeScript project scaffold for AgentCube's web UI.

---

## 📋 Task Overview

The writers were asked to create a minimal React project foundation that:
- Initializes Vite with React + TypeScript template
- Configures Tailwind CSS with AgentCube dark theme
- Sets up React Router with 3 main routes
- Creates directory structure (components, pages, hooks, types)
- Implements Navigation component and placeholder pages
- Enables TypeScript strict mode
- Follows KISS principles (no unnecessary dependencies)

**Time Budget:** 2-3 hours

**Reference Documents:**
- Task specification: `implementation/web-ui/tasks/01-project-scaffold.md`
- Writer prompt: `.prompts/writer-prompt-01-project-scaffold.md`
- Architecture spec: `planning/web-ui.md`

---

## 🔍 Review Process

### Step 1: Identify Writer Branches

```bash
# Find the writer branches for task 01-project-scaffold
git branch -r | grep "01-project-scaffold"
```

You should see two branches like:
- `origin/writer-<model-a>/01-project-scaffold`
- `origin/writer-<model-b>/01-project-scaffold`

### Step 2: Review Each Implementation

For each writer branch, examine:

```bash
# Checkout writer branch
git checkout writer-<model>/01-project-scaffold

# Review files changed
git diff main --stat
git diff main --name-only

# Review the actual changes
git diff main web-ui/

# Check commit history
git log main..HEAD --oneline

# Examine directory structure
ls -la web-ui/
ls -la web-ui/src/
```

### Step 3: Test Functionality

For each implementation, test the project:

```bash
cd web-ui

# Install dependencies
npm install

# Check TypeScript compilation
npx tsc --noEmit

# Build the project
npm run build

# Start dev server
npm run dev
# Should start on http://localhost:5173
```

**Manual Testing:**
1. Visit `http://localhost:5173` - should see Dashboard
2. Visit `http://localhost:5173/tasks/test-123` - should see TaskDetail
3. Visit `http://localhost:5173/tasks/test-123/decisions` - should see Decisions
4. Click navigation links - routes should work
5. Check browser console - no errors or warnings
6. Verify dark theme applied (not white background)

---

## ✅ Evaluation Criteria

Score each criterion on a scale of 0-10, where:
- **0-3**: Does not meet requirements, significant issues
- **4-6**: Partially meets requirements, some issues
- **7-8**: Meets requirements, minor issues
- **9-10**: Exceeds requirements, exemplary

### 1. Correctness (Weight: 30%)

**Does the implementation meet all functional requirements?**

- [ ] Vite project created with `react-ts` template
- [ ] Tailwind CSS installed and configured
- [ ] React Router v6 installed and configured
- [ ] TypeScript strict mode enabled in `tsconfig.json`
- [ ] Directory structure matches specification:
  - [ ] `src/components/` with `Navigation.tsx`
  - [ ] `src/pages/` with `Dashboard.tsx`, `TaskDetail.tsx`, `Decisions.tsx`
  - [ ] `src/hooks/` directory created
  - [ ] `src/types/` with `index.ts`
- [ ] Three routes configured correctly:
  - [ ] `/` → Dashboard
  - [ ] `/tasks/:id` → TaskDetail
  - [ ] `/tasks/:id/decisions` → Decisions
- [ ] Navigation component renders with links
- [ ] Dark theme applied (AgentCube colors)
- [ ] Dev server runs on port 5173
- [ ] README.md with setup instructions
- [ ] Package.json has correct dependencies (minimal)

**Deductions:**
- Missing route: -3 points per route
- Missing page component: -2 points per component
- Wrong directory structure: -3 points
- TypeScript strict mode not enabled: -4 points
- Tailwind not configured: -5 points
- Dev server doesn't start: -10 points

**Score: __/10**

### 2. Code Quality (Weight: 25%)

**Is the code clean, maintainable, and well-structured?**

**Evaluate:**
- TypeScript type annotations on all functions
- Explicit return types (`JSX.Element` for components)
- No `any` types anywhere
- Props interfaces defined for components with props
- Clean, readable code
- Consistent code style
- Proper imports organization
- No unused imports or variables
- Component naming conventions (PascalCase)

**Red flags:**
- Using `any` types: -3 points per occurrence
- Missing return type annotations: -2 points
- No TypeScript errors in compilation: critical
- Inconsistent naming: -2 points
- Messy imports: -1 point

**Score: __/10**

### 3. Architecture Adherence (Weight: 20%)

**Does the implementation follow KISS principles and planning doc specifications?**

**Key requirements:**
- ✅ Minimal dependencies (react, react-dom, react-router-dom)
- ✅ Tailwind CSS only (no custom CSS files)
- ✅ No UI libraries (MUI, Chakra, etc.)
- ✅ No state management libraries
- ✅ Exact directory structure from planning doc
- ✅ Dark theme using Tailwind custom colors
- ❌ No unnecessary Vite configuration
- ❌ No additional plugins
- ❌ No CSS-in-JS libraries

**Evaluate:**
- Follows planning doc structure exactly
- Minimal dependencies (check `package.json`)
- No over-engineering
- Uses Vite defaults
- Tailwind utility classes only
- No custom CSS files

**Critical violations:**
- Adding UI library (MUI, Chakra): -8 points
- Custom CSS instead of Tailwind: -5 points
- State management library: -5 points
- Wrong directory structure: -4 points
- Complex Vite configuration: -3 points

**Score: __/10**

### 4. Styling & Theme (Weight: 15%)

**Is the dark theme properly implemented with Tailwind?**

**Check:**
- Tailwind config has custom cube colors:
  - `cube-dark: #1a1a1a`
  - `cube-gray: #2a2a2a`
  - `cube-light: #3a3a3a`
- Dark background applied (`bg-cube-dark`)
- White/gray text for readability
- Navigation bar styled appropriately
- No custom CSS files (only Tailwind utilities)
- Theme applied consistently across pages
- Responsive container (`container mx-auto`)

**Visual check:**
- Background is dark (not white)
- Text is readable
- Navigation bar visible and styled
- No layout issues

**Deductions:**
- No custom Tailwind colors: -4 points
- White background (not dark): -5 points
- Custom CSS files used: -4 points
- Poor text contrast: -2 points
- Inconsistent styling: -2 points

**Score: __/10**

### 5. TypeScript Configuration (Weight: 5%)

**Is TypeScript properly configured with strict mode?**

**Check:**
- `tsconfig.json` has `"strict": true`
- Compilation succeeds: `npx tsc --noEmit`
- No TypeScript errors
- Proper type imports from react-router-dom
- Type definitions present

**Deductions:**
- Strict mode not enabled: -5 points
- TypeScript errors on compilation: -3 points per error
- Missing type definitions: -2 points

**Score: __/10**

### 6. Testing & Verification (Weight: 5%)

**Has the implementation been properly tested?**

**Evidence of testing:**
- `npm run build` succeeds
- `npx tsc --noEmit` succeeds
- `npm run dev` starts cleanly
- All routes accessible and working
- Browser console clean (no errors)
- Commit messages indicate testing
- Changes pushed to remote branch

**Deductions:**
- Build fails: -5 points
- TypeScript compilation errors: -4 points
- Routes don't work: -3 points
- Console errors: -2 points
- No evidence of testing: -3 points
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

### ❌ Anti-Pattern 1: Over-Engineering with Dependencies

```json
// BAD: Adding unnecessary libraries
{
  "dependencies": {
    "react": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "@mui/material": "^5.0.0",        // ❌ Not needed
    "styled-components": "^6.0.0",    // ❌ Use Tailwind
    "redux": "^4.0.0",                // ❌ No state management yet
    "framer-motion": "^10.0.0"        // ❌ Not required
  }
}
```

**Impact:** REQUEST_CHANGES if UI library added, REJECTED if multiple unnecessary deps

### ❌ Anti-Pattern 2: Custom CSS Instead of Tailwind

```css
/* BAD: custom.css or similar */
.navigation {
  background-color: #2a2a2a;
  padding: 16px;
}

.dark-theme {
  background: #1a1a1a;
}
```

**Impact:** REQUEST_CHANGES - Must use Tailwind utilities only

### ❌ Anti-Pattern 3: Missing Type Annotations

```typescript
// BAD: No return types, using any
function Navigation() {  // ❌ No return type
  return <nav>...</nav>;
}

function handleClick(data: any) {  // ❌ any type
  console.log(data);
}
```

**Impact:** REQUEST_CHANGES if >20% of functions lack types

### ❌ Anti-Pattern 4: Wrong Directory Structure

```
// BAD: Not following planning doc
src/
├── Components/           // ❌ Wrong case
├── Pages/               // ❌ Wrong case
├── utils/               // ❌ Not specified
├── services/            // ❌ Not needed yet
└── lib/                 // ❌ Not needed yet
```

**Impact:** REQUEST_CHANGES - Must match spec exactly

### ❌ Anti-Pattern 5: No Dark Theme or Wrong Colors

```typescript
// BAD: No custom colors, using default Tailwind
<div className="bg-white text-black">  // ❌ Wrong theme
```

**Impact:** REQUEST_CHANGES - Must implement AgentCube dark theme

### ❌ Anti-Pattern 6: Complex Vite Configuration

```typescript
// BAD: Over-configured vite.config.ts
export default defineConfig({
  plugins: [
    react(),
    customPlugin(),      // ❌ Unnecessary
    visualizer(),        // ❌ Not needed
  ],
  build: {
    rollupOptions: {     // ❌ Complex config
      // ... lots of config
    }
  },
  resolve: {
    alias: {             // ❌ Not required yet
      // ...
    }
  }
});
```

**Impact:** REQUEST_CHANGES - Keep it simple, use Vite defaults

---

## 📝 Decision Template

After reviewing both implementations, provide your decision using this exact JSON format:

```json
{
  "task_id": "01-project-scaffold",
  "judge_id": "judge-<your-model>",
  "timestamp": "2025-11-11T<time>Z",
  "reviews": {
    "writer_a": {
      "branch": "writer-<model-a>/01-project-scaffold",
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
      "branch": "writer-<model-b>/01-project-scaffold",
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
- Test functionality (run dev server, test routes)
- Check for TypeScript errors
- Verify directory structure matches spec
- Examine package.json for dependencies

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
- Project runs without errors
- Minor issues can be addressed in follow-up

**REQUEST_CHANGES:**
- Total score 4.0 - 6.9
- Some requirements not met
- Fixable issues identified
- Core structure present but needs improvement
- TypeScript errors or build issues

**REJECTED:**
- Total score < 4.0
- Critical requirements missing
- Fundamental architecture violations
- Project doesn't run or build
- Would require complete rewrite

---

## 🔗 Reference Files

Review these files to understand the requirements:

```bash
# Task specification
cat implementation/web-ui/tasks/01-project-scaffold.md

# Writer prompt
cat .prompts/writer-prompt-01-project-scaffold.md

# Architecture spec
cat planning/web-ui.md
```

---

## ✅ Judge Checklist

Before submitting your review:

- [ ] Reviewed both writer branches completely
- [ ] Tested both implementations (ran dev server)
- [ ] Checked TypeScript compilation for both
- [ ] Verified build succeeds for both
- [ ] Tested all routes in browser
- [ ] Examined package.json dependencies
- [ ] Verified directory structure
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
.sessions/<task-id>/decisions/judge-<your-model>.json
```

Your review will be aggregated with other judges to make the final decision.

---

## 📋 Quick Reference: What Good Looks Like

### ✅ Excellent Implementation Checklist

**Structure:**
- [ ] Exact directory structure from spec
- [ ] All required files present
- [ ] No extra/unnecessary files

**Dependencies (package.json):**
- [ ] react, react-dom (from Vite template)
- [ ] react-router-dom
- [ ] Tailwind CSS dev dependencies
- [ ] No UI libraries
- [ ] No state management libs

**TypeScript:**
- [ ] Strict mode enabled
- [ ] All functions typed
- [ ] No `any` types
- [ ] Explicit return types

**Styling:**
- [ ] Custom Tailwind colors defined
- [ ] Dark theme applied consistently
- [ ] No custom CSS files
- [ ] Readable text contrast

**Routing:**
- [ ] 3 routes configured correctly
- [ ] Navigation component works
- [ ] useParams typed properly
- [ ] Links use React Router

**Quality:**
- [ ] `npm run build` succeeds
- [ ] `npx tsc --noEmit` succeeds
- [ ] No console errors
- [ ] Clean, readable code
- [ ] Committed and pushed

---

**Remember:** Your role is to ensure quality, catch issues, and help select the best implementation. Be thorough, fair, and constructive in your review.

Good luck! 🎯
