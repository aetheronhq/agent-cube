# CodeRabbit CLI Judge Integration

**Status:** Planning Complete  
**Architecture:** Ports/Adapters (Hexagonal)  
**Integration Point:** Judge Panel System

---

## 🎯 Overview

This implementation adds CodeRabbit CLI as a third judge option in AgentCube's multi-judge review system. CodeRabbit provides objective, static-analysis-based code reviews that complement the subjective reviews from AI judges like GPT-4.5 and Gemini.

**Key Benefits:**
- **Objective Analysis:** Rules-based review catches issues AI might miss
- **Security Focus:** Identifies vulnerabilities and security anti-patterns
- **AI Slop Detection:** Flags hallucinations, incomplete error handling, edge cases
- **Consistent Scoring:** Deterministic evaluation based on measurable metrics

---

## 📐 Architecture

### Ports/Adapters Pattern

CodeRabbit integrates through the same adapter interface used by cursor-agent and gemini:

```
┌─────────────────────────────────────────┐
│         Judge Panel Orchestrator        │
│      (cube.automation.judge_panel)      │
└────────────────┬────────────────────────┘
                 │
                 ├─── CLIAdapter (Port/Interface)
                 │
    ┌────────────┼────────────┬────────────┐
    │            │            │            │
    ▼            ▼            ▼            ▼
┌────────┐  ┌────────┐  ┌────────────┐
│ Cursor │  │ Gemini │  │ CodeRabbit │  ← Adapters
│ Adapter│  │ Adapter│  │  Adapter   │
└────────┘  └────────┘  └────────────┘
    │            │            │
    ▼            ▼            ▼
┌────────┐  ┌────────┐  ┌────────────┐
│ Cursor │  │ Gemini │  │ CodeRabbit │  ← External CLIs
│  CLI   │  │  CLI   │  │    CLI     │
└────────┘  └────────┘  └────────────┘
```

**No Special Cases:** CodeRabbit is treated identically to other judges at the orchestration level.

### Components

1. **CodeRabbitAdapter** (`python/cube/core/adapters/coderabbit_adapter.py`)
   - Implements `CLIAdapter` interface
   - Executes `coderabbit review --json --plain --yes`
   - Yields JSON output lines for parsing

2. **CodeRabbitParser** (`python/cube/core/parsers/coderabbit_parser.py`)
   - Converts CodeRabbit JSON to `StreamMessage` format
   - Maps review comments, summaries, and errors
   - Handles malformed input gracefully

3. **Decision Generator** (`python/cube/core/coderabbit_decision.py`)
   - Analyzes CodeRabbit findings for both writers
   - Calculates scores across 5 categories
   - Generates standard judge decision JSON
   - Determines winner based on objective metrics

4. **Registry Integration**
   - Adapter registered in `core/adapters/registry.py`
   - Parser registered in `core/parsers/registry.py`
   - Configured via `cube.yaml`

---

## 📋 Task Breakdown

### Phase 0: Foundation (2-3 hours)
- **Task 01:** [CodeRabbit Adapter](tasks/01-coderabbit-adapter.md)
  - Implement `CLIAdapter` interface
  - Execute CodeRabbit CLI
  - Handle authentication and errors

### Phase 1: Parsing (2-3 hours)
- **Task 02:** [CodeRabbit Parser](tasks/02-coderabbit-parser.md)
  - Parse JSON output
  - Convert to StreamMessage format
  - Handle edge cases

### Phase 2: Decision Logic (4-5 hours)
- **Task 03:** [Decision Generation](tasks/03-decision-generation.md)
  - Implement scoring algorithm
  - Generate decision files
  - Winner determination logic

### Phase 3: Integration (3-4 hours)
- **Task 04:** [Integration & Testing](tasks/04-integration-testing.md)
  - Configuration integration
  - End-to-end testing
  - Documentation

**Total Estimate:** 11-15 hours

---

## 🔧 Configuration

### cube.yaml Example

```yaml
judges:
  judge_1:
    model: gpt-4.5
    cli_tool: cursor-agent
    label: "Judge 1 (GPT)"
    color: yellow
  
  judge_2:
    model: gemini-2.5-flash-thinking-exp-01-21
    cli_tool: gemini
    label: "Judge 2 (Gemini)"
    color: cyan
  
  judge_3:
    model: coderabbit
    cli_tool: coderabbit
    label: "Judge 3 (CodeRabbit)"
    color: magenta

cli_tools:
  gpt-4.5: cursor-agent
  gemini-2.5-flash-thinking-exp-01-21: gemini
  coderabbit: coderabbit
```

