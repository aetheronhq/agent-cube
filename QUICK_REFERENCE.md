# Cube CLI Quick Reference

Both bash and Python versions installed and ready to use!

## Commands

| Command | Bash | Python |
|---------|------|--------|
| **Launch dual writers** | `cube writers <task-id> <prompt>` | `cube-py writers <task-id> <prompt>` |
| **Launch judge panel** | `cube panel <task-id> <prompt>` | `cube-py panel <task-id> <prompt>` |
| **Send feedback** | `cube feedback <writer> <task-id> <feedback>` | `cube-py feedback <writer> <task-id> <feedback>` |
| **Resume session** | `cube resume <target> <task-id> "<msg>"` | `cube-py resume <target> <task-id> "<msg>"` |
| **Peer review** | `cube peer-review <task-id> <prompt>` | `cube-py peer-review <task-id> <prompt>` |
| **List sessions** | `cube sessions` | `cube-py sessions` |
| **Check status** | `cube status <task-id>` | `cube-py status <task-id>` |
| **Generate prompt** | `cube orchestrate prompt <task>` | `cube-py orchestrate prompt <task>` |
| **Version** | `cube --version` | `cube-py --version` |

## Flags

| Flag | Description | Bash | Python |
|------|-------------|------|--------|
| `--resume` | Resume existing sessions | ✅ | ✅ |
| `--fresh` | Launch new judges (peer-review) | ✅ | ✅ |
| `--copy` | Copy to clipboard (orchestrate) | ✅ | ✅ |

## Quick Examples

### Bash Version

```bash
cube writers 01-api-client prompts/writer.md
cube panel 01-api-client prompts/panel.md
cube feedback codex 01-api-client prompts/synthesis.md
cube peer-review 01-api-client prompts/peer-review.md
```

### Python Version

```bash
cube-py writers 01-api-client prompts/writer.md
cube-py panel 01-api-client prompts/panel.md
cube-py feedback codex 01-api-client prompts/synthesis.md
cube-py peer-review 01-api-client prompts/peer-review.md
```

### Mix Both

```bash
# Start with bash
cube writers my-task prompt.md

# Continue with Python
cube-py sessions
cube-py panel my-task panel.md

# Back to bash
cube peer-review my-task peer-review.md
```

They're fully compatible!

## Which to Use?

**Bash (`cube`):**
- Default, stable, no dependencies
- Faster startup
- Use for production

**Python (`cube-py`):**
- Better error messages
- Type safety
- Easier to extend
- Use for development

**Both work identically!** Choose based on preference.

## Installation

Already installed! Both commands available:
- `cube` - Bash version
- `cube-py` - Python version

## Documentation

- `AGENT_CUBE.md` - Core framework
- `AGENT_CUBE_AUTOMATION.md` - Automation guide
- `python/README.md` - Python version docs
- `PYTHON_IMPLEMENTATION.md` - Implementation details
- `python/TESTING.md` - Testing guide
