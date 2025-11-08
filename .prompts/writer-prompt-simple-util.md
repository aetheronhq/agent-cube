# Writer Prompt: Add String Utility Functions

You are a Writer Agent working on the "Add String Utility Functions" task for Agent Cube.

## Model Identification

**FIRST:** Identify which model you are and create the appropriate branch:

- **Claude Sonnet 4.5** → Branch: `writer-sonnet/simple-util`
- **GPT-5 Codex High** → Branch: `writer-codex/simple-util`
- **Other models** → Branch: `writer-<your-model-slug>/simple-util`

## Context

This task creates a foundational utility module for string manipulation operations. These utilities will be reusable across the codebase and demonstrate:

- TypeScript module organization and exports
- Type-safe function implementations
- Comprehensive test coverage
- Clean, maintainable utility patterns

This is a standalone module that should have **zero external dependencies** and follow strict type safety practices.

## Requirements

Create a TypeScript string utilities module with three core functions.

### Functional Requirements

1. **Create `src/utils/string-utils.ts`** with three exported functions:

   **Function 1: `capitalize`**
   - Signature: `capitalize(str: string): string`
   - Behavior: Capitalizes the first letter of the string, lowercases the rest
   - Example: `capitalize("hello")` → `"Hello"`
   - Example: `capitalize("HELLO")` → `"Hello"`
   - Edge case: Empty string → empty string

   **Function 2: `truncate`**
   - Signature: `truncate(str: string, maxLength: number): string`
   - Behavior: Truncates string to `maxLength` characters, adds "..." if truncated
   - The "..." counts toward the maxLength
   - Example: `truncate("Hello World", 8)` → `"Hello..."`
   - Edge case: If string <= maxLength, return unchanged
   - Edge case: If maxLength < 3, return the string truncated without ellipsis

   **Function 3: `slugify`**
   - Signature: `slugify(str: string): string`
   - Behavior: Converts string to URL-safe slug
   - Lowercase all characters
   - Replace spaces with hyphens
   - Remove all non-alphanumeric characters except hyphens
   - Remove leading/trailing hyphens
   - Collapse multiple consecutive hyphens to single hyphen
   - Example: `slugify("Hello World!")` → `"hello-world"`
   - Example: `slugify("  Foo  Bar  ")` → `"foo-bar"`

2. **Create comprehensive tests** in `src/utils/string-utils.test.ts`:
   - Test each function with normal cases
   - Test edge cases (empty strings, special characters, etc.)
   - Test boundary conditions (maxLength edge cases for truncate)
   - All tests must pass

3. **Export from barrel file** `src/utils/index.ts`:
   - Re-export all three functions from string-utils
   - Allow clean imports: `import { capitalize } from '@/utils'`

### Technical Requirements

- TypeScript strict mode enabled
- Explicit return types on all functions
- Explicit parameter types on all parameters
- No use of `any` type
- No external dependencies (pure TypeScript/JavaScript)
- Proper ESM module exports
- JSDoc comments on all exported functions
- Test file following naming convention (`*.test.ts`)
- 100% test coverage for all functions

## Implementation Steps

Follow these steps in order:

### Step 1: Project Setup Verification

- [ ] Verify `src/utils/` directory exists (create if needed)
- [ ] Check for existing TypeScript configuration
- [ ] Identify test framework in use (Jest, Vitest, etc.)
- [ ] Check if `src/utils/index.ts` exists

### Step 2: Implement the Utility Functions

- [ ] Create `src/utils/string-utils.ts`
- [ ] Implement `capitalize` function with explicit types and JSDoc
- [ ] Implement `truncate` function with explicit types and JSDoc
- [ ] Implement `slugify` function with explicit types and JSDoc
- [ ] Ensure all functions are exported

**Example structure:**

```typescript
/**
 * Capitalizes the first letter of a string and lowercases the rest.
 * @param str - The string to capitalize
 * @returns The capitalized string
 */
export function capitalize(str: string): string {
  if (str.length === 0) return str;
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

// ... other functions
```

### Step 3: Create Comprehensive Tests

- [ ] Create `src/utils/string-utils.test.ts`
- [ ] Import all three functions
- [ ] Write test suite for `capitalize`:
  - Normal case: "hello" → "Hello"
  - Already capitalized: "Hello" → "Hello"
  - All caps: "HELLO" → "Hello"
  - Empty string: "" → ""
  - Single character: "a" → "A"
- [ ] Write test suite for `truncate`:
  - Normal truncation with ellipsis
  - String shorter than maxLength (no truncation)
  - String exactly maxLength
  - Very short maxLength (< 3)
  - Empty string
