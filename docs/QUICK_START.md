# Agent Cube - Quick Start

**Get from idea to PR in 30 minutes**

---

## ⚡ **5-Minute Setup**

```bash
# 1. Clone
git clone https://github.com/aetheronhq/agent-cube.git
cd agent-cube

# 2. Install
./install.sh

# 3. Verify
cube --version
```

**Prerequisites:** cursor-agent CLI (install: https://cursor.com)

---

## 🚀 **Your First Autonomous Workflow**

### **Step 1: Create a task file (2min)**

```bash
cat > my-task.md << 'EOF'
# Task: Add String Utilities

Create TypeScript utility functions:
- capitalize(str) - Capitalize first letter
- slugify(str) - Convert to URL slug

Requirements:
- TypeScript strict mode
- Comprehensive tests
- No external dependencies

Acceptance:
- All tests pass
- TypeScript compiles
- Commit and push
EOF
```

### **Step 2: Run it! (30min unattended)**

```bash
cube auto my-task.md
```

**What happens:**
1. Prompter AI generates detailed writer prompt
2. Two writers implement independently (Sonnet + Codex)
3. Three judges review both implementations
4. System picks winner or synthesizes best of both
5. Peer review validates final solution
6. PR automatically created

**You:** ☕ Get coffee, check back in 30min

### **Step 3: Check results**

```bash
# See what happened
cube status my-task

# View decisions
cube decide my-task

# Check the PR
gh pr list
```

**Done!** PR is ready for human review and merge.

---

## 🎓 **The 5 Essential Commands**

### **1. Start Workflow**
```bash
cube auto <task-file>           # Full autonomous
cube auto <task-file> --resume  # Continue from checkpoint
```

### **2. Check Status**
```bash
cube status                 # All active tasks
cube status my-task         # Specific task details
```

### **3. Make Decision**
```bash
cube decide my-task         # Aggregate judge votes
cube decide my-task --peer  # Check peer review
```

### **4. Intervene**
```bash
cube resume writer-sonnet my-task "Fix the tests"
cube resume judge-2 my-task "Re-review the types"
cube feedback codex my-task "Address these issues: ..."
```

### **5. Clean Up**
```bash
cube clean my-task      # Remove sessions/state
cube clean --old        # Clean sessions >7 days
```

---

## 🎯 **Common Workflows**

### **Scenario 1: Everything works**
```bash
cube auto task.md
# Wait 30min
# PR created automatically
# Review and merge!
```

### **Scenario 2: Need to intervene**
```bash
cube auto task.md
# Phase 5: Decides SYNTHESIS needed

cube status task
# Shows: Winner B, 3 blockers

# Let it continue (auto-handles synthesis)
# Or manually help:
cube resume writer-codex task "Fix blocker: timeout issue"
```

### **Scenario 3: Judge made mistake**
```bash
cube decide task
# Missing Judge 3 decision

cube resume judge-3 task "Write your decision JSON"
# Judge 3 completes
cube decide task  # Now shows 3/3
```

### **Scenario 4: Resume interrupted work**
```bash
# Left off at Phase 6
cube auto task.md --resume  # Smart resume
# Or
cube continue task  # Even simpler!
```

---

## 📚 **Next Steps**

**Learn more:**
- Planning: `docs/PLANNING_GUIDE.md`
- Task breakdown: `docs/TASK_BREAKDOWN.md`
- Full framework: `AGENT_CUBE.md`

**See it in action:**
- v2 example: `aetheron-connect-v2/implementation/`
- Panel metrics: `aetheron-connect-v2/implementation/panel/panel-metrics.md`

**Get help:**
- GitHub Issues: https://github.com/aetheronhq/agent-cube/issues
- GitHub Discussions: https://github.com/aetheronhq/agent-cube/discussions

---

## ⚙️ **Configuration**

**Customize models:**

Edit `python/cube.yaml`:
```yaml
writers:
  writer_a:
    model: "sonnet-4.5-thinking"  # Or any model!
  writer_b:
    model: "gpt-5-codex-high"

judges:
  judge_1:
    model: "sonnet-4.5-thinking"
  judge_2:
    model: "gpt-5-codex-high"
  judge_3:
    model: "gemini-2.5-pro"  # Or grok!
```

**That's it!** Fully configurable.

---

## 🐛 **Troubleshooting**

**"No session found"**
```bash
cube sessions  # List all active
# Session might be for different task ID
```

**"cursor-agent not found"**
```bash
# Install cursor-agent
curl https://cursor.com/install -fsSL | bash
```

**"Judge 3 (Gemini) missing decision"**
```bash
# Known issue, working on it
# Resume and explicitly ask:
cube resume judge-3 task "Write decision to PROJECT_ROOT/.prompts/decisions/judge-3-task-decision.json"
```

**"Workflow stuck"**
```bash
cube status task        # See current phase
cube logs task          # Check for errors
cube auto task --reset  # Nuclear option: start fresh
```

---

## 🎯 **Success Tips**

**1. Write clear task files**
- Specific requirements
- Clear acceptance criteria
- Reference any planning docs

**2. Use planning docs**
- More planning = better results
- Agents follow references
- See v2 for examples

**3. Monitor progress**
- `cube status` frequently
- Check decisions
- Intervene early if needed

**4. Trust but verify**
- Let it run autonomous
- But review PRs before merge
- Human judgment still essential

**5. Report issues**
- GitHub issues for bugs
- Quick fixes (we iterate daily!)

---

**NOW GO BUILD SOMETHING!** 🚀

