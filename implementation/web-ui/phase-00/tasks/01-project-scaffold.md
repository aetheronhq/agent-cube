# Task 01: Project Scaffold

**Goal:** Set up Vite + React + TypeScript + Tailwind project with routing and basic structure.

**Time Estimate:** 2-3 hours

---

## 📖 **Context**

**What this builds on:**
- Fresh React project setup
- Foundation for all other UI tasks
- No dependencies on other tasks

**Planning docs (Golden Source):**
- `planning/web-ui.md` - Frontend stack, file structure, component hierarchy

---

## ✅ **Requirements**

### **1. Vite Project Setup**

**Deliverable:**
- Initialize Vite project with React + TypeScript template
- Configure Tailwind CSS
- Set up strict TypeScript configuration
- Add React Router for navigation

**Acceptance criteria:**
- [ ] `npm create vite@latest web-ui -- --template react-ts` executed
- [ ] Tailwind CSS installed and configured
- [ ] TypeScript strict mode enabled
- [ ] React Router v6 installed and basic routes defined
- [ ] Dev server runs on `http://localhost:5173`

### **2. Directory Structure**

**Deliverable:**
- Create component, page, hook, and type directories
- Set up basic layout components
- Create placeholder pages

**Acceptance criteria:**
- [ ] `src/components/` directory with placeholder files
- [ ] `src/pages/` directory with Dashboard, TaskDetail, Decisions pages
- [ ] `src/hooks/` directory created
- [ ] `src/types/` directory with `index.ts` for shared types
- [ ] `App.tsx` with router configuration

### **3. Basic UI Shell**

**Deliverable:**
- Top navigation bar
- Route-based page rendering
- Dark theme (AgentCube aesthetic)

**Acceptance criteria:**
- [ ] Navigation bar with links to Dashboard, Tasks
- [ ] Routes render correct page components
- [ ] Dark theme applied (gray/blue palette)
- [ ] Responsive layout (works on laptop screens)

---

## 📝 **Implementation Steps**

**Suggested order:**

1. **Initialize Vite project**
   - [ ] Run `npm create vite@latest web-ui -- --template react-ts`
   - [ ] `cd web-ui && npm install`
   - [ ] Verify dev server: `npm run dev`

2. **Install dependencies**
   - [ ] `npm install -D tailwindcss postcss autoprefixer`
   - [ ] `npx tailwindcss init -p`
   - [ ] `npm install react-router-dom`
   - [ ] `npm install -D @types/node` (for path aliases)

3. **Configure Tailwind**
   - [ ] Update `tailwind.config.js` with content paths
   - [ ] Add Tailwind directives to `src/index.css`
   - [ ] Remove default Vite styles

4. **TypeScript configuration**
   - [ ] Enable strict mode in `tsconfig.json`
   - [ ] Configure path aliases (optional)
   - [ ] Add `types/` to include

5. **Create directory structure**
   - [ ] `mkdir -p src/{components,pages,hooks,types}`
   - [ ] Create placeholder `index.ts` files

6. **Set up routing**
   - [ ] Create `App.tsx` with BrowserRouter
   - [ ] Define routes: `/`, `/tasks/:id`, `/tasks/:id/decisions`
   - [ ] Create page components: `Dashboard.tsx`, `TaskDetail.tsx`, `Decisions.tsx`

7. **Basic layout**
   - [ ] Create `components/Navigation.tsx`
   - [ ] Add dark theme colors to Tailwind config
   - [ ] Style navigation bar

8. **Verify**
   - [ ] Run `npm run build` (no errors)
   - [ ] Run `npm run dev` and visit all routes
   - [ ] Check TypeScript compilation: `npx tsc --noEmit`

9. **Finalize**
   - [ ] Update `README.md` with setup instructions
   - [ ] Commit changes
   - [ ] Push to branch

---

## 🏗️ **Architecture Constraints**

### **Must Follow**

**Planning docs:**
- Use exact stack from `planning/web-ui.md`: Vite + React 18+ + TypeScript + Tailwind
- Follow file structure defined in planning doc

**Technical constraints:**
- TypeScript strict mode (no `any` types)
- Explicit return types on functions
- Tailwind for all styling (no custom CSS except theme)

**KISS Principles:**
- ✅ Use Vite defaults (no custom config unless needed)
- ✅ Use React Router defaults (no complex routing logic)
- ✅ Minimal dependencies (no UI libraries like MUI/Chakra)
- ❌ No state management libraries yet (just React Router)

