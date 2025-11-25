"""Judge layout (delegates to DynamicLayout singleton)."""

from .dynamic_layout import DynamicLayout

def get_triple_layout():
    """Get the dynamic layout (singleton)."""
    return DynamicLayout


