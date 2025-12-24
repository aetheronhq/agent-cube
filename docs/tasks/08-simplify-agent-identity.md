# Task: Simplify Agent Identity Architecture

**Priority:** P1 (High)
**Complexity:** High
**Estimated Time:** 2-3 hours
**Files:** ~20 files across core, automation, commands, models

---

## Problem

The current agent identity system is overly complex with multiple overlapping concepts:

### Current Writer Identity (5 different identifiers!)
| Field | Example | Purpose |
|-------|---------|---------|
| `key` | `writer_a` | Config lookup key |
| `name` (slug) | `opus` | Worktree paths |
| `label` | `Writer Opus` | UI display |
| `letter` | `A` | Session keys |
| `WRITER_LETTERS` | hardcoded dict | Letter lookup |

### Current Judge Identity (2 identifiers)
| Field | Example | Purpose |
|-------|---------|---------|
| `key` | `judge_1`, `judge_4` | Everything |
| `label` | `Judge Opus`, `CodeRabbit` | UI display |

### The Mapping Hell
```python
# Current code has all these:
writer_slug_map: Dict[str, str]   # slug -> writer key
writer_alias_map: Dict[str, str]  # alias -> slug
WRITER_LETTERS = {"opus": "A", "codex": "B"}  # hardcoded
judge_alias_map: Dict[str, str]   # alias -> key
```

### Path Inconsistency
- Worktrees: `writer-opus-task123`
- Logs: `writer-opus-task123-*.json`
- Sessions: `WRITER_A_task123_SESSION_ID.txt`

---

## Solution: Single `id` Architecture

### New Config Format
```yaml
# cube.yaml - BEFORE
writers:
  writer_a:
    name: opus
    model: opus-4.5-thinking
    label: Writer Opus
    color: cyan
    letter: A

judges:
  judge_1:
    model: sonnet-4.5-thinking
    label: Judge Sonnet
    color: green

# cube.yaml - AFTER
agents:
  opus:
    model: opus-4.5-thinking
    label: Opus
    color: cyan
    role: writer
    
  codex:
    model: gpt-5.1-codex-max
    label: Codex
    color: yellow
    role: writer
    
  sonnet:
    model: sonnet-4.5-thinking
    label: Sonnet
    color: green
    role: judge
    
  gemini:
    model: gemini-2.5-pro
    label: Gemini
    color: blue
    role: judge
    
  coderabbit:
    type: cli-review
    cmd: "coderabbit review --plain --type all --cwd {{worktree}}"
    label: CodeRabbit
    color: magenta
    role: judge
    peer_review_only: true
```

### New Unified Model
```python
@dataclass
class AgentConfig:
    """Single unified agent configuration."""
    id: str           # Primary key: "opus", "codex", "sonnet", "coderabbit"
    model: str        # Model name for LLM agents
    label: str        # Short display name: "Opus", "Codex", "CodeRabbit"
    color: str        # Rich color for terminal
    role: str         # "writer" or "judge"
    
    # Judge-specific (optional)
    type: str = "llm"           # "llm" or "cli-review"
    cmd: Optional[str] = None   # Command for cli-review
    peer_review_only: bool = False
    
    @property
    def display_name(self) -> str:
        """Full display name: 'Writer Opus', 'Judge CodeRabbit'"""
        return f"{self.role.title()} {self.label}"
    
    def session_key(self, task_id: str) -> str:
        """Session file key: 'OPUS_my-task'"""
        return f"{self.id.upper()}_{task_id}"
    
    def worktree_name(self, task_id: str) -> str:
        """Worktree directory name: 'opus-my-task'"""
        return f"{self.id}-{task_id}"
    
    def log_prefix(self, task_id: str) -> str:
        """Log file prefix: 'opus-my-task'"""
        return f"{self.id}-{task_id}"
    
    def branch_name(self, task_id: str) -> str:
        """Git branch: 'opus/my-task'"""
        return f"{self.id}/{task_id}"
```

### Derived Patterns (No Maps Needed)
| Pattern | Format | Example |
|---------|--------|---------|
| Display | `{role.title()} {label}` | "Writer Opus" |
| Worktree | `{id}-{task}` | `opus-my-task` |
| Branch | `{id}/{task}` | `opus/my-task` |
| Log file | `{id}-{task}-{ts}.json` | `opus-my-task-123.json` |
| Session | `{ID}_{task}` | `OPUS_my-task` |

---

## Implementation Steps

### Phase 1: New Config Layer (Non-Breaking)

1. **Create new unified model** in `models/types.py`:
   ```python
   @dataclass
   class AgentConfig:
       id: str
       model: str
       label: str
       color: str
       role: str  # "writer" | "judge"
       type: str = "llm"
       cmd: Optional[str] = None
       peer_review_only: bool = False
   ```

2. **Add new config loading** in `user_config.py`:
   - Support both old format (`writers`/`judges`) and new format (`agents`)
   - Build `AgentConfig` objects from either format
   - Deprecation warning for old format

