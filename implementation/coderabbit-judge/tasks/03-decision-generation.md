# Task 03: Decision File Generation for CodeRabbit

**Goal:** Implement logic to generate standard judge decision JSON files from CodeRabbit review output, including scoring, winner selection, and blocker identification.

**Time Estimate:** 4-5 hours

---

## 📖 **Context**

**What this builds on:**
- Task 01: CodeRabbitAdapter (executes reviews)
- Task 02: CodeRabbitParser (parses output)
- Existing decision file format from `cube.core.decision_files`
- Judge panel decision aggregation system

**Planning docs (Golden Source):**
- `planning/coderabbit-judge.md` - Decision generation strategy and scoring

---

## ✅ **Requirements**

### **1. Decision Generator Module**

**Deliverable:**
- New module `python/cube/core/coderabbit_decision.py`
- Generate decision JSON from CodeRabbit review results
- Analyze both writer A and writer B implementations
- Produce standard judge decision format

**Acceptance criteria:**
- [ ] Module with `generate_decision()` function
- [ ] Takes CodeRabbit output for both writers
- [ ] Returns decision dict matching standard format
- [ ] Includes all required fields

### **2. Scoring Algorithm**

**Deliverable:**
- Calculate scores for both writers based on CodeRabbit findings
- Map severity levels to score deductions
- Score categories: kiss_compliance, architecture, type_safety, tests, production_ready

**Acceptance criteria:**
- [ ] Base score: 10 for each category
- [ ] Errors deduct more points than warnings
- [ ] Different categories affected by different issue types
- [ ] Scores never go below 0
- [ ] Total weighted score calculated

**Scoring rules:**
```
Errors: -2 points per error
Warnings: -0.5 points per warning
Info: -0.1 points per info issue

Category mapping:
- type_safety: type errors, null checks, undefined variables
- production_ready: security issues, error handling, edge cases
- tests: missing tests, test coverage issues
- architecture: code organization, coupling, complexity
- kiss_compliance: over-engineering, unnecessary abstraction
```

### **3. Winner Determination**

**Deliverable:**
- Compare total weighted scores
- Select winner (A, B, or TIE)
- Handle tie-breaking logic

**Acceptance criteria:**
- [ ] Winner is writer with higher total_weighted score
- [ ] TIE if scores within 0.5 points
- [ ] Logic is clear and documented

### **4. Blocker Identification**

**Deliverable:**
- Extract blocker issues from CodeRabbit output
- Include file:line references
- Filter by severity level

**Acceptance criteria:**
- [ ] Only "error" severity issues are blockers
- [ ] Formatted as: `"file:line - message"`
- [ ] Empty array if no blockers
- [ ] Deduplicated (no duplicate issues)

### **5. Decision Field Population**

**Deliverable:**
- Populate all required decision fields
- Set decision: APPROVED/REQUEST_CHANGES/REJECTED
- Generate recommendation text

**Acceptance criteria:**
- [ ] `decision`: "APPROVED" if no errors, "REQUEST_CHANGES" if errors
- [ ] `winner`: A/B/TIE based on scores
- [ ] `blocker_issues`: array of error messages
- [ ] `recommendation`: explains why winner was chosen
- [ ] `timestamp`: ISO 8601 format
- [ ] `judge`: judge number (passed as parameter)
- [ ] `task_id`: task ID (passed as parameter)

---

## 📝 **Implementation Steps**

**Suggested order:**

1. **Create decision module**
   - [ ] Create `python/cube/core/coderabbit_decision.py`
   - [ ] Import required modules: `json`, `datetime`, `Path`, `Dict`, `List`

2. **Define issue aggregator**
   - [ ] Function to collect all issues from CodeRabbit output
   - [ ] Parse log file or collect from parsed messages
   - [ ] Group by writer (A/B) and severity

3. **Implement scoring function**
   - [ ] `calculate_scores(issues: List[dict]) -> dict`
   - [ ] Start with base score 10 for each category
   - [ ] Apply deductions based on issue type and severity
   - [ ] Calculate total_weighted (average of categories)

