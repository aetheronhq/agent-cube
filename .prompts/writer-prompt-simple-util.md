# Writer Prompt: String Utility Functions

## Context

You are participating in a dual-writer workflow where two AI agents independently implement the same task. Your implementation will be compared against another writer's approach, with differences analyzed by a judge panel to select the best solution.

**Your Goal:** Implement a clean, type-safe TypeScript utility module for string manipulation functions.

## Task Overview

Create a simple TypeScript utility module with string helper functions that can be used across the codebase.

## Requirements

### 1. Create Module File
- **Path:** `src/utils/string-utils.ts`
- Implement as a standalone module with no external dependencies
- Use TypeScript with strict type checking

### 2. Implement Three Functions

#### Function 1: `capitalize(str: string): string`
- Capitalize the first letter of a string
- Leave remaining characters unchanged
- Handle empty strings gracefully
- Example: `capitalize("hello")` → `"Hello"`

#### Function 2: `truncate(str: string, maxLength: number): string`
- Truncate string to specified maximum length
- Add ellipsis (`...`) when truncated
- Ellipsis should count toward max length
- Handle edge cases (empty string, maxLength ≤ 3)
- Example: `truncate("Hello World", 8)` → `"Hello..."`

#### Function 3: `slugify(str: string): string`
- Convert string to URL-safe slug
- Convert to lowercase
- Replace spaces with hyphens
- Remove special characters
- Handle multiple consecutive spaces/hyphens
- Example: `slugify("Hello World!")` → `"hello-world"`

### 3. Add Comprehensive Tests
- Create test file: `src/utils/string-utils.test.ts`
- Test all functions with multiple scenarios
- Cover edge cases: empty strings, special characters, unicode, etc.
- Ensure 100% code coverage
- All tests must pass

### 4. Export from Index
- Update or create `src/utils/index.ts`
- Re-export all three functions
- Follow standard barrel export pattern

## Implementation Steps

1. **Setup**: Create `src/utils/` directory if it doesn't exist
2. **Implement**: Write `string-utils.ts` with all three functions
3. **Type Safety**: Add proper TypeScript types and JSDoc comments
4. **Test**: Create comprehensive test suite
5. **Run Tests**: Execute and verify all tests pass
6. **Export**: Add barrel export in `index.ts`
7. **Verify**: Final check of all functionality
8. **Commit**: Create git commit with your changes
9. **Push**: Push your implementation to the remote repository

## Constraints

### Must Have
- ✅ TypeScript with strict mode compliance
- ✅ No external dependencies (use only native JavaScript)
- ✅ Pure functions (no side effects)
- ✅ Input validation for edge cases
- ✅ All tests passing
- ✅ Clear, descriptive function and variable names

### Must Not Have
- ❌ External libraries (no lodash, underscore, etc.)
- ❌ Mutations of input parameters
- ❌ Console logs or debugging code
- ❌ Dead code or commented-out code
- ❌ Type assertions (`as any`)
- ❌ `@ts-ignore` comments

## Code Quality Standards

### Readability
- Code should be self-documenting
- Minimal comments (only where truly needed)
- Consistent formatting and naming conventions
- Logical organization of code

### TypeScript Best Practices
- Explicit return types on all functions
- Use const for immutable values
- Leverage type inference where appropriate
- No implicit any types

### Testing Standards
- Descriptive test names that explain what's being tested
- Arrange-Act-Assert pattern
- Test both happy path and edge cases
- Use appropriate matchers (toBe, toEqual, etc.)

## Anti-Patterns to Avoid

### ❌ Over-Engineering
```typescript
// DON'T: Complex regex when simple logic suffices
const capitalize = (str: string): string => 
  str.replace(/^(.)(.*)$/, (_, first, rest) => first.toUpperCase() + rest);
```

### ❌ Poor Edge Case Handling
```typescript
// DON'T: Assume non-empty string
const capitalize = (str: string): string => 
  str[0].toUpperCase() + str.slice(1); // Fails on empty string!
```

### ❌ Type Unsafe Code
```typescript
// DON'T: Use any or loose types
const truncate = (str: any, max: any) => { /* ... */ }
```

### ❌ Mutation
```typescript
// DON'T: Mutate input
const slugify = (str: string): string => {
  str = str.toLowerCase(); // Mutating parameter!
  return str;
}
```

### ❌ Inadequate Testing
```typescript
// DON'T: Test only happy path
test('capitalize works', () => {
  expect(capitalize('hello')).toBe('Hello');
  // Missing: empty string, single char, already capitalized, etc.
});
```

## Success Criteria

Your implementation will be evaluated on:

### ✅ Correctness (30%)
- All functions work as specified
- All edge cases handled properly
- All tests pass

### ✅ Code Quality (30%)
- Clean, readable code
- Proper TypeScript usage
- No code smells or anti-patterns
- Follows best practices

### ✅ Testing (20%)
- Comprehensive test coverage
- Well-written test cases
- Edge cases covered
- Clear test descriptions

### ✅ Simplicity (10%)
- No unnecessary complexity
- No external dependencies
- Straightforward logic
- Maintainable code

### ✅ Completeness (10%)
- All requirements met
- Proper file structure
- Correct exports
- Clean git history

## Deliverables Checklist

Before finalizing your implementation, verify:

- [ ] `src/utils/string-utils.ts` exists with all 3 functions
- [ ] All functions have proper TypeScript types
- [ ] `src/utils/string-utils.test.ts` exists with comprehensive tests
- [ ] All tests pass (run test suite)
- [ ] `src/utils/index.ts` exports all functions
- [ ] No TypeScript compilation errors
- [ ] No external dependencies added
- [ ] Code is clean and readable
- [ ] Git commit created with descriptive message
- [ ] Changes pushed to remote repository

## Final Steps (CRITICAL)

**After completing implementation and verifying all tests pass:**

1. **Stage your changes:**
   ```bash
   git add src/utils/
   ```

2. **Create a descriptive commit:**
   ```bash
   git commit -m "feat: add string utility functions (capitalize, truncate, slugify)"
   ```

3. **Push to remote:**
   ```bash
   git push
   ```

**⚠️ IMPORTANT:** The dual-writer workflow requires your implementation to be pushed to the remote repository for comparison. **You MUST commit and push your changes** before completing this task.

## Notes

- Focus on writing clean, maintainable code rather than clever tricks
- When in doubt, prioritize simplicity over complexity
- Your implementation will be compared with another writer's approach
- The judge panel will evaluate both implementations for quality and correctness
- Good luck!
