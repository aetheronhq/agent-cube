# Task 04: Integration and Testing

**Goal:** Integrate CodeRabbit judge into cube configuration system, test end-to-end with judge panel, and document usage.

**Time Estimate:** 3-4 hours

---

## 📖 **Context**

**What this builds on:**
- Task 01: CodeRabbitAdapter (CLI execution)
- Task 02: CodeRabbitParser (output parsing)
- Task 03: Decision Generation (decision files)
- Existing judge panel system and configuration

**Planning docs (Golden Source):**
- `planning/coderabbit-judge.md` - Full integration architecture

---

## ✅ **Requirements**

### **1. Configuration Integration**

**Deliverable:**
- Support CodeRabbit in `cube.yaml` configuration
- Document configuration options
- Provide example configuration

**Acceptance criteria:**
- [ ] `cube.yaml` supports `cli_tool: coderabbit`
- [ ] Example config in documentation
- [ ] Default configuration works without customization
- [ ] Configuration validation handles CodeRabbit correctly

### **2. Judge Panel Integration**

**Deliverable:**
- CodeRabbit works as judge in 3-judge panel
- Runs in parallel with other judges
- Produces decision files like other judges

**Acceptance criteria:**
- [ ] `cube panel` command works with CodeRabbit as a judge
- [ ] CodeRabbit runs in parallel with Cursor/Gemini judges
- [ ] Decision file written to correct location
- [ ] No special-case logic needed in judge_panel.py

### **3. Authentication & Pre-flight Checks**

**Deliverable:**
- Check CodeRabbit CLI authentication before starting panel
- Provide clear error messages for setup issues
- Fast-fail on missing dependencies

**Acceptance criteria:**
- [ ] Check if CodeRabbit CLI installed before panel start
- [ ] Check if authenticated (`coderabbit --version` works)
- [ ] Clear error message if not installed
- [ ] Clear instructions if not authenticated

### **4. End-to-End Testing**

**Deliverable:**
- Test complete flow: dual writers → judge panel with CodeRabbit → synthesis
- Verify decision files generated correctly
- Test with real code review scenario

**Acceptance criteria:**
- [ ] Can run `cube writers` with test task
- [ ] Can run `cube panel` with CodeRabbit as judge
- [ ] CodeRabbit reviews both writer implementations
- [ ] Decision file created and valid
- [ ] Synthesis command reads CodeRabbit decision

### **5. Documentation**

**Deliverable:**
- README documenting CodeRabbit judge usage
- Installation instructions
- Configuration examples
- Troubleshooting guide

**Acceptance criteria:**
- [ ] Installation steps documented
- [ ] Configuration example provided
- [ ] Usage instructions clear
- [ ] Common issues documented

---

## 📝 **Implementation Steps**

**Suggested order:**

1. **Review existing integration points**
   - [ ] Read `python/cube/core/user_config.py` to understand config loading
   - [ ] Read `python/cube/automation/judge_panel.py` to see judge initialization
   - [ ] Understand how other adapters are configured

2. **Create example configuration**
   - [ ] Create `python/cube.yaml.example` or update existing
   - [ ] Add CodeRabbit as judge option
   - [ ] Document configuration fields

3. **Add authentication check**
   - [ ] In CodeRabbitAdapter, add `check_authenticated()` method
   - [ ] Try to run `coderabbit --version`
   - [ ] Return boolean indicating auth status

4. **Update judge panel pre-flight checks**
   - [ ] In `judge_panel.py`, verify all CLI tools installed
   - [ ] For CodeRabbit, also check authentication
   - [ ] Provide actionable error messages

5. **Create test task**
   - [ ] Create simple test task file (e.g., `.prompts/test-coderabbit.md`)
   - [ ] Task: "Add a simple utility function with intentional issues"
   - [ ] Use for testing CodeRabbit judge

6. **Test dual writers**
   - [ ] Run `cube writers test-coderabbit .prompts/test-coderabbit.md`
   - [ ] Verify both writers complete
   - [ ] Check branches created

7. **Configure CodeRabbit as judge**
   - [ ] Update `cube.yaml` to use CodeRabbit as one of the judges
   - [ ] Example:
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

8. **Test judge panel**
   - [ ] Run `cube panel test-coderabbit .prompts/test-panel-prompt.md`
   - [ ] Monitor CodeRabbit judge output
   - [ ] Verify decision file created
   - [ ] Check decision file format

