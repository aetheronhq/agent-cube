# Task: Add String Utility Functions

You are a Writer working on creating a TypeScript string utilities module.

## Model Identification

**Identify your model and create the appropriate branch:**

- If you are **Claude Sonnet 4.5**: Create branch `writer-sonnet/string-utils`
- If you are **GPT-5 Codex High**: Create branch `writer-codex/string-utils`
- If you are another model: Create branch `writer-<model-slug>/string-utils`

**Do not coordinate with the other writer.** Work independently.

## 🎯 PRIMARY DIRECTIVE: K.I.S.S (Keep It Simple, Stupid)

**CONTINUOUSLY ASK YOURSELF: "Is this the simplest solution?"**

- **Minimalistic**: Every line of code must earn its keep. No unnecessary abstractions.
- **Clean**: Readable > clever. Explicit > implicit. Direct > wrapped.
- **Elegant**: Simple solutions to complex problems. No gold plating.
- **Question everything**: Pass-through wrapper? Delete it. Duplicate type? Remove it. "For future flexibility"? YAGNI - don't build it.

## Context

Create a simple TypeScript utility module with common string helper functions. This is a foundational utility that should be type-safe, well-tested, and have zero external dependencies.

## Requirements

### 1. Create Main Utility File

**File:** `src/utils/string-utils.ts`

Implement exactly 3 functions with these signatures:

```typescript
/**
 * Capitalize the first letter of a string
 * @param str - Input string
 * @returns String with first letter capitalized
 */
export function capitalize(str: string): string

/**
 * Truncate a string to a maximum length with ellipsis
 * @param str - Input string
 * @param maxLength - Maximum length (must be >= 3 for ellipsis)
 * @returns Truncated string with '...' if truncated
 */
export function truncate(str: string, maxLength: number): string

/**
 * Convert string to URL-safe slug
 * @param str - Input string
 * @returns Lowercase slug with hyphens
 */
export function slugify(str: string): string
```

### 2. Implementation Guidelines

**`capitalize(str)`:**
- Handle empty strings (return empty string)
- Preserve remaining characters as-is
- Example: `"hello world"` → `"Hello world"`

**`truncate(str, maxLength)`:**
- If `str.length <= maxLength`, return unchanged
- Otherwise, truncate to `maxLength - 3` and append `"..."`
- Validate `maxLength >= 3` (throw error if not)
- Example: `truncate("Hello World", 8)` → `"Hello..."`

**`slugify(str)`:**
- Convert to lowercase
- Replace spaces and non-alphanumeric chars with hyphens
- Collapse multiple hyphens to single hyphen
- Trim leading/trailing hyphens
- Example: `"Hello World! 123"` → `"hello-world-123"`

### 3. Add Comprehensive Tests

**File:** `src/utils/string-utils.test.ts`

Test coverage must include:

**For `capitalize`:**
- Empty string
- Single character
- Already capitalized
- Lowercase string
- String with numbers/special chars

**For `truncate`:**
- String shorter than maxLength
- String equal to maxLength
- String longer than maxLength
- maxLength < 3 (should throw error)
- Edge cases: maxLength = 3, very long strings

**For `slugify`:**
- Simple words with spaces
- Mixed case
- Special characters
- Multiple consecutive spaces
- Leading/trailing spaces
- Numbers and letters
- Unicode/emoji handling (basic)

### 4. Export from Index

**File:** `src/utils/index.ts`

Create or update to export all functions:

```typescript
export { capitalize, truncate, slugify } from './string-utils';
```

## Implementation Steps

1. **Create directory structure** (if not exists):
   ```bash
   mkdir -p src/utils
   ```

2. **Implement `src/utils/string-utils.ts`**:
   - Add JSDoc comments for each function
   - Implement all 3 functions following guidelines above
   - Keep implementations simple and readable
   - Use TypeScript strict mode

3. **Create `src/utils/string-utils.test.ts`**:
   - Use your project's test framework (Jest, Vitest, etc.)
   - Write comprehensive test cases for all functions
   - Organize tests in `describe` blocks per function
   - Include edge cases and error scenarios

4. **Create/update `src/utils/index.ts`**:
   - Export all three functions
   - Keep it minimal (just exports, no logic)

5. **Verify implementation**:
   - Run TypeScript compiler: `tsc --noEmit`
   - Run linter: `npm run lint` or `eslint src/utils/`
   - Run tests: `npm test` or `jest src/utils/`
   - All checks must pass

6. **Create basic TypeScript config if needed**:
   - Only if `tsconfig.json` doesn't exist
   - Minimal config: strict mode, ES2020+ target

## Constraints

### Type Safety
- **Strict TypeScript**: No `any`, no type assertions unless absolutely necessary
- **Type all parameters**: Explicit types for all function parameters
- **Return types**: Explicit return types for all functions
- **No unsafe casts**: Avoid `as` unless unavoidable

### Dependencies
- **Zero external dependencies** for the utility functions
- **Only dev dependencies** for testing (Jest/Vitest)
- Do not install lodash, ramda, or any string utility libraries

### Code Style
- **Simple, direct implementations**: No complex abstractions
- **Readable over clever**: Clear logic beats one-liners
- **Consistent naming**: camelCase for functions, clear parameter names
- **JSDoc comments**: Document purpose, params, returns, and examples

