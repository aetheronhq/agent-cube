# Task 01: CodeRabbit CLI Adapter

**Goal:** Implement CodeRabbitAdapter as a new CLIAdapter that executes CodeRabbit CLI reviews and yields standardized stream output.

**Time Estimate:** 3-4 hours

---

## 📖 **Context**

**What this builds on:**
- Existing `CLIAdapter` interface in `python/cube/core/cli_adapter.py`
- Reference implementations: `CursorAdapter` and `GeminiAdapter`
- Adapter registry pattern in `python/cube/core/adapters/registry.py`

**Planning docs (Golden Source):**
- `planning/coderabbit-judge.md` - Full CodeRabbit integration architecture

---

## ✅ **Requirements**

### **1. Implement CLIAdapter Interface**

**Deliverable:**
- `CodeRabbitAdapter` class in `python/cube/core/adapters/coderabbit_adapter.py`
- Implements all required methods: `run`, `check_installed`, `get_install_instructions`
- Async generator pattern matching other adapters

**Acceptance criteria:**
- [ ] Class inherits from `CLIAdapter`
- [ ] `run()` method executes `coderabbit review` command
- [ ] Yields JSON lines compatible with stream processing
- [ ] `check_installed()` verifies CodeRabbit CLI is available
- [ ] `get_install_instructions()` returns helpful install message

### **2. CodeRabbit CLI Execution**

**Deliverable:**
- Execute `coderabbit review` with appropriate flags
- Use `--json` for structured output
- Use `--plain` for AI agent optimized mode
- Use `--yes` for non-interactive operation

**Acceptance criteria:**
- [ ] Command includes `--json --plain --yes` flags
- [ ] Executes in correct worktree directory
- [ ] Captures stdout and stderr properly
- [ ] Handles authentication errors gracefully
- [ ] Returns meaningful error messages on failure

### **3. Stream Output Format**

**Deliverable:**
- Yield JSON-encoded lines from CodeRabbit output
- Buffer and parse output correctly
- Handle multi-line output and partial reads

**Acceptance criteria:**
- [ ] Uses `read_stream_with_buffer` helper from `cli_adapter.py`
- [ ] Yields complete JSON lines only
- [ ] Handles CodeRabbit's output format correctly
- [ ] No data loss or corruption

### **4. Error Handling**

**Deliverable:**
- Handle authentication errors (not logged in)
- Handle rate limiting
- Handle command not found
- Provide actionable error messages

**Acceptance criteria:**
- [ ] Detects "not authenticated" errors
- [ ] Detects rate limit errors
- [ ] Raises `RuntimeError` with clear message
- [ ] Exit code checking implemented

---

## 📝 **Implementation Steps**

**Suggested order:**

1. **Create adapter file**
   - [ ] Create `python/cube/core/adapters/coderabbit_adapter.py`
   - [ ] Import required modules: `asyncio`, `Path`, `AsyncGenerator`, `shutil`
   - [ ] Import base class: `from ..cli_adapter import CLIAdapter, read_stream_with_buffer`

2. **Implement check_installed()**
   - [ ] Use `shutil.which("coderabbit")` to check if CLI is installed
   - [ ] Check PATH and common install locations
   - [ ] Return boolean

3. **Implement get_install_instructions()**
   - [ ] Return multi-line string with install instructions
   - [ ] Include macOS, Linux, and Windows (WSL) instructions
   - [ ] Include authentication steps

4. **Implement run() method skeleton**
   - [ ] Define async method signature matching `CLIAdapter.run()`
   - [ ] Build command list: `["coderabbit", "review", "--json", "--plain", "--yes"]`
   - [ ] Set up environment variables if needed

5. **Execute subprocess**
   - [ ] Use `asyncio.create_subprocess_exec()`
   - [ ] Set stdout to PIPE
   - [ ] Set cwd to worktree parameter
   - [ ] Set appropriate buffer limit

6. **Stream output**
   - [ ] Use `read_stream_with_buffer()` to read stdout
   - [ ] Yield each complete line
   - [ ] Track errors for better diagnostics

7. **Wait and handle exit code**
   - [ ] Call `await process.wait()`
   - [ ] Check exit code for errors
   - [ ] Raise appropriate exceptions with context

8. **Register adapter**
   - [ ] Import in `python/cube/core/adapters/__init__.py`
   - [ ] Add to registry in `python/cube/core/adapters/registry.py`

9. **Verify**
   - [ ] Test with `coderabbit --version` (manual check)
   - [ ] Test check_installed() returns correct value
   - [ ] Test run() executes command (may need test repo)
   - [ ] Check error handling paths

