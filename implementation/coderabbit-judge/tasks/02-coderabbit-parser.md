# Task 02: CodeRabbit Parser

**Goal:** Implement CodeRabbitParser that converts CodeRabbit CLI JSON output into standardized StreamMessage format for cube processing.

**Time Estimate:** 2-3 hours

---

## 📖 **Context**

**What this builds on:**
- Task 01: CodeRabbitAdapter (provides raw JSON lines)
- Existing parser interface and examples in `python/cube/core/parsers/`
- StreamMessage format from cube automation system

**Planning docs (Golden Source):**
- `planning/coderabbit-judge.md` - Parser specifications and message mapping

---

## ✅ **Requirements**

### **1. Parser Implementation**

**Deliverable:**
- `CodeRabbitParser` class in `python/cube/core/parsers/coderabbit_parser.py`
- Parse CodeRabbit JSON output lines
- Convert to StreamMessage objects
- Handle different CodeRabbit output types

**Acceptance criteria:**
- [ ] Class follows existing parser pattern
- [ ] `parse()` method takes JSON string, returns StreamMessage or None
- [ ] Handles all major CodeRabbit output types
- [ ] Returns None for unparseable input (graceful degradation)

### **2. Message Type Mapping**

**Deliverable:**
- Map CodeRabbit output types to StreamMessage types
- Extract relevant fields (file, line, severity, message)
- Format content appropriately for display

**Acceptance criteria:**
- [ ] `review_comment` → `tool_call` StreamMessage
- [ ] `summary` → `output` StreamMessage
- [ ] `fix_suggestion` → `tool_call` with suggestion
- [ ] `error` → `error` StreamMessage
- [ ] Unknown types logged and skipped

### **3. Content Formatting**

**Deliverable:**
- Format CodeRabbit messages for readable display
- Include file:line references
- Show severity levels
- Extract code suggestions

**Acceptance criteria:**
- [ ] Format: `"[SEVERITY] file:line - message"`
- [ ] Code suggestions included when available
- [ ] Timestamps preserved
- [ ] Agent name passed through

### **4. Error Handling**

**Deliverable:**
- Handle malformed JSON gracefully
- Handle missing fields in CodeRabbit output
- Log parsing errors without crashing

**Acceptance criteria:**
- [ ] JSON parse errors caught and logged
- [ ] Missing fields use defaults
- [ ] Returns None on unparseable input
- [ ] No exceptions bubble up

---

## 📝 **Implementation Steps**

**Suggested order:**

1. **Examine existing parsers**
   - [ ] Read `python/cube/core/parsers/cursor_parser.py`
   - [ ] Read `python/cube/core/parsers/gemini_parser.py`
   - [ ] Understand StreamMessage structure
   - [ ] Note common patterns

2. **Create parser file**
   - [ ] Create `python/cube/core/parsers/coderabbit_parser.py`
   - [ ] Import required modules: `json`, `logging`, `Optional`
   - [ ] Import StreamMessage type from models

3. **Define parser class**
   - [ ] Create class with `parse()` method
   - [ ] Method signature: `def parse(self, line: str) -> Optional[StreamMessage]`
   - [ ] Return type matches other parsers

4. **Implement JSON parsing**
   - [ ] Try to parse line as JSON
   - [ ] Catch `json.JSONDecodeError` and return None
   - [ ] Extract type field from parsed JSON

5. **Implement type routing**
   - [ ] Switch on CodeRabbit message type
   - [ ] Route `review_comment` to review handler
   - [ ] Route `summary` to summary handler
   - [ ] Route `fix_suggestion` to fix handler
   - [ ] Route `error` to error handler
   - [ ] Default: log and return None

6. **Implement review_comment handler**
   - [ ] Extract: file, line, severity, message
   - [ ] Format: `"[{severity}] {file}:{line} - {message}"`
   - [ ] Return StreamMessage with type="tool_call"

7. **Implement other handlers**
   - [ ] Summary: type="output", content=summary text
   - [ ] Fix suggestion: type="tool_call", include suggestion
   - [ ] Error: type="error", content=error message

8. **Add session_id extraction**
   - [ ] Check if CodeRabbit output includes session/review IDs
   - [ ] Extract if available for StreamMessage
   - [ ] Leave None if not available

9. **Register parser**
   - [ ] Import in `python/cube/core/parsers/__init__.py`
   - [ ] Add to registry in `python/cube/core/parsers/registry.py`
   - [ ] Map "coderabbit" CLI to CodeRabbitParser

10. **Verify**
    - [ ] Test with sample CodeRabbit JSON output
    - [ ] Test with malformed JSON
    - [ ] Test with missing fields
    - [ ] Verify output matches StreamMessage format

11. **Finalize**
    - [ ] Add type hints
    - [ ] Add docstrings
    - [ ] Run linter
    - [ ] Commit changes

---

## 🏗️ **Architecture Constraints**

### **Must Follow**

