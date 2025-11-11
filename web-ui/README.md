# AgentCube Web UI

React-based web interface for AgentCube agent orchestration with real-time thinking box visualization.

## 🚀 Setup

```bash
# Install dependencies
npm install

# Start development server (runs on http://localhost:5173)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 📦 Tech Stack

- **Vite** - Fast build tool and dev server
- **React 19** - UI library
- **TypeScript** (strict mode) - Type safety
- **React Router v7** - Client-side routing
- **Tailwind CSS** - Utility-first styling
- **Server-Sent Events (SSE)** - Real-time streaming

## 📁 Project Structure

```
src/
├── components/        # Reusable UI components
│   ├── Navigation.tsx       # Top navigation bar
│   ├── TaskCard.tsx         # Task list item
│   ├── ThinkingBox.tsx      # Individual thinking box
│   ├── DualLayout.tsx       # Writer A + Writer B layout
│   ├── TripleLayout.tsx     # Judge panel layout
│   ├── OutputStream.tsx     # Tool call stream
│   ├── JudgeVote.tsx        # Judge vote display
│   └── SynthesisView.tsx    # Synthesis results
├── pages/            # Route page components
│   ├── Dashboard.tsx        # Task list view
│   ├── TaskDetail.tsx       # Live task monitoring
│   └── Decisions.tsx        # Judge decisions view
├── hooks/            # Custom React hooks
│   └── useSSE.ts            # SSE connection management
├── types/            # TypeScript type definitions
│   └── index.ts             # Shared types
├── App.tsx           # Router configuration
├── main.tsx          # React entry point
└── index.css         # Tailwind directives
```

## 🎨 Routes

| Route | Component | Description |
|-------|-----------|-------------|
| `/` | Dashboard | List all tasks with status overview |
| `/tasks/:id` | TaskDetail | Live monitoring with thinking boxes |
| `/tasks/:id/decisions` | Decisions | Judge votes and synthesis results |

## 🧪 Testing

```bash
# Type check (no emit)
npx tsc --noEmit

# Build (includes type checking)
npm run build

# Lint
npm run lint
```

## 🎯 Features

- **Real-time Updates** - SSE streams thinking and output in real-time
- **Dark Theme** - AgentCube aesthetic with custom color palette
- **Responsive Layout** - Works on laptop screens and larger
- **TypeScript Strict** - Full type safety with explicit return types
- **Zero Dependencies** - No UI libraries, minimal bundle size

## 🔧 Configuration

### Environment Variables

Create `.env.local` (optional):

```env
VITE_API_BASE_URL=http://localhost:3030/api
```

### Tailwind Theme

Custom colors defined in `tailwind.config.js`:

- `cube-dark`: #1a1a1a (main background)
- `cube-gray`: #2a2a2a (secondary background)
- `cube-light`: #3a3a3a (borders/highlights)

## 🚀 Development

The dev server supports:
- Hot Module Reload (HMR)
- Fast refresh for React components
- TypeScript type checking
- Tailwind CSS with JIT compilation

Default ports:
- Frontend (Vite): `http://localhost:5173`
- Backend (FastAPI): `http://localhost:3030`

## 📚 Architecture

The UI is a thin display layer that:
- Connects to FastAPI backend via REST + SSE
- Uses existing AgentCube state files (no database)
- Mirrors CLI thinking box UX in the browser
- Runs locally on `localhost` (development tool)

See `planning/web-ui.md` for complete architecture documentation.
