# AgentCube Web UI

React-based web interface for AgentCube agent orchestration.

## Getting Started

```bash
npm install
npm run dev
```

The dev server runs on `http://localhost:5173` with hot module reload.

## Verification

Run the standard checks before opening a PR:

```bash
npm run build    # Type-check + production bundle
npx tsc --noEmit # Optional: strict type checking only
```

## Tech Stack

- Vite + React 19 + TypeScript (strict mode)
- React Router v6
- Tailwind CSS for styling
- Server-Sent Events (SSE) plumbing for live updates

## Project Structure

- `src/main.tsx` – App bootstrap
- `src/App.tsx` – Router configuration
- `src/components/` – Shared UI elements (navigation, layouts, etc.)
- `src/pages/` – Route-level components (Dashboard, Task Detail, Decisions)
- `src/hooks/` – Custom hooks (`useSSE`)
- `src/types/` – Shared TypeScript definitions
