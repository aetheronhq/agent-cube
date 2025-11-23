# CodeRabbit CLI Judge Integration

Guide for integrating CodeRabbit CLI as a judge in AgentCube.

---

## 🏗️ Architecture: CLI Review Adapter

CodeRabbit integration now uses the generic **CLI Review Adapter** pattern, which pipes the output of ANY CLI tool to an Orchestrator Agent (LLM) for synthesis and decision making.

```
Judge Panel Orchestrator
         │
         ├─── CLIReviewAdapter (Generic)
         │    │
         │    ├── 1. Runs Tool (CodeRabbit)
         │    │      Target: Writer A Branch
         │    │      Target: Writer B Branch
         │    │
         │    └── 2. Runs Synthesizer (LLM)
         │           Input: Tool Outputs
         │           Task: Compare & Decide
         │           Output: JSON Decision
```

This replaces the previous plan of writing a complex regex parser for CodeRabbit's text output. Instead, we let an LLM read the text report and make the decision.

---

## ⚙️ Configuration

Configure in `cube.yaml`:

```yaml
judges:
  judge_3:
    type: "cli-review"
    
    # Command to run on each writer's branch
    # {{worktree}} is replaced with the checkout path
    cmd: "coderabbit review --plain --type all --cwd {{worktree}}"
    
    # Agent model to synthesize the results
    orchestrator: "composer-1"  # or claude-3-5-sonnet
    
    label: "CodeRabbit (via Composer)"
    color: "magenta"
```

---

## 🚀 How it Works

1. **Dual Execution**: The adapter runs `coderabbit review` TWICE (once for each writer's branch).
2. **Visibility**: Tool output is streamed to the user as "thinking" so you see progress.
3. **Synthesis**: The raw output from both runs is fed into a prompt for the Orchestrator Agent.
4. **Decision**: The Orchestrator generates a standard `judge-3-task-decision.json` file.

---

## ✅ Benefits

- **Robustness**: Doesn't break if CodeRabbit output format changes.
- **Intelligence**: LLM understands context ("critical security issue" vs "nitpick").
- **Flexibility**: Can be used for Snyk, Semgrep, ESLint, or any other CLI tool.
- **Simplicity**: No custom parsers code needed.

---

## 📚 Reference

- **Adapter Code**: `python/cube/core/adapters/cli_review_adapter.py`
- **Config Logic**: `python/cube/core/user_config.py`
- **PR**: #28
