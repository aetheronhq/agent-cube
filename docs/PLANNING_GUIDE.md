# Agent Cube Planning Guide

**How to go from idea to autonomous implementation**

Based on Aetheron Connect v2: 20+ features, 10 phases, ~10k LOC in 11 days.

---

## 🎯 **The Process: Idea → Planning → Tasks → Implementation**

### **Step 1: Architecture Meetings (3-5 hours)**

**What:** Team discusses feature, architecture, constraints  
**Output:** Miro boards, notes, decisions  
**Participants:** Tech lead, developers, product

**Example from v2:**
- Pain points from v1
- Multi-tenancy requirements
- Auth0 vs custom auth decision
- Database choices (Kysely, PostgreSQL)

**Key insight:** Get alignment on architecture FIRST, before tasks.

---

### **Step 2: Create Planning Docs (1-2 days)**

**Format:** Markdown files, architecture-first (not feature-first)

**v2 Structure:**
```
planning/
├── api-conventions.md      # Errors, pagination, headers
├── crud-factory.md         # Resource registration pattern
├── db-conventions.md       # Schema, IDs, soft deletes
├── rbac.md                 # Roles, permissions
├── error-handling.md       # Error taxonomy
├── observability.md        # Logging, tracing
└── ...33 planning docs total
```

**Inspired by OpenSpec** but format-agnostic!

**Rules:**
1. **Architecture over features** (api-conventions, not "user-management")
2. **Examples required** (good code, bad code, edge cases)
3. **Constraints explicit** (KISS, no premature optimization)
4. **Cross-references** (link related planning docs)

**Template:**
```markdown
# [Architecture Area]

## Principles
- Core principle 1
- Core principle 2

## Requirements
- Specific requirement
- With code examples

## Anti-Patterns
❌ Don't do this: [bad example]
✅ Do this instead: [good example]

## Integration Points
- Links to related planning docs
- Dependencies

## Open Questions
- TBD items with owners
```

---

### **Step 3: Orchestrator Proposes Tasks (2-3 hours with AI)**

**Process:**
1. Orchestrator agent reads ALL planning docs
2. Proposes task breakdown
3. Human reviews and refines
4. Orchestrator updates

**Example prompt:**
```
Read all planning docs in planning/*.md

Propose tasks for Phase 02 (Core Services).

Requirements:
- Each task 2-8 hours (good for dual-writer comparison)
- Clear acceptance criteria
- No overlapping file edits (parallel-safe)
- Reference specific planning docs

Output: Task files in implementation/phase-02/tasks/
```

**v2 Result:** Phase 02 had 13 tasks, all parallelizable

---

### **Step 4: Define Path Ownership (Critical!)**

**The Integrator Pattern:**

One agent owns "composition files" (server.ts, main.tsx, etc.)
Other agents own domain modules (auth, db, crud, etc.)

**From v2 agent-0-integrator.md:**
```
Integrator owns:
- apps/api/src/server.ts
- apps/api/src/routes/*.ts  
- apps/web/src/app/layout.tsx
- etc.

Other agents NEVER edit these files directly.
Integrator imports and wires their modules.
```

**Why this matters:**
- Prevents merge conflicts
- Enables true parallel development
- Clear integration points

**Example:**
```
Task: 02-auth-middleware
Owns: apps/api/src/lib/middleware/auth.ts
Does NOT touch: server.ts

Task: 00-integrator
Owns: server.ts
Imports: auth middleware and registers it
```

---

### **Step 5: Phases Emerge Through Iteration**

**Not predefined!** Orchestrator discovers dependency graph.

**v2 Evolution:**
```
Initial: "We need auth, CRUD, and SDK"

After analysis:
Phase 00: Scaffold (dependencies for everything)
Phase 01: Foundation (logging, errors, server shell)
Phase 02: Core Services (auth, DB, CRUD - can parallel)
Phase 03: Contracts (OpenAPI, SDK - depends on Phase 02)
Phase 04: Integration (wire it together)
...Phases 05-10 emerged as needs discovered
```

**Process:**
1. Start with obvious groupings
2. Orchestrator analyzes dependencies
3. Creates phase structure
4. You approve/refine
5. **Phases updated as you learn!**

