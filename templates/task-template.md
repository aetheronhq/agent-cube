# Task XX: [Feature/Component Name]

**Goal:** [One sentence - what this task delivers]

**Time Estimate:** [2-8 hours ideal]

---

<!--
## Writing Effective Task Files

Task files are consumed by Agent Cube's two-stage pipeline:
1. A Prompter AI reads this file and generates a detailed writer prompt
2. Writer AIs receive that prompt and implement the task (with full codebase access)

This means:
- Writers CAN read planning docs and codebase files directly — don't duplicate content
- Specify WHAT to build and constraints, not HOW to build it step-by-step
- Keep code examples minimal — show patterns/style (2-5 lines), not implementations
- Anti-patterns work best as brief constraints, not full bad/good code blocks
- Requirements and acceptance criteria are the highest-value sections
- Overly prescriptive instructions reduce solution quality (writers can't explore alternatives)

Research shows: Goal-oriented prompts with clear constraints outperform verbose
procedural instructions. AI agents exploit surface patterns in code examples rather
than reasoning about requirements — keep examples short and pattern-focused.
-->

## 📖 **Context**

**What this builds on:**
- [Previous task or foundation]
- [How it fits in the bigger picture]

**Required reading (Golden Source):**
- `planning/[relevant-doc-1].md` — [What it defines]
- `planning/[relevant-doc-2].md` — [What it defines]

> Writers: Read these planning docs before implementing. They contain
> the authoritative patterns, types, and constraints for this task.

---

## ✅ **Requirements**

### **1. [Requirement Category]**

**Deliverable:**
- [Specific item 1]
- [Specific item 2]

**Acceptance criteria:**
- [ ] [Testable criterion 1]
- [ ] [Testable criterion 2]
- [ ] [Testable criterion 3]

### **2. [Another Category]**

[Repeat structure]

---

## 🏗️ **Constraints**

**Architecture (from planning docs):**
- [Specific constraint from planning-doc-1.md]
- [Specific constraint from planning-doc-2.md]

**Technical:**
- TypeScript strict mode, no `any` types
- [Project-specific constraint]

**KISS:**
- Simplest solution that meets requirements
- No unnecessary abstractions or "for future flexibility"

---

## 🚫 **Anti-Patterns**

<!--
Keep anti-patterns brief — state the constraint and why, with minimal code.
A 1-2 line example showing the wrong pattern is more effective than
full bad/good implementation blocks. Writers reason better from constraints
than from code to copy.
-->

- **Don't [anti-pattern 1]** — [Why it's wrong]. Use [correct approach] instead.
- **Don't [anti-pattern 2]** — [Why it breaks]. See `planning/[doc].md` for the correct pattern.

---

## 📂 **Owned Paths**

**This task owns:**
```
[directory/]
├── [file1].ts
├── [file2].ts
└── [file3].test.ts
```

**Must NOT modify:**
- `[file]` (owned by [other task])

---

## 🧪 **Testing Requirements**

- [ ] Unit tests for core functions
- [ ] Edge cases: [specific to this task]
- [ ] Error paths tested
- [ ] [Domain-specific test requirement]

---

## ✅ **Acceptance Criteria**

- [ ] All requirements met
- [ ] Planning docs followed (see Required Reading above)
- [ ] Tests passing, TypeScript compiles, linter clean
- [ ] No unnecessary complexity
- [ ] Changes committed and pushed

---

## 🔗 **Integration Points**

**Depends on:** [Previous tasks]
**Enables:** [Future tasks]

---

## 📊 **Style Reference**

<!--
Only include if there's a specific pattern the writer must follow that
ISN'T already in the planning docs. Keep to 2-5 lines showing the pattern,
not a full implementation. The writer will read planning docs for details.
-->

```typescript
// Show the pattern/convention, not a full implementation
```

---

## 🎓 **Pitfalls**

- ⚠️ [Common mistake — how to avoid]
- ⚠️ [Edge case to watch for]

---

**FINAL STEPS - CRITICAL:**

After implementing and verifying all tests pass:

```bash
git add [files]
git commit -m "feat: [brief description]"
git push origin writer-[your-model-slug]/[task-id]
git status
```

**⚠️ IMPORTANT:** Uncommitted or unpushed changes will NOT be reviewed!

---

**Built with:** Agent Cube v1.0
**Template version:** 2.0
**Last updated:** 2025-02-11
