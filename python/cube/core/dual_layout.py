"""Dual writer layout (creates DynamicLayout instance)."""

from .dynamic_layout import DynamicLayout
from .user_config import get_writer_config

def create_dual_layout():
    """Create a fresh dynamic layout for writers."""
    writer_a = get_writer_config("writer_a")
    writer_b = get_writer_config("writer_b")
    boxes = {"writer_a": writer_a.label, "writer_b": writer_b.label}
    return DynamicLayout(boxes, lines_per_box=3)

# Backwards compatibility
def get_dual_layout():
    """Alias for create_dual_layout."""
    return create_dual_layout()