**Planning docs:**
- Message type mapping from `planning/coderabbit-judge.md`
- StreamMessage format from existing parsers
- Graceful error handling (no crashes)

**Technical constraints:**
- Python 3.10+ type hints
- Optional return type (can return None)
- No async (synchronous parsing)
- Match existing parser interface

**KISS Principles:**
- ✅ Simple type-based routing
- ✅ Direct field extraction
- ✅ Minimal transformation
- ❌ No complex state management
- ❌ No caching or optimization (premature)

---

## 🚫 **Anti-Patterns**

### **❌ DON'T: Create Complex Parser State**

```python
# Bad: Stateful parser with accumulated context
class CodeRabbitParser:
    def __init__(self):
        self.file_context = {}
        self.current_review = None
        self.message_queue = []
    
    def parse(self, line: str) -> Optional[StreamMessage]:
        # BAD: Accumulating state across calls
        self.update_context(line)
        return self.process_with_context()
```

**Instead:**
```python
# Good: Stateless parser, each line independent
class CodeRabbitParser:
    def parse(self, line: str) -> Optional[StreamMessage]:
        # Each call is independent
        try:
            data = json.loads(line)
            return self._handle_message(data)
        except json.JSONDecodeError:
            return None
```

### **❌ DON'T: Transform Business Logic**

```python
# Bad: Parser making decisions about content
def parse(self, line: str) -> Optional[StreamMessage]:
    data = json.loads(line)
    if data["severity"] == "info":
        return None  # BAD: Filtering based on business rules
    
    # BAD: Scoring or evaluation logic
    score = self._calculate_severity_score(data)
```

**Instead:**
```python
# Good: Parser just transforms format
def parse(self, line: str) -> Optional[StreamMessage]:
    data = json.loads(line)
    # Just convert, don't filter or evaluate
    return StreamMessage(
        type="tool_call",
        content=f"[{data['severity']}] {data['file']}:{data['line']} - {data['message']}"
    )
```

---

## 📂 **Owned Paths**

**This task owns:**
```
python/cube/core/parsers/
├── __init__.py            # Add import
├── coderabbit_parser.py   # NEW FILE
└── registry.py            # Add registration
```

**Must NOT modify:**
- Adapter files (Task 01)
- StreamMessage definition
- Other parser files (reference only)

**Integration:**
- Export `CodeRabbitParser` from `__init__.py`
- Register in `registry.py` with key `"coderabbit"`
- Matches adapter registration from Task 01

---

## 🧪 **Testing Requirements**

**Test data (sample CodeRabbit output):**
```json
{"type": "review_comment", "file": "src/api.ts", "line": 42, "severity": "error", "message": "Potential null pointer dereference", "suggestion": "Add null check"}
{"type": "summary", "total_issues": 5, "blockers": 2, "warnings": 3}
{"type": "fix_suggestion", "file": "src/utils.ts", "line": 15, "fix": "if (obj !== null) { return obj.value; }"}
{"type": "error", "message": "Rate limit exceeded"}
```

**Manual testing:**
```python
# Test in Python REPL
from cube.core.parsers.coderabbit_parser import CodeRabbitParser

parser = CodeRabbitParser()

# Test 1: Review comment
line1 = '{"type": "review_comment", "file": "src/api.ts", "line": 42, "severity": "error", "message": "Null pointer"}'
msg1 = parser.parse(line1)
assert msg1 is not None
assert msg1.type == "tool_call"
print(msg1.content)  # Should show formatted message

# Test 2: Malformed JSON
line2 = '{broken json'
msg2 = parser.parse(line2)
assert msg2 is None  # Should handle gracefully

# Test 3: Unknown type
line3 = '{"type": "unknown_type", "data": "something"}'
msg3 = parser.parse(line3)
# Should log warning and return None

# Test 4: Summary
line4 = '{"type": "summary", "total_issues": 5}'
msg4 = parser.parse(line4)
assert msg4.type == "output"
```

**Edge cases:**
- [ ] Empty string input
- [ ] Non-JSON input
- [ ] JSON with missing required fields
- [ ] Very long messages (truncation?)

---

## ✅ **Acceptance Criteria**

**Definition of Done:**

- [ ] `CodeRabbitParser` class created
- [ ] `parse()` method implemented
- [ ] All message types handled
- [ ] Error handling implemented
- [ ] Type hints on all functions
- [ ] Docstrings added
- [ ] Registered in parser registry
- [ ] Exported from `__init__.py`
- [ ] Manual testing completed
- [ ] Edge cases handled
- [ ] Changes committed

**Quality gates:**
- [ ] Follows KISS (no unnecessary complexity)
- [ ] Stateless design
- [ ] Graceful error handling
- [ ] Matches existing parser patterns

---

## 🔗 **Integration Points**

**Dependencies (requires these first):**
- Task 01: CodeRabbitAdapter (provides input to parse)