9. **Test synthesis**
   - [ ] Run `cube synthesize test-coderabbit` or similar
   - [ ] Verify CodeRabbit decision included
   - [ ] Check aggregated results

10. **Validate decision format**
    - [ ] Read generated decision file
    - [ ] Validate against schema
    - [ ] Check all required fields present
    - [ ] Verify scores are reasonable

11. **Test error scenarios**
    - [ ] Test without CodeRabbit installed
    - [ ] Test without authentication
    - [ ] Test with network issues
    - [ ] Verify error messages are helpful

12. **Write documentation**
    - [ ] Create `implementation/coderabbit-judge/README.md`
    - [ ] Document installation
    - [ ] Document configuration
    - [ ] Document usage
    - [ ] Document troubleshooting

13. **Update main README**
    - [ ] Add CodeRabbit judge to main project README
    - [ ] Update judge configuration section
    - [ ] Add to features list

14. **Finalize**
    - [ ] Run all tests again
    - [ ] Verify all documentation accurate
    - [ ] Clean up test files if needed
    - [ ] Commit all changes

---

## 🏗️ **Architecture Constraints**

### **Must Follow**

**Planning docs:**
- No special-case logic from `planning/coderabbit-judge.md`
- Standard adapter interface only
- Configuration follows existing patterns

**Technical constraints:**
- No changes to judge panel orchestration
- No changes to decision file schema
- CodeRabbit is just another adapter

**KISS Principles:**
- ✅ Use existing configuration system
- ✅ Use existing error handling patterns
- ✅ Minimal documentation (just essentials)
- ❌ No new command-line flags
- ❌ No custom CodeRabbit commands

---

## 🚫 **Anti-Patterns**

### **❌ DON'T: Add CodeRabbit-Specific Commands**

```bash
# Bad: Special CodeRabbit command
cube coderabbit-review task-01

# Bad: CodeRabbit-specific flags
cube panel task-01 --use-coderabbit --coderabbit-config=...
```

**Instead:**
```bash
# Good: Standard panel command, CodeRabbit configured in cube.yaml
cube panel task-01 .prompts/panel-prompt.md
```

### **❌ DON'T: Create CodeRabbit-Specific Logic in Judge Panel**

```python
# Bad: Special handling
async def launch_judge_panel(...):
    for judge in judges:
        if judge.cli_tool == "coderabbit":
            # BAD: Special case logic
            await run_coderabbit_judge(judge)
        else:
            await run_judge(judge)
```

**Instead:**
```python
# Good: Uniform handling through adapter interface
async def launch_judge_panel(...):
    for judge in judges:
        # All judges treated the same
        await run_judge(judge)  # Uses adapter pattern
```

---

## 📂 **Owned Paths**

**This task owns:**
```
implementation/coderabbit-judge/
├── README.md              # NEW FILE - Usage documentation
└── tasks/
    └── 04-integration-testing.md  # This file

python/
└── cube.yaml.example      # Updated with CodeRabbit config
```

**May read (reference):**
```
python/cube/core/user_config.py
python/cube/automation/judge_panel.py
```

**May modify (pre-flight checks):**
```
python/cube/automation/judge_panel.py  # Add auth check if needed
```

---

## 🧪 **Testing Requirements**

### **Pre-requisites**

- [ ] CodeRabbit CLI installed: `coderabbit --version`
- [ ] CodeRabbit authenticated: `coderabbit login`
- [ ] Cube environment set up
- [ ] Git repository with commits

### **Test Scenario 1: Full Workflow**

```bash
# Create test task
mkdir -p .prompts
cat > .prompts/test-coderabbit.md << 'EOF'
# Test Task: Simple Utility Function

Create a file `utils/string-helpers.ts` with:
- A function to capitalize strings
- A function to trim and lowercase strings
- Export both functions

Intentionally introduce:
- Missing null checks (for CodeRabbit to catch)
- Unused variables (for CodeRabbit to flag)
EOF

# Run writers
cube writers test-cr-01 .prompts/test-coderabbit.md

# Wait for completion, then run panel
cat > .prompts/panel-prompt.md << 'EOF'
Review both implementations and provide scoring.
EOF

cube panel test-cr-01 .prompts/panel-prompt.md

# Check results
ls .prompts/decisions/
# Should see: judge-1-test-cr-01-decision.json
#             judge-2-test-cr-01-decision.json
#             judge-3-test-cr-01-decision.json

# Verify CodeRabbit decision
cat .prompts/decisions/judge-3-test-cr-01-decision.json
# Should be valid JSON with all required fields
```

