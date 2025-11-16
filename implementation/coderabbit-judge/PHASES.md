# CodeRabbit Judge Implementation Phases

**Project:** CodeRabbit CLI Integration as Judge  
**Architecture:** Ports/Adapters (Hexagonal)  
**Total Estimate:** 11-15 hours

---

## Phase 0: Adapter Foundation

**Goal:** Implement CLI adapter for executing CodeRabbit reviews

**Tasks:**
- Task 01: CodeRabbit Adapter (3-4 hours)

**Deliverables:**
- `python/cube/core/adapters/coderabbit_adapter.py`
- Implements `CLIAdapter` interface
- Registered in adapter registry

**Key Features:**
- Execute `coderabbit review` command
- Check installation and authentication
- Stream JSON output

**Success Criteria:**
- [ ] Adapter implements CLIAdapter interface
- [ ] CLI execution works in worktree context
- [ ] Error handling for auth and installation
- [ ] Registered and importable

---

## Phase 1: Output Parsing

**Goal:** Parse CodeRabbit JSON output into standard stream messages

**Tasks:**
- Task 02: CodeRabbit Parser (2-3 hours)

**Deliverables:**
- `python/cube/core/parsers/coderabbit_parser.py`
- Message type mapping
- Registered in parser registry

**Key Features:**
- Parse JSON output lines
- Convert to StreamMessage format
- Handle review comments, summaries, errors
- Graceful error handling

**Success Criteria:**
- [ ] Parser converts CodeRabbit JSON to StreamMessages
- [ ] All major message types handled
- [ ] Malformed input handled gracefully
- [ ] Registered and importable

---

## Phase 2: Decision Logic

**Goal:** Generate standard judge decisions from CodeRabbit analysis

**Tasks:**
- Task 03: Decision Generation (4-5 hours)

**Deliverables:**
- `python/cube/core/coderabbit_decision.py`
- Scoring algorithm
- Winner determination
- Decision file generation

**Key Features:**
- Calculate scores across 5 categories
- Map severity levels to deductions
- Compare both writer implementations
- Generate standard decision JSON

**Success Criteria:**
- [ ] Scoring algorithm implemented
- [ ] Decision format matches schema
- [ ] Winner determination logic correct
- [ ] Blocker issues extracted properly

---

## Phase 3: Integration

**Goal:** Integrate CodeRabbit into judge panel system and test end-to-end

**Tasks:**
- Task 04: Integration & Testing (3-4 hours)

**Deliverables:**
- Configuration integration
- End-to-end testing
- Documentation
- Example configurations

**Key Features:**
- Works in standard judge panel
- Pre-flight authentication checks
- Full workflow testing
- User documentation

**Success Criteria:**
- [ ] CodeRabbit configurable in cube.yaml
- [ ] Works in parallel with other judges
- [ ] End-to-end testing complete
- [ ] Documentation written

---

## Implementation Strategy

### Sequential Execution

**Phases must be completed in order:**

```
Phase 0 (Adapter)
    ↓
Phase 1 (Parser)
    ↓
Phase 2 (Decision Logic)
    ↓
Phase 3 (Integration)
```

**Why sequential:**
- Parser depends on adapter output format
- Decision logic depends on parsed messages
- Integration depends on all components

### Parallel Work (If Multiple Agents)

**Can work in parallel within phases:**
- Documentation can be written alongside implementation
- Test data can be prepared while coding
- Examples can be created independently

**Cannot parallelize across phases:**
- Don't start parser before adapter interface is clear
- Don't start decision logic before parser output is defined

---

## Milestones

### Milestone 1: Adapter Complete
- [ ] CodeRabbitAdapter implements CLIAdapter
- [ ] Executes CodeRabbit CLI successfully
- [ ] Handles errors gracefully
- [ ] Registered in adapter registry

**Verification:** Can execute `coderabbit review` through adapter

---

### Milestone 2: Parser Complete
- [ ] CodeRabbitParser converts JSON to StreamMessages
- [ ] All message types handled
- [ ] Registered in parser registry
- [ ] Integration with adapter works

**Verification:** Can parse real CodeRabbit output into messages

---

### Milestone 3: Decision Logic Complete
- [ ] Scoring algorithm implemented
- [ ] Decision files generated correctly
- [ ] Format matches standard schema
- [ ] Integration with adapter works

