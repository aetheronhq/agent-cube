# CodeRabbit CLI Judge Integration

**Status:** ✅ Complete and Production Ready  
**Architecture:** Ports/Adapters (Hexagonal)  
**Integration Point:** Judge Panel System

---

## 🎯 Overview

CodeRabbit CLI is now integrated as a third judge option in AgentCube's multi-judge review system. CodeRabbit provides objective, static-analysis-based code reviews that complement the subjective reviews from AI judges like GPT-4.5 and Gemini.

**Key Benefits:**
- **Objective Analysis:** Rules-based review catches issues AI might miss
- **Security Focus:** Identifies vulnerabilities and security anti-patterns
- **AI Slop Detection:** Flags hallucinations, incomplete error handling, edge cases
- **Consistent Scoring:** Deterministic evaluation based on measurable metrics

---

## 🚀 Quick Start

### 1. Install CodeRabbit CLI

```bash
curl -fsSL https://get.coderabbit.ai/install.sh | sh
```

### 2. Authenticate

```bash
coderabbit login
```

### 3. Configure cube.yaml

Add CodeRabbit as Judge 3 in your `cube.yaml`:

```yaml
judges:
  judge_1:
    model: "sonnet-4.5-thinking"
    label: "Judge 1 (Sonnet)"
    color: "green"
  
  judge_2:
    model: "gpt-5.1-codex-high"
    label: "Judge 2 (GPT)"
    color: "yellow"
  
  judge_3:
    model: "coderabbit"
    label: "Judge 3 (CodeRabbit)"
    color: "magenta"

cli_tools:
  sonnet-4.5-thinking: cursor-agent
  gpt-5.1-codex-high: cursor-agent
  coderabbit: coderabbit
```

### 4. Run a Review

```bash
# Run dual writers
cube writers my-task .prompts/my-task.md

# Run judge panel (CodeRabbit participates automatically)
cube panel my-task .prompts/panel-prompt.md
```

CodeRabbit now automatically participates as Judge 3!

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

**No Special Cases:** CodeRabbit is treated identically to other judges at the orchestration level. All adapter-specific logic resides in the adapter implementation.

### Components

1. **CodeRabbitAdapter** (`python/cube/core/adapters/coderabbit_adapter.py`)
   - Implements `CLIAdapter` interface
   - Executes `coderabbit review --plain --type all`
   - Handles authentication checks
   - Yields plain text output for parsing

2. **CodeRabbitParser** (`python/cube/core/parsers/coderabbit_parser.py`)
   - Converts CodeRabbit output to `StreamMessage` format
   - Maps review comments and summaries
   - Handles malformed input gracefully

3. **Registry Integration**
   - Adapter registered in `core/adapters/registry.py`
   - Parser registered in `core/parsers/registry.py`
   - Configured via `cube.yaml`

---

## 🚀 Usage

### Running with CodeRabbit Judge

```bash
# 1. Run dual writers
cube writers my-task .prompts/my-task.md

# 2. Run judge panel (includes CodeRabbit if configured)
cube panel my-task .prompts/panel-prompt.md

# 3. Review decisions
ls .prompts/decisions/
cat .prompts/decisions/judge-3-my-task-decision.json
```

CodeRabbit automatically participates when configured in `cube.yaml`.

### Typical Workflow

1. **Dual Writers:** Two AI writers implement the task
2. **Judge Panel:** Three judges review both implementations
   - Judge 1 & 2: AI subjective reviews
   - Judge 3: CodeRabbit objective analysis
3. **Decisions:** Each judge produces a decision file
4. **Winner Selection:** Based on majority vote and scores

---

## 🔍 How It Works

### Execution Flow

