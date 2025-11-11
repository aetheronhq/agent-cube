# Prompt: Plan Web UI for Agent Cube

**Give this to another Cursor agent to record the planning process**

---

You are helping plan a new feature for Agent Cube: A lightweight React web UI.

## Your Task

Read the existing Agent Cube codebase and create:

1. **Architecture Planning Document**
   - File: `planning/web-ui.md`
   - What: Complete technical architecture
   - Include: Component design, API endpoints, real-time streaming strategy
   - Based on: Existing terminal implementation (dual/triple thinking boxes, phase tracking)

2. **Task Breakdown**
   - Files: `implementation/web-ui/tasks/01-XX.md` through `06-XX.md`
   - What: 6 small, comparable tasks for dual-writer workflow
   - Size: 2-6 hours each (perfect for agent comparison)
   - Requirements: Clear scope, owned paths, acceptance criteria

## Context

**Existing Implementation:**
- Python CLI with Rich Layout thinking boxes
- Autonomous workflow (10 phases)
- Real-time agent streaming
- State management with JSON files
- Decision aggregation

**Goal:** Web version of this UX for managing multiple workflows in parallel

## Requirements for Planning Doc

**Must include:**
- Technical stack recommendation (React + Vite + TypeScript)
- Backend approach (FastAPI wrapping Python modules vs CLI subprocess)
- Real-time strategy (SSE vs WebSocket)
- Component architecture (thinking boxes, output stream, decisions UI)
- API endpoints needed
- File structure

**Format:**
- Architecture-first (not feature-first)
- Show examples (code snippets)
- List anti-patterns
- Integration points with existing Python code

## Requirements for Task Breakdown

**Create 6 tasks:**

**Suggested split:**
1. Project scaffold (Vite + React + Tailwind setup)
2. Backend API (FastAPI server)
3. Thinking boxes component (dual/triple layouts)
4. Dashboard (multi-workflow management)
5. Task detail view (live monitoring)
6. Decisions UI (judge decisions visualization)

**Each task file must have:**
- Clear goal (one sentence)
- Context (what it builds on)
- Requirements (specific, testable)
- Owned paths (which files)
- Acceptance criteria (definition of done)
- Time estimate (2-6 hours)
- KISS constraints

**Reference for format:**
- Look at existing v2 tasks: `aetheron-connect-v2/implementation/phase-*/tasks/*.md`
- Follow same structure
- Same level of detail

## Constraints

**KISS Principles:**
- Simplest solution that works
- No over-engineering
- Use established libraries (don't reinvent)
- Minimal dependencies

**Integration:**
- Must use existing `cube-py` Python modules
- Don't duplicate logic
- Thin UI layer over robust backend

**Parallel-safe:**
- Each task should be independently buildable
- Clear file ownership
- No overlapping edits

## Output

Generate files in:
- `planning/web-ui.md` (architecture doc)
- `implementation/web-ui/tasks/01-project-scaffold.md`
- `implementation/web-ui/tasks/02-backend-api.md`
- `implementation/web-ui/tasks/03-thinking-boxes.md`
- `implementation/web-ui/tasks/04-dashboard.md`
- `implementation/web-ui/tasks/05-task-detail-view.md`
- `implementation/web-ui/tasks/06-decisions-ui.md`

**Commit and push when complete!**

