# Writer Prompt: Project Scaffold

**Task ID:** 01-project-scaffold  
**Writer Role:** You are a frontend developer implementing the foundation for the AgentCube Web UI  
**Time Estimate:** 2-3 hours  
**Date:** 2025-11-11

---

## 🎯 Your Mission

You will create a Vite + React + TypeScript + Tailwind CSS project that serves as the foundation for the AgentCube Web UI. This UI will display real-time agent thinking boxes, task dashboards, and decision panels - bringing the AgentCube CLI experience to the browser.

**This is a foundation task:** Everything you build here will be used by tasks 03, 04, 05, and 06. Get it right, keep it simple, and follow the planning doc exactly.

---

## 📖 Context & Background

### What is AgentCube?

AgentCube is a CLI tool for orchestrating AI agent workflows. Currently, it displays "thinking boxes" in the terminal showing real-time agent reasoning. The Web UI project aims to:
- Provide a browser-based alternative to CLI visualization
- Add multi-task dashboard capabilities
- Enable better decision review interfaces

### What You're Building

A **minimal, clean React project** with:
- Dark theme matching AgentCube aesthetic
- React Router for navigation (3 main routes)
- Tailwind CSS for styling (no custom CSS)
- TypeScript strict mode enabled
- Foundation for real-time SSE components (later tasks)

### Key Architectural Principles (from planning/web-ui.md)

1. **KISS - Keep It Simple, Stupid**
   - Minimal dependencies
   - No UI libraries (MUI, Chakra, etc.)
   - No state management libraries yet
   - Thin UI layer - logic stays in Python backend

2. **Real-time First**
   - Everything will stream via SSE (Server-Sent Events)
   - No polling, no complex WebSocket setup
   - Foundation must support live updates

3. **Local-Only Development Tool**
   - No auth needed (localhost only)
   - No database (uses JSON state files)
   - Desktop-first (mobile not critical)

---

## ✅ Requirements Checklist

### 1. Vite Project Initialization

**You must:**
- [ ] Initialize Vite with React + TypeScript template
- [ ] Install and configure Tailwind CSS
- [ ] Add React Router v6
- [ ] Enable TypeScript strict mode
- [ ] Verify dev server runs on `http://localhost:5173`

**Commands:**
```bash
npm create vite@latest web-ui -- --template react-ts
cd web-ui && npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
npm install react-router-dom
npm install -D @types/node
```

### 2. Directory Structure

**Create this exact structure:**
```
web-ui/
├── src/
│   ├── components/
│   │   └── Navigation.tsx
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── TaskDetail.tsx
│   │   └── Decisions.tsx
│   ├── hooks/
│   │   └── .gitkeep
│   ├── types/
│   │   └── index.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
└── README.md
```

### 3. Routing Configuration

**Define these routes in App.tsx:**
- `/` → Dashboard page (task list, status overview)
- `/tasks/:id` → TaskDetail page (live thinking boxes)
- `/tasks/:id/decisions` → Decisions page (judge votes, synthesis)

### 4. Dark Theme

**Configure Tailwind with AgentCube colors:**
```javascript
// tailwind.config.js
theme: {
  extend: {
    colors: {
      'cube-dark': '#1a1a1a',
      'cube-gray': '#2a2a2a',
      'cube-light': '#3a3a3a',
    }
  }
}
```

**Apply dark theme globally:**
- Background: `bg-cube-dark`
- Text: `text-white`
- Cards/sections: `bg-cube-gray`

### 5. Navigation Component

**Must have:**
- Links to: Dashboard, (eventually) Tasks
- Sticky top navigation
- Clean, minimal design
- Uses React Router's `<Link>` components

---

## 🔨 Implementation Steps

Follow these steps **in order:**

### Step 1: Initialize Vite Project
```bash
npm create vite@latest web-ui -- --template react-ts
cd web-ui
npm install
npm run dev  # Verify it starts
```

### Step 2: Install Dependencies
```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
npm install react-router-dom
npm install -D @types/node
```

### Step 3: Configure Tailwind