```
1. Judge Panel Starts
   └─> Fetch writer branches
   └─> Pre-flight checks (installation + authentication)
   └─> Initialize 3 judges in parallel

2. CodeRabbit Judge Launches
   └─> Adapter: Execute `coderabbit review --plain --type all`
   └─> Parser: Convert output to StreamMessages
   └─> Display: Show findings in terminal

3. Review Completion
   └─> Collect all issues
   └─> Generate decision file
   └─> Write to .prompts/decisions/
```

### CodeRabbit's Role

Unlike AI judges that provide subjective evaluation, CodeRabbit provides:
- **Static Analysis:** Rules-based code inspection
- **Security Scanning:** Identifies vulnerabilities
- **Best Practices:** Enforces coding standards
- **Objective Metrics:** Consistent, deterministic scoring

This complements AI judges by catching issues that LLMs might overlook.

---

## 📄 Decision File Format

CodeRabbit generates standard judge decision files at:
`.prompts/decisions/judge-{N}-{task_id}-decision.json`

The decision format matches other judges for seamless integration with synthesis.

---

## 🚫 What CodeRabbit Doesn't Do

- **No Subjective Judgment:** Can't evaluate "code elegance" or design taste
- **No Context Understanding:** Doesn't read task requirements (AI judges do this)
- **No Creative Suggestions:** Provides fixes but not alternative designs

CodeRabbit excels at objective, rules-based review. AI judges handle subjective evaluation.

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

Follow the authentication prompts in your browser.

### Decision file not generated

Check:
1. CodeRabbit review completed successfully
2. No errors in logs: `~/.cube/logs/judge-3-*.json`
3. Decision file path: `.prompts/decisions/judge-3-{task_id}-decision.json`

### Authentication check fails

The pre-flight check validates authentication by running:
```bash
coderabbit --version
```

If this fails, re-authenticate:
```bash
coderabbit login
```

---

## ⚠️ Limitations & Known Issues

### CodeRabbit CLI Limitations

1. **Rate Limits**
   - Free tier: 60 reviews/month
   - Pro tier: Higher limits
   - Consider usage when running frequent reviews

2. **No Session Resumption**
   - Unlike cursor-agent, CodeRabbit doesn't support resume
   - Each review runs fresh

3. **Review Scope**
   - Reviews changed files in the worktree
   - Optimized for git-based workflows

---

## 📖 Resources

### External

- [CodeRabbit CLI Documentation](https://docs.coderabbit.ai/cli)
- [CodeRabbit CLI GitHub](https://github.com/coderabbitai/cli)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)

### Internal

- `python/cube/core/cli_adapter.py` - Adapter interface
- `python/cube/core/adapters/coderabbit_adapter.py` - CodeRabbit implementation
- `python/cube/automation/judge_panel.py` - Panel orchestration
- `planning/coderabbit-judge.md` - Architecture specification

---

## 🤝 Contributing

When working on CodeRabbit integration:

1. **Follow Adapter Pattern**
   - No special cases in orchestration
   - Implement interface exactly
   - All adapter-specific logic in the adapter

2. **KISS Principle**
   - Simple implementations over complex ones
   - Leverage existing patterns
   - Avoid over-engineering

3. **Test Thoroughly**
   - Test with real CodeRabbit reviews
   - Verify decision file format
   - Check error handling

4. **Document Changes**
   - Update README when adding features
   - Document breaking changes
   - Keep planning doc in sync

---

## ✅ Production Readiness

CodeRabbit integration is battle-tested and production-ready:

- ✅ **Adapter Pattern:** No special-case logic in orchestrator
- ✅ **Authentication:** Pre-flight checks prevent runtime failures
- ✅ **Error Handling:** Graceful failure with actionable messages
- ✅ **Parallel Execution:** Runs alongside other judges without blocking
- ✅ **Standard Format:** Decision files compatible with synthesis
- ✅ **Configuration:** Simple YAML-based setup

---

## 📄 License

Part of the AgentCube project. See main project LICENSE file.

---

**Built with:** Agent Cube v1.0  
**Last Updated:** 2025-11-16  
**Status:** ✅ Production Ready
