# Task 10: Consolidate Parser Structure

## Objective
Clean up duplicate parser patterns by moving base class into proper directory.

## Current State
```
python/cube/core/
├── parser_adapter.py       # Base class (21 lines)
├── parsers/
│   ├── __init__.py
│   ├── registry.py
│   ├── cursor_parser.py
│   ├── gemini_parser.py
│   └── cli_review_parser.py
```

## Target State
```
python/cube/core/parsers/
├── __init__.py             # Export ParserAdapter base class
├── base.py                 # ParserAdapter ABC (from parser_adapter.py)
├── registry.py
├── cursor.py               # Renamed from cursor_parser.py
├── gemini.py               # Renamed from gemini_parser.py
└── cli_review.py           # Renamed from cli_review_parser.py
```

## Changes Required

1. **Move `parser_adapter.py` → `parsers/base.py`**

2. **Rename parser files** (remove `_parser` suffix)
   - `cursor_parser.py` → `cursor.py`
   - `gemini_parser.py` → `gemini.py`
   - `cli_review_parser.py` → `cli_review.py`

3. **Update `parsers/__init__.py`**
   ```python
   from .base import ParserAdapter
   from .cursor import CursorParser
   from .gemini import GeminiParser
   from .cli_review import CLIReviewParser
   ```

4. **Update all imports** throughout codebase

5. **Delete old file**
   - Remove `python/cube/core/parser_adapter.py`

## Verification
- All tests pass
- `cube auto` works end-to-end
- No import errors

