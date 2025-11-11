# Task Breakdown Guide

**How to split features into agent-comparable tasks**

Based on v2: 15 tasks, perfect parallelization, zero conflicts.

---

## 🎯 **The Goal**

Create tasks that are:
- ✅ **Comparable** - 2 agents can propose different valid approaches
- ✅ **Independent** - Can run in parallel without conflicts
- ✅ **Complete** - Shippable unit of value
- ✅ **Sized right** - 2-8 hours (sweet spot for quality comparison)

---

## 📏 **Task Sizing**

### **Too Small (<2 hours)**
```
❌ "Add a constant"
❌ "Update import"
❌ "Fix typo"
```

**Problem:** No room for different approaches, not worth dual-writer overhead

### **Just Right (2-8 hours)**
```
✅ "CRUD Factory Core" (02-crud-factory-core)
✅ "Auth Middleware" (02-auth-middleware)
✅ "OpenAPI Generator" (03-openapi-generator)
```

**Perfect:** Enough complexity for approaches to differ, small enough to compare

### **Too Large (>8 hours)**
```
❌ "Complete authentication system" (auth + RBAC + sessions + tests)
❌ "Full frontend" (too many decisions)
```

**Problem:** Too many sub-decisions, hard to judge holistically, long feedback cycles

---

## 🗂️ **Splitting Strategies**

### **Strategy 1: By Layer**

**Feature:** Error Handling

**Split:**
- `02-error-handler.ts` - Core error middleware
- `02-error-types.ts` - Error taxonomy (if complex enough)
- `02-error-tests.ts` - Test suite (if substantial)

**v2 example:** Single task (02-error-handler) worked well at 323 lines

### **Strategy 2: By Component**

**Feature:** Observability Stack

**Split:**
- `02-structured-logging` - Logger setup
- `02-otel-instrumentation` - Tracing
- `02-otel-collector-config` - Collector setup

**v2 example:** Combined into one (02-observability-complete) due to tight integration

### **Strategy 3: By Interface**

**Feature:** Database Layer

**Split:**
- `02-db-middleware-and-rls` - Request-scoped DB, transactions
- `02-data-driver-and-repos` - Tenant-scoped wrapper
- `02-migration-helpers` - Schema factory utilities

**v2 example:** Worked perfectly - each independently valuable

### **Strategy 4: By Contract**

**Feature:** API + SDK

**Split:**
- `03-openapi-generator` - Zod → OpenAPI spec
- `03-sdk-build` - OpenAPI → TypeScript SDK

**v2 example:** Perfect split - clean interface between tasks

---

## 🔑 **Path Ownership Rules**

### **The Integrator Pattern**

**One agent owns composition:**
```
agent-0-integrator owns:
- server.ts
- main.tsx  
- route files
- config assembly
```

**Domain agents own modules:**
```
02-auth-middleware owns:
- lib/middleware/auth.ts
- Does NOT touch server.ts

00-integrator later:
- Imports auth middleware
- Registers in server.ts
```

**Why:** Prevents conflicts, enables parallel work

### **Ownership Declaration**

**In each task file:**
```markdown
## Owned Paths
This task owns:
- apps/api/src/lib/auth/**
- apps/api/src/lib/auth.ts

Must NOT modify:
- apps/api/src/server.ts (owned by integrator)
- Other middleware files
```

### **v2 Pattern:**
```
Phase 02 had 9 parallel tasks:
- Each owned distinct paths
- Zero file overlap
- Integrator wired them together in Phase 04
- Result: All 9 ran simultaneously!
```

---

## 📋 **Task File Checklist**

**Every task must have:**

- [ ] **Context** - What this builds on
- [ ] **Requirements** - Specific, testable
- [ ] **Planning References** - Which docs to follow
- [ ] **Owned Paths** - Clear file ownership
- [ ] **Anti-Patterns** - What NOT to do
- [ ] **Acceptance Criteria** - Definition of done
- [ ] **Integration Points** - How it connects
- [ ] **Time Estimate** - Rough guidance

**Optional but valuable:**
- Examples (good/bad code)
- Architecture constraints
- Testing requirements
- Migration notes

---

## 🎨 **Real Examples from v2**

### **Example 1: CRUD Factory (Perfect Split)**

**Task:** `02-crud-factory-core.md`

**What made it good:**
- Clear scope: Factory pattern for CRUD endpoints
- Self-contained: All in `lib/crud/`
- Comparable: Many ways to implement factories
- Testable: Integration tests possible
- **Result:** Huge architectural debate, synthesis produced 73% simpler solution!

