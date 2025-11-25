# Task: Add Unit Tests for Core Modules

**Priority:** P1 (Major)
**Complexity:** Medium
**Files:** Create 4+ new test files

## Problem

Current test coverage is ~6% (500 lines of tests for 8,300 lines of code).
Critical modules have zero tests:
- `decision_parser.py` - Parses judge decisions
- `user_config.py` - Loads cube.yaml config
- `state.py` - Workflow state management
- `base_layout.py` - Terminal UI

## Requirements

### 1. Test `decision_parser.py`

Create `tests/core/test_decision_parser.py`:

```python
def test_parse_valid_json_decision():
    """Parse a well-formed judge decision JSON."""

def test_parse_malformed_json():
    """Handle malformed JSON gracefully."""

def test_extract_winner_from_various_formats():
    """Winner can be 'A', 'writer_a', 'Writer A', etc."""

def test_aggregate_decisions_majority_vote():
    """3 judges vote: A, A, B -> Winner A."""

def test_aggregate_decisions_tie():
    """Tie handling when no majority."""
```

### 2. Test `user_config.py`

Create `tests/core/test_user_config.py`:

```python
def test_load_default_config():
    """Load config when no cube.yaml exists."""

def test_merge_repo_config():
    """Repo cube.yaml overrides base config."""

def test_get_writer_config():
    """Retrieve writer by key."""

def test_get_judge_config():
    """Retrieve judge by key."""

def test_resolve_writer_alias():
    """'sonnet', 'writer-a', 'A' all resolve to writer_a."""
```

### 3. Test `state.py`

Create `tests/core/test_state.py`:

```python
def test_save_and_load_state():
    """State persists correctly."""

def test_update_phase():
    """Phase updates increment correctly."""

def test_validate_resume():
    """Can't resume from phase 5 if only completed phase 2."""

def test_clear_state():
    """State file is deleted."""
```

### 4. Test `base_layout.py`

Create `tests/core/test_base_layout.py`:

```python
def test_truncate_long_lines():
    """Lines exceeding terminal width are truncated."""

def test_buffer_flushes_on_punctuation():
    """Buffer flushes when sentence ends with .!?"""

def test_add_output_scrolls():
    """Output region shows most recent lines."""
```

### Directory Structure

```
tests/
├── core/
│   ├── __init__.py
│   ├── test_decision_parser.py
│   ├── test_user_config.py
│   ├── test_state.py
│   └── test_base_layout.py
├── cli/
│   └── (existing tests)
└── conftest.py
```

## Verification

- [ ] `pytest tests/core/` passes
- [ ] Coverage for tested modules > 80%
- [ ] Tests are isolated (use tmp_path, mock configs)
- [ ] No flaky tests

## Notes

- Use `pytest` fixtures for common setup
- Mock file I/O where possible
- Use `tmp_path` fixture for state file tests
- Focus on edge cases and error handling

