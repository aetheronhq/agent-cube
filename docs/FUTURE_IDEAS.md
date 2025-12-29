# Future Feature Ideas

Ideas for future Agent Cube enhancements. Not prioritized, not fully spec'd - just a collection of possibilities.

---

## CLI Tool Support

### Additional AI CLIs
- **Codex CLI** - OpenAI Codex command-line interface
- **Aider** - AI pair programming in the terminal
- **OpenCode** - Open-source code assistant

**Implementation:** Follow adapter/parser pattern like cursor-agent, gemini, claude-code

### Static Analysis Tools
- **SonarQube CLI** - Use with cli-review adapter for code quality analysis
- **Semgrep** - Security scanning
- **CodeQL** - Security analysis
- **ESLint/Ruff/etc** - Language-specific linters

**Implementation:** Extend cli-review adapter to support any CLI tool that outputs findings

---

## Automatic Verification Commands

**Concept:** Run verification commands automatically during writer execution for instant feedback

### Auto-verification modes
```yaml
behavior:
  auto_verify:
    - command: "npm test"
      on: ["after_changes", "before_commit"]
    - command: "ruff check ."
      on: ["after_changes"]
    - command: "mypy python/cube --strict"
      on: ["before_commit"]
```

### Features
- Run tests automatically after code changes
- Run linters before allowing commit
- Instant feedback in terminal UI
- Different from review CLI (runs during execution, not after)
- Writer sees failures immediately and can fix

### Benefits
- Catch test failures before judge review
- Prevent broken code from being committed
- Faster iteration (no waiting for judges to find test failures)

---

## UI Enhancements

### Make UI Production-Ready
**Current:** Experimental, read-only
**Goal:** Full-featured web interface

#### Features needed:
- **Write operations:** Send feedback, trigger actions from UI
- **Task management:** Create/edit/delete tasks from UI
- **Real-time updates:** WebSocket for live agent output
- **Session management:** Pause/resume/cancel from UI
- **Decision editing:** Override judge decisions, provide guidance
- **Branch comparison:** Side-by-side diff view for writer implementations
- **Performance metrics:** Track task duration, cost, success rate

#### Technical:
- Add WebSocket support to FastAPI backend
- Build React/Vue frontend with real-time features
- Add authentication/authorization
- Persistent storage (SQLite/Postgres)

---

## Remote & Cloud Modes

### Server Mode (Remote Access)
**Use case:** Run on your laptop, access from phone/tablet/other PCs

#### Features:
- REST API server runs on laptop
- Secure authentication (API keys)
- Web UI accessible from any device
- Mobile-friendly responsive design
- Push notifications when tasks complete

#### Implementation:
```yaml
server:
  mode: remote
  host: 0.0.0.0
  port: 8080
  auth_token: xxx
```

### Cloud Mode (EC2/Cloud VM)
**Use case:** Run on cloud VM with all tools pre-installed, control from anywhere

#### Features:
- One-click deploy to EC2/GCP/Azure
- Pre-configured with all CLI tools (cursor-agent, gemini, coderabbit, etc.)
- VPN/SSH tunnel for security
- Persistent storage (EBS/Cloud Storage)
- Cost tracking and auto-shutdown when idle

#### Deployment:
- Terraform/CloudFormation templates
- Docker container with all dependencies
- GitHub Actions integration for CI/CD
- Webhook triggers (run task on PR creation)

#### Use cases:
- Send task from phone while traveling
- Background processing of large refactors
- Team shared instance
- CI/CD integration

---

## Usage & Result Tracking

### Local-First Analytics

#### Track:
- **Per-task metrics:**
  - Duration (wall clock vs API time)
  - Cost (tokens, API calls)
  - Success rate (merged vs abandoned)
  - Writer win rates
  - Judge agreement patterns
  
- **Per-writer stats:**
  - Win rate by task type
  - Average score
  - Common failure patterns
  - Cost per task
  
- **Per-judge stats:**
  - Review duration
  - Agreement with other judges
  - False positive rate (approved but later failed)

#### Storage:
```
~/.cube/analytics/
  tasks.db (SQLite)
  sessions.db
  costs.json
```

#### UI:
- Dashboard showing success rates
- Cost breakdown by writer/judge/task
- Trends over time
- Recommendations (which writers for which tasks)

### Remote Tracking (Optional)
- Push anonymized metrics to cloud
- Compare your stats with community
- Learn which models work best for which tasks
- Cost optimization recommendations

---

## Jira Integration

### Current:
- Manual task creation
- No status sync

### Enhanced Integration:

#### Bidirectional sync:
```yaml
jira:
  enabled: true
  project: PROJ
  auto_sync: true
  
  # Pull tasks from Jira
  import_query: "project = PROJ AND status = 'To Do' AND labels = 'agent-cube'"
  
  # Update Jira when task progresses
  status_mapping:
    phase_1: "In Progress"
    phase_5: "In Review"
    merged: "Done"
```

#### Features:
- Auto-create Agent Cube tasks from Jira tickets
- Update Jira status as workflow progresses
- Link PR to Jira issue
- Post judge feedback as Jira comments
- Track time in Jira

#### Commands:
```bash
cube jira sync                    # Pull new tickets
cube jira status PROJ-123         # Check status
cube auto --jira PROJ-123         # Run task and update Jira
```

---

## Automated Planning & Dependency Analysis

### Current:
- Manual task creation
- Manual dependency tracking (PHASES.md)

### Automated Planning:

#### Features:
- **Dependency detection:** Analyze codebase to find dependencies between tasks
- **Phase planning:** Automatically group tasks into parallel batches
- **Conflict detection:** Warn if tasks might interfere with each other
- **Optimal scheduling:** Suggest execution order to minimize wall-clock time

#### Commands:
```bash
cube plan analyze docs/tasks/*.md           # Analyze all tasks
cube plan optimize                          # Suggest optimal execution order
cube plan batch --max-parallel 3            # Create execution batches
cube plan execute --batch 1                 # Run batch 1 tasks
```

#### Auto-generated:
```markdown
# Auto-generated plan

## Batch 1 (parallel, no conflicts)
- Task 13: Consolidate layouts
- Task 15: Single writer mode
- Task 17: mypy

## Batch 2 (depends on Batch 1)
- Task 16: Claude Code (needs 09, 10)
- Task 14: Decision parsing (needs 04)

## Batch 3 (final)
- Task 05: Tests (needs stable code)
- Task 06: Docs (needs 05)
```

#### Smart features:
- Parse task requirements/dependencies from task files
- Detect file conflicts (two tasks editing same files)
- Estimate duration based on past tasks
- Suggest parallelization opportunities
- Warn about risky combinations

---

## Ideas Backlog Priority

**High Value, Medium Effort:**
- Auto-verification commands (instant feedback)
- Usage/cost tracking (local-first)
- Server mode (remote access)

**High Value, High Effort:**
- Production UI (write operations, real-time)
- Automated planning & dependency detection
- Cloud mode (EC2 deployment)

**Medium Value, Low Effort:**
- Additional CLI tools (Aider, OpenCode, SonarQube)
- Jira basic integration (status sync)

**Future/Experimental:**
- Remote analytics sharing
- Advanced Jira workflows
- Multi-tenant cloud hosting

---

## Notes

These are ideas, not commitments. Prioritization depends on:
- User demand
- Implementation complexity
- Strategic value
- Resource availability

Some may never be built. Some may evolve into different features. This is a living document.

