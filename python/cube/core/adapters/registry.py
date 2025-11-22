"""CLI adapter registry and factory."""

from typing import Dict, Type
from ..cli_adapter import CLIAdapter
from .coderabbit_adapter import CodeRabbitAdapter
from .cursor_adapter import CursorAdapter
from .gemini_adapter import GeminiAdapter

_ADAPTERS: Dict[str, Type[CLIAdapter]] = {
    "cursor-agent": CursorAdapter,
    "gemini": GeminiAdapter,
    "coderabbit": CodeRabbitAdapter,
}

def get_adapter(cli_name: str) -> CLIAdapter:
    """Get CLI adapter instance by name."""
    adapter_class = _ADAPTERS.get(cli_name)
    
    if not adapter_class:
        raise ValueError(f"Unknown CLI tool: {cli_name}. Available: {list(_ADAPTERS.keys())}")
    
    return adapter_class()

def register_adapter(name: str, adapter_class: Type[CLIAdapter]) -> None:
    """Register a new CLI adapter."""
    _ADAPTERS[name] = adapter_class

def list_adapters() -> list[str]:
    """List all registered CLI adapters."""
    return list(_ADAPTERS.keys())

