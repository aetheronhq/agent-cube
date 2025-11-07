# Writer Task: Add Hello Function (test-hello)

You are implementing a test task to add a simple hello function in TypeScript.

## Model Identification

**REQUIRED:** Identify which model you are and create the appropriate branch:

- **Claude Sonnet 4.5** → Branch: `writer-sonnet/test-hello`
- **GPT-5 Codex High** → Branch: `writer-codex/test-hello`

## Task Requirements

Create a simple hello function in TypeScript that:

1. Lives in `src/hello.ts`
2. Exports a function that returns "Hello from Agent Cube!"
3. Has a test to verify it works
4. Is type-safe (strict TypeScript)

## Acceptance Criteria

- ✅ Function works and returns correct string
- ✅ Test passes
- ✅ Type-safe (no `any`, strict mode)
- ✅ Code committed and pushed to your branch

## 🎯 PRIMARY DIRECTIVE: K.I.S.S (Keep It Simple, Stupid)

**CONTINUOUSLY ASK YOURSELF: "Is this the simplest solution?"**

- **Minimalistic**: Every line of code must earn its keep
- **Clean**: Readable > clever. Explicit > implicit
- **Elegant**: Simple solutions to complex problems
- **No gold plating**: This is a simple hello function, don't overcomplicate it

For this task:
- Just export a simple function
- No classes, no abstractions, no fancy patterns
- Just the function, the test, and nothing more

## Current State

This is the `agent-cube` repository. You need to create:
- `src/hello.ts` - The hello function
- A test file for the hello function

## Process

1. **Identify your model** and create branch: `writer-<model-slug>/test-hello`
2. **Create the source file** `src/hello.ts` with the hello function
3. **Create a test file** to verify the function works
4. **Verify it works** - run the test if possible
5. **Ensure TypeScript strict mode compliance** - no `any`, proper types

6. **REQUIRED: Commit and push branch**

   **⚠️ CRITICAL: You MUST commit and push your work. Uncommitted or unpushed changes will NOT be reviewed by the panel.**
   
   ```bash
   git add src/hello.ts src/hello.test.ts  # or wherever your files are
   git commit -m "feat(test): add hello function for orchestrator test"
   git push origin writer-<model-slug>/test-hello
   ```
   
   Verify push succeeded: `git status` should show "Your branch is up to date with 'origin/...'"

7. **REQUIRED: Provide final summary ONLY AFTER successful push:**
   - State your branch name
   - Confirm push succeeded
   - Example: "Writer codex complete for test-hello. Branch writer-codex/test-hello pushed successfully."

## Constraints

- **Simplicity first**: This is a test task, keep it minimal
- **No unnecessary abstractions**: Just export a function
- **Type-safe**: Use proper TypeScript types
- **Testable**: Include a test that verifies the function
- **No external dependencies**: Use standard TypeScript/Node.js only

## Example Implementation Guidance

The implementation should be extremely simple. Here's the complexity level expected:

**hello.ts:**
```typescript
export function hello(): string {
  return "Hello from Agent Cube!";
}
```

**Test:** Verify the function returns the correct string.

That's it. Don't add more complexity than needed.

## Testing

If you can run tests locally, do so. If not, ensure your test is syntactically correct and would pass.

## Final Checklist

Before committing:
- [ ] Function exists in `src/hello.ts`
- [ ] Function returns "Hello from Agent Cube!"
- [ ] Function is properly typed
- [ ] Test exists and would pass
- [ ] No `any` types used
- [ ] Code is committed
- [ ] Code is pushed to your branch
- [ ] Git status confirms successful push

## Task File Reference

Original task: `test-prompts/task-test-orchestrator.md`

---

**Remember:** This is a test of the orchestrator workflow. Keep it simple, functional, and type-safe. The goal is to verify the dual-writer → panel → synthesis → PR workflow works correctly.
