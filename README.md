# 🧊 Agent Cube

**Autonomous multi-agent coding workflow with competitive development and judicial review**

```bash
# Two AI coders compete. Three judges pick the winner.
cube auto task.md
```

[![GitHub stars](https://img.shields.io/github/stars/aetheronhq/agent-cube?style=flat&color=94FFBC)](https://github.com/aetheronhq/agent-cube)
[![License](https://img.shields.io/github/license/aetheronhq/agent-cube?color=94FFBC)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-94FFBC)](https://python.org)

---

## 🚀 **What Is Agent Cube?**

A self-improving coding workflow that orchestrates multiple AI agents to build production-ready features autonomously.

**The Process:**
1. **2 AI writers** implement the same task independently (Sonnet + Codex)
2. **3 AI judges** review both implementations
3. **System picks winner** or synthesizes best of both
4. **Peer review validates** final solution
5. **PR automatically created** for human approval

**The Result:**
- 7x productivity improvement (conservative estimate)
- Dual approaches evaluated (not just 1)
- 3 independent reviews per feature
- Institutional knowledge captured
- Production-ready code

---

## ⚡ **Quick Start**

### **Install**

```bash
git clone https://github.com/aetheronhq/agent-cube.git
cd agent-cube
./install.sh
```

**Prerequisites:** [cursor-agent CLI](https://cursor.com)

### **Your First Task**

```bash
# Create a task file
cat > my-task.md << 'EOF'
# Add String Utilities

Create capitalize() and slugify() functions in TypeScript.
Include tests. No external dependencies.
EOF

# Run autonomous workflow
cube auto my-task.md

# Watch it work (optional)
cube status my-task

# PR created automatically!
```

---

## 📚 **Documentation**

### **Getting Started**
- [Quick Start Guide](docs/QUICK_START.md) - 5 commands, 5 minutes
- [Installation](INSTALL.md) - Detailed setup
- [Core Concepts](AGENT_CUBE.md) - Framework overview

### **Planning & Process**
- [Planning Guide](docs/PLANNING_GUIDE.md) - Architecture-first planning (v2 example)
- [Task Breakdown](docs/TASK_BREAKDOWN.md) - How to split features
- [Phase Organization](docs/PHASE_ORGANIZATION.md) - How phases emerge
- [Templates](templates/) - Planning docs + task file templates

### **Usage**
- [Automation Guide](AGENT_CUBE_AUTOMATION.md) - Autonomous workflows
- [Human-in-Loop](docs/HUMAN_IN_LOOP.md) - When and how to intervene

---

## 🎯 **The 4 Essential Commands**

```bash
# 1. Start autonomous workflow
cube auto task.md

# 2. Check progress
cube status task

# 3. See decisions
cube decide task

# 4. Resume/continue
cube auto task --resume
```

**That's it.** The tool guides you for everything else.

---

## 🏗️ **Architecture**

### **Agents³ = Cube**

**Layer 1: Orchestrator**
- Plans workflow
- Breaks down features
- Coordinates execution

**Layer 2: Prompt Writers**
- Generate detailed task prompts
- Create judge panel prompts
- Generate synthesis feedback

**Layer 3: Code Writers + Judges**
- 2 writers compete (different models)
- 3 judges independently review
- System picks winner or synthesizes

### **Technical Foundation**

**Git Worktrees:**
- Each agent gets isolated filesystem
- Own branch, own git state
- Zero conflicts, true parallelization

**Ports & Adapters:**
- Pluggable CLI adapters (cursor-agent, gemini, etc.)
- Parser plugins for output formats
- Layout adapters for display

**State Management:**
- Explicit phase tracking
- Resume from any point
- Atomic writes, no corruption

---

## 📊 **Proven Results**

### **Aetheron Connect v2 (Oct-Nov 2025)**

**Output:**
- 15 production features
- ~34,000 lines of code
- Multi-tenancy, Auth0, CRUD factory, OpenAPI + SDK
- Production-ready quality (full tests, security scans, CI passing)

**Timeline:**
- 15 active work days
- 1 developer + Agent Cube
- vs 7-8 person team traditionally

**Economics:**
- Cost: $15k (salary + LLM)
- Traditional: $63-96k
- **Savings: $48-81k (75-85%)**

**Quality:**
- Synthesis improved 40% of tasks
- Multiple feedback rounds caught bugs early
- Comprehensive test coverage

### **Model Performance Patterns**

**Sonnet 4.5:** UI/Frontend wins (3-0, 100%)
**Codex High:** Backend wins (7/8, 88%)
**Grok:** Best balanced judge

**Insight:** Task-model matching > using "best model" for everything

---

## ⚙️ **Configuration**

Fully customizable - use any models you want:

```yaml
# python/cube.yaml
writers:
  writer_a:
    model: "sonnet-4.5-thinking"
  writer_b:
    model: "gpt-5-codex-high"

judges:
  judge_1:
    model: "sonnet-4.5-thinking"
  judge_2:
    model: "gpt-5-codex-high"
  judge_3:
    model: "gemini-2.5-pro"  # Or grok, claude-code, etc.

cli_tools:
  sonnet-4.5-thinking: cursor-agent
  gpt-5-codex-high: cursor-agent
  gemini-2.5-pro: gemini
```

**No vendor lock-in. Fully extensible.**

---

## 🎓 **Key Concepts**

### **Competitive Development**
Two AI models implement the same task independently. Different approaches reveal trade-offs.

### **Judicial Review**
Three independent AI judges review both implementations. Majority vote or consensus determines winner.

###

 **Synthesis**
When both approaches have merit, system combines best elements. 40% of v2 features improved this way.

### **Human-in-the-Loop**
~5 interventions per complex feature. Tool provides clear guidance when it needs help.

### **The AI Village**
Like pair programming × 5. Multiple perspectives, ideas you wouldn't have thought of, issues you would've missed.

---

## 🔍 **When to Use Agent Cube**

### **✅ Good For:**
- New features (2-8 hours scope)
- Complex architecture decisions
- Refactoring (multiple valid approaches)
- Production-critical code (needs thorough review)

### **❌ Not Good For:**
- Tiny changes (<1 hour)
- Emergency hotfixes (too slow)
- Experimental code (unclear requirements)
- Simple scaffolding (overkill)

**The sweet spot:** Features where exploring alternatives adds value

---

## 🐛 **Known Limitations**

**Current Issues:**
- Gemini decision filing: ~30% failure rate (improving!)
- Requires cursor-agent CLI setup
- $200-400 per feature LLM costs (4-5x ROI though)
- Learning curve for planning docs
- Human validation always required

**All improving weekly. Rapid iteration.**

---

## 🗺️ **Roadmap**

**This Month:**
- Web UI for managing multiple workflows
- Integration test framework
- More CLI adapters (Claude Code, Codex CLI direct)

**This Quarter:**
- Auto-orchestration (dependency-based task execution)
- Cost tracking and analytics
- Learning system (model selection optimization)
- Team collaboration features

---

## 🤝 **Contributing**

Found a bug? Have an idea? Want to help?

**Raise an issue:** https://github.com/aetheronhq/agent-cube/issues

We'll use Agent Cube to fix Agent Cube! 🎯

---

## 📖 **Example: v2 Project Structure**

See [aetheron-connect-v2](https://github.com/aetheronhq/aetheron-connect-v2) for complete example:

```
planning/               # 33 architecture docs
implementation/
├── phase-00/          # Scaffold
├── phase-01/          # Foundation
├── phase-02/          # Core (9 parallel tasks!)
│   └── tasks/
│       ├── 02-auth-middleware.md
│       ├── 02-crud-factory.md
│       └── ...
└── panel/
    └── panel-metrics.md  # All decisions, scores, learnings
```

**Learn from a real project that shipped!**

---

## 🎬 **The Claim**

**7x productivity improvement** (conservative estimate)
- 1 person = 2 teams' output
- 3-5x ROI on cost
- Higher quality through competition
- Validated on real projects

**Not replacing engineers. Multiplying output.**

---

## 📞 **Support**

- **Documentation:** Start with [docs/QUICK_START.md](docs/QUICK_START.md)
- **Issues:** GitHub Issues
- **Questions:** Slack @jacob (internal) or GitHub Discussions

---

## 📄 **License**

MIT License - see [LICENSE](LICENSE) file

---

**Built with Agent Cube, for Agent Cube.** 🧊✨
# Test Change
