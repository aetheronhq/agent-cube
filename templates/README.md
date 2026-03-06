# Agent Cube Templates

**Ready-to-use templates for planning docs, tasks, and more**

---

## 📋 **Available Templates**

### **Planning Documentation**

**`planning-doc-template.md`**
- Architecture-area planning doc
- Principles, requirements, anti-patterns
- Integration points
- Based on v2's 33 planning docs

**Use when:** Creating new planning docs for your project

### **Task Files**

**`task-template.md`**
- Complete task specification
- Requirements, owned paths, acceptance criteria
- Integration points, testing requirements
- Based on v2's successful task format

**Use when:** Breaking down features into agent tasks

---

## 🎯 **How to Use**

### **For Planning Docs**

```bash
# 1. Copy template
cp templates/planning-doc-template.md planning/api-conventions.md

# 2. Fill in sections
# - Replace [placeholders]
# - Add your requirements
# - Include examples
# - List anti-patterns

# 3. Reference in task files
# Tasks will read these as source of truth
```

### **For Task Files**

```bash
# 1. Copy template  
cp templates/task-template.md implementation/phase-02/tasks/02-my-feature.md

# 2. Customize
# - Clear goal
# - Specific requirements
# - Planning doc references
# - Owned paths
# - Examples

# 3. Run it!
cube auto implementation/phase-02/tasks/02-my-feature.md
```

---

## ✅ **Template Checklist**

**Good planning doc has:**
- [ ] Clear principles
- [ ] Specific requirements
- [ ] Code examples (good & bad)
- [ ] Anti-patterns listed
- [ ] Integration points defined
- [ ] TBD items tracked

**Good task file has:**
- [ ] One-sentence goal
- [ ] Context (why/what builds on)
- [ ] Planning references
- [ ] Owned paths (clear boundaries)
- [ ] Acceptance criteria (testable)
- [ ] Examples
- [ ] 2-8 hour estimate

---

## 🎓 **Best Practices**

**Planning Docs:**
- ✅ Architecture-first (not feature-first)
- ✅ Show examples (code > words)
- ✅ List anti-patterns (what NOT to do)
- ✅ Keep updated (living documents)
- ❌ Don't prescribe implementation details
- ❌ Don't assume agent knowledge

**Task Files:**
- ✅ Small scope (2-8 hours)
- ✅ Clear boundaries (owned paths)
- ✅ Testable criteria
- ✅ Reference planning docs
- ❌ Don't overlap with other tasks
- ❌ Don't leave integration unclear

---

## 📚 **Examples**

**See v2 for real examples:**
- Planning: `your-project/planning/`
- Tasks: `your-project/implementation/phase-*/tasks/`
- Metrics: `your-project/implementation/panel/panel-metrics.md`

**Learn from what worked!**

---

## 🔄 **Iteration**

**Templates evolve:**
- Start with these
- Customize for your project
- Improve based on results
- Share improvements back!

**Found a better pattern?** Update the template!

---

**READY TO PLAN YOUR FIRST FEATURE WITH AGENT CUBE!** 🚀

