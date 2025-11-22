# Task: CLI Tool Manager with Auto-Setup

## Overview

Create a unified CLI tool management system using ports and adapters pattern that handles installation detection, version checking, login state verification, and automated setup for all external CLI tools (cursor-agent, gemini, gh, coderabbit).

## Current State

Each adapter currently does basic checks independently:
- `cursor_adapter.py` - checks `cli-config.json` for login
- `gemini_adapter.py` - basic installation check only
- No version checking
- No auto-install/update capabilities
- Inconsistent error messages

## Requirements

### 1. Unified CLI Tool Interface

Create `python/cube/core/cli_tools/base.py`:

```python
class CLITool(ABC):
    """Base interface for external CLI tools."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name (e.g., 'cursor-agent', 'gemini')."""
        pass
    
    @property
    @abstractmethod
    def min_version(self) -> Optional[str]:
        """Minimum required version (e.g., '0.17.0' for gemini)."""
        pass
    
    @abstractmethod
    def check_installed(self) -> bool:
        """Check if tool is installed."""
        pass
    
    @abstractmethod
    def get_version(self) -> Optional[str]:
        """Get installed version."""
        pass
    
    @abstractmethod
    def check_logged_in(self) -> bool:
        """Check if tool is authenticated/logged in."""
        pass
    
    @abstractmethod
    def get_install_command(self) -> str:
        """Command to install the tool."""
        pass
    
    @abstractmethod
    def get_login_command(self) -> str:
        """Command to login/authenticate."""
        pass
    
    @abstractmethod
    def get_update_command(self) -> Optional[str]:
        """Command to update the tool (None if same as install)."""
        pass
    
    @abstractmethod
    def run_health_check(self) -> tuple[bool, str]:
        """Run quick health check. Returns (success, message)."""
        pass
    
    def needs_update(self) -> bool:
        """Check if installed version is below minimum."""
        current = self.get_version()
        if not current or not self.min_version:
            return False
        return version_compare(current, self.min_version) < 0
```

### 2. Implement Tool-Specific Classes

**CursorAgentTool** (`python/cube/core/cli_tools/cursor_agent.py`):
- Check: `~/.cursor/cli-config.json` for login
- Version: Parse from `cursor-agent --version`
- Min version: None (any version works)
- Install: `npm install -g @cursor/cli`
- Login: `cursor-agent login`
- Health check: `cursor-agent --help` (exit 0)

**GeminiCLITool** (`python/cube/core/cli_tools/gemini.py`):
- Check: `~/.gemini/settings.json` for login
- Version: Parse from `gemini --version`
- Min version: `0.17.0` (for --resume latest support)
- Install: `npm install -g @google/gemini-cli@latest`
- Login: `gemini` (interactive, prompt user)
- Health check: `gemini --help`

**GitHubCLITool** (`python/cube/core/cli_tools/gh.py`):
- Check: `gh auth status` for login
- Version: Parse from `gh --version`
- Min version: `2.0.0` (for modern pr create)
- Install: Platform-specific (brew on mac, apt on linux)
- Login: `gh auth login`
- Health check: `gh --help`

**CodeRabbitTool** (`python/cube/core/cli_tools/coderabbit.py`):
- Check: Config file or API key env var
- Version: Parse from `coderabbit --version`
- Min version: `0.3.0`
- Install: Instructions (varies by setup)
- Login: Instructions (API key setup)
- Health check: `coderabbit --help`

### 3. Tool Manager

Create `python/cube/core/cli_tools/manager.py`:

```python
class CLIToolManager:
    """Manages CLI tool lifecycle and validation."""
    
    def validate_tool(self, tool: CLITool, auto_fix: bool = False) -> ToolStatus:
        """Validate tool and optionally auto-fix issues.
        
        Returns:
            ToolStatus with: installed, version, logged_in, ready, issues[]
        """
        
    def ensure_tool_ready(self, tool_name: str, auto_setup: bool = False) -> None:
        """Ensure tool is installed, up-to-date, and logged in.
        
        Raises:
            RuntimeError with helpful instructions if not ready
        """
        
    def auto_install(self, tool: CLITool) -> bool:
        """Attempt to auto-install the tool. Returns success."""
        
    def auto_update(self, tool: CLITool) -> bool:
        """Attempt to auto-update the tool. Returns success."""
        
    def prompt_login(self, tool: CLITool) -> bool:
        """Prompt user to login and verify. Returns success."""
```

### 4. Integration Points

Update existing adapters to use the tool manager:

