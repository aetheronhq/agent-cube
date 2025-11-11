# The Audit Trail - Why We Keep Everything

**Every decision, every thought, every iteration - preserved forever**

---

## ��️ **What Gets Saved**

### **1. Panel Decisions (JSON)**
```
.prompts/decisions/
├── judge-1-task-decision.json
├── judge-2-task-decision.json
├── judge-3-task-decision.json
└── task-aggregated.json
```

**Contains:**
- Scores for each writer (A vs B)
- Blocker issues
- Recommendations
- Vote (APPROVED/REQUEST_CHANGES)
- Timestamp

**Why:** Complete record of why decisions were made

### **2. Peer Review Decisions**
```
.prompts/decisions/
├── judge-1-task-peer-review.json
├── judge-2-task-peer-review.json
└── judge-3-task-peer-review.json
```

**Contains:**
- Were synthesis changes verified?
- Remaining issues?
- Ready to merge decision

**Why:** Tracks iteration quality

### **3. Agent Logs (Full JSON)**
```
~/.cube/logs/
├── writer-sonnet-task-timestamp.json
├── writer-codex-task-timestamp.json
├── judge-1-task-panel-timestamp.json
└── ...
```

**Contains:**
- Every thought (thinking stream)
- Every tool call (read, write, shell)
- Full conversation
- Timestamps

**Why:** Complete audit trail of what agents did

### **4. Session IDs**
```
.agent-sessions/
├── WRITER_A_task_SESSION_ID.txt
├── JUDGE_1_task_panel_SESSION_ID.txt
└── ...
```

**Contains:**
- Session identifiers
- Metadata (model, timestamp)

**Why:** Can resume any agent, any time

### **5. Workflow State**
```
~/.cube/state/
└── task.json
```

**Contains:**
- Current phase
- Completed phases
- Winner
- Path (SYNTHESIS/FEEDBACK/MERGE)

**Why:** Resume from any point

### **6. Generated Prompts**
```
.prompts/
├── writer-prompt-task.md
├── panel-prompt-task.md
├── synthesis-task.md
└── peer-review-task.md
```

**Contains:**
- Exact instructions given to agents
- Context provided
- Requirements specified

**Why:** Reproduce decisions, improve prompts

---

## 💎 **The Goldmine**

### **Analysis Opportunities**

**1. Model Performance**
```python
# From panel decisions:
sonnet_wins = sum(1 for d in decisions if d['winner'] == 'A')
codex_wins = sum(1 for d in decisions if d['winner'] == 'B')

# Pattern discovery:
frontend_tasks = [t for t in tasks if 'frontend' in t]
sonnet_frontend_wins = ... # 100% !

# Insight: Sonnet dominates UI
```

**2. Quality Trends**
```python
# Score improvements over time
# Synthesis effectiveness
# Iteration patterns
# Judge agreement rates
```

**3. Cost Analysis**
```python
# From logs: Token counts
# Time per phase
# Cost per feature
# ROI calculations
```

**4. Decision Patterns**
```python
# Which issues judges catch
# Common synthesis patterns
# Model blind spots
# When humans intervene
```

### **Business Intelligence**

**v2 Insights Discovered:**
- Codex: 88% backend win rate
- Sonnet: 100% frontend win rate
- 40% synthesis improvement rate
- Judge 1 (Sonnet): Catches KISS violations
- Judge 2 (Codex): Catches type/security issues
- Judge 3 (Grok): Balances both

**Actionable:**
- Route UI tasks to Sonnet
- Route backend to Codex
- Expect synthesis on complex features
- Budget for 1.5 feedback rounds average

---

## 🔍 **Audit Capabilities**

### **Compliance**

**Question:** "Why did we choose implementation B?"

**Answer:** Complete audit trail:
1. Panel decisions show scores (A: 6.5, B: 8.9)
2. Judge 1 reasoning in logs
3. Judge 2 reasoning in logs
4. Judge 3 reasoning in logs
5. Synthesis notes if applied
6. Peer review validation
7. Timestamp of final approval

**Traceable from idea → merged PR!**

### **Debugging**

**Question:** "Why did this feature have bugs?"

**Answer:** Check the trail:
1. Were requirements clear? (task file)
2. Did judges catch issues? (decisions)
3. Was synthesis applied correctly? (logs)
4. Did peer review pass? (peer decisions)
5. What did agents miss? (compare to bug)

**Learning:** Improve prompts, planning, or add checks

### **Improvement**

**Question:** "How do we get better at X?"

**Answer:** Mine the data:
- Which prompts led to better code?
- Which planning docs were most effective?
- Which models excel at what?
- What synthesis patterns work?

**Continuous improvement from data!**

---

## 📊 **Data Retention**

**Current:**
- Sessions: Keep forever (small files)
- Decisions: Keep forever (learning data!)
- Logs: Keep 30 days (large, can archive)
- State: Keep until task done
- Prompts: Keep forever (reproducibility)

**Storage:**
- Sessions: ~100KB per task
- Decisions: ~50KB per task
- Logs: ~500KB - 2MB per task
- Total: ~1-3MB per feature

**For 100 features:** ~100-300MB (tiny!)

---

## 🎓 **Teaching Tool**

**The saved data is PERFECT for:**

**1. Onboarding**
- "Here's how we built CRUD factory"
- Show decisions, iterations, synthesis
- New devs learn patterns

**2. Best Practices**
- "This is what good looks like"
- Compare winning vs losing approaches
- Share with team

**3. Post-Mortems**
- "What went wrong?"
- Full context available
- Learn and improve

**4. Research**
- "Which prompts work best?"
- "How does synthesis improve quality?"
- Publishable insights!

---

## 🚀 **The Pitch**

**For the Session:**

"We don't just build features. We build a knowledge base.

Every decision is preserved.
Every iteration is tracked.
Every agent's reasoning is captured.

This isn't just automation.
It's institutional knowledge, compounding.

In 6 months, we'll have data on:
- Which models excel at what
- Which patterns work best
- How to optimize prompts
- What synthesis strategies succeed

This data is more valuable than the code.
It's how we get smarter, faster."

---

**ADD THIS TO SLIDE 14 or 15!** ��
