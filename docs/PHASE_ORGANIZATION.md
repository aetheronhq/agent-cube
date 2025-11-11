# Phase Organization Guide

**How phases emerge from dependency analysis**

Based on v2: Started with 3 ideas, orchestrator discovered 10 phases.

---

## 🎯 **Core Concept**

**Phases are NOT arbitrary groupings.**

They're **dependency layers** discovered through analysis:
- What must come first?
- What can run in parallel?
- What are the integration points?

**v2 lesson:** Orchestrator discovered the optimal structure!

---

## 🔄 **How Phases Emerge**

### **Step 1: Start with Goals**

**v2 Beginning:**
```
We need:
- Authentication
- CRUD operations
- SDK generation
```

That's it. No phases yet.

### **Step 2: Orchestrator Analyzes**

**Prompt to orchestrator:**
```
Given these goals and planning docs,
propose task breakdown and phases.

Consider:
- Dependencies (what depends on what)
- Parallelization (what can run together)
- Integration points
- Testing gates
```

**Orchestrator thinks:**
```
Auth needs:
- Server running
- Error handling
- Logging

CRUD needs:
- Auth (to test protected endpoints)
- Database middleware
- Error handling

SDK needs:
- OpenAPI spec
- CRUD endpoints done

Therefore...
```

### **Step 3: Phases Discovered**

**v2 Orchestrator Output:**
```
Phase 00: Monorepo Scaffold
- Everything depends on build system working
- Gate: Can build, lint, test

Phase 01: Foundation
- Server skeleton
- Logging
- Error handling  
- Gate: Basic server responding

Phase 02: Core Services (9 tasks!)
- Auth (needs Phase 01 error handling)
- DB middleware (independent)
- CRUD factory (needs DB + auth)
- Migrations (independent)
- Can ALL run in parallel!
- Gate: Core services operational

Phase 03: Contracts
- OpenAPI (needs Phase 02 CRUD)
- SDK (needs OpenAPI)
- Gate: SDK usable

Phase 04: Integration
- Wire everything together
- Integrator assembles
- Gate: End-to-end works
```

**Human:** "Perfect! Approved."

### **Step 4: Implementation Reveals More**

**During Phase 02:**
```
Discovery: "Migrations have tons of boilerplate"

Orchestrator: "Add task: migration-helpers.md"