**Edit `tailwind.config.js`:**
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'cube-dark': '#1a1a1a',
        'cube-gray': '#2a2a2a',
        'cube-light': '#3a3a3a',
      }
    },
  },
  plugins: [],
}
```

**Edit `src/index.css`:**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

**Delete default Vite styles** (remove all other CSS in `index.css`).

### Step 4: TypeScript Configuration

**Edit `tsconfig.json`** - ensure strict mode:
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    // ... rest of Vite defaults
  }
}
```

### Step 5: Create Directory Structure
```bash
mkdir -p src/{components,pages,hooks,types}
touch src/hooks/.gitkeep
```

### Step 6: Create Page Components

**`src/pages/Dashboard.tsx`:**
```typescript
export default function Dashboard(): JSX.Element {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">AgentCube Dashboard</h1>
      <p className="text-gray-400">Task list coming soon...</p>
    </div>
  );
}
```

**`src/pages/TaskDetail.tsx`:**
```typescript
import { useParams } from 'react-router-dom';

export default function TaskDetail(): JSX.Element {
  const { id } = useParams<{ id: string }>();
  
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Task {id}</h1>
      <p className="text-gray-400">Thinking boxes coming soon...</p>
    </div>
  );
}
```

**`src/pages/Decisions.tsx`:**
```typescript
import { useParams } from 'react-router-dom';

export default function Decisions(): JSX.Element {
  const { id } = useParams<{ id: string }>();
  
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Decisions - Task {id}</h1>
      <p className="text-gray-400">Judge panel coming soon...</p>
    </div>
  );
}
```

### Step 7: Create Navigation Component

**`src/components/Navigation.tsx`:**
```typescript
import { Link } from 'react-router-dom';

export default function Navigation(): JSX.Element {
  return (
    <nav className="bg-cube-gray border-b border-cube-light">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center space-x-6">
          <h1 className="text-xl font-bold">AgentCube</h1>
          <div className="flex space-x-4">
            <Link 
              to="/" 
              className="text-gray-300 hover:text-white transition-colors"
            >
              Dashboard
            </Link>
            {/* More links as tasks develop */}
          </div>
        </div>
      </div>
    </nav>
  );
}
```

### Step 8: Set Up Router in App.tsx

**`src/App.tsx`:**
```typescript
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import Dashboard from './pages/Dashboard';
import TaskDetail from './pages/TaskDetail';
import Decisions from './pages/Decisions';

function App(): JSX.Element {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-cube-dark text-white">
        <Navigation />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/tasks/:id" element={<TaskDetail />} />
            <Route path="/tasks/:id/decisions" element={<Decisions />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
```

### Step 9: Create Types File

**`src/types/index.ts`:**
```typescript
// Shared TypeScript types
// More types will be added in future tasks

export interface Task {
  id: string;
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
}

export interface ThinkingBox {
  id: string;
  agent: string;
  lines: string[];
}
```

### Step 10: Verification

**Run these checks:**
```bash
# TypeScript compilation (no errors)
npx tsc --noEmit

# Build (no errors)
npm run build

# Dev server (should start on :5173)
npm run dev
```

**Manual testing:**
- Visit `http://localhost:5173` - should see Dashboard
- Click navigation links - routes should work
- Visit `/tasks/123` - should see TaskDetail
- Visit `/tasks/123/decisions` - should see Decisions
- Check browser console - no errors

### Step 11: Update README

**Create `web-ui/README.md`:**
```markdown
# AgentCube Web UI

React-based web interface for AgentCube agent orchestration.

## Setup

```bash
npm install
npm run dev  # Start dev server on :5173
```

## Stack

- Vite + React 18 + TypeScript (strict)
- React Router v6
- Tailwind CSS
- Server-Sent Events (SSE) for real-time updates

## Structure

- `src/components/` - Reusable UI components
- `src/pages/` - Route page components
- `src/hooks/` - Custom React hooks
- `src/types/` - TypeScript type definitions

## Development

- `npm run dev` - Start dev server
- `npm run build` - Production build
- `npm run preview` - Preview production build
```

