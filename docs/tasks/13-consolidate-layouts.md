# Task 13: Consolidate Layout Classes

## Objective
Clarify the relationship between 3 layout files and potentially consolidate.

## Current State
```
python/cube/core/
├── base_layout.py      # 9669 bytes - BaseLayout class with Rich Live display
├── dynamic_layout.py   # 2206 bytes - DynamicLayout (class-level state wrapper)
├── single_layout.py    # 472 bytes  - SingleLayout for single-agent display
```

## Analysis Needed

### `base_layout.py`
- Core implementation with Rich Live display
- Box-based layout system
- Truncation logic
- Most of the actual functionality

### `dynamic_layout.py`
- Thin wrapper around BaseLayout
- Uses class-level state (singleton pattern)
- Provides `initialize()`, `start()`, `close()` class methods

### `single_layout.py`
- Simplified single-box layout
- Used for single agent runs (prompter, feedback)
- 472 bytes - very small

## Options

### Option A: Keep All Three (Document Purpose)
- Add docstrings explaining when to use each
- `BaseLayout` - Direct instantiation for custom layouts
- `DynamicLayout` - Singleton for parallel agent runs (writers, judges)
- `SingleLayout` - For single-agent sequential runs

### Option B: Merge into One Module
```python
# python/cube/core/layout.py
class BaseLayout: ...
class SingleLayout(BaseLayout): ...
class DynamicLayout:  # Class-level singleton wrapper
    _instance: Optional[BaseLayout] = None
    ...
```

### Option C: Keep Separate but Rename
- `base_layout.py` → `layout/base.py`
- `dynamic_layout.py` → `layout/dynamic.py`  
- `single_layout.py` → `layout/single.py`

## Recommendation
**Option A** - Keep all three, add clear docstrings explaining purpose.
The separation makes sense for the different use cases.

## Changes Required
1. Add module-level docstrings to each file explaining purpose
2. Add class-level docstrings with usage examples
3. Consider adding a `layout/__init__.py` that exports all three

## Verification
- All layout scenarios still work (writers, judges, single agent)
- No visual regressions in terminal output