**Verification:** Can generate valid decision files from CodeRabbit output

---

### Milestone 4: Integration Complete
- [ ] Configuration system updated
- [ ] End-to-end testing passed
- [ ] Documentation written
- [ ] Ready for production use

**Verification:** Can run full judge panel with CodeRabbit as one judge

---

## Testing Strategy by Phase

### Phase 0 Testing
```bash
# Manual adapter test
python3 -c "
from cube.core.adapters.coderabbit_adapter import CodeRabbitAdapter
adapter = CodeRabbitAdapter()
print(adapter.check_installed())
"
```

### Phase 1 Testing
```python
# Manual parser test
from cube.core.parsers.coderabbit_parser import CodeRabbitParser
parser = CodeRabbitParser()
msg = parser.parse('{"type": "review_comment", "file": "test.ts", ...}')
print(msg)
```

### Phase 2 Testing
```python
# Manual decision generation test
from cube.core.coderabbit_decision import generate_decision
decision = generate_decision(3, "test", issues_a, issues_b)
print(json.dumps(decision, indent=2))
```

### Phase 3 Testing
```bash
# Full integration test
cube writers test-task .prompts/test-task.md
cube panel test-task .prompts/panel-prompt.md
cat .prompts/decisions/judge-3-test-task-decision.json
```

---

## Risk Management

### High Risk Items

1. **CodeRabbit CLI API Changes**
   - Risk: Output format may change
   - Mitigation: Parser handles unknown types gracefully

2. **Authentication Issues**
   - Risk: Users forget to login
   - Mitigation: Pre-flight authentication check

3. **Rate Limiting**
   - Risk: Free tier limits exhausted
   - Mitigation: Clear error messages, graceful degradation

4. **Scoring Algorithm Tuning**
   - Risk: Scores may not reflect quality accurately
   - Mitigation: Make algorithm configurable, document tuning process

### Medium Risk Items

1. **Decision Format Compatibility**
   - Risk: Decision format doesn't match expectations
   - Mitigation: Validate against schema in testing

2. **Performance**
   - Risk: CodeRabbit reviews too slow
   - Mitigation: Review only changed files, not full codebase

---

## Dependencies

### External Dependencies
- CodeRabbit CLI (user must install)
- CodeRabbit account (user must authenticate)

### Internal Dependencies
- `CLIAdapter` interface (existing)
- `StreamMessage` type (existing)
- Judge panel orchestration (existing)
- Decision file format (existing)

### No New Dependencies
- No new Python packages required
- No changes to core abstractions
- No changes to orchestration logic

---

## Success Metrics

### Code Quality
- [ ] All type hints present
- [ ] Docstrings on all public functions
- [ ] Linter passes (no warnings)
- [ ] Follows existing patterns

### Functionality
- [ ] Adapter executes CodeRabbit CLI
- [ ] Parser converts all message types
- [ ] Decision files match schema
- [ ] Integration with judge panel works

### Testing
- [ ] Unit tests for each component
- [ ] Integration test passes
- [ ] Edge cases handled
- [ ] Error scenarios tested

### Documentation
- [ ] Planning doc complete
- [ ] Task files detailed
- [ ] README comprehensive
- [ ] Troubleshooting guide included

---

## Phase Completion Checklist

### After Each Phase

- [ ] Code committed to git
- [ ] Tests passing
- [ ] Documentation updated
- [ ] Peer review completed (if applicable)
- [ ] Ready for next phase

### After All Phases

- [ ] All tasks completed
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Integration verified
- [ ] Ready for merge

---

## Next Steps After Completion

1. **Monitor Usage**
   - Track CodeRabbit decision quality
   - Collect user feedback
   - Identify tuning opportunities

2. **Iterate on Scoring**
   - Adjust deduction values based on feedback
   - Refine category mappings
   - Consider configurable scoring rules

3. **Expand Features (Optional)**
   - Support CodeRabbit configuration files
   - Add custom review rules
   - Integrate more CodeRabbit features

4. **Documentation**
   - Create video tutorial
   - Write blog post
   - Add to main project docs

---

**Last Updated:** 2025-11-15  
**Status:** Planning Complete  
**Ready to Begin:** Phase 0 - Adapter Foundation

