# Task 17: Add mypy Type Checking to Workflow

**Priority:** P2 (Medium-High)
**Complexity:** Low
**Estimated Time:** 30-60 minutes
**Depends On:** None

---

## Problem

Python's type hints are not enforced at runtime, leading to AttributeErrors that could be caught statically:

```python
# This fails at RUNTIME, not when written:
writer_info.letter  # AttributeError if 'letter' field missing
```

**Recent examples:**
- `WriterInfo.letter` missing → 3 tasks crashed
- `WriterConfig.letter` missing → 2 tasks crashed  
- `run_synthesis(both_writers=...)` → invalid parameter

mypy is already configured in `pyproject.toml` but not integrated into the workflow.

---

## Solution

Add mypy type checking to catch these issues before code runs.

### 1. Add to E2E Workflow

**File:** `.github/workflows/e2e.yml`

Add mypy check before tests:

```yaml
- name: Type check with mypy
  run: |
    pip install mypy
    mypy python/cube --ignore-missing-imports
```

### 2. Add Pre-commit Hook (Optional)

**File:** `.git/hooks/pre-commit`

```bash
#!/bin/bash
mypy python/cube --ignore-missing-imports
if [ $? -ne 0 ]; then
  echo "❌ mypy type check failed"
  exit 1
fi
```

### 3. Update Development Docs

**File:** `CONTRIBUTING.md`

Add section:
```markdown
## Type Checking

Run mypy before committing:
```bash
mypy python/cube --ignore-missing-imports
```

Install dev dependencies:
```bash
pip install -e ".[dev]"
```

### 4. Fix Existing Type Issues

Run mypy and fix any existing issues:
```bash
mypy python/cube --ignore-missing-imports
```

Common fixes:
- Add missing type hints
- Fix incorrect return types
- Add `# type: ignore` for unavoidable issues

---

## Configuration

Current `pyproject.toml` config (already exists):

```toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_ignores = true
```

May need to add:
```toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_ignores = true
ignore_missing_imports = true  # For external packages
check_untyped_defs = true
disallow_untyped_defs = false  # Too strict for now
```

---

## Verification

1. Run mypy on entire codebase: `mypy python/cube`
2. Fix all errors (or add `# type: ignore` with justification)
3. Verify E2E tests still pass
4. Test pre-commit hook (if added)

---

## Success Criteria

- [ ] mypy runs in CI/CD (E2E workflow)
- [ ] No mypy errors in `python/cube/` (or justified ignores)
- [ ] Documentation updated with type-checking instructions
- [ ] (Optional) Pre-commit hook installed

---

## Benefits

- Catch AttributeErrors at write-time, not runtime
- Catch invalid function arguments before execution
- Better IDE autocomplete and error detection
- Prevent type-related bugs from reaching production

---

## Estimated Impact

**High value, low effort:**
- Prevents entire classes of bugs (AttributeError, TypeError)
- Already configured, just needs integration
- ~30-60 minutes to add to workflow and fix existing issues


**Priority:** P2 (Medium-High)
**Complexity:** Low
**Estimated Time:** 30-60 minutes
**Depends On:** None

---

## Problem

Python's type hints are not enforced at runtime, leading to AttributeErrors that could be caught statically:

```python
# This fails at RUNTIME, not when written:
writer_info.letter  # AttributeError if 'letter' field missing
```

**Recent examples:**
- `WriterInfo.letter` missing → 3 tasks crashed
- `WriterConfig.letter` missing → 2 tasks crashed  
- `run_synthesis(both_writers=...)` → invalid parameter

mypy is already configured in `pyproject.toml` but not integrated into the workflow.

---

## Solution

Add mypy type checking to catch these issues before code runs.

### 1. Add to E2E Workflow

**File:** `.github/workflows/e2e.yml`

Add mypy check before tests:

```yaml
- name: Type check with mypy
  run: |
    pip install mypy
    mypy python/cube --ignore-missing-imports
```

### 2. Add Pre-commit Hook (Optional)

**File:** `.git/hooks/pre-commit`

```bash
#!/bin/bash
mypy python/cube --ignore-missing-imports
if [ $? -ne 0 ]; then
  echo "❌ mypy type check failed"
  exit 1
fi
```

### 3. Update Development Docs

**File:** `CONTRIBUTING.md`

Add section:
```markdown
## Type Checking

Run mypy before committing:
```bash
mypy python/cube --ignore-missing-imports
```

Install dev dependencies:
```bash
pip install -e ".[dev]"
```

### 4. Fix Existing Type Issues

Run mypy and fix any existing issues:
```bash
mypy python/cube --ignore-missing-imports
```

Common fixes:
- Add missing type hints
- Fix incorrect return types
- Add `# type: ignore` for unavoidable issues

---

## Configuration

Current `pyproject.toml` config (already exists):

```toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_ignores = true
```

May need to add:
```toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_ignores = true
ignore_missing_imports = true  # For external packages
check_untyped_defs = true
disallow_untyped_defs = false  # Too strict for now
```

---

## Verification

1. Run mypy on entire codebase: `mypy python/cube`
2. Fix all errors (or add `# type: ignore` with justification)
3. Verify E2E tests still pass
4. Test pre-commit hook (if added)

---

## Success Criteria

- [ ] mypy runs in CI/CD (E2E workflow)
- [ ] No mypy errors in `python/cube/` (or justified ignores)
- [ ] Documentation updated with type-checking instructions
- [ ] (Optional) Pre-commit hook installed

---

## Benefits

- Catch AttributeErrors at write-time, not runtime
- Catch invalid function arguments before execution
- Better IDE autocomplete and error detection
- Prevent type-related bugs from reaching production

---

## Estimated Impact

**High value, low effort:**
- Prevents entire classes of bugs (AttributeError, TypeError)
- Already configured, just needs integration
- ~30-60 minutes to add to workflow and fix existing issues

