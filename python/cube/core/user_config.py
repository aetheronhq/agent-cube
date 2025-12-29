"""User configuration management."""

import sys
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class WriterConfig:
    """Configuration for a writer persona."""
    key: str
    name: str
    model: str
    label: str
    letter: str  # Writer letter: A, B, C...
    color: str
    
    def session_key(self, task_id: str) -> str:
        """Session file key - use config key directly (e.g., WRITER_A_taskid)."""
        return f"{self.key.upper()}_{task_id}"
    
    def worktree_name(self, task_id: str) -> str:
        """Worktree directory name (e.g., writer-opus-taskid)."""
        return f"writer-{self.name}-{task_id}"

@dataclass
class JudgeConfig:
    """Configuration for a judge persona."""
    key: str
    model: str
    label: str
    color: str
    type: str = "llm"  # "llm" or "cli-review"
    cmd: Optional[str] = None
    peer_review_only: bool = False  # Skip in panel, only run in peer-review
    
    def session_key(self, task_id: str, review_type: str) -> str:
        """Session file key (e.g., JUDGE_1_taskid_panel)."""
        return f"{self.key.upper()}_{task_id}_{review_type}"

@dataclass
class CubeConfig:
    """Main configuration."""
    writers: Dict[str, WriterConfig]
    writer_order: list[str]
    judges: Dict[str, JudgeConfig]
    judge_order: list[str]
    cli_tools: Dict[str, str]
    prompter_model: str
    auto_commit: bool
    auto_push: bool
    auto_update: bool
    session_recording_at_start: bool

_config_cache: Optional[CubeConfig] = None

def clear_config_cache() -> None:
    """Clear the config cache to force reload."""
    global _config_cache
    _config_cache = None

def find_config_files() -> tuple[Optional[Path], Optional[Path], Optional[Path]]:
    """Find the base, global and repo-level config files.
    
    Returns:
        Tuple of (base_config, global_config, repo_config)
    """
    base_config = None
    global_config = None
    repo_config = None
    
    # 1. Base (python/cube.yaml)
    base_path = Path(__file__).parent.parent.parent / "cube.yaml"
    if base_path.exists():
        base_config = base_path

    # 2. Global (~/.cube/cube.yaml)
    global_path = Path.home() / ".cube" / "cube.yaml"
    if global_path.exists():
        global_config = global_path

    # 3. Repo (cube.yaml in CWD or root)
    # Walk up from CWD to find cube.yaml
    current = Path.cwd()
    while True:
        check_path = current / "cube.yaml"
        if check_path.exists():
            repo_config = check_path
            break
        
        if (current / ".git").exists():
            # Stop at git root
            break
            
        if current.parent == current:
            # Stop at filesystem root
            break
            
        current = current.parent
    
    return base_config, global_config, repo_config


def merge_config_data(base: dict, override: dict) -> dict:
    """Deep merge override config into base config recursively."""
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_config_data(result[key], value)
        else:
            result[key] = value
    
    return result


def load_config() -> CubeConfig:
    """Load configuration from cube.yaml or use defaults.
    
    Priority order (later overrides earlier):
    1. Hardcoded Defaults
    2. Base config (python/cube.yaml)
    3. Global config (~/.cube/cube.yaml)
    4. Repo-level config (cube.yaml)
    """
    global _config_cache
    
    if _config_cache:
        return _config_cache
    
    data: dict[str, Any] = {}
    
    base_config, global_config, repo_config = find_config_files()
    
    if base_config:
        with open(base_config) as f:
            try:
                base_data = yaml.safe_load(f)
                if base_data:
                    data = merge_config_data(data, base_data)
            except (yaml.YAMLError, Exception) as e:
                print(f"Warning: Failed to parse base config {base_config}: {e}", file=sys.stderr)
    
    if global_config:
        with open(global_config) as f:
            try:
                global_data = yaml.safe_load(f)
                if global_data:
                    data = merge_config_data(data, global_data)
            except (yaml.YAMLError, Exception) as e:
                print(f"Warning: Failed to parse global config {global_config}: {e}", file=sys.stderr)
    
    if repo_config:
        with open(repo_config) as f:
            try:
                repo_data = yaml.safe_load(f)
                if repo_data:
                    data = merge_config_data(data, repo_data)
            except (yaml.YAMLError, Exception) as e:
                print(f"Warning: Failed to parse repo config {repo_config}: {e}", file=sys.stderr)
    
    writer_order: list[str] = []
    writers: Dict[str, WriterConfig] = {}
    for idx, (key, w) in enumerate(data.get("writers", {}).items()):
        writer_order.append(key)
        # Derive letter from key suffix (writer_a -> A, writer_b -> B)
        # This ensures stable session keys even if config order changes
        letter = key.split('_')[-1].upper()
        writers[key] = WriterConfig(
            key=key,
            name=w["name"],
            model=w["model"],
            label=w["label"],
            letter=letter,
            color=w["color"]
        )
    
    judges: Dict[str, JudgeConfig] = {}
    judge_order: list[str] = []
    for key, j in data.get("judges", {}).items():
        judge_order.append(key)
        judges[key] = JudgeConfig(
            key=key,
            model=j.get("model", "sonnet-4.5-thinking"),
            label=j.get("label", key),
            color=j.get("color", "green"),
            type=j.get("type", "llm"),
            cmd=j.get("cmd"),
            peer_review_only=j.get("peer_review_only", False)
        )
    
    cli_tools = data.get("cli_tools", {})
    behavior = data.get("behavior", {})
    prompter = data.get("prompter", {})
    prompter_model = prompter.get("model", "opus-4.5-thinking")
    
    _config_cache = CubeConfig(
        writers=writers,
        writer_order=writer_order,
        judges=judges,
        judge_order=judge_order,
        cli_tools=cli_tools,
        prompter_model=prompter_model,
        auto_commit=behavior.get("auto_commit", True),
        auto_push=behavior.get("auto_push", True),
        auto_update=behavior.get("auto_update", True),
        session_recording_at_start=behavior.get("session_recording_at_start", True)
    )
    
    return _config_cache

