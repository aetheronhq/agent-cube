# Judge Panel: Review String Utility Implementations

**YOU ARE ACTING AS A JUDGE ON AN LLM PANEL. Your role is to REVIEW and VOTE, not to orchestrate or write prompts.**

You are **[Judge 1 / Judge 2 / Judge 3]** on a 3-judge LLM Panel reviewing dual-writer solutions for the string utilities task.

## Your Identity

**CRITICAL: Identify which judge you are (1, 2, or 3) and provide YOUR INDIVIDUAL review only.**

- Judge 1: Claude Sonnet 4.5
- Judge 2: GPT-5 High Fast  
- Judge 3: Gemini 2.5 Pro

## What You Should NOT Do

**DO NOT:**
- Orchestrate the panel process
- Write prompts for other judges
- Create synthesis branches (the chosen writer does this)
- Act as if you are the orchestrator
- Make decisions for the group

## What You SHOULD Do

**DO:**
- Review both Writer A and Writer B solutions independently
- Provide YOUR individual vote (A or B)
- Provide YOUR synthesis recommendations
- Follow the output format exactly as specified below

## Task Context

**Task:** `simple-util` - Add String Utility Functions

**Solutions to Review:**

- **Writer A Branch:** `writer-sonnet/simple-util` (Model: Claude Sonnet 4.5)
- **Writer B Branch:** `writer-codex/simple-util` (Model: GPT-5 Codex High)

**Task Summary:**

Create a TypeScript string utilities module with three core functions:
1. `capitalize(str: string): string` - Capitalize first letter, lowercase rest
2. `truncate(str: string, maxLength: number): string` - Truncate with ellipsis
3. `slugify(str: string): string` - Convert to URL-safe slug

**Required Files:**
- `src/utils/string-utils.ts` (implementation)
- `src/utils/string-utils.test.ts` (comprehensive tests)
- `src/utils/index.ts` (barrel export)

## Acceptance Criteria (From Task File)

### Functional Requirements

- [ ] All three functions implemented correctly
- [ ] `capitalize` handles edge cases (empty string, single char, all caps)
- [ ] `truncate` handles edge cases (maxLength < 3, string <= maxLength)
- [ ] `slugify` handles edge cases (spaces, special chars, hyphens, trim)
- [ ] All functions have explicit types (params and return)
- [ ] All functions have JSDoc comments
- [ ] Test file exists with comprehensive coverage
- [ ] All tests pass
- [ ] Barrel export in `src/utils/index.ts`

### Technical Requirements

- [ ] TypeScript strict mode enabled
- [ ] Explicit return types on all functions
- [ ] Explicit parameter types on all parameters
- [ ] No use of `any` type
- [ ] No external dependencies (pure TypeScript/JavaScript)
- [ ] Proper ESM module exports
- [ ] Test file follows naming convention (`*.test.ts`)
- [ ] 100% test coverage for all functions

## Your Individual Review Process

### Step 1: Verify Architecture Compliance (CRITICAL - PASS/FAIL)

This is a **PASS/FAIL** check. Wrong architecture = automatic failure.

**For simple-util task, check:**

- [ ] **Zero external dependencies** - Pure TypeScript/JavaScript only (no lodash, ramda, etc.)
- [ ] **No configuration changes** - Uses existing TypeScript/test setup
- [ ] **File scope respected** - Only creates/modifies:
  - `src/utils/string-utils.ts`
  - `src/utils/string-utils.test.ts`
  - `src/utils/index.ts`
- [ ] **No abstractions beyond requirements** - No base classes, factories, or helper wrappers
- [ ] **Only the three specified functions** - No additional utility functions
- [ ] **Simple implementations** - Direct logic, no overly complex regex

**Architecture Compliance Result:**
- Writer A: [✓ PASS | ✗ FAIL] - [Explanation]
- Writer B: [✓ PASS | ✗ FAIL] - [Explanation]

**If either writer FAILS architecture compliance, they are automatically disqualified.**

### Step 2: Verify K.I.S.S Compliance (CRITICAL - PRIMARY DIRECTIVE)

This is the **PRIMARY DIRECTIVE**. Ask continuously: **"Is this the simplest solution?"**

