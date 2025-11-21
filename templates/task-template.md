# Task XX: [Feature/Component Name]

**Goal:** [One sentence - what this task delivers]

**Time Estimate:** [2-8 hours ideal]

---

## 📖 **Context**

**What this builds on:**
- [Previous task or foundation]
- [Why this is needed now]
- [How it fits in the bigger picture]

**Planning docs (Golden Source):**
- `planning/[relevant-doc-1].md` [KEY] - [What it defines]
- `planning/[relevant-doc-2].md` - [What it defines - reference only]

**Note:** Mark critical planning docs with `[KEY]` - orchestrator will automatically include them in writer prompts. Non-KEY docs are included as references only.

---

## 📚 **Required Reading** (MANDATORY)

**BEFORE implementing, you MUST read these external documentation sources:**

### [Third-Party Tool Name] (e.g., DaisyUI v5)

**Documentation:**
- **Primary Docs:** [URL to official documentation]
  - **Why:** [Brief explanation - e.g., "We use v5, NOT v4 - API has breaking changes"]
  - **Time:** [Estimated reading time - e.g., "15 minutes"]

**Sections to read:**
- **[Section Name]:** [URL to specific section]
  - **Focus on:** [What to pay attention to]
- **[Another Section]:** [URL]
  - **Focus on:** [What to pay attention to]

### [Another Tool Name] (if applicable)

[Repeat structure above]

**Critical:** Don't skip these docs! Judges will verify you:
- ✅ Used the correct versions
- ✅ Followed the documented patterns
- ✅ Avoided deprecated APIs

---

## ✅ **Requirements**

### **1. [Requirement Category]**

**Deliverable:**
- [Specific item 1]
- [Specific item 2]
- [Specific item 3]

**Acceptance criteria:**
- [ ] [Testable criterion 1]
- [ ] [Testable criterion 2]
- [ ] [Testable criterion 3]

### **2. [Another Category]**

[Repeat structure]

---

## 📝 **Implementation Steps**

**Suggested order:**

1. **[Step 1]**
   - [ ] Substep A
   - [ ] Substep B

2. **[Step 2]**
   - [ ] Substep A
   - [ ] Substep B

3. **[Step 3]**
   - [ ] Substep A
   - [ ] Substep B

4. **Verify**
   - [ ] Run tests
   - [ ] Run typecheck
   - [ ] Run linter
   - [ ] Manually test [key functionality]

5. **Finalize**
   - [ ] Commit changes
   - [ ] Push to branch
   - [ ] Verify push succeeded

---

## 🏗️ **Architecture Constraints**

### **Must Follow**

**Planning docs:**
- [Specific requirement from planning-doc-1.md]
- [Specific requirement from planning-doc-2.md]

**Technical constraints:**
- TypeScript strict mode
- No `any` types
- Explicit return types
- Tests required

**KISS Principles:**
- ✅ Simplest solution that works
- ✅ No unnecessary abstractions
- ✅ No premature optimization
- ❌ No "for future flexibility"

---

## 🚫 **Anti-Patterns**

### **❌ DON'T: [Anti-pattern 1]**

```typescript
// Bad example
const overEngineered = {
  // Why this is bad
}
```

**Instead:**
```typescript
// Good alternative
const simple = {
  // Why this is better
}
```

### **❌ DON'T: [Anti-pattern 2]**

[Repeat structure]

---

## 📂 **Owned Paths**

**This task owns:**
```
apps/api/src/lib/[feature]/
├── [file1].ts
├── [file2].ts
└── [file3].test.ts
```

**Must NOT modify:**
- `apps/api/src/server.ts` (owned by integrator)
- `[Other protected files]`

**Integration:**
- Export [module/middleware/function]
- Integrator will import and wire in separate task

---

## 🧪 **Testing Requirements**

**Test coverage:**
- [ ] Unit tests for core functions
- [ ] Integration tests (if applicable)
- [ ] Edge cases covered
- [ ] Error paths tested

**Test quality:**
- Descriptive test names
- Arrange-Act-Assert pattern
- No flaky tests
- Fast execution (<5s)

---

## ✅ **Acceptance Criteria**

**Definition of Done:**

- [ ] All requirements met
- [ ] Planning docs followed
- [ ] Tests written and passing
- [ ] TypeScript compiles (no errors)
- [ ] Linter passes (no warnings)
- [ ] Code is self-documenting
- [ ] No unnecessary complexity
- [ ] Integration points clear
- [ ] Changes committed
- [ ] Branch pushed to remote

**Quality gates:**
- [ ] Follows KISS principles
- [ ] No security issues
- [ ] Performance acceptable
- [ ] Error handling complete

---

## 🔗 **Integration Points**

**Dependencies (requires these first):**
- [Task or component this needs]
- [Another dependency]

**Dependents (these will use this):**
- [Task that will integrate this]
- [Component that will consume this]

**Integrator task:**
- [Which task wires this into server/app]
- [What integration looks like]

---

## 📊 **Examples**

### **Success Example**

**From:** [Similar task in v2 or reference]

**What made it good:**
- [Quality aspect 1]
- [Quality aspect 2]

**Code snippet:**
```typescript
// Reference example
```

---

## 🎓 **Common Pitfalls**

**Watch out for:**
- ⚠️ [Common mistake 1]
- ⚠️ [Common mistake 2]
- ⚠️ [Common mistake 3]

**If you see [X], it means [Y] - fix by [Z]**

---

## 📝 **Notes**

**Additional context:**
- [Important note 1]
- [Important note 2]

**Nice-to-haves (not required):**
- [Optional improvement 1]
- [Optional improvement 2]

---

**FINAL STEPS - CRITICAL:**

After completing implementation and verifying all tests pass:

```bash
# Stage your changes
git add [files]

# Commit with descriptive message
git commit -m "feat: [brief description]"

# Push to remote
git push origin writer-[your-model-slug]/[task-id]

# Verify push succeeded
git status  # Should show "up to date with origin"
```

**⚠️ IMPORTANT:** Uncommitted or unpushed changes will NOT be reviewed!

---

**Built with:** Agent Cube v1.0
**Template version:** 1.0
**Last updated:** 2025-11-11