---

## 🎯 Scoring Algorithm

CodeRabbit evaluates both writers across 5 categories:

### Score Categories

| Category | Focus | Deduction Sources |
|----------|-------|-------------------|
| **type_safety** | Type correctness | Type errors, null checks, undefined vars |
| **production_ready** | Robustness | Security issues, error handling, edge cases |
| **tests** | Test coverage | Missing tests, test quality |
| **architecture** | Code structure | Organization, coupling, complexity |
| **kiss_compliance** | Simplicity | Over-engineering, unnecessary abstraction |

### Scoring Rules

```
Base score per category: 10

Deductions:
- Error severity:   -2.0 points
- Warning severity: -0.5 points
- Info severity:    -0.1 points

Total weighted score: Average of all 5 categories
```

### Winner Determination

```python
if abs(score_a - score_b) < 0.5:
    winner = "TIE"
elif score_a > score_b:
    winner = "A"
else:
    winner = "B"
```

### Decision Value

```python
if error_count == 0:
    decision = "APPROVED"
elif error_count > 10:
    decision = "REJECTED"
else:
    decision = "REQUEST_CHANGES"
```

---

## 📄 Decision File Format

CodeRabbit generates standard judge decision files at:
`.prompts/decisions/judge-{N}-{task_id}-decision.json`

### Schema

```json
{
  "judge": 3,
  "task_id": "example-task",
  "timestamp": "2025-11-15T10:30:00Z",
  "decision": "REQUEST_CHANGES",
  "winner": "A",
  "scores": {
    "writer_a": {
      "kiss_compliance": 9,
      "architecture": 8,
      "type_safety": 7,
      "tests": 8,
      "production_ready": 7,
      "total_weighted": 7.8
    },
    "writer_b": {
      "kiss_compliance": 8,
      "architecture": 7,
      "type_safety": 5,
      "production_ready": 4,
      "tests": 7,
      "total_weighted": 6.2
    }
  },
  "blocker_issues": [
    "writer-b/api.ts:55 - Missing error handling",
    "writer-b/api.ts:60 - SQL injection vulnerability"
  ],
  "recommendation": "Writer A preferred: fewer critical security issues (1 error vs 3 errors)"
}
```

---

## 🚀 Usage

### Installation

```bash
# Install CodeRabbit CLI
curl -fsSL https://get.coderabbit.ai/install.sh | sh

# Authenticate
coderabbit login

# Verify
coderabbit --version
```

### Running with CodeRabbit Judge

```bash
# 1. Run dual writers
cube writers my-task .prompts/my-task.md

# 2. Run judge panel (includes CodeRabbit if configured)
cube panel my-task .prompts/panel-prompt.md

# 3. Review decisions
ls .prompts/decisions/
cat .prompts/decisions/judge-3-my-task-decision.json

# 4. Synthesize results
cube synthesize my-task
```

CodeRabbit automatically participates when configured in `cube.yaml`.

---

## 🔍 How It Works

### Execution Flow

```
1. Judge Panel Starts
   └─> Fetch writer branches
   └─> Initialize 3 judges in parallel

2. CodeRabbit Judge Launches
   └─> Adapter: Execute `coderabbit review --json --plain --yes`
   └─> Parser: Convert JSON output to StreamMessages
   └─> Display: Show findings in terminal

3. Review Completion
   └─> Collect all issues (errors, warnings, info)
   └─> Calculate scores for writer A and B
   └─> Determine winner
   └─> Generate decision file

4. Synthesis
   └─> Read all 3 judge decisions
   └─> Aggregate votes
   └─> Select final winner
```

### CodeRabbit's Role

Unlike AI judges that provide subjective evaluation, CodeRabbit provides:
- **Static Analysis:** Rules-based code inspection
- **Security Scanning:** Identifies vulnerabilities
- **Best Practices:** Enforces coding standards
- **Objective Metrics:** Consistent, deterministic scoring

This complements AI judges by catching issues that LLMs might overlook.

---

## 🚫 What CodeRabbit Doesn't Do

- **No Subjective Judgment:** Can't evaluate "code elegance" or design taste
- **No Context Understanding:** Doesn't understand business logic intent
- **No Learning from Prompt:** Doesn't read task requirements (AI judges do this)
- **No Creative Suggestions:** Provides fixes but not alternative designs

CodeRabbit excels at objective, rules-based review. AI judges handle subjective evaluation.

---

## 📚 Planning Documents

- **[planning/coderabbit-judge.md](../../planning/coderabbit-judge.md)** - Complete architecture specification

