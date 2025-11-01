# Agent Cube CLI

**Orchestrate parallel LLM coding agents with automated dual-writer workflows and judge panels.**

A command-line tool for running multiple LLM agents in parallel, comparing their solutions, and synthesizing the best of both worlds. Built for production-grade code quality through competitive agent evaluation.

## Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/aetheronhq/agent-cube/main/install.sh | bash
```

Or download the distribution package and run:
```bash
bash install-cube.sh
```

## What It Does

- **Dual Writers**: Launch 2 LLM agents in parallel to solve the same coding task independently
- **Judge Panel**: 3 AI judges review both solutions and vote for the winner
- **Synthesis**: Winning agent integrates improvements from both solutions
- **Automation**: Full workflow automation with real-time streaming output

## Usage

```bash
# Launch dual writers for a task
cube writers <task-id> <prompt-file>

# Launch 3-judge panel
cube panel <task-id> <panel-prompt-file>

# Send feedback to writer
cube feedback <writer> <task-id> <feedback-file>

# Resume a session
cube resume <writer> <task-id> "message"

# Check status
cube status <task-id>

# List sessions
cube sessions
```

## Prerequisites

- **jq**: `brew install jq` (macOS) or `apt-get install jq` (Linux)
- **cursor-agent**: `npm install -g @cursor/cli`
- **Cursor account**: `cursor-agent login`

## Documentation

- [Installation Guide](INSTALL.md) - Detailed installation instructions
- [Agent Cube Framework](AGENT_CUBE.md) - Complete workflow methodology
- [CLI Automation Guide](AGENT_CUBE_AUTOMATION.md) - Advanced usage and automation

## Example Workflow

```bash
# 1. Create writer prompt for your task
cat > my-task-prompt.md << 'EOF'
You are implementing feature X. Read planning docs and implement...
EOF

# 2. Launch dual writers
cube writers my-task implementation/my-task-prompt.md

# Writers work in parallel, commit, and push their branches

# 3. Create panel prompt
cat > my-task-panel.md << 'EOF'
Review both writer solutions and vote for the winner...
EOF

# 4. Launch judge panel
cube panel my-task implementation/my-task-panel.md

# Judges review, vote, provide synthesis instructions

# 5. Send synthesis to winner
cube feedback codex my-task implementation/my-task-synthesis.md

# Winner applies synthesis, runs tests, commits, pushes
```

## Features

- ✅ **Parallel Execution**: Writers work in isolated git worktrees
- ✅ **Real-time Streaming**: Color-coded output with tool call tracking
- ✅ **Session Management**: Automatic session ID capture for resumption
- ✅ **Git Integration**: Automatic branch creation and worktree management
- ✅ **Quality Gates**: Ensures code is committed and pushed
- ✅ **Path Handling**: Automatically adds cursor-agent to PATH

## Architecture

```
Agent Cube Workflow:
┌─────────────┐
│   Task      │
└──────┬──────┘
       │
   ┌───┴───┐
   │       │
Writer A  Writer B  (parallel implementation)
   │       │
   └───┬───┘
       │
  ┌────┴────┐
  │ Panel   │  (3 judges review and vote)
  └────┬────┘
       │
  ┌────┴────┐
  │Synthesis│  (winner integrates best of both)
  └────┬────┘
       │
   ┌───┴───┐
   │  PR   │
   └───────┘
```

## Models

**Writers:**
- Claude Sonnet 4.5 Thinking (`sonnet-4.5-thinking`)
- GPT-5 Codex High (`gpt-5-codex-high`)

**Judges:**
- Judge 1: Claude Sonnet 4.5 Thinking
- Judge 2: GPT-5 Codex High
- Judge 3: Cursor Composer

## Performance

**Observed Metrics:**
- Writer task completion: 2-15 minutes per agent
- Judge panel review: 2-5 minutes per judge (parallel)
- Total dual-writer cycle: ~15-25 minutes
- Manual equivalent: ~60-90 minutes

**Automation Rate:** ~70-90% depending on complexity

## Requirements

- macOS or Linux (tested on macOS)
- Bash shell
- Git for worktree management
- Node.js/npm for cursor-agent installation

## License

MIT

## Contributing

Issues and PRs welcome! This is an early experimental tool.

## Credits

Built by the Aetheron team for automating high-quality parallel LLM coding workflows.

