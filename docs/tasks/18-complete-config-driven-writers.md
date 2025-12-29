# Task 18: Complete Config-Driven Writers (Finish Task 08)

**Priority:** P2 (Medium)
**Complexity:** High
**Estimated Time:** 3-4 hours
**Depends On:** 08 (partially complete)
**Blocks:** N-writer support

---

## Problem

Task 08 (simplify-agent-identity) only partially completed the goal. It removed some complexity but:
- ❌ Still has 126 hardcoded `"writer_a"` / `"writer_b"` references
- ❌ Added `letter` field (MORE complexity, not less)
- ❌ System still assumes exactly 2 writers

The codebase is NOT truly config-driven.

---

## Goal

Make the system work with ANY writer keys from config, not just `writer_a`/`writer_b`.

**Test:** Rename `writer_a` → `writer_x` in `cube.yaml` and everything should still work.

---

## Changes Required

### 1. Remove Hardcoded Writer Keys (126 occurrences)

**Files with most occurrences:**
- `python/cube/automation/judge_panel.py` (27)
- `python/cube/commands/orchestrate/prompts.py` (18)
- `python/cube/core/decision_parser.py` (14)
- `python/cube/core/user_config.py` (11)
- `python/cube/automation/dual_feedback.py` (7)
- `python/cube/commands/decide.py` (6)
- `python/cube/automation/dual_writers.py` (6)
- And 13 more files...

**Pattern to replace:**
```python
# Before (hardcoded):
writer_a = get_writer_config("writer_a")
writer_b = get_writer_config("writer_b")

# After (config-driven):
config = load_config()
writers = [get_writer_config(key) for key in config.writer_order]
writer_a, writer_b = writers[0], writers[1]  # Or iterate
```

### 2. Remove `letter` Field

The `letter` field was added as a band-aid. Remove it:

**WriterConfig:**
```python
@dataclass
class WriterConfig:
    key: str
    name: str
    model: str
    label: str
    letter: str  # ← REMOVE THIS
    color: str
```

**Session keys:** Use key directly:
```python
# Before:
save_session(f"WRITER_{writer.letter}", task_id, session_id)

# After:
save_session(writer.key.upper(), task_id, session_id)
```

### 3. Make Dual Writers Support N Writers

Currently assumes exactly 2 writers. Make it generic:

**dual_writers.py:**
```python
# Support any number of writers from config
async def launch_dual_writers(task_id: str, prompt_path: Path, resume_mode: bool = False):
    config = load_config()
    writers = []
    
    for writer_key in config.writer_order:
        wconfig = get_writer_config(writer_key)
        # ... create WriterInfo ...
        writers.append(writer_info)
    
    # Dynamic layout with N boxes
    boxes = {wconfig.key: wconfig.label for wconfig in writers}
    DynamicLayout.initialize(boxes)
```

### 4. Update Prompts to Be Generic

**prompts.py:** Don't assume writer_a/writer_b exist:
```python
# Before:
writer_a = get_writer_config("writer_a")
writer_b = get_writer_config("writer_b")

# After:
writers = [get_writer_config(key) for key in config.writer_order]
# Generate prompts dynamically for each writer
```

---

## Verification

### Test 1: Rename Writers
```yaml
# cube.yaml
writers:
  writer_x:  # Changed from writer_a
    name: opus
    ...
  writer_y:  # Changed from writer_b
    name: gemini
    ...
```

Run: `cube auto test-task.md`
Expected: ✅ Works without errors

### Test 2: Add Third Writer
```yaml
writers:
  writer_a:
    name: opus
  writer_b:
    name: gemini
  writer_c:
    name: codex
```

Expected: System handles 3 writers (or gracefully limits to first 2)

### Test 3: Grep Check
```bash
rg '"writer_a"|"writer_b"' python/cube/
```

Expected: 0 matches (or only in comments/docs)

---

## Success Criteria

- [ ] No hardcoded `"writer_a"` or `"writer_b"` strings in code
- [ ] `letter` field removed from `WriterConfig` and `WriterInfo`
- [ ] Session keys use `writer_key.upper()` directly
- [ ] System works when writers renamed in config
- [ ] All tests pass
- [ ] Grep shows 0 hardcoded writer key references

---

## Benefits

- ✅ Truly config-driven (no hardcoded assumptions)
- ✅ Support for N writers (not just 2)
- ✅ Simpler code (no letter mapping)
- ✅ Easier to add new writers
- ✅ No confusion about writer identity

---

## Notes

This completes what Task 08 started. Task 08 removed some complexity (WRITER_LETTERS, alias maps) but didn't go far enough. This task finishes the job.

