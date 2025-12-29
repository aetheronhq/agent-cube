# Agent Cube Task Phases

**Generated:** 2025-12-29
**Total Tasks:** 16 (3 complete, 1 partial, 1 in review, 11 pending)
**Estimated Total Time:** 20-28 hours parallel execution

---

## Task Status Summary

| Task | Description | Status | Complexity | Est. Time |
|------|-------------|--------|------------|-----------|
| 01 | pyproject.toml | ✅ DONE | Low | - |
| 02 | Fix bare excepts | ✅ DONE | Low | - |
| 03 | Delete dead layouts | ✅ DONE | Low | - |
| 04 | Split orchestrate.py | 🔄 IN REVIEW | High | 4-6 hrs |
| 05 | Add core tests | ❌ TODO | Medium | 4-6 hrs |
| 06 | Add docstrings | ❌ TODO | Low | 2-3 hrs |
| 07 | Add OSS files | 🟡 PARTIAL | Low | 30 min |
| 08 | Simplify agent identity | ❌ TODO | High | 3-4 hrs |
| 09 | Consolidate adapters | ❌ TODO | Medium | 1-2 hrs |
| 10 | Consolidate parsers | ❌ TODO | Medium | 1-2 hrs |
| 11 | Fix raw prints | ❌ TODO | Low | 30 min |
| 12 | Extract constants | ❌ TODO | Low | 30 min |
| 13 | Consolidate layouts | ❌ TODO | Medium | 1-2 hrs |
| 14 | Centralize decision parsing | ❌ TODO | Medium | 2-3 hrs |
| 15 | Single writer mode | ❌ TODO | High | 3-4 hrs |
| 16 | Claude Code adapter | ❌ TODO | Medium | 2-3 hrs |

---

## Dependency Graph

```
PHASE 0: Quick Wins (No Dependencies)
├── Task 03: Delete dead layouts
├── Task 07: Add OSS files  
├── Task 11: Fix raw prints
└── Task 12: Extract constants

PHASE 0b: In Review
└── Task 04: Split orchestrate.py ──┐
                                    │
PHASE 1: Structure Cleanup          │
├── Task 13: Consolidate layouts    │ (depends on 03)
├── Task 14: Centralize parsing ◄───┘ (benefits from 04)
├── Task 09: Consolidate adapters
└── Task 10: Consolidate parsers

PHASE 2: Architecture
└── Task 08: Simplify agent identity (wide impact, sequential)

PHASE 3: New Features
├── Task 15: Single writer mode (depends on clean structure)
└── Task 16: Claude Code adapter (depends on 09, 10)

PHASE 4: Quality
├── Task 05: Add core tests (after structure stable)
└── Task 06: Add docstrings (after code stable)
```

---

## Phase 0: Quick Wins

**Parallelizable:** ✅ Yes (all 3 remaining tasks)
**Est. Time:** 1.5 hours total
**Risk:** Low

### Tasks

| Task | Files Changed | Description | Status |
|------|---------------|-------------|--------|
| 03 | Delete 2 files | Remove `dual_layout.py`, `triple_layout.py` | ✅ DONE |
| 07 | Create 2 files | Add `CODE_OF_CONDUCT.md`, `CHANGELOG.md` | 🟡 PARTIAL |
| 11 | Edit 3 files | Replace ~11 `print()` with `console.print()` | ❌ TODO |
| 12 | Edit 2 files | Extract magic numbers to constants | ❌ TODO |

### Execution
```bash
# Remaining 3 can run in parallel
cube auto docs/tasks/07-add-oss-files.md &
cube auto docs/tasks/11-fix-raw-prints.md &
cube auto docs/tasks/12-extract-constants.md &
```

---

## Phase 1: Structure Cleanup

**Parallelizable:** ✅ Partial (09+10 parallel, 13+14 parallel)
**Est. Time:** 4-6 hours
**Risk:** Medium
**Dependencies:** Task 03 complete, Task 04 merged

### Tasks

| Task | Depends On | Description |
|------|------------|-------------|
| 09 | None | Move `cli_adapter.py` → `adapters/base.py` |
| 10 | None | Move `parser_adapter.py` → `parsers/base.py` |
| 13 | 03 | Consolidate layout classes |
| 14 | 04 | Centralize decision parsing |

### Execution
```bash
# Batch 1: Adapter/Parser consolidation
cube auto docs/tasks/09-consolidate-adapters.md &
cube auto docs/tasks/10-consolidate-parsers.md &
wait

# Batch 2: Layout/Parsing consolidation  
cube auto docs/tasks/13-consolidate-layouts.md &
cube auto docs/tasks/14-centralize-decision-parsing.md &
```

---

## Phase 2: Architecture

**Parallelizable:** ❌ No (wide-reaching changes)
**Est. Time:** 3-4 hours
**Risk:** High
**Dependencies:** Phase 1 complete

### Tasks

| Task | Impact | Description |
|------|--------|-------------|
| 08 | ~20 files | Simplify agent identity to single `id` |

### Execution
```bash
# Sequential - too many file touches for parallel
cube auto docs/tasks/08-simplify-agent-identity.md
```

---

## Phase 3: New Features

**Parallelizable:** ✅ Yes (both tasks)
**Est. Time:** 5-7 hours
**Risk:** Medium
**Dependencies:** Phase 1 complete (clean adapter/parser structure)

### Tasks

| Task | New Files | Description |
|------|-----------|-------------|
| 15 | ~3 files modified | Add `--single` / `--writer` flags |
| 16 | 2 new files | `claude_code_adapter.py`, `claude_code_parser.py` |

### Execution
```bash
# Both can run in parallel
cube auto docs/tasks/15-single-writer-mode.md &
cube auto docs/tasks/16-claude-code-adapter.md &
```

---

## Phase 4: Quality

**Parallelizable:** ❌ No (tests should verify stable code)
**Est. Time:** 6-9 hours
**Risk:** Low
**Dependencies:** All prior phases complete

### Tasks

| Task | New Files | Description |
|------|-----------|-------------|
| 05 | 4+ test files | Unit tests for core modules |
| 06 | 10+ files | Google-style docstrings |

### Execution
```bash
# Sequential - tests first, then docs
cube auto docs/tasks/05-add-core-tests.md
cube auto docs/tasks/06-add-docstrings.md
```

---

## Timeline Summary

| Phase | Tasks | Parallel? | Time | Cumulative |
|-------|-------|-----------|------|------------|
| 0 | 03, 07, 11, 12 | ✅ | 1.5h | 1.5h |
| 0b | 04 | - | In Review | - |
| 1 | 09, 10, 13, 14 | ✅ | 4-6h | 6-8h |
| 2 | 08 | ❌ | 3-4h | 9-12h |
| 3 | 15, 16 | ✅ | 5-7h | 14-19h |
| 4 | 05, 06 | ❌ | 6-9h | 20-28h |

**Total Estimated:** 20-28 hours of agent time
**With parallelization:** ~15-20 hours wall clock

---

## Critical Path

The longest dependency chain determines minimum completion time:

```
04 (Split Orchestrate) 
  → 14 (Centralize Parsing)
    → 08 (Simplify Identity)  
      → 15 (Single Writer Mode)
        → 05 (Add Tests)
          → 06 (Add Docstrings)
```

**Critical path time:** ~18-24 hours

---

## Notes

- **Task 04** is the bottleneck - blocks 14, which blocks 08
- **Phase 0** can start immediately while 04 is in review
- **Tasks 15 & 16** are the user-facing features - prioritize if shipping soon
- **Tasks 05 & 06** are quality tasks - can be deferred for initial OSS release