**Dependents (these will use this):**
- Task 03: Decision Generation (uses parsed messages)
- Judge panel system (uses parser through registry)

**Integrator task:**
- Task 04: Integration Testing (tests adapter + parser together)

---

## 📊 **Examples**

### **CodeRabbitParser Implementation**

```python
"""CodeRabbit CLI output parser."""

import json
import logging
from typing import Optional
from ...models.types import StreamMessage

logger = logging.getLogger(__name__)


class CodeRabbitParser:
    """Parser for CodeRabbit CLI JSON output."""
    
    def parse(self, line: str) -> Optional[StreamMessage]:
        """Parse CodeRabbit JSON output line into StreamMessage.
        
        Args:
            line: JSON string from CodeRabbit CLI output
            
        Returns:
            StreamMessage if parseable, None otherwise
        """
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            return None
        
        msg_type = data.get("type")
        
        if msg_type == "review_comment":
            return self._parse_review_comment(data)
        elif msg_type == "summary":
            return self._parse_summary(data)
        elif msg_type == "fix_suggestion":
            return self._parse_fix_suggestion(data)
        elif msg_type == "error":
            return self._parse_error(data)
        else:
            logger.debug(f"Unknown CodeRabbit message type: {msg_type}")
            return None
    
    def _parse_review_comment(self, data: dict) -> StreamMessage:
        """Parse review comment into tool_call message."""
        file = data.get("file", "unknown")
        line = data.get("line", 0)
        severity = data.get("severity", "info").upper()
        message = data.get("message", "")
        
        content = f"[{severity}] {file}:{line} - {message}"
        
        if "suggestion" in data:
            content += f"\n  Suggestion: {data['suggestion']}"
        
        return StreamMessage(
            type="tool_call",
            content=content,
            session_id=data.get("review_id")
        )
    
    def _parse_summary(self, data: dict) -> StreamMessage:
        """Parse summary into output message."""
        total = data.get("total_issues", 0)
        blockers = data.get("blockers", 0)
        warnings = data.get("warnings", 0)
        
        content = f"Review complete: {total} issues found ({blockers} errors, {warnings} warnings)"
        
        return StreamMessage(
            type="output",
            content=content
        )
    
    def _parse_fix_suggestion(self, data: dict) -> StreamMessage:
        """Parse fix suggestion into tool_call message."""
        file = data.get("file", "unknown")
        line = data.get("line", 0)
        fix = data.get("fix", "")
        
        content = f"Fix suggestion for {file}:{line}\n{fix}"
        
        return StreamMessage(
            type="tool_call",
            content=content
        )
    
    def _parse_error(self, data: dict) -> StreamMessage:
        """Parse error into error message."""
        message = data.get("message", "Unknown error")
        
        return StreamMessage(
            type="error",
            content=f"CodeRabbit error: {message}"
        )
```

### **Registry Registration**

```python
# In python/cube/core/parsers/registry.py
from .coderabbit_parser import CodeRabbitParser

_PARSERS: Dict[str, Type] = {
    "cursor-agent": CursorParser,
    "gemini": GeminiParser,
    "coderabbit": CodeRabbitParser,  # ADD THIS
}
```

### **StreamMessage Type (Reference)**

```python
# From python/cube/models/types.py
@dataclass
class StreamMessage:
    type: str  # "thinking", "tool_call", "output", "error"
    content: str
    session_id: Optional[str] = None
    timestamp: Optional[str] = None
```

---

## 🎓 **Common Pitfalls**

**Watch out for:**
- ⚠️ CodeRabbit output format may vary by version
- ⚠️ Some fields may be optional or missing
- ⚠️ Error messages from CLI may not be JSON
- ⚠️ Multi-line suggestions need proper formatting

**If you see [JSONDecodeError], it means [non-JSON output from CLI] - fix by [returning None gracefully]**

**If you see [KeyError], it means [missing field in data] - fix by [using data.get() with defaults]**

---

## 📝 **Notes**

**Additional context:**
- CodeRabbit CLI is evolving, output format may change
- Parser should be resilient to format changes
- Logging helps debug parsing issues

**Nice-to-haves (not required):**
- Support for code snippets in output
- Color/styling hints in messages
- Grouping related messages

---

**FINAL STEPS - CRITICAL:**

After completing implementation and verifying tests pass:

```bash
# Stage your changes
git add python/cube/core/parsers/coderabbit_parser.py
git add python/cube/core/parsers/__init__.py
git add python/cube/core/parsers/registry.py

# Commit with descriptive message
git commit -m "feat(parsers): add CodeRabbit CLI parser for stream message conversion"

# Push to remote
git push origin writer-[your-model-slug]/02-coderabbit-parser

# Verify push succeeded
git status  # Should show "up to date with origin"
```

**⚠️ IMPORTANT:** Uncommitted or unpushed changes will NOT be reviewed!

---

**Built with:** Agent Cube v1.0
**Template version:** 1.0
**Last updated:** 2025-11-15

