# Task 11: Replace Raw Print Statements

## Objective
Replace raw `print()` statements with proper output functions for consistent formatting.

## Files to Update

### `python/cube/core/user_config.py` (3 instances)
```python
# Lines 134, 143, 152 - Warning messages during config loading
print(f"Warning: Failed to parse base config {base_config}: {e}")
```
**Fix:** Use `from .output import print_warning` or logging

### `python/cube/commands/peer_review.py` (6 instances)
```python
# Lines 95-103 - Session file instructions
print()
print("Make sure you've run the panel first:")
print(f"  cube panel {task_id} <panel-prompt.md>")
```
**Fix:** Use `console.print()` from rich

### `python/cube/commands/writers.py` (2 instances)
```python
# Lines 22-23 - Installation instructions
print()
print("Install cursor-agent:")
```
**Fix:** Use `console.print()` from rich

### `python/cube/core/updater.py` (1 instance)
```python
# Line 105 - Empty line
print()
```
**Fix:** Use `console.print()` from rich

### `python/cube/cli.py` (1 instance)
```python
# Line 42 - Error fallback (this one is OK - it's the fallback when Rich fails)
print(f"\n❌ Error: {msg}\n", file=sys.stderr)
```
**Keep as-is:** This is intentionally a fallback for when Rich isn't available

## Pattern to Use
```python
from ..core.output import console, print_warning, print_error, print_info

# Instead of print("message")
console.print("message")

# Instead of print(f"Warning: {x}")
print_warning(f"{x}")
```

## Verification
- `grep -rn "^[[:space:]]*print(" python/cube --include="*.py"` should only show:
  - `cli.py:42` (intentional fallback)
  - Any debug code that should be removed

