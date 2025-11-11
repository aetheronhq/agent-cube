---
marp: true
theme: dark
paginate: true
footer: 'Agent Cube | Nov 2025'
---

<!-- _class: lead -->

# 🎲 The Agent Cube

**Resistance is Futile**

Jacob Ellis
Dev Forum Special Edition

---

<!-- _class: lead -->

# Last 2.5 Weeks

**Built TWO things simultaneously:**

**v2:** 15 features, 10k LOC, 0 bugs
**Agent Cube:** Complete tool, 3.5k LOC

**1 person. Working nights & weekends.**

vs Traditional: 7-8 person team, 2-3 months

---

# The Economics - Honest

**Agent Cube costs $200/feature**
Premium models, 10+ agents, iterations
This is real money.

**BUT...**

| Approach | Time | Cost |
|----------|------|------|
| **Me + Cube** | 12 days | $12k |
| **7-8 person team** | 12 days | $50k |

**7x productivity (conservative!)**
Could argue 10-15x (2 separate projects)

---

<!-- _class: lead -->

# Meta-Moment²

**These slides?**

**Agent Cube planned them.**
**Leo's techdecks built them.**

Process:
1. Cube: 2 writers → 3 judges → winning outline
2. techdecks: Markdown → beautiful presentation

AI planned. AI built. Human presents.

**You're experiencing the winner.**

---

# Agents³ = Cube

```
Agents controlling Agents controlling Agents

Layer 1: Orchestrator (plans workflow)
Layer 2: Writers (2 competing implementations)  
Layer 3: Judges (3 independent reviews)

Agents³ = Cube
```

"We cubed the agents."

---

# Git Worktrees - The Foundation

**How 18 agents run without conflicts:**

```
Main: /aetheron-connect-v2
Writer A: ~/.cube/worktrees/.../writer-sonnet-task/
Writer B: ~/.cube/worktrees/.../writer-codex-task/
× 6 more for parallel tasks
```

**Each agent gets:**
✅ Own branch
✅ Own filesystem  
✅ Own git state

**Result:** Zero conflicts, true parallelization

---

# The F1 Analogy

| F1 Racing | Agent Cube |
|-----------|------------|
| 2 drivers compete | 2 AI writers |
| Telemetry analysis | 3 AI judges |
| Best strategy wins | Best code merges |

**Competition drives quality**

---

<!-- _class: lead -->

# Live Demo

**Building Agent Cube Web UI**

*[Play Loom recording here]*

---

# The Planning Process

**Architecture-first, not feature-first**

```
planning/
├── api-conventions.md (errors, pagination)
├── crud-factory.md (resource patterns)
├── db-conventions.md (schemas, RLS)
└── ...33 documents total
```

**Process:**
1. Architecture meetings → Planning docs
2. Orchestrator reads & proposes tasks
3. Phases emerge from dependencies
4. Plans evolve (85% → 100%)

---

# The Science

**Research-backed approach:**

1. **Best-of-N Sampling** - Anthropic (35% error reduction)
2. **LLM-as-Judge** - 85% human agreement
3. **Self-Refine Loops** - Iterative improvement
4. **Multi-Model Ensembles** - Diversity wins
5. **Cursor 2.0** - Direct inspiration

**Not experimental. Proven.**

---

# Model Performance Patterns

**From 15 v2 features:**

**Sonnet 4.5 wins:**
✅ UI/Frontend (3-0 record)
✅ Documentation
✅ Simple solutions

**Codex High wins:**
✅ Backend complexity (7/8 tasks)
✅ Type-heavy code
✅ Security features
✅ Integration tests

**Insight:** Task-model matching > "best model"

---

# Maximum Parallelization

**Real screenshot: 3 tasks simultaneously**

```
Task 1: 04-exemplar (6 agents)
Task 2: 05-feature-flags (6 agents)
Task 3: 05-rate-limit (6 agents)

18 AI agents working
0 conflicts
0 human time
```

**Building 3 features at once ⚡🔥**

Traditional: 6 days sequential
Agent Cube: 1 day parallel

---

# The Synthesis Power

**40% of tasks improved via synthesis:**

- Error Handler: Codex types + Sonnet tests
- API Server: Sonnet logging + Codex patterns  
- SDK: Codex impl + Sonnet modern deps

**Better than either approach alone!**

---

# The Human Catch ⚠️

**Task:** 01-api-client-scaffold

```
Panel:  3/3 APPROVED ✅
Peer:   3/3 APPROVED ✅
Human:  REJECTED ❌
```

**All 3 judges missed:** Wrong architecture

**Lesson:** AI assistance, NOT replacement
Human validation essential

---

# The Audit Trail - Data Goldmine

**Everything preserved:**

📊 Panel decisions (every vote, score, blocker)
🔄 Peer reviews (iteration tracking)
📝 Agent logs (~2MB each - every thought!)
💾 Workflow state (resume from any point)

**The goldmine:**
- Model performance analysis
- Quality trends
- Cost tracking
- Pattern library

**Storage:** ~2MB per feature
**Value:** Compounds forever

---

# Human-in-the-Loop

**Guided automation, not magic:**

**Common interventions (~5 per feature):**
- Judge doesn't save decision
- Synthesis needs clarification
- Network errors

**The tool tells you exactly what to do:**
```
cube resume judge-3 task "Write decision JSON"
```

**Goal:** 5 interventions today → 1-2 next quarter

**But always:** Human validates final PR

---

# The 5 Commands

```bash
# 1. Autonomous workflow
cube auto task.md

# 2. Check progress
cube status task

# 3. See decisions  
cube decide task

# 4. Intervene
cube resume agent task "message"

# 5. Clean up
cube clean task
```

**That's it. Everything else is handled.**

---

# The Future

**This Week:** Web UI (you saw it being built!)
**This Month:** Integration tests, more CLIs
**This Quarter:** Learning system, cost tracking

**Limitations (honest):**
- Gemini quirks (~30% decision filing issues)
- Setup requires cursor-agent
- ~$200/feature LLM cost

**All improving weekly!**

---

<!-- _class: lead -->

# The Ask

**Try ONE task this week**

**Raise GitHub issues** (Cube fixes them!)

**Slack me feedback** anytime

**github.com/aetheronhq/agent-cube**

---

<!-- _class: lead -->

# Questions?

**Let's talk**

Agent Cube: 7x productivity
Proven. Real. Ready to use.

Your turn to try it.

---

