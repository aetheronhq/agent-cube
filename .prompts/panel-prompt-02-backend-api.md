# Judge Panel: Review Backend API Implementations

You are a judge on a panel reviewing two implementations of the FastAPI backend for AgentCube's web UI.

---

## 📋 Task Overview

The writers were asked to create a thin FastAPI wrapper that:
- Exposes REST endpoints for task management
- Wraps existing `cube.automation` and `cube.core` modules
- Provides workflow control (dual writers, judge panel, feedback)
- Implements a `cube ui` CLI command
- Uses background tasks for non-blocking operations
- Configures CORS for the React frontend

**Time Budget:** 3-4 hours

**Reference Documents:**
- Task specification: `implementation/web-ui/tasks/02-backend-api.md`
- Architecture spec: `planning/web-ui.md`

---

## 🔍 Review Process

### Step 1: Identify Writer Branches

```bash
# Find the writer branches for task 02-backend-api
git branch -r | grep "02-backend-api"
```

You should see two branches like:
- `origin/writer-<model-a>/02-backend-api`
- `origin/writer-<model-b>/02-backend-api`

### Step 2: Review Each Implementation

For each writer branch, examine:

```bash
# Checkout writer branch
git checkout writer-<model>/02-backend-api

# Review files changed
git diff main --stat
git diff main --name-only

# Review the actual changes
git diff main python/cube/ui/
git diff main python/cube/commands/ui.py
git diff main python/cube/cli.py
git diff main python/requirements.txt

# Check commit history
git log main..HEAD --oneline
```

### Step 3: Test Functionality

For each implementation, test the server:

```bash
# Install dependencies (if needed)
cd python
pip install -r requirements.txt

# Test server startup
cube ui

# In another terminal, test endpoints
curl http://localhost:3030/health
curl http://localhost:3030/api/tasks
curl -H "Origin: http://localhost:5173" -I http://localhost:3030/health

# Stop the server (Ctrl+C)
```

---

## ✅ Evaluation Criteria

Score each criterion on a scale of 0-10, where:
- **0-3**: Does not meet requirements, significant issues
- **4-6**: Partially meets requirements, some issues
- **7-8**: Meets requirements, minor issues
- **9-10**: Exceeds requirements, exemplary

### 1. Correctness (Weight: 25%)

**Does the implementation meet all functional requirements?**

- [ ] FastAPI app created in `python/cube/ui/server.py`
- [ ] CORS middleware configured for `http://localhost:5173`
- [ ] Server runs on port 3030 (default)
- [ ] `GET /health` returns `{"status": "ok"}`
- [ ] `GET /api/tasks` lists tasks from state directory
- [ ] `GET /api/tasks/{id}` returns task detail using `load_state()`
- [ ] `GET /api/tasks/{id}/logs` returns agent logs
- [ ] `POST /api/tasks/{id}/writers` delegates to `launch_dual_writers`
- [ ] `POST /api/tasks/{id}/panel` delegates to `launch_judge_panel`
- [ ] `POST /api/tasks/{id}/feedback` implemented
- [ ] Background tasks used for long-running operations
- [ ] `cube ui` command launches server and opens browser
- [ ] Command registered in `cli.py`

**Deductions:**
- Missing endpoints: -2 points per endpoint
- Blocking on long operations (no BackgroundTasks): -5 points
- Server doesn't start: -10 points
- CORS not configured: -3 points

**Score: __/10**

### 2. Code Quality (Weight: 25%)

**Is the code clean, maintainable, and well-structured?**

**Evaluate:**
- Type hints on all functions
- Pydantic models for request/response validation
- Proper error handling (HTTPException, try/except)
- Clear function and variable names
- Appropriate code comments (not excessive)
- Docstrings on public functions
- Consistent code style
- No code duplication
- Proper module organization

**Red flags:**
- Missing type hints: -2 points
- No error handling: -3 points
- Code duplication from cube.automation: -5 points
- Poor naming conventions: -2 points
- Excessive or no comments: -1 point

**Score: __/10**

### 3. Architecture Adherence (Weight: 20%)

**Does the implementation follow the KISS principle and thin wrapper pattern?**

**Key requirements:**
- ✅ Direct imports from `cube.automation` and `cube.core` (no duplication)
- ✅ Thin wrapper layer (no business logic in API)
- ✅ File-based state (no custom state management)
- ✅ Background tasks for async operations
- ❌ No database implementation
- ❌ No authentication/authorization
- ❌ No complex middleware beyond CORS