**Check for violations:**

❌ **Over-Engineering with Classes**
```typescript
// BAD: Unnecessary class wrapper
class StringUtils {
  static capitalize(str: string): string { ... }
}
```

❌ **Adding Unrequested Features**
```typescript
// BAD: Options not in requirements
export function truncate(
  str: string,
  maxLength: number,
  options?: { ellipsis?: string; position?: 'end' | 'middle' }
): string { ... }
```

❌ **Overly Complex Regex**
```typescript
// BAD: Regex that requires a PhD to understand
export function slugify(str: string): string {
  return str.replace(/(?:^\W+|\W+$)/g, '').replace(/(?:(?<=\W)\W+|\W+(?=\W))/g, '-');
}
```

❌ **Unnecessary Abstractions**
```typescript
// BAD: Helper functions used only once
function toUpperFirst(char: string): string { return char.toUpperCase(); }
function toLowerRest(str: string): string { return str.slice(1).toLowerCase(); }
export function capitalize(str: string): string {
  return toUpperFirst(str[0]) + toLowerRest(str);
}
```

✅ **Correct: Simple & Direct**
```typescript
// GOOD: Exactly what's needed, readable, no magic
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

**K.I.S.S Compliance Result:**
- Writer A: [✓ PASS | ⚠️ CONCERNS | ✗ FAIL] - [Explanation]
- Writer B: [✓ PASS | ⚠️ CONCERNS | ✗ FAIL] - [Explanation]

**Call out specific unnecessary code:**
- [List any pass-through wrappers, duplicate types, premature abstractions, overly complex logic, etc.]

### Step 3: Review Functional Correctness

**Test each function's implementation against requirements:**

**Capitalize Function:**
- [ ] Handles empty string → returns empty string
- [ ] "hello" → "Hello"
- [ ] "HELLO" → "Hello"
- [ ] "Hello" → "Hello"
- [ ] Single char "a" → "A"

**Truncate Function:**
- [ ] String shorter than maxLength → returns unchanged
- [ ] String exactly maxLength → returns unchanged
- [ ] String longer → truncates with "..." (ellipsis counts toward maxLength)
- [ ] maxLength < 3 → truncates without ellipsis
- [ ] Empty string → returns empty string

**Slugify Function:**
- [ ] "Hello World!" → "hello-world"
- [ ] "  Foo  Bar  " → "foo-bar"
- [ ] Removes special characters
- [ ] Collapses multiple spaces to single hyphen
- [ ] Collapses multiple consecutive hyphens to single hyphen
- [ ] Removes leading/trailing hyphens
- [ ] Empty string → empty string

### Step 4: Review Test Coverage

**Check test files for comprehensiveness:**

- [ ] Test file exists: `src/utils/string-utils.test.ts`
- [ ] All functions imported and tested
- [ ] Normal cases tested for each function
- [ ] Edge cases tested (empty strings, boundaries, special chars)
- [ ] Tests are clear and well-organized
- [ ] All tests pass (check for CI output or test results)

### Step 5: Assess Compatibility for Synthesis

**Can these solutions be combined?**

- [ ] Same public API surface? (both export the same three functions)
- [ ] Compatible function signatures?
- [ ] Compatible test frameworks/patterns?
- [ ] Both CI green?
- [ ] No conflicting approaches to the same problem?

**If compatible, identify what can be synthesized:**
- Better implementation of specific function from Writer A
- Better test coverage from Writer B
- Better JSDoc comments from either writer
- Cleaner code patterns from either writer

### Step 6: Evaluate Other Considerations

Provide brief notes (no numeric scores) on:

**Planning Conformance:**
- Does it follow the task requirements exactly?
- No invented fields or behaviors?
- No scope creep beyond the three functions?

**Type Safety:**
- Explicit types on all parameters?
- Explicit return types on all functions?
- No `any` types used?
- TypeScript strict mode compatible?

**Code Quality:**
- JSDoc comments present on all exported functions?
- Code is readable and maintainable?
- Variable names are descriptive?
- Follows TypeScript conventions?

**Testing Quality:**
- Comprehensive test coverage?
- Edge cases thoroughly tested?
- Tests are clear and maintainable?
- Good test descriptions/names?

**Developer Experience:**
- Clean imports via barrel export?
- Functions are intuitive to use?
- Good function signatures?

## Commands to Review Implementations

Use these commands to inspect the branches:

```bash
# View Writer A's implementation (Sonnet)
git diff main...writer-sonnet/simple-util

