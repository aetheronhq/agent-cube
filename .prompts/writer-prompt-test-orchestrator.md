# Writer Prompt: Add Hello Function

You are a Writer Agent working on the "Add Hello Function" task for Agent Cube.

## Model Identification

**FIRST:** Identify which model you are and create the appropriate branch:

- **Claude Sonnet 4.5** → Branch: `writer-sonnet/test-hello-function`
- **GPT-5 Codex High** → Branch: `writer-codex/test-hello-function`
- **Other models** → Branch: `writer-<your-model-slug>/test-hello-function`

## Context

This task demonstrates the Agent Cube dual-writer workflow by creating a simple, type-safe TypeScript function. This is a foundational test task that validates:

- TypeScript configuration and tooling
- Testing infrastructure
- Basic module structure
- Git workflow integration

This task builds on the existing Agent Cube project structure and serves as a reference implementation for future tasks.

## Requirements

Create a TypeScript hello function with the following specifications:

### Functional Requirements

1. **Create `src/hello.ts`** with a named export function
2. **Function signature:** `export function hello(): string`
3. **Return value:** `"Hello from Agent Cube!"`
4. **Type safety:** Strict TypeScript with explicit return type
5. **Test coverage:** At least one test verifying the function works

### Technical Requirements

- TypeScript strict mode enabled
- No use of `any` type
- Proper ESM module exports
- Test file following naming convention (`*.test.ts` or `*.spec.ts`)
- All tests must pass

## Implementation Steps

Follow these steps in order:

### Step 1: Project Setup Verification

- [ ] Verify `src/` directory exists (create if needed)
- [ ] Check for existing TypeScript configuration
- [ ] Identify test framework in use (Jest, Vitest, etc.)

### Step 2: Implement the Function

- [ ] Create `src/hello.ts`
- [ ] Add JSDoc comment explaining the function
- [ ] Implement the function with explicit return type
- [ ] Ensure the function is exported

**Example structure:**

```typescript
/**
 * Returns a greeting message from Agent Cube.
 * @returns {string} The greeting message
 */
export function hello(): string {
  return "Hello from Agent Cube!";
}
```

### Step 3: Create Tests

- [ ] Create test file (e.g., `src/hello.test.ts`)
- [ ] Import the `hello` function
- [ ] Write test case(s) verifying:
  - Function returns expected string
  - Return type is string
  - No runtime errors

### Step 4: Verify Implementation

- [ ] Run TypeScript compiler (`tsc --noEmit` or similar)
- [ ] Run tests and ensure they pass
- [ ] Check for linting errors
- [ ] Verify no console warnings or errors

## Architecture Constraints

### Primary Directive: K.I.S.S (Keep It Simple, Stupid)

**CONTINUOUSLY ASK:** "Is this the simplest solution?"

- **Minimalistic:** Every line must earn its keep. No unnecessary abstractions.
- **Clean:** Readable > clever. Explicit > implicit. Direct > wrapped.
- **Elegant:** Simple solutions to complex problems. No gold plating.
- **Question everything:** 
  - Pass-through wrapper? DELETE IT.
  - Duplicate type? REMOVE IT.
  - "For future flexibility"? YAGNI - DON'T BUILD IT.

### Constraints for This Task

1. **No extra features** - Only what's specified in requirements
2. **No configuration changes** - Use existing TypeScript/test setup
3. **No dependencies** - This is pure TypeScript, no external libraries needed
4. **File scope:** Only `src/hello.ts` and its test file
5. **No abstractions** - Direct implementation, no factories or wrappers

### TypeScript Standards

- Strict mode enabled
- Explicit return types on functions
- No `any`, `unknown` without proper type guards
- Prefer `const` over `let`
- Use descriptive variable names

## Anti-Patterns to Avoid

### ❌ Over-Engineering

```typescript
// DON'T: Unnecessary abstraction
class HelloService {
  private message: string = "Hello from Agent Cube!";
  
  public getMessage(): string {
    return this.message;
  }
}

export const hello = () => new HelloService().getMessage();
```

### ❌ Gold Plating