### **Test Scenario 2: Error Handling**

```bash
# Test 1: Not installed
coderabbit --version  # Should work
# If not, test error message when running panel

# Test 2: Not authenticated
coderabbit logout  # Logout
cube panel test-cr-01 .prompts/panel-prompt.md
# Should show: "CodeRabbit not authenticated. Run: coderabbit login"

# Re-authenticate
coderabbit login
```

### **Test Scenario 3: Configuration Validation**

```yaml
# Test invalid config in cube.yaml
judges:
  judge_3:
    model: coderabbit-invalid  # Wrong model name
    cli_tool: coderabbit

# Should handle gracefully or show clear error
```

### **Manual Validation Checklist**

- [ ] CodeRabbit runs in parallel with other judges
- [ ] Decision file written to correct path
- [ ] Decision file format matches schema
- [ ] All required fields present
- [ ] Scores are reasonable (0-10 range)
- [ ] Winner determination makes sense
- [ ] Blocker issues correctly extracted
- [ ] Recommendation text is clear

---

## ✅ **Acceptance Criteria**

**Definition of Done:**

- [ ] CodeRabbit integrated into configuration system
- [ ] Works as judge in panel command
- [ ] Pre-flight authentication check implemented
- [ ] End-to-end testing completed successfully
- [ ] Documentation written (README)
- [ ] Example configuration provided
- [ ] Error messages are actionable
- [ ] No special-case logic in judge panel
- [ ] All tests pass
- [ ] Changes committed and pushed

**Quality gates:**
- [ ] Follows adapter pattern (no special cases)
- [ ] Error handling is user-friendly
- [ ] Documentation is clear and complete
- [ ] Configuration is simple

---

## 🔗 **Integration Points**

**Dependencies (requires these first):**
- Task 01: CodeRabbitAdapter
- Task 02: CodeRabbitParser
- Task 03: Decision Generation

**Dependents (these will use this):**
- None (this is the final integration task)

**Completes:**
- Full CodeRabbit judge integration
- Ready for production use

---

## 📊 **Examples**

### **cube.yaml Configuration**

```yaml
# User configuration for AgentCube

# Writer configuration
writers:
  writer_a:
    model: claude-sonnet-4.5
    label: "Writer A (Sonnet)"
    color: green
  writer_b:
    model: o3-mini
    label: "Writer B (Codex)"
    color: blue

# Judge configuration
judges:
  judge_1:
    model: gpt-4.5
    cli_tool: cursor-agent
    label: "Judge 1 (GPT)"
    color: yellow
  judge_2:
    model: gemini-2.5-flash-thinking-exp-01-21
    cli_tool: gemini
    label: "Judge 2 (Gemini)"
    color: cyan
  judge_3:
    model: coderabbit
    cli_tool: coderabbit
    label: "Judge 3 (CodeRabbit)"
    color: magenta

# CLI tool mapping
cli_tools:
  claude-sonnet-4.5: cursor-agent
  o3-mini: cursor-agent
  gpt-4.5: cursor-agent
  gemini-2.5-flash-thinking-exp-01-21: gemini
  coderabbit: coderabbit
```

### **README.md Structure**

```markdown
# CodeRabbit Judge Integration

Integration of CodeRabbit CLI as a judge in the AgentCube system.

## Features

- Static code analysis as judge in 3-judge panel
- Objective metrics for code quality
- Catches AI hallucinations and code smells
- Complements subjective AI judges

## Installation

1. Install CodeRabbit CLI:
   ```bash
   curl -fsSL https://get.coderabbit.ai/install.sh | sh
   ```

2. Authenticate:
   ```bash
   coderabbit login
   ```

3. Verify:
   ```bash
   coderabbit --version
   ```

## Configuration

Update your `python/cube.yaml`:

[Configuration example here]

## Usage

CodeRabbit automatically participates when configured as a judge:

```bash
# Run dual writers
cube writers my-task .prompts/my-task.md