Key sections:
- Principles: Ports/adapters, quality gate, consistent interface
- Requirements: Adapter, parser, decision generation
- Anti-patterns: What NOT to do
- Best practices: Integration guidelines

---

## 🧪 Testing Strategy

### Unit Testing

```python
# Test adapter
adapter = CodeRabbitAdapter()
assert adapter.check_installed() == True

# Test parser
parser = CodeRabbitParser()
msg = parser.parse('{"type": "review_comment", ...}')
assert msg.type == "tool_call"

# Test decision generation
decision = generate_decision(3, "task-01", issues_a, issues_b)
assert decision["winner"] in ["A", "B", "TIE"]
```

### Integration Testing

```bash
# End-to-end test
cube writers test-task .prompts/test-task.md
cube panel test-task .prompts/panel-prompt.md

# Verify decision file
cat .prompts/decisions/judge-3-test-task-decision.json | jq .
```

### Edge Cases

- No issues found (perfect code)
- Tie scenario (equal scores)
- Authentication failure
- Rate limit exceeded
- Network errors

---

## ⚠️ Limitations & Known Issues

### CodeRabbit CLI Limitations

1. **Rate Limits**
   - Free tier: 60 reviews/month
   - Pro tier: Higher limits

2. **No Session Resumption**
   - Unlike cursor-agent, CodeRabbit doesn't support resume
   - `resume` parameter is ignored

3. **Review Scope**
   - Reviews only changed files (git diff)
   - Full codebase review too slow

### Implementation Notes

1. **Authentication Required**
   - Must run `coderabbit login` before first use
   - Pre-flight check validates authentication

2. **Decision Generation**
   - Scoring algorithm is heuristic-based
   - May need tuning based on feedback

3. **Parser Robustness**
   - CodeRabbit output format may evolve
   - Parser handles unknown types gracefully

---

## 🛠️ Troubleshooting

### "CodeRabbit CLI not installed"

```bash
curl -fsSL https://get.coderabbit.ai/install.sh | sh
```

### "Not authenticated"

```bash
coderabbit login
```

### "Rate limit exceeded"

Wait until next month or upgrade to Pro plan.

### Decision file not generated

Check:
1. CodeRabbit review completed successfully
2. No errors in logs: `~/.cube/logs/judge-3-*.json`
3. Decision file path: `.prompts/decisions/judge-3-{task_id}-decision.json`

### Scores seem wrong

Scoring algorithm can be tuned in `coderabbit_decision.py`:
- Adjust severity deductions
- Modify category mappings
- Change tie threshold

---

## 📖 Resources

### External

- [CodeRabbit CLI Documentation](https://docs.coderabbit.ai/cli)
- [CodeRabbit CLI GitHub](https://github.com/coderabbitai/cli)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)

### Internal

- `python/cube/core/cli_adapter.py` - Adapter interface
- `python/cube/core/adapters/cursor_adapter.py` - Reference adapter
- `python/cube/automation/judge_panel.py` - Panel orchestration

---

## 🤝 Contributing

When working on CodeRabbit integration:

1. **Follow Adapter Pattern**
   - No special cases in orchestration
   - Implement interface exactly
   - Match existing adapter conventions

2. **KISS Principle**
   - Simple algorithms over complex ones
   - Keyword matching over NLP
   - Straightforward scoring over ML

3. **Test Thoroughly**
   - Unit tests for each component
   - Integration tests for full flow
   - Edge case coverage

4. **Document Changes**
   - Update README when adding features
   - Document breaking changes
   - Keep planning doc in sync

---

## 📋 Checklist for Implementation

- [ ] Task 01: CodeRabbit Adapter
  - [ ] Implements CLIAdapter
  - [ ] Executes CLI correctly
  - [ ] Registered in registry
- [ ] Task 02: CodeRabbit Parser
  - [ ] Parses JSON output
  - [ ] Returns StreamMessages
  - [ ] Registered in registry
- [ ] Task 03: Decision Generation
  - [ ] Scoring algorithm implemented
  - [ ] Decision file format correct
  - [ ] Winner determination logic
- [ ] Task 04: Integration
  - [ ] Configuration working
  - [ ] End-to-end testing complete
  - [ ] Documentation written

**When all tasks complete:**
- [ ] CodeRabbit fully integrated as judge
- [ ] Works in parallel with other judges
- [ ] Produces standard decision files
- [ ] Ready for production use

---

## 📄 License

Part of the AgentCube project. See main project LICENSE file.

---

**Built with:** Agent Cube v1.0  
**Last Updated:** 2025-11-15  
**Status:** Planning Complete, Ready for Implementation