---

## 🚫 Critical Anti-Patterns

### ❌ DON'T: Add Unnecessary Dependencies

**Bad:**
```json
{
  "dependencies": {
    "@mui/material": "^5.0.0",
    "styled-components": "^6.0.0",
    "framer-motion": "^10.0.0",
    "redux": "^4.0.0"
  }
}
```

**Why:** Over-engineering. Tailwind + React Router is sufficient.

### ❌ DON'T: Use Any Types

**Bad:**
```typescript
function handleData(data: any) {
  // TypeScript strict mode should prevent this
}
```

**Why:** Defeats purpose of TypeScript. Use proper types.

### ❌ DON'T: Write Custom CSS

**Bad:**
```css
/* custom.css */
.my-card {
  background: #2a2a2a;
  padding: 16px;
  border-radius: 8px;
}
```

**Why:** Use Tailwind utility classes instead: `bg-cube-gray p-4 rounded-lg`

### ❌ DON'T: Complex Vite Configuration

**Bad:**
```typescript
export default defineConfig({
  plugins: [react(), customPlugin(), anotherPlugin()],
  build: {
    rollupOptions: { /* complex config */ }
  }
});
```

**Why:** Defaults work fine. KISS principle.

---

## ✅ Success Criteria

Your implementation is complete when **ALL** of these are true:

- [ ] Vite project initialized with React + TypeScript template
- [ ] Tailwind CSS installed and configured with cube-dark theme
- [ ] React Router v6 configured with 3 routes working
- [ ] Directory structure matches planning doc exactly
- [ ] Navigation component renders and links work
- [ ] Dark theme applied (black background, white text)
- [ ] TypeScript strict mode enabled
- [ ] `npm run build` succeeds with no errors
- [ ] `npm run dev` starts server on port 5173
- [ ] `npx tsc --noEmit` shows no TypeScript errors
- [ ] Browser console shows no warnings or errors
- [ ] README.md created with setup instructions
- [ ] All files use TypeScript (no `.jsx` or `.js` in `src/`)
- [ ] No custom CSS files (only Tailwind utilities)
- [ ] No UI component libraries installed

---

## 🧪 Testing Checklist

**Before committing, verify:**

1. **TypeScript Compilation:**
   ```bash
   npx tsc --noEmit
   # Should output nothing (success)
   ```

2. **Build:**
   ```bash
   npm run build
   # Should complete without errors
   ```

3. **Dev Server:**
   ```bash
   npm run dev
   # Should start on http://localhost:5173
   ```

4. **Manual Navigation:**
   - [ ] Go to `/` - see Dashboard
   - [ ] Go to `/tasks/test-123` - see TaskDetail with ID
   - [ ] Go to `/tasks/test-123/decisions` - see Decisions
   - [ ] Click nav links - routes change correctly

5. **Visual Inspection:**
   - [ ] Background is dark (not white)
   - [ ] Text is readable (white/gray)
   - [ ] Navigation bar visible at top
   - [ ] No layout issues

6. **Console Check:**
   - [ ] Open browser DevTools
   - [ ] Console tab shows no errors (red)
   - [ ] Console tab shows no warnings (yellow)

---

## 🎓 Common Pitfalls

### Pitfall #1: Forgetting Tailwind Directives

**Symptom:** Tailwind classes don't work, styles not applied

**Fix:** Ensure `src/index.css` has:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### Pitfall #2: Port Conflicts

**Symptom:** `npm run dev` fails with EADDRINUSE

**Fix:** Vite uses 5173 by default. Backend will use 3030. These shouldn't conflict.

### Pitfall #3: TypeScript Path Resolution

**Symptom:** Import errors with `@/components`

**Fix:** Don't use path aliases yet. Use relative imports:
```typescript
import Navigation from './components/Navigation';  // ✅
import Navigation from '@/components/Navigation'; // ❌ (not configured)
```

### Pitfall #4: Missing Route Parameters

**Symptom:** `useParams()` returns undefined

