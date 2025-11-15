# CodeRabbit CLI Judge Integration

**Purpose:** Define the architecture for integrating CodeRabbit CLI as a judge/reviewer in the AgentCube system using the ports/adapters pattern.

**Related Docs:** This builds on the existing adapter architecture in `cube.core.adapters` and the judge panel system in `cube.automation.judge_panel`.

---

## 🎯 **Principles**

**Core principles for this architecture:**

1. **Ports/Adapters Pattern (Hexagonal Architecture)**
   - CodeRabbit CLI is a new adapter implementing the `CLIAdapter` port
   - Same interface as cursor-agent and gemini adapters
   - Clean separation between domain logic and external tool integration
   - Why it matters: Allows pluggable CLI tools without changing core orchestration logic

2. **CodeRabbit as Quality Gate**
   - Acts as specialized judge focused on code quality, security, and best practices
   - Complements AI judges (Cursor, Gemini) with static analysis
   - Catches AI hallucinations, code smells, and security issues
   - Why it matters: Provides objective, rules-based review alongside subjective AI review

3. **Consistent Judge Interface**
   - CodeRabbit participates in standard 3-judge panel
   - Produces same decision JSON format as other judges
   - Uses same worktree and session management
   - Trade-offs: CodeRabbit CLI may need special prompt formatting to work within judge framework

---

## 📋 **Requirements**

### **CodeRabbit CLI Adapter**

**Must have:**
- Implement `CLIAdapter` interface (`run`, `check_installed`, `get_install_instructions`)
- Execute `coderabbit review` command in worktree context
- Parse CodeRabbit CLI output into standard stream format
- Handle authentication state (CLI requires login)
- Support resume capability if CodeRabbit CLI supports it

**Example (good):**
```python
class CodeRabbitAdapter(CLIAdapter):
    async def run(
        self,
        worktree: Path,
        model: str,
        prompt: str,
        session_id: Optional[str] = None,
        resume: bool = False
    ) -> AsyncGenerator[str, None]:
        cmd = ["coderabbit", "review", "--json"]
        
        if "--plain" in prompt or "AI agent" in prompt:
            cmd.append("--plain")
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=worktree,
            env=env
        )
        
        async for line in read_stream_with_buffer(process.stdout):
            yield line
```

**Example (bad):**
```python
class CodeRabbitAdapter:
    def review_code(self, files: List[str]) -> dict:
        # BAD: Custom interface, doesn't implement CLIAdapter
        # BAD: Synchronous instead of async generator
        # BAD: Different abstraction than other adapters
        result = subprocess.run(["coderabbit", "review"])
        return json.loads(result.stdout)
```

### **CodeRabbit Parser**

**Must have:**
- Parse CodeRabbit CLI JSON output
- Convert to standard `StreamMessage` format
- Extract thinking (review reasoning)
- Extract tool calls (file analysis, fix suggestions)
- Map CodeRabbit output types to cube message types

**CodeRabbit CLI output format:**
```json
{
  "type": "review_comment",
  "file": "src/example.ts",
  "line": 42,
  "severity": "error",
  "message": "Potential null pointer dereference",
  "suggestion": "Add null check before accessing property"
}
```

**Mapped to StreamMessage:**
```typescript
{
  "type": "tool_call",
  "agent": "judge-3",
  "content": "Found error in src/example.ts:42 - Potential null pointer dereference",
  "timestamp": "2025-11-15T..."
}
```

### **Judge Configuration**

**Must have:**
- CodeRabbit CLI as configurable judge option
- Support in `cube.yaml` configuration:
  ```yaml
  judges:
    judge_1:
      model: gpt-4.5
      cli_tool: cursor-agent
    judge_2:
      model: gemini-2.5-flash-thinking-exp-01-21
      cli_tool: gemini
    judge_3:
      model: coderabbit
      cli_tool: coderabbit
  ```
- Handle special case where "model" is the tool name itself

### **Decision File Generation**

**Must have:**
- CodeRabbit adapter must produce decision JSON file
- Use CodeRabbit review output to populate decision fields
- Map CodeRabbit severity levels to judge scores
- Format: `.prompts/decisions/judge-{N}-{task_id}-decision.json`

