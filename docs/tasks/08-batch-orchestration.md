# Task: Batch Orchestration - Run Multiple Tasks in Parallel

**Priority:** P1 (Major Feature)
**Complexity:** High
**Files:** New command, new layout

## Problem

Currently `cube auto` runs one task at a time. For large projects with multiple task files, you have to run them sequentially or manually open multiple terminals.

## Proposed Usage

```bash
# Run all tasks in a folder
cube auto batch ./docs/tasks/

# Run specific task files
cube auto batch task1.md task2.md task3.md

# With options
cube auto batch ./tasks/ --max-parallel 3
```

## Requirements

### CLI Interface

```python
@app.command(name="batch")
def batch(
    paths: Annotated[list[str], typer.Argument(help="Folder path or list of task files")],
    max_parallel: Annotated[int, typer.Option("--max-parallel", "-p", help="Max concurrent tasks")] = 4,
    resume: Annotated[bool, typer.Option("--resume", help="Resume incomplete tasks")] = False,
):
    """Run multiple tasks in parallel with unified status display."""
```

### Functional Requirements

- [ ] Accept folder path - find all `.md` files inside
- [ ] Accept list of specific file paths
- [ ] Spawn subprocess for each task: `cube auto <task.md>`
- [ ] Limit concurrent tasks with `--max-parallel`
- [ ] Queue additional tasks until slot available
- [ ] Handle task completion/failure gracefully
- [ ] Support `--resume` to skip completed tasks

### Display Requirements

Create a new `BatchLayout` showing:

```
╭─────────────────────── Batch Orchestration (4/7 tasks) ───────────────────────╮
│                                                                               │
│  01-pyproject-toml      ✅ Complete (12m 34s)                                 │
│  02-fix-bare-excepts    ✅ Complete (8m 12s)                                  │
│  03-delete-dead-layouts 🔄 Phase 4: Panel (running 3m)                        │
│  04-split-orchestrate   🔄 Phase 2: Writers (running 5m)                      │
│  05-add-core-tests      ⏳ Queued                                             │
│  06-add-docstrings      ⏳ Queued                                             │
│  07-add-oss-files       ⏳ Queued                                             │
│                                                                               │
╰───────────────────────────────────────────────────────────────────────────────╯

─── Recent Activity ────────────────────────────────────────────────────────────
[03-delete-dead-layouts] Judge Sonnet: Reviewing implementations...
[04-split-orchestrate]   Writer A: Creating orchestrate/prompts.py...
[03-delete-dead-layouts] Judge Codex: Both approaches valid, slight preference...
[04-split-orchestrate]   Writer B: I'll start by analyzing the current...
```

### Status Tracking

Track each task's state:
```python
@dataclass
class BatchTaskState:
    task_id: str
    task_file: str
    status: Literal["queued", "running", "complete", "failed"]
    current_phase: Optional[int]
    phase_name: Optional[str]
    start_time: Optional[float]
    end_time: Optional[float]
    subprocess: Optional[subprocess.Popen]
    last_output: deque[str]  # Last N lines of output
    error: Optional[str]
```

### Implementation Approach

1. **Subprocess per task:**
   ```python
   proc = subprocess.Popen(
       ["cube", "auto", task_file, "--resume"],
       stdout=subprocess.PIPE,
       stderr=subprocess.STDOUT,
       text=True,
       bufsize=1  # Line buffered
   )
   ```

2. **Output parsing:**
   - Parse stdout for phase transitions (`═══ Phase N:`)
   - Capture recent lines for activity feed
   - Detect completion/failure

3. **Concurrency control:**
   ```python
   async def run_batch(tasks: list[str], max_parallel: int):
       semaphore = asyncio.Semaphore(max_parallel)
       async with asyncio.TaskGroup() as tg:
           for task in tasks:
               tg.create_task(run_with_semaphore(task, semaphore))
   ```

### File Structure

```
python/cube/
├── commands/
│   └── batch.py           # New command
├── core/
│   └── batch_layout.py    # New layout for batch display
```

### Output Parsing

Parse subprocess output for status:
```python
PHASE_PATTERNS = {
    r"═══ Phase (\d+): (.+) ═══": "phase_start",
    r"✅.*(Complete|Approved)": "success", 
    r"❌.*(Error|Failed)": "failure",
}
```

## Verification

- [ ] `cube auto batch ./docs/tasks/` runs all tasks
- [ ] `cube auto batch a.md b.md c.md` runs specific files
- [ ] `--max-parallel 2` limits concurrent tasks
- [ ] Status display updates in real-time
- [ ] Completed tasks show duration
- [ ] Failed tasks show error
- [ ] `--resume` skips already-complete tasks
- [ ] Ctrl+C gracefully stops all subprocesses

## Edge Cases

- [ ] Empty folder - error message
- [ ] Non-existent files - skip with warning
- [ ] Task fails mid-run - mark failed, continue others
- [ ] All tasks complete - show summary and exit
- [ ] Subprocess hangs - timeout after 30 min?

## Notes

- Consider saving batch state to allow resume of entire batch
- Could add `--dry-run` to show what would run
- Future: web UI for batch monitoring
- The subprocess approach keeps each task isolated
- Could alternatively use multiprocessing but subprocess is simpler

