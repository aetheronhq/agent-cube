# Task: Add Docstrings to Public Functions

**Priority:** P2 (Minor)
**Complexity:** Low
**Files:** 10+ files, 30 functions

## Problem

30 public functions lack docstrings, making the code harder to understand and preventing proper API documentation generation.

## Functions Missing Docstrings

### High Priority (frequently used)

1. `base_layout.py`:
   - `start()` - Initialize and display layout
   - `add_thinking()` - Add thinking text to box
   - `add_output()` - Add to main output region
   - `add_assistant_message()` - Add buffered assistant message
   - `mark_complete()` - Mark a box as complete
   - `flush_buffers()` - Flush pending buffers
   - `close()` - Stop layout and print final output

2. `cli.py`:
   - `decide()` - Parse judge decisions and determine winner

3. `ui/routes/stream.py`:
   - `add_subscriber()` - Add SSE subscriber
   - `remove_subscriber()` - Remove SSE subscriber
   - `get_history()` - Get message history

### Medium Priority

4. `orchestrate.py`:
   - `generate_feedback_a()` - Generate feedback for Writer A
   - `generate_feedback_b()` - Generate feedback for Writer B

5. `automation/dual_feedback.py`:
   - `send_to_a()` - Send feedback to Writer A
   - `send_to_b()` - Send feedback to Writer B

6. `ui/routes/tasks.py`:
   - `validate_payload()` - Validate request payload

7. `ui/sse_layout.py`:
   - `add_thinking()` - Add thinking to SSE stream
   - `add_output()` - Add output to SSE stream

## Requirements

### Docstring Format

Use Google-style docstrings:

```python
def add_thinking(self, box_id: str, text: str) -> None:
    """Add thinking text to a specific box.
    
    Buffers text until a complete sentence is detected, then
    adds to the box's line buffer for display.
    
    Args:
        box_id: The identifier of the thinking box.
        text: Text chunk to add (may be partial sentence).
    """
```

### Guidelines

- One-line summary for simple functions
- Full docstring for complex functions
- Include Args/Returns/Raises where applicable
- Mention side effects (e.g., "Updates internal buffer")

## Verification

- [ ] `python -c "from cube.core.base_layout import BaseThinkingLayout; help(BaseThinkingLayout)"` shows docstrings
- [ ] No "missing docstring" warnings from pylint/pydocstyle
- [ ] All 30 functions have docstrings

## Notes

- Don't add docstrings to private functions (starting with `_`)
- Keep docstrings concise but informative
- Focus on "what" and "why", not "how"

