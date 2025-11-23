"""Dual writer layout (delegates to DynamicLayout)."""

from .dynamic_layout import DynamicLayout

def get_dual_layout():
    """Get the dynamic layout for writers."""
    return DynamicLayout

