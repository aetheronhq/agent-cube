# Task 18: Complete Agent Identity Simplification

**Priority:** P2 (Medium)
**Complexity:** High  
**Estimated Time:** 3-4 hours
**Depends On:** 08 (partially complete)

---

## Problem

Task 08 added the `letter` field but didn't actually remove the hardcoded `writer_a`/`writer_b` complexity. There are still **126 hardcoded references** to these keys throughout the codebase.

The `letter` field is a band-aid that adds MORE complexity instead of removing it.

---

## Goal

**Zero hardcoded writer keys.** Make the system truly config-driven so users can:
- Use any keys: `writer_x`, `writer_alpha`, `writer_primary`
- Support 3+ writers without code changes
- Reorder writers in config without breaking anything

---

## Changes Required

### 1. Remove Hardcoded String Lookups

**Find all:** `rg '"writer_[ab]"' python/cube/`

**Replace:**
```python
# BAD:
writer_a = get_writer_config("writer_a")
writer_b = get_writer_config("writer_b")

# GOOD:
writers = [get_writer_config(key) for key in config.writer_order]
# Or iterate dynamically without unpacking
```

### 2. Make Dual Writers Generic

**File:** `python/cube/automation/dual_writers.py`

```python
async def launch_writers(task_id: str, prompt_path: Path, writer_keys: Optional[List[str]] = None):
    """Launch N writers in parallel (default: all from config)."""
    config = load_config()
    keys_to_run = writer_keys or config.writer_order
    
    writers = []
    for writer_key in keys_to_run:
        wconfig = get_writer_config(writer_key)
        # ... create WriterInfo ...
        writers.append(writer)
    
    # Run all in parallel
    await asyncio.gather(*[run_writer(w, prompt, False) for w in writers])
```

### 3. Session Keys Use Config Keys

**Remove letter entirely:**
```python
# BAD:
session = load_session(f"WRITER_{writer.letter}", task_id)

# GOOD:
session = load_session(writer.key.upper(), task_id)  # WRITER_A, WRITER_OPUS, etc.
```

### 4. Remove Letter Field

**Files:**
- `python/cube/models/types.py` - Remove `letter: str` from `WriterInfo`
- `python/cube/core/user_config.py` - Remove `letter: str` from `WriterConfig`
- Remove all `letter` derivation logic

### 5. Dynamic Layout for N Writers

**File:** `python/cube/core/dynamic_layout.py`

Support arbitrary number of boxes (not just 2):
```python
# Create boxes from config
boxes = {
    wconfig.key: wconfig.label 
    for wconfig in [get_writer_config(k) for k in config.writer_order]
}
DynamicLayout.initialize(boxes)
```

---

## Files to Update

**High priority (many hardcoded references):**
- `python/cube/commands/orchestrate/prompts.py` (18)
- `python/cube/automation/judge_panel.py` (27)
- `python/cube/automation/dual_feedback.py` (7)
- `python/cube/commands/decide.py` (6)
- `python/cube/automation/dual_writers.py` (6)
- `python/cube/commands/feedback.py` (4)
- `python/cube/commands/orchestrate/phases.py` (6)

**Total:** 126 references across 20 files

---

## Verification

### 1. Test with Custom Keys

Edit `cube.yaml`:
```yaml
writers:
  writer_x:  # Not writer_a!
    name: opus
    model: opus-4.5-thinking
    label: Writer Opus
    color: cyan
  
  writer_y:  # Not writer_b!
    name: gemini
    model: gemini-2.5-pro
    label: Writer Gemini
    color: blue
```

Run: `cube auto task.md`

Should work without code changes!

### 2. Test with 3 Writers

```yaml
writers:
  writer_a:
    name: opus
  writer_b:
    name: codex
  writer_c:
    name: gemini
```

System should support 3-way comparison (future feature).

### 3. Grep Check

```bash
# Should return 0 (or only comments/docs):
rg '"writer_[ab]"' python/cube/ | grep -v "# Example" | wc -l
```

---

## Success Criteria

- [ ] Zero hardcoded `"writer_a"` / `"writer_b"` strings in code
- [ ] `letter` field removed from `WriterConfig` and `WriterInfo`
- [ ] Session keys use config keys directly (`WRITER_A`, `WRITER_OPUS`, etc.)
- [ ] System works with custom writer keys (`writer_x`, `writer_alpha`)
- [ ] All tests pass
- [ ] Documentation updated

---

## Why This Matters

1. **Extensibility:** Users can add writer_c, writer_d without code changes
2. **Clarity:** One identifier (key) instead of 5 (key, name, label, letter, slug)
3. **Maintainability:** No mapping dictionaries to keep in sync
4. **Flexibility:** Users can name writers whatever they want

---

## Notes

This completes what Task 08 started. Task 08 removed some complexity but added the `letter` field as a workaround. This task finishes the job by removing the need for letters entirely.