---

## 🚫 **Anti-Patterns**

### **❌ DON'T: Add Unnecessary Dependencies**

```json
// Bad: Over-engineering with UI library
{
  "dependencies": {
    "@mui/material": "^5.0.0",
    "styled-components": "^6.0.0",
    "framer-motion": "^10.0.0"
  }
}
```

**Instead:**
```json
// Good: Minimal deps
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0"
  }
}
```

### **❌ DON'T: Complex Vite Configuration**

```typescript
// Bad: Unnecessary complexity
export default defineConfig({
  plugins: [react(), customPlugin(), anotherPlugin()],
  build: { /* complex custom config */ }
});
```

**Instead:**
```typescript
// Good: Use defaults
export default defineConfig({
  plugins: [react()]
});
```

---

## 📂 **Owned Paths**

**This task owns:**
```
web-ui/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
├── index.html
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── index.css
│   ├── components/
│   │   └── Navigation.tsx
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── TaskDetail.tsx
│   │   └── Decisions.tsx
│   ├── hooks/
│   │   └── .gitkeep
│   └── types/
│       └── index.ts
└── README.md
```

**Must NOT modify:**
- Python code (separate task)
- Other implementation directories

**Integration:**
- Provides foundation for tasks 03, 04, 05, 06
- Task 02 (backend) runs independently

---

## 🧪 **Testing Requirements**

**Test coverage:**
- [ ] Dev server starts without errors
- [ ] Build completes without TypeScript errors
- [ ] All routes navigate correctly
- [ ] Navigation links work

**Manual testing:**
- Navigate to each route and verify page renders
- Check browser console for errors
- Verify dark theme applied

---

## ✅ **Acceptance Criteria**

**Definition of Done:**

- [ ] Vite project initialized with React + TypeScript
- [ ] Tailwind CSS configured and working
- [ ] React Router configured with 3 routes
- [ ] Directory structure created per planning doc
- [ ] Navigation component renders
- [ ] Dark theme applied
- [ ] TypeScript strict mode enabled
- [ ] `npm run build` succeeds
- [ ] `npm run dev` starts server on port 5173
- [ ] No TypeScript errors: `npx tsc --noEmit`
- [ ] README.md updated with setup instructions
- [ ] Changes committed and pushed

**Quality gates:**
- [ ] Follows KISS principles (minimal deps)
- [ ] No custom CSS (Tailwind only)
- [ ] Clean console (no warnings/errors)

---

## 🔗 **Integration Points**

**Dependencies (requires these first):**
- None (foundation task)

**Dependents (these will use this):**
- Task 03: Thinking boxes (builds on component structure)
- Task 04: Dashboard (uses page structure)
- Task 05: Task detail (uses routing)
- Task 06: Decisions UI (uses routing)

**Integrator task:**
- None (this is self-contained)

---

## 📊 **Examples**

### **Tailwind Config**

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

### **Basic App.tsx**

```typescript
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import Dashboard from './pages/Dashboard';
import TaskDetail from './pages/TaskDetail';
import Decisions from './pages/Decisions';

function App() {
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

---

## 🎓 **Common Pitfalls**

**Watch out for:**
- ⚠️ Forgetting to add `@tailwind` directives to CSS
- ⚠️ TypeScript path resolution issues (use `tsconfig.json` paths)
- ⚠️ Port conflicts (Vite defaults to 5173, FastAPI will use 3030)

**If you see [blank screen], it means [routing not configured] - fix by [checking App.tsx routes]**

---

## 📝 **Notes**

**Additional context:**
- This is a development tool (local-only, no auth needed)
- Target audience: developers using AgentCube CLI
- Desktop-first (responsive not critical, but nice to have)

**Nice-to-haves (not required):**
- Hot module reload confirmation
- TypeScript path aliases for cleaner imports

---

**FINAL STEPS - CRITICAL:**

After completing implementation and verifying all tests pass:

```bash
# Stage your changes
git add web-ui/

# Commit with descriptive message
git commit -m "feat(ui): initialize Vite + React + TypeScript project scaffold"

# Push to remote
git push origin writer-[your-model-slug]/01-project-scaffold

# Verify push succeeded
git status  # Should show "up to date with origin"
```

**⚠️ IMPORTANT:** Uncommitted or unpushed changes will NOT be reviewed!

---

**Built with:** Agent Cube v1.0
**Template version:** 1.0
**Last updated:** 2025-11-11

