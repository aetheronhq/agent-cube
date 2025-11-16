# CodeRabbit CLI Judge Integration

Quick reference for implementing CodeRabbit as a judge in AgentCube.

---

## 📍 Location

**Planning Documents:**
- **Architecture:** [planning/coderabbit-judge.md](../planning/coderabbit-judge.md)
- **Implementation:** [implementation/coderabbit-judge/](../implementation/coderabbit-judge/)

---

## 📖 What to Read

### Start Here
1. [implementation/coderabbit-judge/README.md](../implementation/coderabbit-judge/README.md)
   - Overview and architecture
   - How CodeRabbit works as a judge
   - Usage instructions

### For Implementation
2. [planning/coderabbit-judge.md](../planning/coderabbit-judge.md)
   - Complete architecture specification
   - Technical requirements
   - Anti-patterns and best practices

3. [implementation/coderabbit-judge/PHASES.md](../implementation/coderabbit-judge/PHASES.md)
   - Phase breakdown
   - Milestones and testing strategy

### Task Files
4. [implementation/coderabbit-judge/tasks/](../implementation/coderabbit-judge/tasks/)
   - 01-coderabbit-adapter.md (3-4 hours)
   - 02-coderabbit-parser.md (2-3 hours)
   - 03-decision-generation.md (4-5 hours)
   - 04-integration-testing.md (3-4 hours)

---

## 🎯 Quick Summary

### What is This?

Integration of CodeRabbit CLI as a third judge option in AgentCube's multi-judge review system.

### Why?

- **Objective Analysis:** Rules-based review catches issues AI might miss
- **Security Focus:** Identifies vulnerabilities and security anti-patterns  
- **AI Slop Detection:** Flags hallucinations, incomplete error handling
- **Consistent Scoring:** Deterministic evaluation based on measurable metrics

### How?

Uses ports/adapters pattern:
- CodeRabbitAdapter implements CLIAdapter interface
- CodeRabbitParser converts output to StreamMessages
- Decision generator creates standard judge decision files
- No special-case logic needed in orchestration

---

## 🏗️ Architecture

```
Judge Panel Orchestrator
         │
         ├─── CLIAdapter (Port)
         │
    ┌────┴────┬────────────┐
    │         │            │
    ▼         ▼            ▼
 Cursor    Gemini    CodeRabbit  ← New Adapter
 Adapter   Adapter    Adapter
```

**Key Points:**
- Clean separation of concerns
- Same interface as other judges
- Standard decision format
- Parallel execution

---

## 📋 Tasks Overview

| Task | Component | Time | Deliverable |
|------|-----------|------|-------------|
| 01 | Adapter | 3-4h | Execute CodeRabbit CLI |
| 02 | Parser | 2-3h | Parse JSON to StreamMessages |
| 03 | Decision | 4-5h | Generate decision files |
| 04 | Integration | 3-4h | Config, testing, docs |

**Total:** 11-15 hours

---

## 🚀 Quick Start

### For Developers

```bash
# 1. Read the planning doc
cat planning/coderabbit-judge.md

# 2. Read the overview
cat implementation/coderabbit-judge/README.md

# 3. Start with Task 01
cat implementation/coderabbit-judge/tasks/01-coderabbit-adapter.md

# 4. Implement sequentially (01 → 02 → 03 → 04)
```

### For AI Agents

```markdown
Implement CodeRabbit CLI integration as a judge in AgentCube.

**Planning Doc (Golden Source):**
planning/coderabbit-judge.md

**Your Task:**
implementation/coderabbit-judge/tasks/01-coderabbit-adapter.md

**Context:**
- Ports/adapters architecture
- Implement CLIAdapter interface
- Follow KISS principles
- No special-case logic
```

---

## ✅ Success Criteria

When complete, you should be able to:

1. Configure CodeRabbit as judge in `cube.yaml`
2. Run `cube panel` with CodeRabbit as one of 3 judges
3. See CodeRabbit review both writer implementations
4. Get decision file at `.prompts/decisions/judge-3-{task_id}-decision.json`
5. Synthesize results including CodeRabbit's vote

**All without any special-case logic or commands.**

---

## 📚 Key Documents

| Document | Purpose |
|----------|---------|
| [planning/coderabbit-judge.md](../planning/coderabbit-judge.md) | Architecture specification |
| [implementation/coderabbit-judge/README.md](../implementation/coderabbit-judge/README.md) | Overview and usage |
| [implementation/coderabbit-judge/PHASES.md](../implementation/coderabbit-judge/PHASES.md) | Phase breakdown |
| [implementation/coderabbit-judge/PLANNING_COMPLETE.md](../implementation/coderabbit-judge/PLANNING_COMPLETE.md) | Planning summary |

---

## 🔗 Related Features

- **Judge Panel System:** `python/cube/automation/judge_panel.py`
- **Adapter Pattern:** `python/cube/core/adapters/`
- **Decision Files:** `.prompts/decisions/`
- **Configuration:** `python/cube.yaml`

---

## 📞 Questions?

Refer to:
1. Planning doc for architecture decisions
2. README for usage and examples
3. Task files for specific implementation guidance
4. Existing adapters (cursor, gemini) for patterns

---

**Status:** Planning Complete ✅  
**Ready for Implementation:** Yes  
**Last Updated:** 2025-11-15