**Decision mapping:**
```json
{
  "judge": 3,
  "task_id": "01-example",
  "timestamp": "2025-11-15T...",
  "decision": "REQUEST_CHANGES",
  "winner": "A",
  "scores": {
    "writer_a": {
      "kiss_compliance": 8,
      "architecture": 9,
      "type_safety": 9,
      "tests": 7,
      "production_ready": 6,
      "total_weighted": 7.8
    },
    "writer_b": {
      "kiss_compliance": 7,
      "architecture": 8,
      "type_safety": 6,
      "tests": 8,
      "production_ready": 5,
      "total_weighted": 6.8
    }
  },
  "blocker_issues": [
    "src/api.ts:42 - Potential security vulnerability",
    "src/utils.ts:15 - Missing error handling"
  ],
  "recommendation": "Writer A has better code quality based on static analysis"
}
```

---

## 🚫 **Anti-Patterns**

### **❌ Don't: Create Special CodeRabbit-Only Logic**

**Problem:**
- Breaks adapter pattern
- Creates inconsistent judge behavior
- Makes CodeRabbit a special case

**Example:**
```python
# Bad: Special handling in judge_panel.py
async def run_judge(judge_info: JudgeInfo, prompt: str, resume: bool):
    if judge_info.model == "coderabbit":
        # Special CodeRabbit logic here
        return await run_coderabbit_review(...)
    else:
        # Normal judge logic
        return await run_normal_judge(...)
```

**Instead:**
```python
# Good: Uniform adapter interface
async def run_judge(judge_info: JudgeInfo, prompt: str, resume: bool):
    cli_name = config.cli_tools.get(judge_info.model, "cursor-agent")
    adapter = get_adapter(cli_name)
    
    # All judges use same code path
    stream = adapter.run(worktree, judge_info.model, prompt, ...)
```

### **❌ Don't: Bypass Standard Decision Format**

**Problem:**
- CodeRabbit output is structured differently than AI judge output
- Tempting to create CodeRabbit-specific decision format
- Breaks synthesis and voting logic

**Example:**
```json
// Bad: CodeRabbit-specific format
{
  "judge": 3,
  "tool": "coderabbit",
  "issues": [...],
  "coderabbit_specific_fields": {...}
}
```

**Instead:**
```json
// Good: Standard format with CodeRabbit data
{
  "judge": 3,
  "task_id": "01-example",
  "decision": "REQUEST_CHANGES",
  "winner": "A",
  "scores": {...},
  "blocker_issues": [...],
  "recommendation": "Analysis based on static code review",
  "metadata": {
    "tool": "coderabbit",
    "version": "1.0.0"
  }
}
```

### **❌ Don't: Require User Interaction**

**Problem:**
- CodeRabbit CLI may prompt for user input
- Breaks automation flow
- Can't run in background

**Instead:**
- Always use non-interactive flags: `coderabbit review --yes --json --plain`
- Pre-check authentication before starting panel
- Fail fast with clear error if auth needed

---

## ✅ **Best Practices**

### **✅ Do: Use CodeRabbit's `--plain` Mode for AI Integration**

**Why:**
- CodeRabbit CLI has special mode for AI agents
- Provides structured output optimized for LLM consumption
- Reduces need for complex parsing

**Example:**
```python
async def run(self, worktree: Path, model: str, prompt: str, ...):
    cmd = ["coderabbit", "review", "--plain", "--json"]
    
    # --plain mode is designed for AI agent consumption
    # Returns structured data suitable for our parser
```

### **✅ Do: Map CodeRabbit Severity to Judge Scores**

**Why:**
- CodeRabbit outputs severity levels (error, warning, info)
- Need consistent scoring across all judges
- Objective mapping provides fair comparison

**Example:**
```python
def calculate_scores(coderabbit_output: dict) -> dict:
    errors = count_by_severity(coderabbit_output, "error")
    warnings = count_by_severity(coderabbit_output, "warning")
    
    # More errors = lower production_ready score
    production_ready = max(0, 10 - errors * 2 - warnings)
    
    return {
        "type_safety": calculate_type_safety_score(coderabbit_output),
        "production_ready": production_ready,
        "tests": calculate_test_coverage_score(coderabbit_output),
        ...
    }
```

### **✅ Do: Handle CodeRabbit CLI Rate Limits**

**Why:**
- Free tier has rate limits
- May fail during panel execution
- Need graceful degradation