**v2 Example of evolution:**
- Migrations originally "optional helper"
- After seeing CRUD factory → "essential for safety"
- New task added mid-stream
- Phase updated, no problem!

**Key: 85% plan accuracy, 15% evolved**

---

### **Step 6: Task File Format**

**Each task includes:**

```markdown
# Task XX: Feature Name

## Context
What this builds on, why it's needed

## Requirements
1. Specific requirement
2. With acceptance criteria
3. References to planning docs

## Implementation Steps
1. Do this
2. Then this
3. Verify that

## Architecture Constraints
**Must follow:**
- planning/api-conventions.md
- planning/crud-factory.md

**Must NOT:**
- Over-engineer
- Add unnecessary abstractions
- Touch files owned by other agents

## Anti-Patterns
❌ Don't: Bad example
✅ Do: Good example

## Acceptance Criteria
- [ ] Tests pass
- [ ] CI passes
- [ ] Planning docs followed
- [ ] Commit and push

## Owned Paths
- apps/api/src/lib/auth/**
(This agent owns these files)
```

**v2 example:** See `implementation/phase-02/tasks/02-crud-factory-core.md`

---

### **Step 7: Running the Workflow**

**For each task:**
```bash
# Start dual writers
cube writers 02-crud-factory implementation/phase-02/tasks/02-crud-factory-core.md

# Wait for completion (~30min)

# Run judge panel
cube panel 02-crud-factory .prompts/panel-prompt-02-crud.md

# Aggregate decisions
cube decide 02-crud-factory

# If synthesis needed
cube feedback codex 02-crud-factory .prompts/synthesis-02-crud.md

# Peer review
cube peer-review 02-crud-factory .prompts/peer-review-02-crud.md

# If approved
gh pr create --base main --head writer-codex/02-crud-factory
```

**Or autonomous:**
```bash
cube auto implementation/phase-02/tasks/02-crud-factory-core.md
# Handles everything automatically!
```

---

### **Step 8: Agile Refinement**

**Plans evolve as you learn!**

**v2 Examples:**

**Auth0 Organization Sync:**
- Original plan: Simple Auth0 integration
- During implementation: Discovered need for org sync
- Orchestrator: Added auth0-sync task
- Updated Phase 04 dependencies

**Migration Helpers:**
- Original: Optional utility
- After CRUD factory: Essential for DX
- Elevated to required task
- Moved earlier in phases

**Process:**
1. Agent discovers issue/need
2. Raises to orchestrator
3. Orchestrator proposes change
4. Human approves
5. Plans updated
6. Implementation continues

**This is NOT waterfall** - it's agile with AI!

---

## 🎓 **Key Learnings from v2**

### **What Worked:**

**1. Architecture-first planning** (33 docs)
- Agents had clear constraints
- Less back-and-forth
- Better quality

**2. Path ownership** (Integrator pattern)
- Zero merge conflicts
- True parallel work
- Clear integration

**3. Small tasks** (2-8 hours)
- Good for comparison
- Faster iterations
- Easier to judge

**4. Synthesis** (58% of tasks)
- Best of both worlds
- Quality improvement
- Worth the overhead

### **What to Avoid:**

**1. Vague requirements**
- Agents invented features
- Wasted work
- More specific = better

**2. Large tasks** (>8 hours)
- Hard to compare
- Longer feedback cycles
- More can go wrong

**3. Overlapping paths**
- Merge conflicts
- Integration pain
- Slow down

**4. Trusting blindly**
- All judges approved wrong approach (API client)
- Human caught it
- **Always validate critical decisions**

---

## 📋 **Templates**

### **Planning Doc Template**

See: `templates/planning-doc-template.md`

### **Task File Template**

See: `templates/task-template.md`

### **Phase README Template**

See: `templates/phase-readme-template.md`

---

## 🔗 **References**

**v2 as Example:**
- Planning: `aetheron-connect-v2/planning/`
- Implementation: `aetheron-connect-v2/implementation/`
- Metrics: `implementation/panel/panel-metrics.md`

**Agent Cube Framework:**
- Core concepts: `AGENT_CUBE.md`
- Automation: `AGENT_CUBE_AUTOMATION.md`

**Next:** Start with architecture meetings, create planning docs, let Cube do the rest!