- [ ] Write test suite for `slugify`:
  - Normal case with spaces
  - Special characters removal
  - Multiple spaces
  - Leading/trailing spaces
  - Consecutive hyphens
  - Already slug-like string
  - Empty string

### Step 4: Update Barrel Export

- [ ] Create or update `src/utils/index.ts`
- [ ] Export all three functions from string-utils
- [ ] Verify clean import path works

Example `src/utils/index.ts`:

```typescript
export { capitalize, truncate, slugify } from './string-utils';
```

### Step 5: Verify Implementation

- [ ] Run TypeScript compiler (`tsc --noEmit` or similar)
- [ ] Run tests and ensure all pass
- [ ] Check for linting errors
- [ ] Verify no console warnings or errors
- [ ] Manually test a few examples in a scratch file (optional)

## Architecture Constraints

### Primary Directive: K.I.S.S (Keep It Simple, Stupid)

**CONTINUOUSLY ASK:** "Is this the simplest solution?"

- **Minimalistic:** Every line must earn its keep. No unnecessary abstractions.
- **Clean:** Readable > clever. Explicit > implicit. Direct > wrapped.
- **Elegant:** Simple solutions to complex problems. No gold plating.
- **Question everything:**
  - Regular expressions too complex? Simplify or use string methods.
  - Helper function with one use? Inline it.
  - "For future flexibility"? YAGNI - DON'T BUILD IT.

### Constraints for This Task

1. **No external dependencies** - Pure TypeScript/JavaScript only
2. **No configuration changes** - Use existing TypeScript/test setup
3. **File scope:** Only create/modify:
   - `src/utils/string-utils.ts`
   - `src/utils/string-utils.test.ts`
   - `src/utils/index.ts`
4. **No abstractions** - Direct implementations, no base classes or factories
5. **No extra functions** - Only the three specified functions
6. **Simple regex** - If using regex, keep patterns readable

### TypeScript Standards

- Strict mode enabled
- Explicit return types on all functions
- Explicit types on all parameters
- No `any`, no `unknown` without proper guards
- Prefer `const` over `let`
- Use descriptive variable names
- JSDoc on all exported functions

## Anti-Patterns to Avoid

### ❌ Over-Engineering with Classes

```typescript
// DON'T: Unnecessary class wrapper
class StringUtils {
  static capitalize(str: string): string {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }
  
  static truncate(str: string, maxLength: number): string {
    // ...
  }
}

export default StringUtils;
```

### ❌ Adding Unrequested Features

```typescript
// DON'T: Options not in requirements
export function truncate(
  str: string,
  maxLength: number,
  options?: { ellipsis?: string; position?: 'end' | 'middle' }
): string {
  const ellipsis = options?.ellipsis || '...';
  // ... complex logic
}
```

### ❌ Overly Complex Regex

```typescript
// DON'T: Regex that requires a PhD to understand
export function slugify(str: string): string {
  return str
    .replace(/(?:^\W+|\W+$)/g, '')
    .replace(/(?:(?<=\W)\W+|\W+(?=\W))/g, '-')
    .toLowerCase();
}
```

### ❌ Unnecessary Abstractions

```typescript
// DON'T: Helper functions that are used once
function toUpperFirst(char: string): string {
  return char.toUpperCase();
}

function toLowerRest(str: string): string {
  return str.slice(1).toLowerCase();
}

export function capitalize(str: string): string {
  return toUpperFirst(str[0]) + toLowerRest(str);
}
```

### ✅ Correct: Simple & Direct

```typescript
// DO: Exactly what's needed, readable, no magic
export function capitalize(str: string): string {
  if (str.length === 0) return str;
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

export function truncate(str: string, maxLength: number): string {
  if (str.length <= maxLength) return str;
  if (maxLength < 3) return str.slice(0, maxLength);
  return str.slice(0, maxLength - 3) + '...';
}

export function slugify(str: string): string {
  return str
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-+|-+$/g, '');
}
```

## Success Criteria

Your implementation is complete when:

### Functional Verification

- [ ] `src/utils/string-utils.ts` exists with all three functions
- [ ] `capitalize` works correctly with edge cases
- [ ] `truncate` works correctly with edge cases
- [ ] `slugify` works correctly with edge cases
- [ ] All functions have explicit types (params and return)
- [ ] All functions have JSDoc comments
- [ ] Test file exists with comprehensive test coverage
- [ ] All tests pass
- [ ] `src/utils/index.ts` exports all three functions
- [ ] No TypeScript errors or warnings
- [ ] No linting errors