**Example:**
```python
async def run(self, worktree: Path, model: str, prompt: str, ...):
    try:
        async for line in self._execute_review(worktree):
            yield line
    except RateLimitError as e:
        # Provide fallback decision
        yield json.dumps({
            "type": "error",
            "content": "CodeRabbit rate limit reached, judge abstaining"
        })
        yield self._create_abstain_decision()
```

---

## 🔗 **Integration Points**

**This connects with:**

- **`cube.core.adapters.registry`:** Register CodeRabbitAdapter
- **`cube.core.parsers.registry`:** Register CodeRabbitParser
- **`cube.automation.judge_panel`:** Uses adapter through standard interface
- **`cube.core.user_config`:** Configure CodeRabbit as judge option
- **`cube.commands.panel`:** No changes needed (uses adapters)

**Planning docs to read together:**
- This document only (CodeRabbit is isolated adapter addition)

---

## 📐 **Technical Specifications**

### **CodeRabbit CLI Commands**

| Command | Flags | Purpose |
|---------|-------|---------|
| `coderabbit review` | `--json` | Get structured output |
| `coderabbit review` | `--plain` | AI agent optimized mode |
| `coderabbit review` | `--yes` | Non-interactive mode |
| `coderabbit login` | - | Authenticate CLI |
| `coderabbit --version` | - | Check installation |

### **CodeRabbitAdapter Methods**

| Method | Signature | Purpose |
|--------|-----------|---------|
| `run` | `async def run(worktree, model, prompt, session_id, resume)` | Execute review |
| `check_installed` | `def check_installed() -> bool` | Verify CLI installed |
| `get_install_instructions` | `def get_install_instructions() -> str` | Install help |

### **CodeRabbitParser Output**

| CodeRabbit Type | StreamMessage Type | Content |
|-----------------|-------------------|---------|
| `review_comment` | `tool_call` | File:line issue |
| `summary` | `output` | Review summary |
| `fix_suggestion` | `tool_call` | Suggested fix |
| `error` | `error` | CLI error |

### **Decision Generation Strategy**

```python
# CodeRabbit reviews both writers, generates comparison
{
  "winner": "A" if writer_a_score > writer_b_score else "B",
  "scores": {
    "writer_a": calculate_from_coderabbit_review(writer_a_issues),
    "writer_b": calculate_from_coderabbit_review(writer_b_issues)
  },
  "blocker_issues": filter_severity(all_issues, "error"),
  "decision": "APPROVED" if no_blockers else "REQUEST_CHANGES"
}
```

---

## ❓ **Open Questions / TBD**

### **CodeRabbit CLI Session Support**

- **Status:** To be determined
- **Question:** Does CodeRabbit CLI support resuming sessions like cursor-agent?
- **Default:** Assume no session support, ignore resume parameter
- **Action:** Check CodeRabbit CLI docs, implement if available

### **Authentication Flow**

- **Status:** To be determined
- **Question:** How to handle CodeRabbit CLI authentication in automated context?
- **Default:** Pre-check auth, fail fast with clear instructions
- **Options:**
  1. Require `coderabbit login` before first use
  2. Support API key via environment variable
  3. Interactive auth on first run

### **Pro vs Free Tier Differences**

- **Status:** To be determined
- **Question:** What features require CodeRabbit Pro?
- **Default:** Document free tier limitations
- **Action:** Test with free tier, note any Pro-only features

### **Review Scope**

- **Status:** Decided
- **Decision:** Review only changed files (git diff)
- **Rationale:** Full codebase review too slow, git diff matches other judges

---

## 📚 **References**

**External:**
- [CodeRabbit CLI Documentation](https://docs.coderabbit.ai/cli)
- [CodeRabbit CLI GitHub](https://github.com/coderabbitai/cli)
- [Hexagonal Architecture Pattern](https://alistair.cockburn.us/hexagonal-architecture/)

**Internal:**
- `python/cube/core/cli_adapter.py` - CLIAdapter interface
- `python/cube/core/adapters/cursor_adapter.py` - Reference implementation
- `python/cube/core/adapters/gemini_adapter.py` - Another reference
- `python/cube/automation/judge_panel.py` - How judges are orchestrated

**Examples:**
- CursorAdapter and GeminiAdapter are reference implementations
- Follow same patterns for consistency

---

## ✏️ **Revision History**

| Date | Change | Reason |
|------|--------|--------|
| 2025-11-15 | Initial version | Created for CodeRabbit CLI integration |

---

**NOTE:** This is a living document. Update as you learn from implementation!