4. **Implement category mapper**
   - [ ] Map issue messages to score categories
   - [ ] Use keyword matching (simple approach)
   - [ ] Examples:
     - "type" → type_safety
     - "security" → production_ready
     - "test" → tests
     - "complex" → kiss_compliance

5. **Implement winner selector**
   - [ ] Compare total_weighted scores
   - [ ] Apply tie threshold (0.5 points)
   - [ ] Return "A", "B", or "TIE"

6. **Implement blocker extractor**
   - [ ] Filter issues by severity == "error"
   - [ ] Format: `f"{file}:{line} - {message}"`
   - [ ] Return list of formatted strings

7. **Implement decision determiner**
   - [ ] No errors → "APPROVED"
   - [ ] Has errors → "REQUEST_CHANGES"
   - [ ] Many critical errors (>10) → "REJECTED"

8. **Implement recommendation generator**
   - [ ] Generate text explaining winner choice
   - [ ] Include key differentiators
   - [ ] Example: "Writer A has fewer type safety issues (2 vs 5)"

9. **Implement main generate_decision function**
   - [ ] Signature: `generate_decision(judge_num, task_id, writer_a_issues, writer_b_issues) -> dict`
   - [ ] Call all helper functions
   - [ ] Assemble final decision dict
   - [ ] Validate all required fields present

10. **Write decision to file**
    - [ ] Helper function: `write_decision_file(decision: dict, task_id: str, judge_num: int)`
    - [ ] Path: `.prompts/decisions/judge-{judge_num}-{task_id}-decision.json`
    - [ ] Create directory if needed
    - [ ] Write formatted JSON

11. **Integrate with adapter**
    - [ ] Update CodeRabbitAdapter to collect issues during run
    - [ ] Call generate_decision at end of review
    - [ ] Write decision file automatically

12. **Verify**
    - [ ] Test with sample CodeRabbit output
    - [ ] Verify decision format matches schema
    - [ ] Test edge cases (no issues, all errors, tie)
    - [ ] Validate JSON output

13. **Finalize**
    - [ ] Add type hints
    - [ ] Add docstrings
    - [ ] Run linter
    - [ ] Commit changes

---

## 🏗️ **Architecture Constraints**

### **Must Follow**

**Planning docs:**
- Decision format from `planning/coderabbit-judge.md`
- Standard judge decision schema (see Examples section)
- Scoring algorithm from planning doc

**Technical constraints:**
- Python 3.10+ type hints
- Pure function for scoring (no side effects)
- File I/O errors handled gracefully
- JSON output must be valid

**KISS Principles:**
- ✅ Simple keyword-based category mapping
- ✅ Straightforward scoring formula
- ✅ No ML or complex algorithms
- ❌ No optimization (premature)
- ❌ No caching (not needed yet)

---

## 🚫 **Anti-Patterns**

### **❌ DON'T: Implement Complex NLP for Issue Classification**

```python
# Bad: Over-engineering category classification
class IssueClassifier:
    def __init__(self):
        self.model = load_bert_model()
        self.vectorizer = TfidfVectorizer()
    
    def classify(self, issue_text: str) -> str:
        # BAD: ML overkill for simple task
        embedding = self.model.encode(issue_text)
        category = self.predict_category(embedding)
        return category
```

**Instead:**
```python
# Good: Simple keyword matching
def categorize_issue(message: str) -> str:
    message_lower = message.lower()
    
    if any(kw in message_lower for kw in ["type", "null", "undefined"]):
        return "type_safety"
    elif any(kw in message_lower for kw in ["security", "vulnerability"]):
        return "production_ready"
    # ... more simple rules
    
    return "architecture"  # default
```

### **❌ DON'T: Create Complex Weighted Scoring**

```python
# Bad: Over-complicated scoring
def calculate_score(issues):
    # BAD: Complex multi-factor scoring
    base_score = 10
    for issue in issues:
        severity_weight = SEVERITY_MATRIX[issue.severity]
        category_weight = CATEGORY_WEIGHTS[issue.category]
        confidence_factor = issue.confidence_score
        recency_decay = math.exp(-issue.age / DECAY_CONSTANT)
        
        deduction = (severity_weight * category_weight * 
                    confidence_factor * recency_decay)
        base_score -= deduction
```