# Run judge panel (includes CodeRabbit)
cube panel my-task .prompts/panel-prompt.md
```

## How It Works

1. CodeRabbit reviews both writer implementations
2. Analyzes code for issues (errors, warnings, info)
3. Scores based on severity and category
4. Generates decision file matching standard format
5. Participates in 3-judge consensus

## Decision Format

CodeRabbit generates standard judge decisions:
- Scores: kiss_compliance, architecture, type_safety, tests, production_ready
- Winner: A, B, or TIE
- Blocker issues: Error-level issues
- Decision: APPROVED / REQUEST_CHANGES / REJECTED

## Troubleshooting

### "CodeRabbit CLI not installed"

Install using: `curl -fsSL https://get.coderabbit.ai/install.sh | sh`

### "Not authenticated"

Run: `coderabbit login`

### "Rate limit exceeded"

Free tier has limits. Wait or upgrade to Pro.

## Limitations

- Free tier: 60 reviews/month
- No session resumption (resume flag ignored)
- Reviews only changed files (git diff)

## Architecture

Uses ports/adapters pattern:
- `CodeRabbitAdapter`: Executes CLI
- `CodeRabbitParser`: Parses output
- `generate_decision()`: Creates decision files

No special-case logic needed.
```

### **Pre-flight Check in judge_panel.py**

```python
# Add to launch_judge_panel() function
async def launch_judge_panel(...):
    # ... existing code ...
    
    # Check all CLI tools installed and authenticated
    config = load_user_config()
    for judge in judges:
        cli_name = config.cli_tools.get(judge.model, "cursor-agent")
        adapter = get_adapter(cli_name)
        
        if not adapter.check_installed():
            print_error(f"{cli_name} not installed (needed for {judge.model})")
            console.print()
            console.print(adapter.get_install_instructions())
            raise RuntimeError(f"{cli_name} not installed")
        
        # Special check for CodeRabbit authentication
        if cli_name == "coderabbit":
            if not await check_coderabbit_auth(adapter):
                print_error("CodeRabbit not authenticated")
                console.print()
                console.print("Please run: coderabbit login")
                raise RuntimeError("CodeRabbit authentication required")
    
    # ... rest of function ...


async def check_coderabbit_auth(adapter) -> bool:
    """Check if CodeRabbit CLI is authenticated."""
    try:
        process = await asyncio.create_subprocess_exec(
            "coderabbit", "--version",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.wait()
        return process.returncode == 0
    except Exception:
        return False
```

---

## 🎓 **Common Pitfalls**

**Watch out for:**
- ⚠️ CodeRabbit CLI must be authenticated before first use
- ⚠️ Decision file path must match exactly: `.prompts/decisions/judge-{N}-{task_id}-decision.json`
- ⚠️ Configuration key must match adapter registry: `coderabbit`
- ⚠️ Free tier rate limits may cause failures

**If you see [authentication error during panel], it means [CodeRabbit not logged in] - fix by [running `coderabbit login` before panel]**

**If you see [decision file not found], it means [file not written or wrong path] - fix by [checking write_decision_file path logic]**

---

## 📝 **Notes**

**Additional context:**
- This completes the CodeRabbit integration
- After this task, CodeRabbit is a fully functional judge
- Consider adding CodeRabbit as default judge in future

**Nice-to-haves (not required):**
- Performance comparison: CodeRabbit vs AI judges
- Analytics: track how often CodeRabbit catches issues AI judges miss
- Configuration presets (strict mode, balanced mode, lenient mode)

---

**FINAL STEPS - CRITICAL:**

After completing all integration and testing:

```bash
# Stage all changes
git add implementation/coderabbit-judge/README.md
git add python/cube.yaml.example
git add python/cube/automation/judge_panel.py  # if modified
git add .  # Ensure all CodeRabbit files included

# Commit with descriptive message
git commit -m "feat(integration): complete CodeRabbit judge integration with testing and docs"

# Push to remote
git push origin writer-[your-model-slug]/04-integration-testing

# Verify push succeeded
git status  # Should show "up to date with origin"
```

**⚠️ IMPORTANT:** Uncommitted or unpushed changes will NOT be reviewed!

---

**Built with:** Agent Cube v1.0
**Template version:** 1.0
**Last updated:** 2025-11-15