**Evaluate:**
- Proper delegation to existing modules
- No reimplementation of workflow logic
- Minimal logic in route handlers
- Appropriate use of FastAPI features
- No over-engineering

**Critical violations:**
- Reimplementing `launch_dual_writers` or `launch_judge_panel`: -10 points
- Custom state management instead of using existing: -5 points
- Adding unnecessary complexity (auth, database): -5 points

**Score: __/10**

### 4. Error Handling & Edge Cases (Weight: 15%)

**Does the implementation handle errors gracefully?**

**Check:**
- HTTP status codes used correctly (200, 404, 500)
- JSON error responses
- Validation of request data
- Handling of missing files/tasks
- Handling of invalid input
- Logging of errors
- Graceful server shutdown

**Test cases:**
- Request non-existent task: Should return 404
- Invalid prompt file path: Should return 404 or 400
- Malformed JSON in request: Should return 422
- Server error: Should return 500 with error message

**Deductions:**
- No error handling: -5 points
- Incorrect status codes: -2 points
- Server crashes on invalid input: -5 points
- No validation of request data: -3 points

**Score: __/10**

### 5. Testing & Verification (Weight: 10%)

**Has the implementation been properly tested?**

**Evidence of testing:**
- All endpoints manually tested
- Server starts without errors
- Browser auto-opens with `cube ui` command
- CORS headers present in responses
- Background tasks don't block requests
- Commit messages indicate testing

**Deductions:**
- No evidence of testing: -5 points
- Known issues not addressed: -3 points
- Server doesn't start cleanly: -5 points

**Score: __/10**

### 6. Documentation & Dependencies (Weight: 5%)

**Is the implementation properly documented?**

**Check:**
- `requirements.txt` updated with fastapi and uvicorn
- Docstrings on public functions
- Clear commit messages
- No unnecessary dependencies added
- Dependencies have version constraints

**Deductions:**
- Missing dependencies in requirements.txt: -3 points
- No docstrings: -2 points
- Unclear commit messages: -1 point

**Score: __/10**

---

## 📊 Scoring Rubric

Calculate the weighted total score:

```
Total Score = (Correctness × 0.25) + 
              (Code Quality × 0.25) + 
              (Architecture × 0.20) + 
              (Error Handling × 0.15) + 
              (Testing × 0.10) + 
              (Documentation × 0.05)
```

**Grade Interpretation:**

| Score | Grade | Recommendation |
|-------|-------|----------------|
| 9.0 - 10.0 | A+ | APPROVED - Exceptional implementation |
| 8.0 - 8.9 | A | APPROVED - Strong implementation |
| 7.0 - 7.9 | B+ | APPROVED - Good implementation |
| 6.0 - 6.9 | B | REQUEST_CHANGES - Acceptable with minor fixes |
| 5.0 - 5.9 | C | REQUEST_CHANGES - Needs improvements |
| 4.0 - 4.9 | D | REQUEST_CHANGES - Significant issues |
| 0.0 - 3.9 | F | REJECTED - Does not meet requirements |

---

## 🎯 Anti-Pattern Detection

**CRITICAL: Check for these anti-patterns that should result in REQUEST_CHANGES or REJECTED:**

### ❌ Anti-Pattern 1: Reimplementing Workflow Logic

```python
# BAD: Copying code from cube.automation
@app.post("/api/tasks/{task_id}/writers")
async def start_writers(task_id: str, prompt_file: str):
    config = load_config()
    writer_a = config.writers.writer_a
    # ... 100+ lines of duplicated code
```

**Impact:** REJECTED if more than 20 lines of workflow logic reimplemented

### ❌ Anti-Pattern 2: Blocking on Long Operations

```python
# BAD: Waiting for completion
@app.post("/api/tasks/{task_id}/writers")
async def start_writers(task_id: str, prompt_file: str):
    await launch_dual_writers(task_id, Path(prompt_file))  # Blocks!
    return {"status": "completed"}
```

**Impact:** REQUEST_CHANGES - Must use BackgroundTasks

### ❌ Anti-Pattern 3: No Error Handling

```python
# BAD: No validation or error handling
@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    state = load_state(task_id)
    return state.dict()  # Crashes if state is None!
```

**Impact:** REQUEST_CHANGES - Critical endpoints must handle errors

### ❌ Anti-Pattern 4: Missing Type Hints

```python
# BAD: No type annotations
def ui_command(port=3030):
    pass
```

**Impact:** REQUEST_CHANGES if >30% of functions lack type hints

---

## 📝 Decision Template

After reviewing both implementations, provide your decision using this exact JSON format:

