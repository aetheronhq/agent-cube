# Task 14: Centralize Decision Parsing Logic

## Objective
Consolidate decision parsing logic that's currently spread across 5 files.

## Current State
Decision parsing exists in:
1. `python/cube/core/decision_parser.py` - Main parser (should be authoritative)
2. `python/cube/commands/decide.py` - CLI command
3. `python/cube/commands/orchestrate.py` - Workflow orchestration
4. `python/cube/automation/judge_panel.py` - Judge panel
5. `python/cube/ui/routes/tasks.py` - Web UI API

## Problem
Each file has slightly different logic for:
- Finding decision files (underscore vs dash formats)
- Parsing decision JSON
- Extracting issues/status
- Aggregating multiple decisions

## Solution
Make `decision_parser.py` the single source of truth:

### Functions to Expose from `decision_parser.py`
```python
def get_decision_file_path(judge_key: str, task_id: str, review_type: str = "decision") -> Optional[Path]:
    """Find decision file, handling both underscore and dash formats."""

def parse_judge_decision(filepath: Path) -> Dict[str, Any]:
    """Parse a single judge decision file."""

def parse_all_decisions(task_id: str, review_type: str = "decision") -> List[Dict[str, Any]]:
    """Parse all judge decisions for a task."""

def aggregate_decisions(task_id: str) -> Dict[str, Any]:
    """Aggregate all judge decisions into a summary."""

def get_peer_review_status(task_id: str) -> Dict[str, Any]:
    """Get peer review approval status and remaining issues."""
```

### Files to Update

1. **`commands/decide.py`** - Use `aggregate_decisions()` and `get_peer_review_status()`
2. **`commands/orchestrate.py`** - Use `get_peer_review_status()` instead of `run_decide_peer_review()`
3. **`automation/judge_panel.py`** - Use `get_decision_file_path()` for status display
4. **`ui/routes/tasks.py`** - Use `parse_all_decisions()` for API responses

### Remove Duplicates
- Remove inline decision file finding logic from each file
- Remove duplicate JSON parsing patterns
- Remove duplicate issue extraction

## Verification
- `cube decide <task> --peer` shows correct status
- `cube auto` progression works correctly
- Web UI shows correct decision data
- All tests pass