def get_cli_tool_for_model(model: str) -> str:
    """Get the CLI tool to use for a given model."""
    config = load_config()
    return config.cli_tools.get(model, "cursor-agent")

def get_prompter_model() -> str:
    """Get the model to use for prompter agents."""
    config = load_config()
    return config.prompter_model

def get_writer_config(writer_key: str) -> WriterConfig:
    """Get writer configuration by key."""
    config = load_config()
    return config.writers.get(writer_key, config.writers["writer_a"])

def get_writer_slugs() -> list[str]:
    """Return list of writer slugs (names) in order."""
    config = load_config()
    return [config.writers[key].name for key in config.writer_order]

def resolve_writer_alias(alias: str) -> WriterConfig:
    """Resolve a user-provided alias to writer config.
    
    Supports: key (writer_a), name (opus), hyphenated (writer-a), letter (a/A).
    """
    config = load_config()
    alias_lower = alias.lower()
    
    # Direct key match (writer_a, writer_b)
    if alias_lower in config.writers:
        return config.writers[alias_lower]
    
    # By name/slug (opus, codex)
    for w in config.writers.values():
        if w.name.lower() == alias_lower:
            return w
    
    # Hyphenated key (writer-a -> writer_a)
    for key, w in config.writers.items():
        if key.replace("_", "-") == alias_lower:
            return w
    
    # Single letter (a -> writer_a, b -> writer_b)
    if len(alias_lower) == 1 and alias_lower.isalpha():
        idx = ord(alias_lower) - ord('a')
        if 0 <= idx < len(config.writer_order):
            return config.writers[config.writer_order[idx]]
    
    raise KeyError(f"Unknown writer: {alias}")

def get_writer_aliases() -> list[str]:
    """Return list of common writer aliases."""
    config = load_config()
    aliases = []
    for idx, key in enumerate(config.writer_order):
        w = config.writers[key]
        aliases.extend([w.name, key, chr(ord('a') + idx)])
    return sorted(set(aliases))

def get_writer_by_key_or_letter(key_or_letter: str) -> WriterConfig:
    """Get writer config by key (writer_a) or letter (A/a)."""
    return resolve_writer_alias(key_or_letter)

def get_judge_config(judge_key: str) -> JudgeConfig:
    """Get judge configuration by key."""
    config = load_config()
    if judge_key in config.judges:
        return config.judges[judge_key]
    raise KeyError(f"Unknown judge key: {judge_key}")

def get_judge_configs() -> list[JudgeConfig]:
    """Return all judge configs in configured order."""
    config = load_config()
    return [config.judges[key] for key in config.judge_order]

def get_judge_numbers() -> list[str]:
    """Return list of judge keys."""
    return [judge.key for judge in get_judge_configs()]

def resolve_judge_alias(alias: str) -> JudgeConfig:
    """Resolve alias to judge config.
    
    Supports: key (judge_1), hyphenated (judge-1), label (Judge Sonnet).
    """
    config = load_config()
    alias_lower = alias.lower()
    
    # Direct key match (judge_1, judge_2)
    if alias_lower in config.judges:
        return config.judges[alias_lower]
    
    # Hyphenated key (judge-1 -> judge_1)
    for key, j in config.judges.items():
        if key.replace("_", "-") == alias_lower:
            return j
    
    # By label (Judge Sonnet)
    for j in config.judges.values():
        if j.label.lower() == alias_lower:
            return j
    
    raise KeyError(f"Unknown judge: {alias}")

def get_judge_aliases() -> list[str]:
    """Return list of common judge aliases."""
    config = load_config()
    aliases = []
    for key in config.judge_order:
        aliases.extend([key, key.replace("_", "-")])
    return sorted(set(aliases))

