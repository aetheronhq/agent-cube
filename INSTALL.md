# Agent Cube CLI - Installation Guide

The Agent Cube CLI (`cube`) orchestrates parallel LLM coding workflows with automated dual-writer processes and judge panels.

## Quick Install

### Option 1: Install Script (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/aetheronhq/aetheron-connect-v2/feature/agent-cube-cli-automation/install.sh | bash
```

This will:

- Install to `~/.agent-cube/`
- Create symlink in `~/.local/bin/cube`
- Check for prerequisites

### Option 2: Homebrew (macOS/Linux)

```bash
brew tap aetheronhq/cube
brew install cube
```

### Option 3: Manual Installation

```bash
# Clone the repository
git clone --branch feature/agent-cube-cli-automation https://github.com/aetheronhq/aetheron-connect-v2.git ~/.agent-cube

# Create symlink
mkdir -p ~/.local/bin
ln -s ~/.agent-cube/scripts/cube ~/.local/bin/cube
chmod +x ~/.agent-cube/scripts/cube

# Add to PATH (if not already)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

## Prerequisites

### Required

1. **curl** - For downloading files (usually pre-installed)

   ```bash
   # Check if installed
   command -v curl
   ```

2. **jq** - For parsing JSON output

   ```bash
   # macOS
   brew install jq

   # Linux
   sudo apt-get install jq
   ```

3. **cursor-agent CLI** - For running LLM agents
   ```bash
   npm install -g @cursor/cli
   cursor-agent login
   ```

### Verify Installation

```bash
# Check cube is installed
cube version

# Check prerequisites
command -v curl && echo "✅ curl"
command -v jq && echo "✅ jq"
command -v cursor-agent && echo "✅ cursor-agent"
```

## Post-Installation

### Update PATH

If `cube` command is not found, add to your shell config:

```bash
# For Zsh (macOS default)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# For Bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Authenticate with Cursor

```bash
cursor-agent login
```

Follow the prompts to authenticate with your Cursor account.

## Quick Start

```bash
# Show help
cube --help

# List active agent sessions
cube sessions

# Check task status
cube status <task-id>

# Launch dual writers
cube writers <task-id> <prompt-file>

# Launch judge panel
cube panel <task-id> <panel-prompt-file>

# Send feedback to a writer
cube feedback codex <task-id> <feedback-file>

# Resume a writer session
cube resume codex <task-id> "Continue with the implementation"
```

## Updating

### Install Script

```bash
curl -fsSL https://raw.githubusercontent.com/aetheronhq/aetheron-connect-v2/feature/agent-cube-cli-automation/install.sh | bash
```

### Homebrew

```bash
brew update
brew upgrade cube
```

### Manual

```bash
cd ~/.agent-cube
git pull origin main
```

## Uninstalling

### All Methods

```bash
rm -rf ~/.agent-cube
rm ~/.local/bin/cube
```

### Homebrew Only

```bash
brew uninstall cube
brew untap aetheronhq/cube
```

## Troubleshooting

### `cube: command not found`

1. Check if `~/.local/bin` is in your PATH:

   ```bash
   echo $PATH | grep ".local/bin"
   ```

2. If not, add to your shell config and reload:
   ```bash
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```

### `cursor-agent: command not found`

Install cursor-agent:

```bash
npm install -g @cursor/cli
export PATH="$HOME/.local/bin:$PATH"
cursor-agent login
```

### `jq: command not found`

Install jq:

```bash
# macOS
brew install jq

# Linux
sudo apt-get install jq
```

### Agent Sessions Not Found

Ensure you're in a repository with Agent Cube setup:

```bash
ls -la .agent-sessions/
```

Sessions are saved to `.agent-sessions/` in your project root.

## Configuration

Agent Cube uses your project's configuration:

- `.agent-sessions/` - Stores session IDs for resuming
- `scripts/automation/` - Core automation scripts
- `AGENT_CUBE.md` - Workflow documentation
- `AGENT_CUBE_AUTOMATION.md` - CLI automation guide

## Support

- Documentation: See `AGENT_CUBE.md` and `AGENT_CUBE_AUTOMATION.md`
- Issues: https://github.com/aetheronhq/aetheron-connect-v2/issues
- Discussions: https://github.com/aetheronhq/aetheron-connect-v2/discussions

## License

MIT License - See LICENSE file for details
