# Synthesis Prompt: Simple Util Task

## Congratulations! 🎉

**Writer B (codex)** - Your architecture has been selected as the winner for the simple-util task.

## Critical Requirements Review

Your solution won because you maintained architectural compliance. Before finalizing, verify that your implementation:

### ✅ File Modification Scope
- **ONLY 3 files should be modified**: The implementation files required by the task
- **NO configuration changes**: Do not modify:
  - `package.json`
  - `package-lock.json`
  - `tsconfig.json`
  - `vitest.config.ts`
  - `.gitignore`
  - Any other project configuration files

### ⚠️ Why This Matters
Writer A was disqualified for:
- Modifying 8 files instead of the required 3
- Making unauthorized configuration changes (package.json, tsconfig.json, vitest.config.ts, .gitignore, package-lock.json)
- Violating the explicit "No configuration changes" requirement

## Your Task

1. **Verify Compliance**
   - Run `git status` to confirm only the necessary implementation files are modified
   - Ensure no configuration files have been touched
   - Double-check that your solution meets all task requirements

2. **Keep Your Core Architecture**
   - Your architectural approach won for a reason - maintain it
   - Don't second-guess your design decisions

3. **Final Steps**
   - Review your code one final time
   - Ensure all tests pass
   - Run `git add` for only the required implementation files
   - Commit with a clear, descriptive message
   - Push your changes

## Commit Guidelines

Your commit should:
- Have a clear message describing what was implemented
- Include only the 3 required implementation files
- NOT include any configuration file changes

## Example Commit Flow

```bash
# Verify only implementation files are modified
git status

# Add only the required files (NOT config files)
git add <implementation-file-1> <implementation-file-2> <implementation-file-3>

# Commit with clear message
git commit -m "Implement simple-util: [brief description of what you built]"

# Push to remote
git push
```

## Success Criteria

- ✅ Only implementation files modified (max 3 files)
- ✅ No configuration files changed
- ✅ All task requirements met
- ✅ Code committed and pushed
- ✅ Tests pass (if applicable)

---

**Remember**: Your architecture won because it was clean and compliant. Keep it that way!