**In `cursor_adapter.py`**:
```python
def __init__(self):
    from ..cli_tools.registry import get_tool
    self.tool = get_tool("cursor-agent")
    
async def run(self, ...):
    from ..cli_tools.manager import CLIToolManager
    manager = CLIToolManager()
    manager.ensure_tool_ready("cursor-agent")  # Raises if not ready
    # ... rest of run logic
```

**Similarly for**:
- `gemini_adapter.py`
- Any commands that use `gh` CLI
- Future coderabbit integration

### 5. User Experience

When tool not ready, show helpful prompt:

```
❌ Error: gemini CLI not ready

Issues found:
  ✗ Not installed
  
Would you like to install and setup now? [y/N]: y

Installing gemini CLI...
  npm install -g @google/gemini-cli@latest
  ✓ Installed version 0.17.1

Login required. Run: gemini
(Follow prompts to login with Google)

After logging in, run your command again.
```

For auto mode (non-interactive):
```
❌ Error: gemini CLI not ready

Issues:
  ✗ Version 0.16.0 is below minimum 0.17.0
  
To fix:
  npm install -g @google/gemini-cli@latest
  
Or set CUBE_AUTO_SETUP=1 to enable auto-updates
```

### 6. Configuration

Add to `cube.yaml`:
```yaml
behavior:
  auto_install_tools: false  # Prompt before installing
  auto_update_tools: false   # Prompt before updating
  auto_login_tools: false    # Never auto-login (always prompt)
```

Environment variable override:
- `CUBE_AUTO_SETUP=1` - Enable all auto-setup features
- `CUBE_AUTO_INSTALL=1` - Just auto-install
- `CUBE_AUTO_UPDATE=1` - Just auto-update

## Technical Details

### Version Comparison

Implement semantic version comparison:
```python
def version_compare(v1: str, v2: str) -> int:
    """Compare versions. Returns -1 if v1 < v2, 0 if equal, 1 if v1 > v2."""
    # Handle: "1.2.3", "v1.2.3", "1.2.3-beta"
```

### Platform Detection

Handle platform-specific installation:
```python
def get_install_command_for_platform(tool: str) -> str:
    if sys.platform == "darwin":  # macOS
        return f"brew install {tool}"
    elif sys.platform == "linux":
        return f"sudo apt-get install {tool}"
    else:
        return f"# Manual installation required for {tool}"
```

### Health Check Cache

Cache health check results for 5 minutes to avoid repeated checks:
```python
_health_cache: Dict[str, tuple[float, ToolStatus]] = {}
CACHE_TTL = 300  # 5 minutes
```

## Testing Requirements

1. **Unit tests** for each tool implementation:
   - Mock `shutil.which()` for installation checks
   - Mock file existence for login checks
   - Mock subprocess calls for version checks

2. **Integration test**:
   - Create script that simulates missing tools
   - Verify helpful error messages
   - Test version comparison logic

3. **Manual testing**:
   - Uninstall gemini CLI, verify auto-install prompt
   - Install old version, verify update prompt
   - Logout of cursor-agent, verify login prompt

## Success Criteria

✅ All external CLI tools use unified interface  
✅ Version checking works with semantic versioning  
✅ Login state detection accurate for all tools  
✅ Helpful error messages with actionable steps  
✅ Optional auto-setup (with user confirmation)  
✅ Health checks cached to avoid overhead  
✅ Platform-aware installation commands  
✅ Backward compatible with existing code  
✅ All tests passing  

## Files to Create/Modify

**New files:**
- `python/cube/core/cli_tools/__init__.py`
- `python/cube/core/cli_tools/base.py`
- `python/cube/core/cli_tools/cursor_agent.py`
- `python/cube/core/cli_tools/gemini.py`
- `python/cube/core/cli_tools/gh.py`
- `python/cube/core/cli_tools/coderabbit.py`
- `python/cube/core/cli_tools/manager.py`
- `python/cube/core/cli_tools/registry.py`
- `python/cube/core/cli_tools/version.py` (version comparison utilities)

**Modified files:**
- `python/cube/core/adapters/cursor_adapter.py` - use tool manager
- `python/cube/core/adapters/gemini_adapter.py` - use tool manager
- `python/cube/core/adapters/coderabbit_adapter.py` - use tool manager
- `python/cube/commands/decide.py` - check gh CLI before suggesting it
- `python/cube/core/user_config.py` - add behavior settings
- `python/cube.yaml` - add behavior defaults

## Implementation Notes

- Keep existing `check_installed()` methods as fallbacks during transition
- Make tool manager optional at first (feature flag)
- Log all auto-install/update actions for transparency
- Never auto-login without explicit user consent
- Graceful degradation if auto-setup fails

## Out of Scope

- Auto-installing system dependencies (node, npm, python)
- Managing multiple versions of tools
- Tool uninstallation
- Rollback of updates

