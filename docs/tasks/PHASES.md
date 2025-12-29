# Agent Cube Task Execution Plan

**Generated:** 2025-12-29
**Total Tasks:** 16 (3 complete, 1 partial, 1 in review, 11 pending)

---

## Task Status

| Task | Description | Status | Blocks | Blocked By |
|------|-------------|--------|--------|------------|
| 01 | pyproject.toml | ✅ DONE | - | - |
| 02 | Fix bare excepts | ✅ DONE | - | - |
| 03 | Delete dead layouts | ✅ DONE | 13 | - |
| 04 | Split orchestrate.py | 🔄 IN REVIEW | 14 | - |
| 05 | Add core tests | ❌ TODO | 06 | All refactoring |
| 06 | Add docstrings | ❌ TODO | - | 05 |
| 07 | Add OSS files | 🟡 PARTIAL | - | - |
| 08 | Simplify agent identity | ❌ TODO | - | - |
| 09 | Consolidate adapters | ❌ TODO | 16 | - |
| 10 | Consolidate parsers | ❌ TODO | 16 | - |
| 11 | Fix raw prints | ❌ TODO | - | - |
| 12 | Extract constants | ❌ TODO | - | - |
| 13 | Consolidate layouts | ❌ TODO | - | 03 ✅ |
| 14 | Centralize decision parsing | ❌ TODO | - | 04 |
| 15 | Single writer mode | ❌ TODO | - | - |
| 16 | Claude Code adapter | ❌ TODO | - | 09, 10 |

---

## Dependency Graph

```
READY NOW (no blockers):
├── 07: Add OSS files
├── 08: Simplify agent identity  
├── 09: Consolidate adapters ────────┐
├── 10: Consolidate parsers ─────────┼──► 16: Claude Code adapter
├── 11: Fix raw prints               │
├── 12: Extract constants            │
├── 13: Consolidate layouts (03 ✅)  │
└── 15: Single writer mode           │
                                     │
WAITING:                             │
├── 04: Split orchestrate 🔄 ──► 14: Centralize parsing
│                                    │
└── 14 + all refactoring ──► 05: Tests ──► 06: Docstrings
```

---

## Execution Strategy

### Batch 1: Run Now (All Independent)

These have no blockers - can all run in parallel:

| Task | Complexity | Est. Time | Priority |
|------|------------|-----------|----------|
| **15** | High | 3-4 hrs | 🔥 Feature |
| **08** | High | 3-4 hrs | 🔥 Architecture |
| **09** | Medium | 1-2 hrs | Structure |
| **10** | Medium | 1-2 hrs | Structure |
| **13** | Medium | 1-2 hrs | Structure |
| **07** | Low | 30 min | OSS |
| **11** | Low | 30 min | Cleanup |
| **12** | Low | 30 min | Cleanup |

**Recommended:** Run 15 + 08 (high value) while quick wins (07, 11, 12) complete fast.

```bash
# High value features
cube auto docs/tasks/15-single-writer-mode.md &
cube auto docs/tasks/08-simplify-agent-identity.md &

# Quick wins (can queue after)
cube auto docs/tasks/07-add-oss-files.md
cube auto docs/tasks/11-fix-raw-prints.md
cube auto docs/tasks/12-extract-constants.md
```

### Batch 2: After 09 + 10 Complete

| Task | Depends On | Est. Time |
|------|------------|-----------|
| **16** | 09, 10 | 2-3 hrs |

```bash
cube auto docs/tasks/16-claude-code-adapter.md
```

### Batch 3: After 04 Merges

| Task | Depends On | Est. Time |
|------|------------|-----------|
| **14** | 04 | 2-3 hrs |

```bash
cube auto docs/tasks/14-centralize-decision-parsing.md
```

### Batch 4: Quality (After All Refactoring)

| Task | Depends On | Est. Time |
|------|------------|-----------|
| **05** | Stable code | 4-6 hrs |
| **06** | 05 | 2-3 hrs |

```bash
cube auto docs/tasks/05-add-core-tests.md
cube auto docs/tasks/06-add-docstrings.md
```

---

## Critical Paths

### Path A: Claude Code Adapter
```
09 (Consolidate adapters) ─┬─► 16 (Claude Code)
10 (Consolidate parsers) ──┘
```
**Time:** 3-5 hrs sequential

### Path B: Decision Parsing
```
04 (Split orchestrate) ──► 14 (Centralize parsing)
```
**Time:** Waiting on PR review + 2-3 hrs

### Path C: Quality
```
All refactoring ──► 05 (Tests) ──► 06 (Docstrings)
```
**Time:** 6-9 hrs, run last

---

## Optimal Parallel Execution

**With 2 writers available:**

| Time | Writer A | Writer B |
|------|----------|----------|
| 0-4h | 15 (Single writer) | 08 (Agent identity) |
| 0-1h | 09 (Adapters) | 10 (Parsers) |
| 1-2h | 13 (Layouts) | 07, 11, 12 (Quick wins) |
| 2-5h | 16 (Claude Code) | - waiting for 04 - |
| 4+h | 14 (Decision parsing) | - after 04 merges - |

**Total wall clock:** ~8-10 hrs (vs 20+ sequential)

---

## What to Run RIGHT NOW

**Highest value, no blockers:**

```bash
# Feature that users want
cube auto docs/tasks/15-single-writer-mode.md
```

Or for structure cleanup:

```bash
# These unblock Claude Code adapter
cube auto docs/tasks/09-consolidate-adapters.md
cube auto docs/tasks/10-consolidate-parsers.md
```
