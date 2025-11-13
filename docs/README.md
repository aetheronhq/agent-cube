# Agent Cube Documentation

**Comprehensive guides for using Agent Cube**

---

## 📚 **Documentation Index**

### **For New Users**

**Start here:**
1. [Quick Start Guide](QUICK_START.md) - 5 commands in 5 minutes
2. [Core Concepts](../AGENT_CUBE.md) - Framework overview
3. [Automation Guide](../AGENT_CUBE_AUTOMATION.md) - Autonomous workflows

### **For Planning**

**Creating effective specifications:**
1. [Planning Guide](PLANNING_GUIDE.md) - Architecture-first planning with v2 example
2. [Task Breakdown Guide](TASK_BREAKDOWN.md) - How to split features for dual-writer comparison
3. [Phase Organization](PHASE_ORGANIZATION.md) - How dependency-driven phases emerge
4. [Templates](../templates/) - Ready-to-use planning doc and task templates

### **For Advanced Users**

1. [Human-in-the-Loop](HUMAN_IN_LOOP.md) - When and how to intervene (~5 times per feature)
2. [Configuration](../python/cube.yaml) - Customize models, CLIs, behavior

---

## 🎯 **The Agent Cube Workflow**

```
Planning Docs (Human)
        ↓
Orchestrator Analyzes (AI)
        ↓
Tasks + Phases Proposed (AI)
        ↓
    FOR EACH TASK:
        ↓
   Dual Writers (AI)
        ↓
   Judge Panel (AI)  
        ↓
  Winner or Synthesis
        ↓
   Peer Review (AI)
        ↓
    PR Created
        ↓
Human Review + Merge
```

**Autonomous execution. Human validation. Continuous improvement.**

---

## 📖 **Learning Path**

**Day 1:** Install + Run first task
- Follow [Quick Start](QUICK_START.md)
- Try simple utility function
- See full workflow

**Day 2:** Understand the process
- Read [Planning Guide](PLANNING_GUIDE.md)
- Study v2 example structure
- Learn task breakdown principles

**Week 1:** Plan and execute a real feature
- Create planning docs (use templates)
- Break into 2-4 tasks
- Run `cube auto` on each
- Review results

**Month 1:** Master the workflow
- Optimize model selection
- Build pattern library
- Contribute improvements

---

## 🏆 **Proven Results**

**Aetheron Connect v2:**
- 15 features in 15 work days
- ~34k LOC, production-ready
- 7x productivity vs traditional team
- 40% of tasks improved via synthesis

**Web UI (Built Nov 11, 2025):**
- 6 tasks in 4 hours
- React + FastAPI + Components
- 50% synthesis rate
- $250 cost vs $1,400 traditional

---

## 🤔 **Common Questions**

**Q: Do I need planning docs?**
A: For best results, yes. The more context agents have, the better they perform.

**Q: How much does it cost?**
A: ~$200-400 per feature in LLM costs. 4-5x ROI vs engineer time.

**Q: Can I use different models?**
A: Yes! Fully configurable. Mix any models via `python/cube.yaml`.

**Q: What if something breaks?**
A: Tool tells you exactly what to do. Usually: `cube auto task --resume`

**Q: Do I still need to review code?**
A: YES! Human validation is essential. AI assists, doesn't replace.

---

## 🔗 **External Resources**

**Inspiration:**
- [OpenSpec.dev](https://openspec.dev) - Specification format inspiration
- [Cursor 2.0](https://cursor.com) - Multi-agent approach
- [Anthropic Research](https://anthropic.com) - Constitutional AI, Best-of-N

**Research Papers:**
- Constitutional AI (Anthropic, 2022)
- Judging LLM-as-a-Judge (Zheng et al., 2023)
- Self-Refine (Madaan et al., 2023)

---

## 🎬 **Next Steps**

1. Read [Quick Start](QUICK_START.md)
2. Try ONE simple task
3. Raise issues if you hit problems
4. Share feedback

**Welcome to the Agent Cube!** 🧊✨