### Quality Verification

- [ ] Code follows K.I.S.S principle (simplest solution)
- [ ] No unnecessary abstractions or wrappers
- [ ] No features beyond requirements
- [ ] No external dependencies used
- [ ] Clean, readable code with clear logic
- [ ] Type safety maintained throughout
- [ ] Good test coverage (edge cases included)

### Testing Verification

```bash
# All of these should succeed:
npm test                    # or your test command
npm run test:coverage       # optional coverage check
npm run typecheck           # or tsc --noEmit
npm run lint                # if linting is configured
```

Expected test output:
- All test suites pass
- All individual tests pass
- No warnings or errors

## Final Steps - CRITICAL

**⚠️ YOU MUST COMMIT AND PUSH YOUR WORK ⚠️**

Uncommitted or unpushed changes will NOT be reviewed by the panel. The judge panel cannot see your work until it's pushed to your branch.

### 1. Review Your Changes

```bash
git status
git diff
```

Verify only the intended files are changed:
- `src/utils/string-utils.ts` (created)
- `src/utils/string-utils.test.ts` (created)
- `src/utils/index.ts` (created or modified)
- No other files modified

### 2. Stage Your Changes

```bash
git add src/utils/string-utils.ts
git add src/utils/string-utils.test.ts
git add src/utils/index.ts
```

Or stage all at once:

```bash
git add src/utils/
```

### 3. Commit With Descriptive Message

```bash
git commit -m "feat(utils): add string utility functions

- Created string-utils.ts with capitalize, truncate, and slugify
- Capitalize: first letter uppercase, rest lowercase
- Truncate: limit string length with ellipsis
- Slugify: convert to URL-safe slug format
- Added comprehensive tests with edge case coverage
- Exported from utils/index.ts for clean imports
- Zero external dependencies, pure TypeScript
- All tests passing, full type safety

Writer: [Your Model Name]"
```

### 4. Push to Your Branch

```bash
git push origin writer-<your-model-slug>/simple-util
```

Examples:
- Claude Sonnet 4.5: `git push origin writer-sonnet/simple-util`
- GPT-5 Codex High: `git push origin writer-codex/simple-util`

### 5. Verify Push Succeeded

```bash
git status
```

Should show: `"Your branch is up to date with 'origin/writer-<model-slug>/simple-util'"`

```bash
git log origin/writer-<your-model-slug>/simple-util..HEAD
```

Should show: **no unpushed commits** (empty output means all commits are pushed)

### 6. Provide Final Summary

State clearly:

```
✅ Writer [Model Name] complete for simple-util

Branch: writer-<model-slug>/simple-util
Commit: [commit hash]
Push Status: SUCCESS (verified with git status)

Changes:
- Created src/utils/string-utils.ts (3 functions)
- Created src/utils/string-utils.test.ts (comprehensive tests)
- Updated src/utils/index.ts (barrel export)
- All tests passing (X/X tests)
- TypeScript compilation successful
- Zero external dependencies
```

## Process Checklist

Before submitting, verify:

- [ ] Identified your model and created correct branch
- [ ] Read and understood all requirements
- [ ] Implemented all three functions correctly
- [ ] All functions have explicit types and JSDoc
- [ ] Tests exist and are comprehensive
- [ ] All tests pass
- [ ] TypeScript compiles without errors
- [ ] No external dependencies added
- [ ] Code follows K.I.S.S principle
- [ ] Barrel export updated in src/utils/index.ts
- [ ] Changes committed with descriptive message
- [ ] Branch pushed to remote successfully
- [ ] Push verified with `git status` and `git log`
- [ ] Final summary provided with branch name and commit hash

## Questions or Issues?

If you encounter blockers:

1. **TypeScript errors:** Check your tsconfig.json configuration and ensure types are explicit
2. **Test framework unclear:** Look for existing test files as examples (e.g., `src/**/*.test.ts`)
3. **Directory structure:** Use `ls -la src/utils/` to verify paths
4. **Git issues:** Ensure you're on the correct branch (`git branch --show-current`)
5. **Edge cases unclear:** Test thoroughly and handle empty strings, boundary values

**Remember:**
- Keep it simple - no clever tricks
- Be explicit - types on everything
- Test thoroughly - edge cases matter
- Commit and push - the panel can't review what they can't see

---

**Good luck! Focus on simplicity, type safety, comprehensive testing, and getting your work committed and pushed.**
