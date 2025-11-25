# Task: Split orchestrate.py into Modules

**Priority:** P1 (Major)
**Complexity:** High
**Files:** Split 1 file (1,020 lines) into 4-5 modules

## Problem

`orchestrate.py` is 1,020 lines doing everything:
- Prompt generation for writers
- Writer launch orchestration
- Judge panel orchestration
- Synthesis workflow
- Peer review workflow
- Feedback generation
- Minor fixes workflow

This violates single responsibility and makes the code hard to maintain.

## Proposed Structure

```
python/cube/commands/orchestrate/
├── __init__.py          # Re-export main functions
├── prompts.py           # generate_writer_prompt, generate_panel_prompt, etc.
├── phases.py            # Phase execution logic (orchestrate_auto_command)
├── synthesis.py         # run_synthesis, run_peer_review
├── feedback.py          # generate_dual_feedback, run_minor_fixes
└── utils.py             # extract_task_id_from_file, helpers
```

## Requirements

### Module Breakdown

1. **`prompts.py`** (~200 lines)
   - `generate_orchestrator_prompt()`
   - `generate_writer_prompt()`
   - `generate_panel_prompt()`
   - All the prompt template strings

2. **`phases.py`** (~300 lines)
   - `orchestrate_auto_command()` - main entry point
   - Phase 1-10 execution logic
   - State management calls

3. **`synthesis.py`** (~200 lines)
   - `run_synthesis()`
   - `run_peer_review()`
   - Decision aggregation

4. **`feedback.py`** (~200 lines)
   - `generate_dual_feedback()`
   - `run_minor_fixes()`
   - Feedback prompt generation

5. **`utils.py`** (~50 lines)
   - `extract_task_id_from_file()`
   - Other helpers

### Maintain Exports

```python
# orchestrate/__init__.py
from .phases import orchestrate_auto_command
from .prompts import orchestrate_prompt_command
from .utils import extract_task_id_from_file

__all__ = ['orchestrate_auto_command', 'orchestrate_prompt_command', 'extract_task_id_from_file']
```

### Update CLI Imports

```python
# cli.py - should still work:
from .commands.orchestrate import orchestrate_auto_command, extract_task_id_from_file
```

## Verification

- [ ] `cube auto task.md` works end-to-end
- [ ] `cube orchestrate prompt task.md` works
- [ ] All phases execute correctly
- [ ] No circular import errors
- [ ] Tests pass

## Notes

- Keep the same function signatures for backward compatibility
- Move imports to module level where possible
- Consider adding `__all__` to each module
- This is a large refactor - do it carefully with tests