**Instead:**
```python
# Good: Simple scoring
def calculate_score(issues):
    score = 10
    for issue in issues:
        if issue["severity"] == "error":
            score -= 2
        elif issue["severity"] == "warning":
            score -= 0.5
        elif issue["severity"] == "info":
            score -= 0.1
    
    return max(0, score)  # Floor at 0
```

### **❌ DON'T: Make Subjective Quality Judgments**

```python
# Bad: CodeRabbit trying to be subjective judge
def generate_recommendation(writer_a_code, writer_b_code):
    # BAD: Trying to evaluate code style subjectively
    a_elegance = rate_code_elegance(writer_a_code)
    b_creativity = rate_code_creativity(writer_b_code)
    
    # CodeRabbit should stick to objective metrics!
```

**Instead:**
```python
# Good: Objective comparison based on measurable metrics
def generate_recommendation(writer_a_issues, writer_b_issues):
    a_errors = count_severity(writer_a_issues, "error")
    b_errors = count_severity(writer_b_issues, "error")
    
    if a_errors < b_errors:
        return f"Writer A has fewer critical issues ({a_errors} vs {b_errors})"
    # ... objective comparison
```

---

## 📂 **Owned Paths**

**This task owns:**
```
python/cube/core/
└── coderabbit_decision.py  # NEW FILE
```

**May modify (integration):**
```
python/cube/core/adapters/coderabbit_adapter.py  # Add decision generation call
```

**Must NOT modify:**
- Decision file schema (read-only reference)
- Judge panel orchestration
- Other adapters

**Integration:**
- Called by CodeRabbitAdapter at end of review
- Writes to `.prompts/decisions/` directory
- Read by synthesis command like other judge decisions

---

## 🧪 **Testing Requirements**

**Test data (sample issues):**
```python
writer_a_issues = [
    {"file": "api.ts", "line": 42, "severity": "error", "message": "Potential null pointer dereference"},
    {"file": "utils.ts", "line": 15, "severity": "warning", "message": "Unused variable 'temp'"},
    {"file": "types.ts", "line": 8, "severity": "info", "message": "Consider using const instead of let"}
]

writer_b_issues = [
    {"file": "api.ts", "line": 55, "severity": "error", "message": "Missing error handling"},
    {"file": "api.ts", "line": 60, "severity": "error", "message": "SQL injection vulnerability"},
    {"file": "utils.ts", "line": 20, "severity": "warning", "message": "Complex function, consider refactoring"}
]
```

**Manual testing:**
```python
from cube.core.coderabbit_decision import generate_decision, calculate_scores

# Test 1: Scoring
scores_a = calculate_scores(writer_a_issues)
print(scores_a)
# Should show deductions: 10 - (2 for error) - (0.5 for warning) - (0.1 for info) ≈ 7.4

scores_b = calculate_scores(writer_b_issues)
print(scores_b)
# Should show more deductions: 10 - (2*2 for 2 errors) - (0.5 for warning) = 5.5

# Test 2: Decision generation
decision = generate_decision(
    judge_num=3,
    task_id="01-test",
    writer_a_issues=writer_a_issues,
    writer_b_issues=writer_b_issues
)

print(json.dumps(decision, indent=2))
# Should show:
# - winner: "A" (higher score)
# - decision: "REQUEST_CHANGES" (has errors)
# - blocker_issues: list of errors from both writers
```

**Edge cases:**
- [ ] Both writers have no issues (perfect scores)
- [ ] Tie scenario (scores within 0.5)
- [ ] One writer has many errors, other has none
- [ ] Unknown issue types (not in category map)

---

## ✅ **Acceptance Criteria**

**Definition of Done:**

- [ ] `coderabbit_decision.py` module created
- [ ] `generate_decision()` function implemented
- [ ] Scoring algorithm implemented
- [ ] Winner selection implemented
- [ ] Blocker extraction implemented
- [ ] Decision file writing implemented
- [ ] All required fields populated
- [ ] Type hints on all functions
- [ ] Docstrings added
- [ ] Manual testing completed
- [ ] Edge cases handled
- [ ] Changes committed