```json
{
  "task_id": "02-backend-api",
  "judge_id": "judge-<your-model>",
  "timestamp": "2025-11-11T<time>Z",
  "reviews": {
    "writer_a": {
      "branch": "writer-<model-a>/02-backend-api",
      "scores": {
        "correctness": 0.0,
        "code_quality": 0.0,
        "architecture": 0.0,
        "error_handling": 0.0,
        "testing": 0.0,
        "documentation": 0.0,
        "total": 0.0
      },
      "strengths": [
        "List 2-4 key strengths"
      ],
      "weaknesses": [
        "List 2-4 key weaknesses or concerns"
      ],
      "critical_issues": [
        "List any blocking issues (empty if none)"
      ],
      "recommendation": "APPROVED | REQUEST_CHANGES | REJECTED",
      "summary": "2-3 sentence summary of the implementation"
    },
    "writer_b": {
      "branch": "writer-<model-b>/02-backend-api",
      "scores": {
        "correctness": 0.0,
        "code_quality": 0.0,
        "architecture": 0.0,
        "error_handling": 0.0,
        "testing": 0.0,
        "documentation": 0.0,
        "total": 0.0
      },
      "strengths": [
        "List 2-4 key strengths"
      ],
      "weaknesses": [
        "List 2-4 key weaknesses or concerns"
      ],
      "critical_issues": [
        "List any blocking issues (empty if none)"
      ],
      "recommendation": "APPROVED | REQUEST_CHANGES | REJECTED",
      "summary": "2-3 sentence summary of the implementation"
    }
  },
  "comparison": {
    "better_implementation": "writer_a | writer_b | tie",
    "rationale": "2-3 sentences explaining why one is better (or why it's a tie)",
    "key_differences": [
      "List 2-3 significant differences between implementations"
    ]
  },
  "panel_recommendation": {
    "final_decision": "APPROVED | REQUEST_CHANGES | REJECTED",
    "selected_writer": "writer_a | writer_b | none",
    "confidence": "high | medium | low",
    "reasoning": "Detailed explanation of final decision (3-5 sentences)",
    "next_steps": [
      "List specific actions to take (merge, request fixes, reject, etc.)"
    ]
  }
}
```

---

## 🎯 Judging Guidelines

### Objectivity

- Focus on technical merit, not style preferences
- Use the scoring rubric consistently
- Cite specific code examples for critiques
- Be fair and balanced in evaluation

### Thoroughness

- Review ALL changed files
- Test functionality where possible
- Check for subtle bugs or edge cases
- Verify integration with existing code

### Constructive Feedback

- Highlight both strengths and weaknesses
- Provide specific, actionable feedback
- Suggest improvements for REQUEST_CHANGES
- Acknowledge good practices when present

### Decision Criteria

**APPROVED:**
- Total score ≥ 7.0
- No critical issues
- All core requirements met
- Minor issues can be addressed in follow-up

**REQUEST_CHANGES:**
- Total score 4.0 - 6.9
- Some requirements not met
- Fixable issues identified
- Core functionality present but needs improvement

**REJECTED:**
- Total score < 4.0
- Critical requirements missing
- Fundamental architecture violations
- Would require complete rewrite

---

## 🔗 Reference Files

Review these files to understand the requirements:

```bash
# Task specification
cat implementation/web-ui/tasks/02-backend-api.md

# Writer prompt
cat .prompts/writer-prompt-02-backend-api.md

# Architecture spec
cat planning/web-ui.md

# Existing automation modules (what should be imported)
cat python/cube/automation/dual_writers.py
cat python/cube/automation/judge_panel.py
cat python/cube/core/state.py
```

---

## ✅ Judge Checklist

Before submitting your review:

- [ ] Reviewed both writer branches completely
- [ ] Tested both implementations (if possible)
- [ ] Scored all 6 criteria for both writers
- [ ] Calculated weighted total scores
- [ ] Identified strengths and weaknesses
- [ ] Listed critical issues (if any)
- [ ] Made clear recommendation for each
- [ ] Compared implementations fairly
- [ ] Provided final panel decision
- [ ] Included reasoning and next steps
- [ ] Used exact JSON format

---

## 🚀 Submit Your Review

Save your decision JSON to:
```
.sessions/<task-id>/decisions/judge-<your-model>.json
```

Your review will be aggregated with other judges to make the final decision.

---

**Remember:** Your role is to ensure quality, catch issues, and help select the best implementation. Be thorough, fair, and constructive in your review.

Good luck! 🎯
