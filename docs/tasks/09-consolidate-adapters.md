# Task 09: Consolidate Adapter Structure

## Objective
Clean up confusing duplicate adapter patterns by moving base classes into their proper directories.

## Current State
```
python/cube/core/
├── cli_adapter.py          # Base class + process tracking (152 lines)
├── adapters/
│   ├── __init__.py
│   ├── registry.py
│   ├── cursor_adapter.py
│   ├── gemini_adapter.py
│   └── cli_review_adapter.py
```

## Target State
```
python/cube/core/adapters/
├── __init__.py             # Export CLIAdapter base class
├── base.py                 # CLIAdapter ABC + process tracking (from cli_adapter.py)
├── registry.py
├── cursor.py               # Renamed from cursor_adapter.py
├── gemini.py               # Renamed from gemini_adapter.py
└── cli_review.py           # Renamed from cli_review_adapter.py
```

## Changes Required

1. **Move `cli_adapter.py` → `adapters/base.py`**
   - Keep all process tracking logic
   - Keep signal handlers
   - Keep `CLIAdapter` ABC

2. **Rename adapter files** (remove `_adapter` suffix)
   - `cursor_adapter.py` → `cursor.py`
   - `gemini_adapter.py` → `gemini.py`
   - `cli_review_adapter.py` → `cli_review.py`

3. **Update `adapters/__init__.py`**
   ```python
   from .base import CLIAdapter
   from .cursor import CursorAdapter
   from .gemini import GeminiAdapter
   from .cli_review import CLIReviewAdapter
   ```

4. **Update all imports** throughout codebase
   - `from ..core.cli_adapter import CLIAdapter` → `from ..core.adapters import CLIAdapter`

5. **Delete old file**
   - Remove `python/cube/core/cli_adapter.py`

## Verification
- All tests pass
- `cube auto` works end-to-end
- No import errors