**Quality gates:**
- [ ] Follows KISS (simple algorithms)
- [ ] Objective metrics only
- [ ] Valid JSON output
- [ ] Matches standard decision format

---

## 🔗 **Integration Points**

**Dependencies (requires these first):**
- Task 01: CodeRabbitAdapter (to call this from)
- Task 02: CodeRabbitParser (to get parsed issues)

**Dependents (these will use this):**
- Synthesis command (reads decision files)
- Judge panel aggregation (counts votes)

**Integrator task:**
- Task 04: Integration Testing (tests full flow)

---

## 📊 **Examples**

### **Decision Schema (Required Format)**

```json
{
  "judge": 3,
  "task_id": "01-example-task",
  "timestamp": "2025-11-15T10:30:00Z",
  "decision": "REQUEST_CHANGES",
  "winner": "A",
  "scores": {
    "writer_a": {
      "kiss_compliance": 9,
      "architecture": 8,
      "type_safety": 7,
      "tests": 8,
      "production_ready": 7,
      "total_weighted": 7.8
    },
    "writer_b": {
      "kiss_compliance": 8,
      "architecture": 7,
      "type_safety": 5,
      "production_ready": 4,
      "tests": 7,
      "total_weighted": 6.2
    }
  },
  "blocker_issues": [
    "writer-b/api.ts:55 - Missing error handling",
    "writer-b/api.ts:60 - SQL injection vulnerability"
  ],
  "recommendation": "Writer A preferred: fewer critical security issues (1 error vs 3 errors)"
}
```

### **Main Decision Generator Function**

