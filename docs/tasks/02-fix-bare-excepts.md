# Task: Fix Bare `except:` Clauses

**Priority:** P0 (Critical)
**Complexity:** Low
**Files:** 6 files, ~10 instances

## Problem

Bare `except:` clauses catch ALL exceptions including:
- `KeyboardInterrupt` (Ctrl+C)
- `SystemExit` (sys.exit())
- `GeneratorExit`

This hides bugs and makes the program uninterruptible.

## Files to Fix

1. `python/cube/ui/routes/stream.py` - 1 instance
2. `python/cube/core/config.py` - 2 instances
3. `python/cube/commands/clean.py` - 1 instance
4. `python/cube/commands/decide.py` - 3 instances
5. `python/cube/commands/logs.py` - 1 instance
6. `python/cube/automation/judge_panel.py` - 2 instances

## Requirements

### For Each Instance

- [ ] Replace `except:` with specific exception type
- [ ] If truly catching "anything", use `except Exception:`
- [ ] Consider logging the exception for debugging
- [ ] Preserve the original fallback behavior

### Pattern to Apply

```python
# Before (BAD):
try:
    something()
except:
    fallback_value = default

# After (GOOD):
try:
    something()
except (KeyError, ValueError, AttributeError) as e:
    fallback_value = default
    # Optional: logger.debug(f"Fallback used: {e}")
```

### Exception Type Guidelines

| Context | Recommended Exception |
|---------|----------------------|
| Dict/config lookup | `KeyError` |
| JSON parsing | `json.JSONDecodeError` |
| File operations | `OSError, IOError` |
| Type conversion | `ValueError, TypeError` |
| Attribute access | `AttributeError` |
| Unknown/any | `Exception` (not bare) |

## Verification

- [ ] `grep -r "except:" python/cube` returns 0 results
- [ ] Ctrl+C still interrupts the program
- [ ] All existing functionality preserved
- [ ] Tests pass

## Notes

- Some bare excepts are in fallback code that truly doesn't care about the error type
- In those cases, `except Exception:` is acceptable but add a comment explaining why

