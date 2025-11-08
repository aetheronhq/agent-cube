"""Dual writer layout."""

from .base_layout import BaseThinkingLayout

class DualWriterLayout(BaseThinkingLayout):
    """Fixed layout with Writer A/B thinking boxes + output region."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            boxes = {"writer_a": "Writer A", "writer_b": "Writer B"}
            BaseThinkingLayout.__init__(cls._instance, boxes, lines_per_box=3)
        return cls._instance
    
    def add_thinking(self, writer: str, text: str) -> None:
        """Add thinking from Writer A or B."""
        box_id = "writer_a" if writer == "A" else "writer_b"
        super().add_thinking(box_id, text)
    
    @classmethod
    def reset(cls):
        """Reset singleton."""
        if cls._instance:
            cls._instance.close()
        cls._instance = None

def get_dual_layout() -> DualWriterLayout:
    """Get the global dual layout instance."""
    return DualWriterLayout()
