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

def find_config_files() -> tuple[Optional[Path], Optional[Path]]:
    """Find the global and repo-level config files.
    
    Returns:
        Tuple of (global_config, repo_config)
    """
    global_config = None
    repo_config = None
    
    global_search_paths = [
        Path.home() / ".cube" / "cube.yaml",
        Path.home() / ".cube" / "config.yaml",
        Path.home() / ".config" / "cube" / "cube.yaml",
        Path(__file__).parent.parent.parent / "cube.yaml",
    ]
    
    for path in global_search_paths:
        if path.exists():
            global_config = path
            break
    
    repo_search_paths = [
        Path.cwd() / ".cube.yml",
        Path.cwd() / ".cube.yaml",
        Path.cwd() / "cube.yaml",
    ]
    
    for path in repo_search_paths:
        if path.exists():
            repo_config = path
            break
    
    return global_config, repo_config

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
    1. Default config
    2. Global config (~/.config/cube/cube.yaml or python/cube.yaml)
    3. Repo-level config (.cube.yml, .cube.yaml, or cube.yaml in repo root)
    """
    global _config_cache
    
    if _config_cache:
        return _config_cache
    
    data = get_default_config()
    
    global_config, repo_config = find_config_files()
    
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
    """Get default configuration."""
    return {
        "cli_tools": {
            "sonnet-4.5-thinking": "cursor-agent",
            "gpt-5-codex-high": "cursor-agent",
            "grok": "cursor-agent",
        },
        "writers": {
            "writer_a": {
                "name": "sonnet",
                "model": "sonnet-4.5-thinking",
                "label": "Writer A",
                "color": "green"
            },
            "writer_b": {
                "name": "codex",
                "model": "gpt-5-codex-high",
                "label": "Writer B",
                "color": "blue"
            }
        },
        "judges": {
            "judge_1": {
                "model": "sonnet-4.5-thinking",
                "label": "Judge 1",
                "color": "green"
            },
            "judge_2": {
                "model": "gpt-5-codex-high",
                "label": "Judge 2",
                "color": "yellow"
            },
            "judge_3": {
                "model": "grok",
                "label": "Judge 3",
                "color": "magenta"
            }
        },
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

