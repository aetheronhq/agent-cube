# Task 04: Split orchestrate.py

## Problem

`python/cube/commands/orchestrate.py` is 1,196 lines and growing. It contains the entire autonomous orchestration workflow plus prompt generation, making it hard to maintain and test.

## Goal

Split the file into logical modules while maintaining all functionality. Target: no single file over 400 lines.

## Current Structure

```
orchestrate.py (1,196 lines)
├── extract_task_id_from_file()     # Utility
├── orchestrate_prompt_command()     # CLI command  
├── generate_orchestrator_prompt()   # 125-line string template
├── orchestrate_auto_command()       # CLI entry point
├── _orchestrate_auto_impl()         # Main workflow (~350 lines)
├── generate_writer_prompt()         # Prompt generation
├── generate_panel_prompt()          # Prompt generation
├── run_decide_and_get_result()      # Decision handling
├── run_decide_peer_review()         # Decision handling
├── run_synthesis()                  # Phase handler
├── run_peer_review()                # Phase handler
├── run_minor_fixes()                # Phase handler
├── generate_dual_feedback()         # Phase handler
├── create_pr()                      # PR creation
```

## Proposed Split

### 1. `orchestrate.py` - Main entry points only (~100 lines)
- `orchestrate_prompt_command()`
- `orchestrate_auto_command()` 
- Keep as thin wrappers that delegate to other modules

### 2. `workflow.py` - Main workflow logic (~400 lines)
- `_orchestrate_auto_impl()` - the main phase orchestration
- Phase routing logic (SYNTHESIS vs MERGE vs FEEDBACK paths)

### 3. `phases.py` (or extend existing) - Individual phase handlers (~300 lines)
- `run_synthesis()`
- `run_peer_review()`
- `run_minor_fixes()`
- `generate_dual_feedback()`

### 4. `prompts.py` - Prompt generation (~250 lines)
- `generate_orchestrator_prompt()` - the big meta-prompt
- `generate_writer_prompt()`
- `generate_panel_prompt()`

### 5. `decisions.py` - Decision handling (~100 lines)
- `run_decide_and_get_result()`
- `run_decide_peer_review()`

### 6. `pr.py` - PR creation (~50 lines)
- `create_pr()`

## Constraints

1. **No behavior changes** - pure refactor, all tests must pass
2. **Maintain imports** - external code imports from `cube.commands.orchestrate`
3. **Keep `__all__` exports** - preserve public API
4. **No circular imports** - be careful with dependency order

## Success Criteria

- [ ] `orchestrate.py` under 150 lines
- [ ] No file over 400 lines
- [ ] All existing functionality works
- [ ] `cube auto` workflow completes successfully
- [ ] Clean imports (no circular dependencies)
