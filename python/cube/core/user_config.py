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
    color: str
    letter: str

@dataclass
class JudgeConfig:
    """Configuration for a judge persona."""
    key: str
    model: str
    label: str
    color: str
    # New fields for CLI reviewers
    type: str = "llm"  # "llm" or "cli-review"
    cmd: Optional[str] = None
    peer_review_only: bool = False  # Skip in panel, only run in peer-review

@dataclass
class CubeConfig:
    """Main configuration."""
    writers: Dict[str, WriterConfig]
    writer_slug_map: Dict[str, str]  # slug -> writer key
    writer_alias_map: Dict[str, str]  # alias -> slug
    writer_order: list[str]
    judges: Dict[str, JudgeConfig]
    judge_order: list[str]
    judge_alias_map: Dict[str, str]
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
    
    data = {}
    
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
    writer_slug_map: Dict[str, str] = {}
    writer_alias_map: Dict[str, str] = {}
    for idx, (key, w) in enumerate(data.get("writers", {}).items()):
        writer_order.append(key)
        slug = w["name"]
        letter = w.get("letter") or chr(ord("A") + idx)
        canonical_slug = slug
        writer_cfg = WriterConfig(
            key=key,
            name=canonical_slug,
            model=w["model"],
            label=w["label"],
            color=w["color"],
            letter=letter.upper()
        )
        writers[key] = writer_cfg
        writer_slug_map[canonical_slug] = key
        
        aliases = {
            canonical_slug,
            canonical_slug.replace("_", "-"),
            key,
            key.replace("_", "-"),
            f"writer-{canonical_slug}",
            f"writer-{canonical_slug}".replace("_", "-"),
            writer_cfg.letter,
            writer_cfg.letter.lower(),
            f"writer-{writer_cfg.letter}",
            f"writer-{writer_cfg.letter.lower()}",
        }
        for alias in aliases:
            writer_alias_map[alias.lower()] = canonical_slug
    
    judges: Dict[str, JudgeConfig] = {}
    judge_order: list[str] = []
    judge_alias_map: Dict[str, str] = {}
    for idx, (key, j) in enumerate(data.get("judges", {}).items()):
        judge_order.append(key)
        judge_cfg = JudgeConfig(
            key=key,
            model=j.get("model", "sonnet-4.5-thinking"),
            label=j.get("label", key),
            color=j.get("color", "green"),
            type=j.get("type", "llm"),
            cmd=j.get("cmd"),
            peer_review_only=j.get("peer_review_only", False)
        )
        judges[key] = judge_cfg
        
        aliases = {
            key,
            key.replace("_", "-"),
            judge_cfg.label.lower(),
        }
        for alias in aliases:
            judge_alias_map[alias.lower()] = key
    
    cli_tools = data.get("cli_tools", {})
    behavior = data.get("behavior", {})
    prompter = data.get("prompter", {})
    prompter_model = prompter.get("model", "opus-4.5-thinking")
    
    _config_cache = CubeConfig(
        writers=writers,
        writer_slug_map=writer_slug_map,
        writer_alias_map=writer_alias_map,
        writer_order=writer_order,
        judges=judges,
        judge_order=judge_order,
        judge_alias_map=judge_alias_map,
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
    """Get writer configuration."""
    config = load_config()
    return config.writers.get(writer_key, config.writers["writer_a"])

def get_writer_config_by_slug(slug: str) -> WriterConfig:
    """Get writer configuration by slug/name."""
    config = load_config()
    if slug not in config.writer_slug_map:
        alias_slug = config.writer_alias_map.get(slug.lower())
        if not alias_slug:
            raise KeyError(f"Unknown writer slug: {slug}")
        slug = alias_slug
    writer_key = config.writer_slug_map[slug]
    return config.writers[writer_key]

def get_writer_slugs() -> list[str]:
    """Return list of writer slugs in order."""
    config = load_config()
    return [config.writers[key].name for key in config.writer_order]

def get_writer_letter(slug: str) -> str:
    """Get the letter (A/B/...) associated with a writer slug."""
    writer = get_writer_config_by_slug(slug)
    return writer.letter

def resolve_writer_alias(alias: str) -> WriterConfig:
    """Resolve a user-provided alias (slug, letter, writer-a, etc.) to a writer config."""
    config = load_config()
    alias_lower = alias.lower()
    slug = config.writer_alias_map.get(alias_lower)
    if not slug:
        raise KeyError(f"Unknown writer alias: {alias}")
    return get_writer_config_by_slug(slug)

def get_writer_aliases() -> list[str]:
    """Return sorted list of known writer aliases."""
    config = load_config()
    return sorted(set(config.writer_alias_map.keys()))

def get_writer_by_letter(letter: str) -> WriterConfig:
    """Get writer config by letter (A/B/...)."""
    config = load_config()
    letter_upper = letter.upper()
    for key in config.writer_order:
        writer = config.writers[key]
        if writer.letter == letter_upper:
            return writer
    raise KeyError(f"No writer found with letter: {letter}")

def get_writer_by_key_or_letter(key_or_letter: str) -> WriterConfig:
    """Get writer config by key (writer_a) or letter (A)."""
    config = load_config()
    
    # Try as key first
    if key_or_letter in config.writers:
        return config.writers[key_or_letter]
    
    # Try as letter
    letter_upper = key_or_letter.upper()
    for key in config.writer_order:
        writer = config.writers[key]
        if writer.letter == letter_upper:
            return writer
    
    raise KeyError(f"No writer found with key or letter: {key_or_letter}")

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
    """Resolve alias (judge-1, 1, key, label) to judge config."""
    config = load_config()
    alias_lower = alias.lower()
    key = config.judge_alias_map.get(alias_lower)
    if not key:
        raise KeyError(f"Unknown judge alias: {alias}")
    return config.judges[key]

def get_judge_aliases() -> list[str]:
    """Return sorted list of judge aliases."""
    config = load_config()
    return sorted(set(config.judge_alias_map.keys()))

