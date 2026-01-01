# Task 15: Single Writer Mode Option

## Summary
Add option to run `cube auto` with a single writer instead of dual writers. Default remains dual-writer for maximum power, but single-writer mode offers a simpler/faster workflow for lower-stakes tasks.

## Motivation
- Dual-writer is powerful but has overhead (2x compute, longer runtime)
- Many tasks don't need the redundancy of competing implementations
- Lower barrier to entry for new users
- The review loop is the core value - single writer still benefits from automated review cycles

## Implementation

### CLI Option
```bash
# Default: dual writers (unchanged)
cube auto task.md

# Single writer mode
cube auto task.md --single
cube auto task.md --writer opus
cube auto task.md --writer gemini
```

### Config Option
```yaml
# cube.yaml
behavior:
  default_mode: "dual"  # or "single"
  default_writer: "opus"  # when single mode
```

### Changes Required
1. Add `--single` / `--writer` flags to CLI
2. Modify `orchestrate_auto_command` to support single-writer flow
3. Skip Phase 2 (parallel writers) when single mode
4. Skip Phase 4 (judge panel comparison) - go straight to peer review
5. Adjust synthesis to just be "review feedback" not "pick winner"

### Simplified Flow (Single Writer)
1. Phase 1: Generate prompt
2. Phase 2: Run single writer
3. Phase 3: Peer review (judges review implementation)
4. Phase 4: Minor fixes loop until approved
5. Phase 5: Create PR

### Acceptance Criteria
- [ ] `cube auto task.md --single` runs with one writer
- [ ] `cube auto task.md --writer opus` specifies which writer
- [ ] Config can set default mode
- [ ] Review loop still works (judge → feedback → fix → judge)
- [ ] Existing dual-writer mode unchanged
- [ ] Clear docs on when to use each mode

