"""User configuration management."""

import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class WriterConfig:
    """Configuration for a writer persona."""
    name: str
    model: str
    label: str
    color: str

@dataclass
class JudgeConfig:
    """Configuration for a judge persona."""
    model: str
    label: str
    color: str

@dataclass
class CubeConfig:
    """Main configuration."""
    writers: Dict[str, WriterConfig]
    judges: Dict[str, JudgeConfig]
    cli_tools: Dict[str, str]
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
    """Deep merge override config into base config."""
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = {**result[key], **value}
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
    
    data = get_default_config()
    
    base_config, global_config, repo_config = find_config_files()
    
    if base_config:
        with open(base_config) as f:
            base_data = yaml.safe_load(f)
            if base_data:
                data = merge_config_data(data, base_data)
    
    if global_config:
        with open(global_config) as f:
            global_data = yaml.safe_load(f)
            if global_data:
                data = merge_config_data(data, global_data)
    
    if repo_config:
        with open(repo_config) as f:
            repo_data = yaml.safe_load(f)
            if repo_data:
                data = merge_config_data(data, repo_data)
    
    writers = {}
    for key, w in data.get("writers", {}).items():
        writers[key] = WriterConfig(
            name=w["name"],
            model=w["model"],
            label=w["label"],
            color=w["color"]
        )
    
    judges = {}
    for key, j in data.get("judges", {}).items():
        judges[key] = JudgeConfig(
            model=j["model"],
            label=j["label"],
            color=j["color"]
        )
    
    cli_tools = data.get("cli_tools", {})
    behavior = data.get("behavior", {})
    
    _config_cache = CubeConfig(
        writers=writers,
        judges=judges,
        cli_tools=cli_tools,
        auto_commit=behavior.get("auto_commit", True),
        auto_push=behavior.get("auto_push", True),
        auto_update=behavior.get("auto_update", True),
        session_recording_at_start=behavior.get("session_recording_at_start", True)
    )
    
    return _config_cache

def get_default_config() -> dict:
    """Get default configuration structure."""
    return {
        "cli_tools": {},
        "writers": {},
        "judges": {},
        "behavior": {
            "auto_commit": True,
            "auto_push": True,
            "auto_update": True,
            "session_recording_at_start": True
        }
    }

def get_cli_tool_for_model(model: str) -> str:
    """Get the CLI tool to use for a given model."""
    config = load_config()
    return config.cli_tools.get(model, "cursor-agent")

def get_writer_config(writer_key: str) -> WriterConfig:
    """Get writer configuration."""
    config = load_config()
    return config.writers.get(writer_key, config.writers["writer_a"])

def get_judge_config(judge_num: int) -> JudgeConfig:
    """Get judge configuration."""
    config = load_config()
    judge_key = f"judge_{judge_num}"
    return config.judges.get(judge_key, list(config.judges.values())[0])

