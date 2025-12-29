# Task 16: Claude Code CLI Adapter

## Summary
Add Claude Code CLI as a supported agent backend, alongside cursor-agent and gemini-cli.

## Motivation
- Claude Code is Anthropic's official CLI for Claude models
- Provides direct access to Claude 4 Opus, Sonnet without going through cursor-agent
- Diversifies model access - not dependent on single CLI tool
- May have different strengths/output patterns than cursor-agent

## Prerequisites
- Claude Code CLI installed: https://github.com/anthropics/claude-code
- Anthropic API key configured

## Implementation

### 1. Create Adapter
`python/cube/core/adapters/claude_code_adapter.py`

```python
class ClaudeCodeAdapter(CLIAdapter):
    """Adapter for Claude Code CLI."""
    
    async def run(self, worktree, model, prompt, session_id, resume):
        cmd = ["claude", "code", "--model", model, ...]
        async for line in run_subprocess_streaming(cmd, worktree, "claude-code"):
            yield line
    
    def check_installed(self) -> bool:
        return shutil.which("claude") is not None
```

### 2. Create Parser
`python/cube/core/parsers/claude_code_parser.py`

Need to analyze Claude Code output format:
- Does it output JSON?
- What message types? (thinking, assistant, tool_call, etc.)
- Session handling?

### 3. Register in Adapters
`python/cube/core/adapters/registry.py`
```python
from .claude_code_adapter import ClaudeCodeAdapter

ADAPTERS = {
    "cursor-agent": CursorAdapter,
    "gemini": GeminiAdapter,
    "claude-code": ClaudeCodeAdapter,  # NEW
}
```

### 4. Register Parser
`python/cube/core/parsers/registry.py`
```python
from .claude_code_parser import ClaudeCodeParser

PARSERS = {
    "cursor-agent": CursorParser,
    "gemini": GeminiParser,
    "claude-code": ClaudeCodeParser,  # NEW
}
```

### 5. Update Config
`cube.yaml` example:
```yaml
cli_tools:
  claude-4-opus: claude-code
  claude-4-sonnet: claude-code
  sonnet-4.5-thinking: cursor-agent  # existing

writers:
  writer_a:
    model: "claude-4-opus"
    # Will use claude-code CLI
```

## Research Needed
- [ ] Claude Code CLI output format (run `claude code --help`)
- [ ] Session/conversation support
- [ ] Model name mappings
- [ ] Any special flags needed

## Acceptance Criteria
- [ ] `ClaudeCodeAdapter` runs Claude Code CLI
- [ ] `ClaudeCodeParser` parses output correctly
- [ ] Can configure writer to use claude-code in cube.yaml
- [ ] Streaming output displays in terminal UI
- [ ] Session resume works (if supported)
- [ ] Install instructions documented

## Notes
- Follow same patterns as `gemini_adapter.py`
- May need trusted folders config like Gemini
- Test with both Opus and Sonnet models