**Owned paths:**
```
apps/api/src/lib/crud/
├── types.ts
├── register.ts
└── register.test.ts
```

**Did NOT touch:** `server.ts`, resource files (separate tasks)

### **Example 2: Auth Middleware (Clean Interface)**

**Task:** `02-auth-middleware.md`

**What made it good:**
- Single responsibility: JWT verification
- Clear planning reference: `planning/rbac.md`
- Integration point: Exports middleware, integrator registers
- Testable: Can mock Auth0
- **Result:** Unanimous vote B (3/3), clean implementation

**Owned paths:**
```
apps/api/src/lib/middleware/auth.ts
```

### **Example 3: Migration Helpers (Emerged Need)**

**Task:** `02-migration-helpers.md` (added mid-stream!)

**Origin story:**
- Not in original plan
- After CRUD factory: Realized boilerplate pain
- Orchestrator proposed: "Factory for tenant table migrations"
- Human approved
- Task created and executed
- **Result:** 80% boilerplate reduction (50→10 lines)

**Lesson:** Plans evolve! Don't be rigid.

---

## 🚫 **Common Mistakes**

### **1. Too Much Scope**
```
❌ BAD: "Complete user management system"
   (auth + CRUD + validation + tests + docs)

✅ GOOD: "User CRUD endpoints"
   (specific, builds on auth from previous task)
```

### **2. Unclear Boundaries**
```
❌ BAD: "Improve error handling"
   (where? how? success criteria?)

✅ GOOD: "Error envelope middleware per api-conventions.md"
   (specific doc reference, clear deliverable)
```

### **3. Path Conflicts**
```
❌ BAD: Both auth and RBAC tasks modify server.ts
   (conflict!)

✅ GOOD: Both export middleware, integrator wires later
   (parallel-safe)
```

### **4. Missing Context**
```
❌ BAD: Just requirements, no why

✅ GOOD: "Builds on 02-auth-middleware, needed for CRUD"
   (agents understand the bigger picture)
```

---

## 🎓 **Decision Framework**

**When deciding how to split, ask:**

**1. Can two agents propose meaningfully different approaches?**
- If NO → Too small or too prescriptive
- If YES → Good task!

**2. Can it run in parallel with other tasks?**
- If NO → Check dependencies, might need different phase
- If YES → Good for velocity!

**3. Does it have clear value when done?**
- If NO → Might be too granular
- If YES → Shippable unit!

**4. Can you test/verify it independently?**
- If NO → Scope might be unclear
- If YES → Clear acceptance criteria!

**5. Is it 2-8 hours for experienced developer?**
- If NO → Resize (split or combine)
- If YES → Perfect comparison window!

---

## 📊 **v2 Task Statistics**

**Phase 02 (Core Services):**
- 9 tasks defined
- 8 ran in parallel (1 was integrator)
- Average task: ~300-500 LOC
- Synthesis: 5/9 tasks (56%)
- Duration: Completed in 4 days (would be 36 days sequential!)

**Optimal task characteristics:**
- Backend: 200-600 lines
- Frontend: 150-400 lines
- Config/Setup: 50-200 lines
- Tests included in estimate

---

## 🔄 **The Workflow**

**Step 1: Feature identified**
```
"We need CRUD operations with tenancy"
```

**Step 2: Check planning docs**
```
planning/crud-factory.md exists? ✅
planning/db-conventions.md exists? ✅
```

**Step 3: Define task scope**
```
Task: Core factory pattern
Not: Specific resources (separate tasks)
Not: Server wiring (integrator task)
```

**Step 4: Identify owned paths**
```
Owns: apps/api/src/lib/crud/
Does NOT touch: server.ts, resource files
```

**Step 5: Write task file**
```
Use template, fill in requirements
Reference planning docs
List anti-patterns
```

**Step 6: Run it!**
```bash
cube auto implementation/phase-02/tasks/02-crud-factory-core.md
```

---

## 🎯 **Templates**

### **Task File Template**
See: `templates/task-template.md`

### **Quick Checklist**
```
Task: [Name]
Scope: [Clear boundary]
Owned paths: [Specific files]
Planning refs: [Which docs]
Time: [2-8 hours]
Testable: [Yes/No]
Parallel-safe: [Yes/No]
```

---

## 🔗 **Next Steps**

1. Read: `docs/PLANNING_GUIDE.md` (architecture meetings → planning docs)
2. Read: `docs/PHASE_ORGANIZATION.md` (how phases emerge)
3. Review: v2 tasks in `aetheron-connect-v2/implementation/`
4. Practice: Split one of YOUR features into tasks

**The art: Small enough to compare, large enough to matter!**