10. **Finalize**
    - [ ] Add type hints to all parameters and return types
    - [ ] Add docstrings to class and methods
    - [ ] Run linter (ruff or flake8)
    - [ ] Commit changes

---

## 🏗️ **Architecture Constraints**

### **Must Follow**

**Planning docs:**
- Implement `CLIAdapter` interface exactly (from `cli_adapter.py`)
- Follow adapter pattern from `planning/coderabbit-judge.md`
- Use same async generator pattern as `cursor_adapter.py`

**Technical constraints:**
- Python 3.10+ async/await
- Type hints on all functions
- Async generator return type
- No blocking calls in async context

**KISS Principles:**
- ✅ Simple command execution, no complex logic
- ✅ Direct delegation to coderabbit CLI
- ✅ Minimal parsing (just yield lines)
- ❌ No custom review logic (CLI does the work)
- ❌ No decision file generation here (that's Task 03)

---

## 🚫 **Anti-Patterns**

### **❌ DON'T: Parse CodeRabbit Output Here**

```python
# Bad: Adapter shouldn't parse content
async def run(self, ...):
    async for line in read_stream_with_buffer(stdout):
        parsed = json.loads(line)
        if parsed["type"] == "review_comment":
            # BAD: Parser logic in adapter
            yield self._format_review_comment(parsed)
```

**Instead:**
```python
# Good: Just yield raw lines, parser handles formatting
async def run(self, ...):
    async for line in read_stream_with_buffer(stdout):
        yield line  # Parser will handle this in Task 02
```

### **❌ DON'T: Implement Custom Review Logic**

```python
# Bad: Adapter doing too much
async def run(self, worktree: Path, model: str, prompt: str, ...):
    # BAD: Analyzing files ourselves
    files = self._find_changed_files(worktree)
    for file in files:
        issues = self._review_file(file)
        # ...
```

**Instead:**
```python
# Good: Let CodeRabbit CLI handle review logic
async def run(self, worktree: Path, model: str, prompt: str, ...):
    # Just execute the CLI tool
    cmd = ["coderabbit", "review", "--json", "--plain", "--yes"]
    process = await asyncio.create_subprocess_exec(*cmd, ...)
```

---

## 📂 **Owned Paths**

**This task owns:**
```
python/cube/core/adapters/
├── __init__.py           # Add import
├── coderabbit_adapter.py # NEW FILE
└── registry.py           # Add registration
```

**Must NOT modify:**
- `cli_adapter.py` (interface only)
- `cursor_adapter.py` (reference only)
- Any files outside `core/adapters/`

**Integration:**
- Export `CodeRabbitAdapter` from `__init__.py`
- Register in `registry.py` with key `"coderabbit"`
- Task 02 will create parser for this adapter

---

## 🧪 **Testing Requirements**

**Pre-requisites:**
- [ ] Install CodeRabbit CLI: Check install instructions
- [ ] Authenticate: `coderabbit login`
- [ ] Verify: `coderabbit --version` should work

**Manual testing:**
```python
# Test in Python REPL
import asyncio
from pathlib import Path
from cube.core.adapters.coderabbit_adapter import CodeRabbitAdapter

adapter = CodeRabbitAdapter()

# Test 1: Check installed
assert adapter.check_installed() == True

# Test 2: Get instructions
print(adapter.get_install_instructions())

# Test 3: Run review (needs git repo with commits)
async def test_run():
    worktree = Path("/path/to/test/repo")
    async for line in adapter.run(worktree, "coderabbit", "", None, False):
        print(line)

asyncio.run(test_run())
```

**Test error handling:**
- [ ] Test with CodeRabbit not installed (uninstall temporarily)
- [ ] Test with not authenticated (`coderabbit logout`, then test)
- [ ] Test with invalid worktree path

---

## ✅ **Acceptance Criteria**

**Definition of Done:**

- [ ] `CodeRabbitAdapter` class created
- [ ] Implements `CLIAdapter` interface
- [ ] All three methods implemented
- [ ] Type hints on all functions
- [ ] Docstrings added
- [ ] Registered in adapter registry
- [ ] Exported from `__init__.py`
- [ ] Manual testing completed
- [ ] Error cases handled
- [ ] Code follows existing adapter patterns
- [ ] Changes committed

**Quality gates:**
- [ ] Follows KISS (no unnecessary complexity)
- [ ] Async/await properly used
- [ ] No blocking operations
- [ ] Error messages are actionable

---

## 🔗 **Integration Points**

**Dependencies (requires these first):**
- None (builds on existing adapter infrastructure)

**Dependents (these will use this):**
- Task 02: CodeRabbit Parser (parses adapter output)
- Task 03: Decision Generation (uses adapter through judge panel)

**Integrator task:**
- Task 04: Integration Testing (tests end-to-end)

---

## 📊 **Examples**

### **CodeRabbitAdapter Implementation**

```python
"""CodeRabbit CLI adapter."""

import asyncio
from pathlib import Path
from typing import AsyncGenerator, Optional
import os
import shutil

from ..cli_adapter import CLIAdapter, read_stream_with_buffer


class CodeRabbitAdapter(CLIAdapter):
    """Adapter for CodeRabbit CLI."""
    
    async def run(
        self,
        worktree: Path,
        model: str,
        prompt: str,
        session_id: Optional[str] = None,
        resume: bool = False
    ) -> AsyncGenerator[str, None]:
        """Run CodeRabbit review and yield JSON output lines.
        
        Note: session_id and resume are not used as CodeRabbit doesn't 
        support session resumption.
        """
        env = os.environ.copy()
        
        cmd = [
            "coderabbit",
            "review",
            "--json",
            "--plain",
            "--yes"
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=worktree,
            env=env,
            limit=1024 * 1024 * 10
        )
        
        last_error = None
        if process.stdout:
            async for line in read_stream_with_buffer(process.stdout):
                if "not authenticated" in line.lower():
                    last_error = "Not authenticated with CodeRabbit"
                elif "rate limit" in line.lower():
                    last_error = "CodeRabbit rate limit exceeded"
                elif "error" in line.lower() and not last_error:
                    last_error = line[:200]
                yield line
        
        exit_code = await process.wait()
        
        if exit_code != 0:
            if last_error:
                raise RuntimeError(f"CodeRabbit CLI failed: {last_error}")
            else:
                raise RuntimeError(f"CodeRabbit CLI exited with code {exit_code}")
    
    def check_installed(self) -> bool:
        """Check if CodeRabbit CLI is installed."""
        return shutil.which("coderabbit") is not None
    
    def get_install_instructions(self) -> str:
        """Get installation instructions."""
        return """Install CodeRabbit CLI:

macOS and Linux:
  curl -fsSL https://get.coderabbit.ai/install.sh | sh

Windows (WSL):
  Same as Linux instructions above

Alternative (npm):
  npm install -g @coderabbitai/cli

After installation, authenticate with:
  coderabbit login

Verify installation:
  coderabbit --version

For more information:
  https://docs.coderabbit.ai/cli"""
```

### **Registry Registration**

```python
# In python/cube/core/adapters/registry.py
from .coderabbit_adapter import CodeRabbitAdapter

_ADAPTERS: Dict[str, Type[CLIAdapter]] = {
    "cursor-agent": CursorAdapter,
    "gemini": GeminiAdapter,
    "coderabbit": CodeRabbitAdapter,  # ADD THIS
}
```

---

## 🎓 **Common Pitfalls**

**Watch out for:**
- ⚠️ CodeRabbit CLI requires authentication before first use
- ⚠️ Free tier has rate limits (60 reviews/month)
- ⚠️ `--plain` flag is important for AI agent consumption
- ⚠️ Output format may differ from cursor-agent/gemini

**If you see [authentication error], it means [user hasn't logged in] - fix by [running `coderabbit login`]**

**If you see [command not found], it means [CLI not installed] - fix by [following install instructions]**

---

## 📝 **Notes**

**Additional context:**
- CodeRabbit CLI is relatively new, API may evolve
- `--plain` mode designed specifically for AI agents
- Session resumption likely not supported (ignore resume parameter)

**Nice-to-haves (not required):**
- Support for `--config` flag to customize review rules
- Environment variable for API key (alternative to login)
- Timeout handling for slow reviews

---

**FINAL STEPS - CRITICAL:**

After completing implementation and verifying tests pass:

```bash
# Stage your changes
git add python/cube/core/adapters/coderabbit_adapter.py
git add python/cube/core/adapters/__init__.py
git add python/cube/core/adapters/registry.py

# Commit with descriptive message
git commit -m "feat(adapters): add CodeRabbit CLI adapter for judge integration"

# Push to remote
git push origin writer-[your-model-slug]/01-coderabbit-adapter

# Verify push succeeded
git status  # Should show "up to date with origin"
```

**⚠️ IMPORTANT:** Uncommitted or unpushed changes will NOT be reviewed!

---

**Built with:** Agent Cube v1.0
**Template version:** 1.0
**Last updated:** 2025-11-15

