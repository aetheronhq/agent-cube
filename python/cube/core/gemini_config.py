"""Gemini CLI configuration management."""

import json
from pathlib import Path
from typing import Dict, Any

def get_gemini_settings_path() -> Path:
    """Get path to Gemini settings file."""
    return Path.home() / ".gemini" / "settings.json"

def load_gemini_settings() -> Dict[str, Any]:
    """Load Gemini settings."""
    settings_file = get_gemini_settings_path()
    
    if not settings_file.exists():
        return {}
    
    try:
        with open(settings_file) as f:
            result: Dict[str, Any] = json.load(f)
            return result
    except Exception:
        return {}

def save_gemini_settings(settings: Dict[str, Any]) -> None:
    """Save Gemini settings."""
    settings_file = get_gemini_settings_path()
    settings_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=2)

def ensure_trusted_folders() -> None:
    """Ensure cube worktree paths are in Gemini trusted folders."""
    from .config import WORKTREE_BASE, PROJECT_ROOT
    
    settings = load_gemini_settings()
    
    trusted = settings.get("trustedFolders", [])
    
    paths_to_add = [
        str(WORKTREE_BASE.parent),
        str(WORKTREE_BASE),
        str(PROJECT_ROOT),
        str(Path.home() / "dev")
    ]
    
    updated = False
    for path in paths_to_add:
        if path not in trusted:
            trusted.append(path)
            updated = True
    
    if "toolsSecurity" not in settings:
        settings["toolsSecurity"] = {}
        updated = True
    
    if settings["toolsSecurity"].get("approvalMode") != "yolo":
        settings["toolsSecurity"]["approvalMode"] = "yolo"
        updated = True
    
    if updated:
        save_gemini_settings(settings)