### File Organization
- **Keep utilities pure**: No side effects, no global state
- **One purpose per function**: Each function does one thing well
- **Predictable behavior**: Same input always produces same output

## Anti-Patterns to Avoid

❌ **Over-engineering:**
```typescript
// BAD: Unnecessary abstraction
class StringTransformer {
  constructor(private strategy: TransformStrategy) {}
  transform(str: string): string { ... }
}
```

✅ **Simple and direct:**
```typescript
// GOOD: Direct function
export function capitalize(str: string): string {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
}
```

❌ **External dependencies:**
```typescript
// BAD: Using lodash
import { capitalize } from 'lodash';
export { capitalize };
```

✅ **Self-contained:**
```typescript
// GOOD: Implement it yourself
export function capitalize(str: string): string { ... }
```

❌ **Complex validation:**
```typescript
// BAD: Over-validated
export function truncate(str: string, maxLength: number): string {
  if (typeof str !== 'string') throw new TypeError('...');
  if (typeof maxLength !== 'number') throw new TypeError('...');
  if (!Number.isInteger(maxLength)) throw new TypeError('...');
  if (maxLength < 0) throw new RangeError('...');
  // ... more validation
}
```

✅ **Minimal validation:**
```typescript
// GOOD: Only essential checks
export function truncate(str: string, maxLength: number): string {
  if (maxLength < 3) throw new Error('maxLength must be >= 3');
  // ... implementation
}
```

❌ **Premature optimization:**
```typescript
// BAD: Complex regex caching, memoization for simple functions
const SLUG_REGEX_CACHE = new Map<string, RegExp>();
```

✅ **Keep it simple:**
```typescript
// GOOD: Just implement it directly
export function slugify(str: string): string {
  return str
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}
```

## Success Criteria

Before committing and pushing, verify:

- [ ] `src/utils/string-utils.ts` created with all 3 functions
- [ ] `src/utils/string-utils.test.ts` created with comprehensive tests
- [ ] `src/utils/index.ts` exports all functions
- [ ] All functions have proper TypeScript types (no `any`)
- [ ] All functions have JSDoc comments
- [ ] TypeScript compilation passes (`tsc --noEmit`)
- [ ] Linter passes (no errors)
- [ ] All tests pass
- [ ] No external dependencies added (only dev dependencies for testing)
- [ ] Code is simple, readable, and follows KISS principle

## Final Steps - ⚠️ CRITICAL ⚠️

After completing all tasks and verifying success criteria:

### 1. Commit Your Changes

```bash
git add src/utils/string-utils.ts
git add src/utils/string-utils.test.ts
git add src/utils/index.ts
# Add any other files you created (tsconfig.json, package.json, etc.)

git commit -m "feat: Add string utility functions

- Implement capitalize, truncate, and slugify functions
- Add comprehensive test coverage for all functions
- Export utilities from src/utils/index.ts
- Zero external dependencies, TypeScript strict mode

Made by Writer [your-model-name]"
```

### 2. Push to Your Branch

```bash
git push origin writer-<model-slug>/string-utils
```

Replace `<model-slug>` with your model identifier (e.g., `sonnet` or `codex`).

### 3. Verify Push Succeeded

```bash
git status
# Should show: "Your branch is up to date with 'origin/writer-<model-slug>/string-utils'"

git log origin/writer-<model-slug>/string-utils..HEAD
# Should show no unpushed commits (empty output)
```

### 4. Provide Final Summary

**State clearly in your response:**

- ✅ Branch name: `writer-<model-slug>/string-utils`
- ✅ Commit hash: `<git log -1 --format=%H>`
- ✅ Push verified: Confirmed with `git status`
- ✅ All success criteria met

**Example:**
```
Writer sonnet complete for string-utils task.
Branch: writer-sonnet/string-utils
Commit: abc123def456...
Push verified: Branch is up to date with origin
All tests passing, TypeScript strict mode, zero dependencies
```

## ⚠️ CRITICAL WARNING ⚠️

**The judge panel needs your pushed changes to review your work!**

If you do not commit and push:
- Your changes will NOT be reviewed
- Your work will NOT be considered
- The panel cannot compare your solution to the other writer's solution

**Do not proceed to the next task until you have confirmed your branch is pushed to origin.**

---

## Testing Commands Reference

Depending on your project setup, use the appropriate commands:

**TypeScript Check:**
```bash
tsc --noEmit
# or
npx tsc --noEmit
```

**Run Tests:**
```bash
npm test
# or
npm run test
# or
jest src/utils/
# or
npx vitest run
```

**Linting:**
```bash
npm run lint
# or
eslint src/utils/
# or
npx eslint src/utils/
```

**If you need to create a basic project setup:**
```bash
# Initialize npm if needed
npm init -y

# Install TypeScript
npm install --save-dev typescript

# Install test framework (choose one)
npm install --save-dev jest @types/jest ts-jest
# or
npm install --save-dev vitest

# Create basic tsconfig.json
npx tsc --init --strict --target ES2020 --module ESNext --moduleResolution node
```

---

Good luck! Remember: **Simple, type-safe, well-tested, zero dependencies.**
