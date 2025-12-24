# Task: Delete Dead Layout Wrapper Files

**Priority:** P1 (Major)
**Complexity:** Low
**Files:** Delete 2 files, update imports

## Problem

Two layout files are useless 8-line wrappers that add no value:

```python
# dual_layout.py (DELETE)
from .dynamic_layout import DynamicLayout
def get_dual_layout():
    return DynamicLayout

# triple_layout.py (DELETE)
from .dynamic_layout import DynamicLayout
def get_triple_layout():
    return DynamicLayout
```

These were likely left over from a refactor to `DynamicLayout`.

## Requirements

### Files to Delete

- [ ] Delete `python/cube/core/dual_layout.py`
- [ ] Delete `python/cube/core/triple_layout.py`

### Update Imports

Search for any imports of these modules and replace:

```python
# Before:
from .core.dual_layout import get_dual_layout
layout = get_dual_layout()

# After:
from .core.dynamic_layout import DynamicLayout
layout = DynamicLayout
```

### Files to Check for Imports

```bash
grep -rn "dual_layout\|triple_layout\|get_dual_layout\|get_triple_layout" python/cube
```

## Verification

- [ ] Both files deleted
- [ ] No import errors when running `python -m cube.cli --help`
- [ ] `cube auto` workflow still works
- [ ] `cube panel` still works
- [ ] Tests pass

## Notes

- `single_layout.py` is NOT dead - it provides `SingleAgentLayout` class with actual logic
- `dynamic_layout.py` is the real implementation
- `base_layout.py` is the base class

