# Quick Setup Guide for Agent Cube

## A) Update Cursor-Agent to Latest

```bash
cursor-agent update
```

Or manually:
```bash
npm uninstall -g cursor-agent
npm install -g cursor-agent@latest
cursor-agent --version
```

---

## B) Example Configuration

### Option 1: Workspace Configuration (Recommended)

Create `cube.yaml` in your project root:

```bash
cat > cube.yaml << 'YAML'
# Agent Cube Configuration

# Writer Configuration
writers:
  writer_a:
    model: sonnet-4.5-thinking
    label: "Writer A (Sonnet)"
    color: green
  writer_b:
    model: gpt-5.1-codex-high
    label: "Writer B (Codex)"
    color: blue

# Judge Configuration
judges:
  judge_1:
    model: sonnet-4.5-thinking
    label: "Judge 1 (Sonnet)"
    color: yellow
  judge_2:
    model: gpt-5.1-codex-high
    label: "Judge 2 (Codex)"
    color: cyan
  judge_3:
    model: gemini-3-pro
    label: "Judge 3 (Gemini)"
    color: magenta

# CLI Tool Mapping
cli_tools:
  sonnet-4.5-thinking: cursor-agent
  gpt-5.1-codex-high: cursor-agent
  gemini-3-pro: cursor-agent
  coderabbit: coderabbit
YAML
```

### Option 2: Global Configuration

Create `~/.cube/cube.yaml`:

```bash
mkdir -p ~/.cube
cat > ~/.cube/cube.yaml << 'YAML'
# Agent Cube Global Configuration

writers:
  writer_a:
    model: sonnet-4.5-thinking
    label: "Writer A (Sonnet)"
    color: green
  writer_b:
    model: gpt-5.1-codex-high
    label: "Writer B (Codex)"
    color: blue

judges:
  judge_1:
    model: sonnet-4.5-thinking
    label: "Judge 1 (Sonnet)"
    color: yellow
  judge_2:
    model: gpt-5.1-codex-high
    label: "Judge 2 (Codex)"
    color: cyan
  judge_3:
    model: gemini-3-pro
    label: "Judge 3 (Gemini)"
    color: magenta

cli_tools:
  sonnet-4.5-thinking: cursor-agent
  gpt-5.1-codex-high: cursor-agent
  gemini-3-pro: cursor-agent
  coderabbit: coderabbit
YAML
```

### Option 3: With CodeRabbit as Judge

```yaml
# Agent Cube Configuration with CodeRabbit

writers:
  writer_a:
    model: sonnet-4.5-thinking
    label: "Writer A (Sonnet)"
    color: green
  writer_b:
    model: gpt-5.1-codex-high
    label: "Writer B (Codex)"
    color: blue

judges:
  judge_1:
    model: sonnet-4.5-thinking
    label: "Judge 1 (Sonnet)"
    color: yellow
  judge_2:
    model: gpt-5.1-codex-high
    label: "Judge 2 (Codex)"
    color: cyan
  judge_3:
    model: coderabbit
    label: "Judge 3 (CodeRabbit)"
    color: magenta

cli_tools:
  sonnet-4.5-thinking: cursor-agent
  gpt-5.1-codex-high: cursor-agent
  gemini-3-pro: cursor-agent
  coderabbit: coderabbit
```

---

## Available Models (cursor-agent 2025.11.06)

- `sonnet-4.5` - Claude Sonnet 4.5
- `sonnet-4.5-thinking` - Claude Sonnet 4.5 with extended thinking
- `gpt-5` - GPT-5
- `gpt-5.1` - GPT-5.1
- `gpt-5-codex` - GPT-5 Codex
- `gpt-5-codex-high` - GPT-5 Codex High
- `gpt-5.1-codex` - GPT-5.1 Codex
- `gpt-5.1-codex-high` - GPT-5.1 Codex High
- `gemini-3-pro` - Gemini 3 Pro (note: currently has connectivity issues)
- `opus-4.1` - Claude Opus 4.1
- `grok` - Grok
- `composer-1` - Composer
- `auto` - Auto-select model

---

## Quick Test

```bash
# Test cursor-agent
cursor-agent --print --force --model sonnet-4.5-thinking "Hello, confirm you're working"

# Test with CodeRabbit (requires installation + auth)
coderabbit --version
coderabbit auth login
```