```typescript
// DON'T: Adding features not requested
export function hello(name?: string, options?: { uppercase?: boolean }): string {
  const msg = name ? `Hello ${name} from Agent Cube!` : "Hello from Agent Cube!";
  return options?.uppercase ? msg.toUpperCase() : msg;
}
```

### ❌ Pass-Through Wrappers

```typescript
// DON'T: Unnecessary indirection
const MESSAGE = "Hello from Agent Cube!";
const getMessage = () => MESSAGE;
export const hello = () => getMessage();
```

### ✅ Correct: Simple & Direct

```typescript
// DO: Exactly what's needed, nothing more
export function hello(): string {
  return "Hello from Agent Cube!";
}
```

## Success Criteria

Your implementation is complete when:

### Functional Verification

- [ ] `src/hello.ts` exists and exports the `hello` function
- [ ] Function returns exactly: `"Hello from Agent Cube!"`
- [ ] Function has explicit return type annotation
- [ ] Test file exists with passing test(s)
- [ ] No TypeScript errors or warnings
- [ ] No linting errors

### Quality Verification

- [ ] Code follows K.I.S.S principle (simplest solution)
- [ ] No unnecessary abstractions or wrappers
- [ ] No features beyond requirements
- [ ] Clean, readable code with proper documentation
- [ ] Type safety maintained throughout

### Testing Verification

```bash
# All of these should succeed:
npm test              # or your test command
npm run typecheck     # or tsc --noEmit
npm run lint          # if linting is configured
```

## Final Steps - CRITICAL

**⚠️ YOU MUST COMMIT AND PUSH YOUR WORK ⚠️**

Uncommitted or unpushed changes will NOT be reviewed by the panel.

### 1. Review Your Changes

```bash
git status
git diff
```

Verify only the intended files are changed:
- `src/hello.ts` (created)
- Test file (created)
- No other files modified

### 2. Stage Your Changes

```bash
git add src/hello.ts
git add src/hello.test.ts  # or your test file name
```

### 3. Commit With Descriptive Message

```bash
git commit -m "feat(test): add hello function

- Created src/hello.ts with typed hello function
- Returns 'Hello from Agent Cube!' message
- Added test coverage with passing tests
- Follows TypeScript strict mode standards

Writer: [Your Model Name]"
```

### 4. Push to Your Branch

```bash
git push origin writer-<your-model-slug>/test-hello-function
```

Example:
- Claude Sonnet 4.5: `git push origin writer-sonnet/test-hello-function`
- GPT-5 Codex High: `git push origin writer-codex/test-hello-function`

### 5. Verify Push Succeeded

```bash
git status
```

Should show: `"Your branch is up to date with 'origin/writer-<model-slug>/test-hello-function'"`

```bash
git log origin/writer-<your-model-slug>/test-hello-function..HEAD
```

Should show: **no unpushed commits** (empty output)

### 6. Provide Final Summary

State clearly:

```
✅ Writer [Model Name] complete for test-hello-function

Branch: writer-<model-slug>/test-hello-function
Commit: [commit hash]
Push Status: SUCCESS (verified with git status)

Changes:
- Created src/hello.ts
- Created src/hello.test.ts
- All tests passing
- TypeScript compilation successful
```

## Process Checklist

Before submitting, verify:

- [ ] Identified your model and created correct branch
- [ ] Read and understood all requirements
- [ ] Implemented only what was requested (K.I.S.S)
- [ ] Tests exist and pass
- [ ] TypeScript compiles without errors
- [ ] Code is clean and well-documented
- [ ] Changes committed with descriptive message
- [ ] Branch pushed to remote successfully
- [ ] Push verified with `git status`
- [ ] Final summary provided with branch name

## Questions or Issues?

If you encounter blockers:

1. **TypeScript errors:** Check your tsconfig.json configuration
2. **Test framework unclear:** Look for existing test files as examples
3. **Directory structure:** Use `ls -la` to verify paths
4. **Git issues:** Ensure you're on the correct branch

**Remember:** Keep it simple. If you're adding complexity, you're probably overthinking it.

---

**Good luck! Focus on simplicity, type safety, and getting your work committed and pushed.**