```python
"""CodeRabbit decision file generation."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from ..config import PROJECT_ROOT


def generate_decision(
    judge_num: int,
    task_id: str,
    writer_a_issues: List[dict],
    writer_b_issues: List[dict]
) -> dict:
    """Generate judge decision from CodeRabbit review output.
    
    Args:
        judge_num: Judge number (1-3)
        task_id: Task identifier
        writer_a_issues: List of issues found in writer A's code
        writer_b_issues: List of issues found in writer B's code
    
    Returns:
        Decision dict matching standard judge format
    """
    scores_a = calculate_scores(writer_a_issues)
    scores_b = calculate_scores(writer_b_issues)
    
    winner = determine_winner(scores_a["total_weighted"], scores_b["total_weighted"])
    
    all_issues = [
        {"writer": "A", **issue} for issue in writer_a_issues
    ] + [
        {"writer": "B", **issue} for issue in writer_b_issues
    ]
    
    blockers = extract_blockers(all_issues)
    
    decision_value = determine_decision(blockers)
    
    recommendation = generate_recommendation(
        winner, scores_a, scores_b, writer_a_issues, writer_b_issues
    )
    
    return {
        "judge": judge_num,
        "task_id": task_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "decision": decision_value,
        "winner": winner,
        "scores": {
            "writer_a": scores_a,
            "writer_b": scores_b
        },
        "blocker_issues": blockers,
        "recommendation": recommendation
    }


def calculate_scores(issues: List[dict]) -> dict:
    """Calculate scores for all categories based on issues."""
    category_scores = {
        "kiss_compliance": 10,
        "architecture": 10,
        "type_safety": 10,
        "tests": 10,
        "production_ready": 10
    }
    
    for issue in issues:
        severity = issue.get("severity", "info")
        message = issue.get("message", "").lower()
        
        # Determine deduction
        if severity == "error":
            deduction = 2
        elif severity == "warning":
            deduction = 0.5
        else:  # info
            deduction = 0.1
        
        # Determine which category to deduct from
        category = categorize_issue(message)
        category_scores[category] = max(0, category_scores[category] - deduction)
    
    # Calculate total weighted (average)
    total = sum(category_scores.values()) / len(category_scores)
    category_scores["total_weighted"] = round(total, 1)
    
    return category_scores


def categorize_issue(message: str) -> str:
    """Map issue message to score category."""
    if any(kw in message for kw in ["type", "null", "undefined", "any"]):
        return "type_safety"
    elif any(kw in message for kw in ["security", "vulnerability", "injection"]):
        return "production_ready"
    elif any(kw in message for kw in ["test", "coverage", "assertion"]):
        return "tests"
    elif any(kw in message for kw in ["complex", "abstraction", "over"]):
        return "kiss_compliance"
    else:
        return "architecture"


def determine_winner(score_a: float, score_b: float) -> str:
    """Determine winner based on total weighted scores."""
    diff = abs(score_a - score_b)
    
    if diff < 0.5:
        return "TIE"
    elif score_a > score_b:
        return "A"
    else:
        return "B"


def extract_blockers(issues: List[dict]) -> List[str]:
    """Extract blocker issues (errors only)."""
    blockers = []
    
    for issue in issues:
        if issue.get("severity") == "error":
            writer = issue.get("writer", "?")
            file = issue.get("file", "unknown")
            line = issue.get("line", 0)
            message = issue.get("message", "")
            
            blocker = f"writer-{writer.lower()}/{file}:{line} - {message}"
            blockers.append(blocker)
    
    return blockers


def determine_decision(blockers: List[str]) -> str:
    """Determine decision value based on blockers."""
    if len(blockers) == 0:
        return "APPROVED"
    elif len(blockers) > 10:
        return "REJECTED"
    else:
        return "REQUEST_CHANGES"


def generate_recommendation(
    winner: str,
    scores_a: dict,
    scores_b: dict,
    issues_a: List[dict],
    issues_b: dict
) -> str:
    """Generate recommendation text."""
    if winner == "TIE":
        return "Both implementations have similar code quality based on static analysis"
    
    winner_score = scores_a["total_weighted"] if winner == "A" else scores_b["total_weighted"]
    loser_score = scores_b["total_weighted"] if winner == "A" else scores_a["total_weighted"]
    
    winner_errors = sum(1 for i in (issues_a if winner == "A" else issues_b) if i.get("severity") == "error")
    loser_errors = sum(1 for i in (issues_b if winner == "A" else issues_a) if i.get("severity") == "error")
    
    return f"Writer {winner} preferred: higher code quality score ({winner_score} vs {loser_score}), fewer critical issues ({winner_errors} errors vs {loser_errors} errors)"


def write_decision_file(decision: dict, task_id: str, judge_num: int) -> Path:
    """Write decision to JSON file."""
    decisions_dir = PROJECT_ROOT / ".prompts" / "decisions"
    decisions_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"judge-{judge_num}-{task_id}-decision.json"
    filepath = decisions_dir / filename
    
    with open(filepath, 'w') as f:
        json.dump(decision, f, indent=2)
    
    return filepath
```

---

## 🎓 **Common Pitfalls**

**Watch out for:**
- ⚠️ Scores going negative (use max(0, score))
- ⚠️ Missing required decision fields (validate before writing)
- ⚠️ Inconsistent file path format in blocker issues
- ⚠️ Division by zero in weighted calculation

**If you see [KeyError in decision], it means [missing required field] - fix by [adding field to decision dict]**

**If you see [negative scores], it means [too many deductions] - fix by [using max(0, score)]**

---

## 📝 **Notes**

**Additional context:**
- CodeRabbit provides objective metrics, perfect for consistent judging
- Scoring should be deterministic (same issues = same score)
- Decision format must match exactly for synthesis to work

**Nice-to-haves (not required):**
- Confidence scores for decisions
- Detailed category breakdown in recommendation
- Historical comparison (how does this compare to past reviews)

---

**FINAL STEPS - CRITICAL:**

After completing implementation and verifying tests pass:

```bash
# Stage your changes
git add python/cube/core/coderabbit_decision.py
git add python/cube/core/adapters/coderabbit_adapter.py  # if modified

# Commit with descriptive message
git commit -m "feat(core): add decision generation for CodeRabbit judge reviews"

# Push to remote
git push origin writer-[your-model-slug]/03-decision-generation

# Verify push succeeded
git status  # Should show "up to date with origin"
```

**⚠️ IMPORTANT:** Uncommitted or unpushed changes will NOT be reviewed!

---

**Built with:** Agent Cube v1.0
**Template version:** 1.0
**Last updated:** 2025-11-15