**Fix:** Route must have `:id` parameter:
```typescript
<Route path="/tasks/:id" element={<TaskDetail />} />  // ✅
<Route path="/tasks/id" element={<TaskDetail />} />   // ❌
```

---

## 📝 Quality Standards

### Code Quality

- ✅ All functions have explicit return types
- ✅ No `any` types anywhere
- ✅ Components return `JSX.Element`
- ✅ Props interfaces defined for all components
- ✅ Imports organized (React first, then libraries, then local)

### Style Quality

- ✅ Consistent spacing (Tailwind classes)
- ✅ Dark theme throughout
- ✅ Readable text contrast
- ✅ Responsive container (`container mx-auto`)

### Architecture Quality

- ✅ Follows planning doc structure exactly
- ✅ Minimal dependencies
- ✅ No premature optimization
- ✅ Clear separation: pages vs components

---

## 🚨 CRITICAL: Git Commit & Push

After completing implementation and verifying **ALL** tests pass:

### Step 1: Stage Your Changes
```bash
cd web-ui
git add .
```

### Step 2: Commit with Descriptive Message
```bash
git commit -m "feat(ui): initialize Vite + React + TypeScript project scaffold

- Set up Vite with React 18 + TypeScript template
- Configure Tailwind CSS with AgentCube dark theme
- Add React Router v6 with 3 main routes
- Create directory structure (components, pages, hooks, types)
- Implement Navigation component
- Create placeholder Dashboard, TaskDetail, Decisions pages
- Enable TypeScript strict mode
- Add README with setup instructions"
```

### Step 3: Push to Remote
```bash
git push origin writer-[your-model-slug]/01-project-scaffold
```

### Step 4: Verify Push Succeeded
```bash
git status
# Should show: "Your branch is up to date with 'origin/...'"
```

### Step 5: Confirm on GitHub
- Visit the repository
- Check that your branch exists
- Verify files are pushed

---

## ⚠️ CRITICAL REMINDERS

1. **COMMIT AND PUSH ARE MANDATORY**
   - Uncommitted work will NOT be reviewed
   - Unpushed commits are invisible to reviewers
   - This is how multi-agent workflows sync

2. **TEST BEFORE COMMITTING**
   - Run ALL verification steps
   - Fix any TypeScript errors
   - Ensure dev server starts cleanly

3. **FOLLOW THE PLANNING DOC**
   - `planning/web-ui.md` is your source of truth
   - Don't deviate from specified stack
   - Don't add dependencies not listed

4. **KEEP IT SIMPLE**
   - You're building a foundation
   - Other tasks will add complexity
   - Your job: clean, minimal, working base

---

## 📚 Reference Links

**Official Docs:**
- [Vite Guide](https://vitejs.dev/guide/)
- [React Router v6](https://reactrouter.com/en/main)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [TypeScript React](https://react-typescript-cheatsheet.netlify.app/)

**Planning Docs (in this repo):**
- `planning/web-ui.md` - Complete architecture (GOLDEN SOURCE)
- `implementation/web-ui/tasks/01-project-scaffold.md` - This task details

---

## ✅ Final Checklist Before Push

Go through this checklist **ONE MORE TIME** before pushing:

- [ ] `npx tsc --noEmit` - no errors
- [ ] `npm run build` - succeeds
- [ ] `npm run dev` - starts on :5173
- [ ] Visit `/` - Dashboard renders
- [ ] Visit `/tasks/123` - TaskDetail renders with ID
- [ ] Visit `/tasks/123/decisions` - Decisions renders
- [ ] Navigation links work
- [ ] Console has no errors
- [ ] Dark theme applied everywhere
- [ ] README.md updated
- [ ] All changes committed
- [ ] Committed changes pushed to remote
- [ ] Verified push on GitHub

---

**You got this!** Keep it simple, follow the plan, test thoroughly, and **PUSH YOUR WORK**.

---

**Built with:** Agent Cube v1.0  
**Generated:** 2025-11-11  
**Task:** 01-project-scaffold  
**Writer Prompt Version:** 1.0