3. **New accessor functions**:
   ```python
   def get_agent(id: str) -> AgentConfig
   def get_writers() -> list[AgentConfig]
   def get_judges() -> list[AgentConfig]
   def get_agents_by_role(role: str) -> list[AgentConfig]
   ```

### Phase 2: Update Consumers

Files to update (in order):

1. **`models/types.py`**
   - Deprecate `WriterInfo`, `JudgeInfo` 
   - Add `AgentInfo` that wraps `AgentConfig` + runtime state

2. **`core/config.py`**
   - Remove `WRITER_LETTERS` dict
   - Update `get_worktree_path()` to use new pattern

3. **`automation/dual_writers.py`**
   - Use `agent.id` instead of `writer_info.name`
   - Use `agent.session_key(task_id)` for sessions
   - Use `agent.display_name` for output

4. **`automation/judge_panel.py`**
   - Use `agent.id` instead of `judge_info.key`
   - Use `agent.session_key(task_id)` for sessions

5. **`commands/feedback.py`**
   - Update session key lookup

6. **`core/session.py`**
   - Simplify session file naming

7. **`core/agent_logger.py`**
   - Use `agent.log_prefix(task_id)` for filenames

8. **`ui/routes/stream.py`** and **`ui/routes/tasks.py`**
   - Update agent identification

9. **`commands/orchestrate.py`**
   - Update all writer/judge references

10. **CLI commands** (`feedback.py`, `peer_review.py`, `resume.py`, etc.)
    - Update argument resolution

### Phase 3: Migration & Cleanup

1. **Migrate existing sessions**:
   - `WRITER_A_task` → `OPUS_task`
   - Script to rename session files

2. **Migrate worktrees**:
   - `writer-opus-task` → `opus-task`
   - Update existing worktree paths

3. **Remove deprecated code**:
   - `WriterConfig`, `JudgeConfig`
   - `WriterInfo`, `JudgeInfo`
   - All alias maps
   - `WRITER_LETTERS`

4. **Update documentation**:
   - Config format docs
   - CLI help text

---

## Files to Modify

| File | Changes |
|------|---------|
| `models/types.py` | New `AgentConfig`, deprecate old types |
| `core/user_config.py` | New loading logic, remove maps |
| `core/config.py` | Remove `WRITER_LETTERS`, update paths |
| `core/session.py` | Simplified session keys |
| `core/agent_logger.py` | Use new patterns |
| `automation/dual_writers.py` | Use `AgentConfig` |
| `automation/judge_panel.py` | Use `AgentConfig` |
| `automation/dual_feedback.py` | Use `AgentConfig` |
| `commands/feedback.py` | Update session lookup |
| `commands/peer_review.py` | Update agent resolution |
| `commands/resume.py` | Update session lookup |
| `commands/orchestrate.py` | Update all references |
| `commands/status.py` | Update display |
| `commands/decide.py` | Update decision parsing |
| `ui/routes/stream.py` | Update agent detection |
| `ui/routes/tasks.py` | Update serialization |
| `core/decision_parser.py` | Update patterns |
| `core/state_backfill.py` | Update patterns |
| `core/dynamic_layout.py` | Update box IDs |

---

## Breaking Changes

### Config Format
Old format will be supported with deprecation warning for 1-2 releases.

### Session Files
Existing sessions will need migration or manual cleanup:
```bash
# Old: ~/.agent-sessions/WRITER_A_my-task_SESSION_ID.txt
# New: ~/.agent-sessions/OPUS_my-task_SESSION_ID.txt
```

### Worktree Paths
Existing worktrees will need migration:
```bash
# Old: ~/.cube/worktrees/project/writer-opus-task
# New: ~/.cube/worktrees/project/opus-task
```

### CLI Arguments
Users using `writer-a`, `writer-b` will need to use `opus`, `codex` instead.
Provide alias support during transition.

---

## Success Criteria

- [ ] Single `AgentConfig` dataclass used everywhere
- [ ] No more `key` vs `name` vs `letter` confusion
- [ ] All alias maps removed
- [ ] `WRITER_LETTERS` removed
- [ ] Consistent path patterns across worktrees, logs, sessions
- [ ] Old config format still works (with warning)
- [ ] All tests pass
- [ ] Migration script for existing sessions/worktrees

---

## Anti-Patterns to Avoid

### ❌ Don't keep both systems
```python
# BAD: Supporting both indefinitely
def get_writer(key_or_id: str):
    if key_or_id in old_writers:
        return old_writers[key_or_id]
    return new_agents[key_or_id]
```

### ❌ Don't add more aliases
```python
# BAD: Adding compatibility aliases
alias_map["writer-a"] = "opus"
alias_map["writer_a"] = "opus"
alias_map["a"] = "opus"
```

### ✅ Do use properties for derived values
```python
# GOOD: Compute from single source
@property
def display_name(self) -> str:
    return f"{self.role.title()} {self.label}"
```

---

## Notes

- This is a significant refactor but will make the codebase much cleaner
- Consider doing in phases to avoid one massive PR
- Keep backward compatibility during transition
- Write migration script early to test

---

## Related Tasks

- Task 04: Split orchestrate.py (should use new agent model)
- Task 05: Add core tests (test new AgentConfig)

