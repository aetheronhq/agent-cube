# Task 01: Web UI Project Scaffold

**Goal:** Set up Vite + React + TypeScript foundation with TailwindCSS

## Context

First task in building Agent Cube Web UI. Creates the foundation that all other tasks build on.

## Requirements

### 1. Project Structure

Create `packages/web-ui/` with:
- Vite + React 18 + TypeScript
- TailwindCSS for styling
- React Router for navigation
- Prettier + ESLint config

### 2. Basic Pages

**Routes:**
- `/` - Dashboard (empty placeholder)
- `/task/:id` - Task detail (empty placeholder)
- `/settings` - Settings (empty placeholder)

### 3. Layout Component

```tsx
<Layout>
  <Header />  // Agent Cube logo, nav
  <main>{children}</main>
</Layout>
```

### 4. Build Pipeline

- `npm run dev` - Dev server on :5173
- `npm run build` - Production build
- `npm run preview` - Preview build
- Fast HMR, TypeScript checking

## Deliverables

- [ ] `packages/web-ui/` created with Vite
- [ ] React Router configured with 3 routes
- [ ] TailwindCSS working (test with colored div)
- [ ] Layout component with header/nav
- [ ] TypeScript strict mode, no errors
- [ ] ESLint + Prettier configured
- [ ] README with setup instructions
- [ ] `npm run dev` shows empty dashboard

## Architecture Constraints

**KISS Principles:**
- Use Vite defaults (don't over-configure)
- Minimal dependencies (no UI libraries yet)
- Standard React patterns (no state management yet)
- Tailwind utility classes (no custom CSS)

**Don't:**
- ❌ Add UI component libraries (MUI, Ant, etc.)
- ❌ Add complex state management
- ❌ Add backend yet
- ❌ Over-engineer routing

**Do:**
- ✅ Use Vite templates as starting point
- ✅ Keep package.json minimal
- ✅ Standard TypeScript config
- ✅ Simple, clean file structure

## Acceptance Criteria

1. `npm run dev` starts dev server
2. Navigate to `/` shows placeholder dashboard
3. TypeScript compiles with no errors
4. Hot reload works
5. Tailwind classes work
6. Clean, organized file structure
7. All dependencies in package.json

## Example Structure

```
packages/web-ui/
├── src/
│   ├── App.tsx
│   ├── main.tsx
│   ├── components/
│   │   ├── Layout.tsx
│   │   └── Header.tsx
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── TaskDetail.tsx
│   │   └── Settings.tsx
│   └── index.css
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── README.md
```

## Time Estimate

2-3 hours for experienced developer

## Dependencies

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "tailwindcss": "^3.4.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0"
  }
}
```

