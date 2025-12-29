"""CLI adapter registry and factory."""

from typing import Dict, Type, Any, Optional
from .base import CLIAdapter
from .cursor import CursorAdapter
from .gemini import GeminiAdapter
from .cli_review import CLIReviewAdapter

_ADAPTERS: Dict[str, Type[CLIAdapter]] = {
    "cursor-agent": CursorAdapter,
    "gemini": GeminiAdapter,
    "cli-review": CLIReviewAdapter,
}

def get_adapter(cli_name: str, config: Optional[Dict[str, Any]] = None) -> CLIAdapter:
    """Get CLI adapter instance by name.
    
    Args:
        cli_name: Name of the adapter/tool
        config: Optional configuration dict for adapters that need it (like CLIReviewAdapter)
    """
    adapter_class = _ADAPTERS.get(cli_name)
    
    if not adapter_class:
        raise ValueError(f"Unknown CLI tool: {cli_name}. Available: {list(_ADAPTERS.keys())}")
    
    # Handle adapters that require config
    if cli_name == "cli-review":
        if not config:
            raise ValueError("CLIReviewAdapter requires config")
        return CLIReviewAdapter(config)
    
    return adapter_class()

def register_adapter(name: str, adapter_class: Type[CLIAdapter]) -> None:
    """Register a new CLI adapter."""
    _ADAPTERS[name] = adapter_class

def list_adapters() -> list[str]:
    """List all registered CLI adapters."""
    return list(_ADAPTERS.keys())