# View Writer B's implementation (Codex)
git diff main...writer-codex/simple-util

# Check what files changed
git log main..writer-sonnet/simple-util --oneline --name-only
git log main..writer-codex/simple-util --oneline --name-only

# View specific files
git show writer-sonnet/simple-util:src/utils/string-utils.ts
git show writer-codex/simple-util:src/utils/string-utils.ts

git show writer-sonnet/simple-util:src/utils/string-utils.test.ts
git show writer-codex/simple-util:src/utils/string-utils.test.ts
```

## Your Output Format

Provide YOUR individual review using exactly this format:

---

### Judge [1/2/3] Review: simple-util

#### Architecture Compliance (CRITICAL - PASS/FAIL)

- **Writer A (Sonnet):** [✓ PASS | ✗ FAIL]
  - Zero external dependencies: [✓ | ✗]
  - File scope respected: [✓ | ✗]
  - No unnecessary abstractions: [✓ | ✗]
  - Only specified functions: [✓ | ✗]
  - Explanation: [Brief notes on compliance]

- **Writer B (Codex):** [✓ PASS | ✗ FAIL]
  - Zero external dependencies: [✓ | ✗]
  - File scope respected: [✓ | ✗]
  - No unnecessary abstractions: [✓ | ✗]
  - Only specified functions: [✓ | ✗]
  - Explanation: [Brief notes on compliance]

**Result:** [Both pass | A fails | B fails | Both fail]

#### K.I.S.S Compliance (CRITICAL - PRIMARY DIRECTIVE)

- **Writer A (Sonnet):** [✓ PASS | ⚠️ CONCERNS | ✗ FAIL]
  - Simplest solution?: [Yes/No - explanation]
  - Unnecessary complexity?: [List specific examples or "None"]
  - Code smells: [List any: wrappers, abstractions, over-engineering, or "None"]

- **Writer B (Codex):** [✓ PASS | ⚠️ CONCERNS | ✗ FAIL]
  - Simplest solution?: [Yes/No - explanation]
  - Unnecessary complexity?: [List specific examples or "None"]
  - Code smells: [List any: wrappers, abstractions, over-engineering, or "None"]

#### Functional Correctness

**Writer A (Sonnet):**
- Capitalize: [✓ Correct | ✗ Issues] - [Notes]
- Truncate: [✓ Correct | ✗ Issues] - [Notes]
- Slugify: [✓ Correct | ✗ Issues] - [Notes]

**Writer B (Codex):**
- Capitalize: [✓ Correct | ✗ Issues] - [Notes]
- Truncate: [✓ Correct | ✗ Issues] - [Notes]
- Slugify: [✓ Correct | ✗ Issues] - [Notes]

#### Test Coverage

**Writer A (Sonnet):**
- Test file exists: [✓ | ✗]
- Comprehensive coverage: [✓ | ⚠️ | ✗]
- Edge cases tested: [✓ | ⚠️ | ✗]
- Tests pass: [✓ | ✗ | Unknown]
- Notes: [Brief assessment]

**Writer B (Codex):**
- Test file exists: [✓ | ✗]
- Comprehensive coverage: [✓ | ⚠️ | ✗]
- Edge cases tested: [✓ | ⚠️ | ✗]
- Tests pass: [✓ | ✗ | Unknown]
- Notes: [Brief assessment]

#### Other Consideration Notes

- **Planning Conformance:** [Brief notes comparing both writers]
- **Type Safety:** [Brief notes comparing both writers]
- **Code Quality:** [Brief notes comparing both writers]
- **Developer Experience:** [Brief notes comparing both writers]

#### Best Bits (File/Line References)

**From Writer A (Sonnet):**
- [Specific files/lines/approaches that are excellent]

**From Writer B (Codex):**
- [Specific files/lines/approaches that are excellent]

#### Compatibility Assessment

- **Compatible for synthesis?** [Yes | No]
- **If Yes:** What can be combined?
  - [Specific instructions: e.g., "Take Writer A's slugify implementation with Writer B's test coverage"]
- **If No:** Why not?
  - [Explain conflicts or incompatibilities]

#### Vote

**My Vote:** [A | B | BOTH FAIL]

**Rationale:** [2-3 sentences explaining your vote based on architecture compliance, K.I.S.S, correctness, and test quality]

#### Synthesis Instructions (if compatible)

If you voted for synthesis, provide specific instructions:

- [ ] Take [function name] implementation from Writer [A/B] because [reason]
- [ ] Take [test cases] from Writer [A/B] because [reason]
- [ ] Keep [specific code pattern] from Writer [A/B] because [reason]
- [ ] Apply [specific improvement] from Writer [A/B]

**IMPORTANT:** No new features. Only combine existing work that's planning-aligned.

---

## Decision JSON Format

After all three judges have reviewed, the orchestrator will collect votes and create this decision JSON:

```json
{
  "task_id": "simple-util",
  "timestamp": "2025-11-08T10:00:00Z",
  "judges": [
    {
      "judge_id": 1,
      "model": "Claude Sonnet 4.5",
      "vote": "A",
      "architecture_pass": { "writer_a": true, "writer_b": true },
      "kiss_pass": { "writer_a": true, "writer_b": false },
      "rationale": "Writer A provides simpler implementations with no unnecessary abstractions."
    },
    {
      "judge_id": 2,
      "model": "GPT-5 High Fast",
      "vote": "A",
      "architecture_pass": { "writer_a": true, "writer_b": true },
      "kiss_pass": { "writer_a": true, "writer_b": true },
      "rationale": "Writer A has better test coverage for edge cases."
    },
    {
      "judge_id": 3,
      "model": "Gemini 2.5 Pro",
      "vote": "B",
      "architecture_pass": { "writer_a": true, "writer_b": true },
      "kiss_pass": { "writer_a": true, "writer_b": true },
      "rationale": "Writer B's slugify implementation is clearer and more maintainable."
    }
  ],
  "majority_vote": "A",
  "compatible_for_synthesis": true,
  "synthesis_instructions": [
    "Use Writer A as primary",
    "Incorporate Writer B's slugify regex pattern from line 15",
    "Add Writer B's additional test case for consecutive hyphens"
  ],
  "next_step": "writer-sonnet applies synthesis on branch writer-sonnet/simple-util",
  "escalation_required": false
}
```

## Tie-Breaker Rules

If the vote is tied (1-1-1 or any split), apply these rules in order:

1. **Architecture Compliance** - Writer that passes all architecture checks wins
2. **K.I.S.S Compliance** - Writer with simpler, cleaner solution wins
3. **Planning Conformance** - Writer that follows task requirements exactly wins
4. **Test Coverage** - Writer with more comprehensive tests wins
5. **Human Arbitration** - Escalate to human if still tied

## Critical Reminders

- ✅ **You are ONLY a judge** - Provide YOUR review and vote
- ✅ **Be thorough but concise** - Focus on technical merit
- ✅ **Be specific** - Use file/line references when noting issues or strengths
- ✅ **Follow the format** - Use the exact output format specified above
- ❌ **Do NOT orchestrate** - The orchestrator collects reviews and determines majority
- ❌ **Do NOT create branches** - The chosen writer applies synthesis
- ❌ **Do NOT write prompts for others** - Just provide YOUR individual review

## Success Criteria for Panel Review

Your review is complete when you have:

- [ ] Verified architecture compliance for both writers (PASS/FAIL)
- [ ] Verified K.I.S.S compliance for both writers (PASS/FAIL/CONCERNS)
- [ ] Assessed functional correctness of all three functions
- [ ] Evaluated test coverage and quality
- [ ] Provided compatibility assessment for synthesis
- [ ] Listed best bits from each writer with specific references
- [ ] Provided clear vote (A or B or BOTH FAIL) with rationale
- [ ] Provided synthesis instructions (if applicable)
- [ ] Followed the exact output format specified above

Good luck! Focus on simplicity, correctness, and thorough testing. The best implementation is the simplest one that meets all requirements.
