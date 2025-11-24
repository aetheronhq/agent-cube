"""Judge layout (creates DynamicLayout instance)."""

from .dynamic_layout import DynamicLayout
from .user_config import get_judge_configs

def create_judge_layout(lines_per_box: int = 2):
    """Create a fresh dynamic layout for judges."""
    judges = get_judge_configs()
    boxes = {j.key: j.label for j in judges}
    return DynamicLayout(boxes, lines_per_box)

# Backwards compatibility
def get_triple_layout():
    """Alias for create_judge_layout."""
    return create_judge_layout()


