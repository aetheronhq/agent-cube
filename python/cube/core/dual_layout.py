"""Dual writer layout."""

from .base_layout import BaseThinkingLayout

class DualWriterLayout:
    """Fixed layout with Writer A/B thinking boxes + output region."""
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            boxes = {"writer_a": "Writer A", "writer_b": "Writer B"}
            cls._instance = BaseThinkingLayout(boxes, lines_per_box=3)
        return cls._instance
    
    @classmethod
    def add_thinking(cls, writer: str, text: str):
        """Add thinking from Writer A or B."""
        box_id = "writer_a" if writer == "A" else "writer_b"
        cls.get_instance().add_thinking(box_id, text)
    
    @classmethod
    def mark_complete(cls, box_id: str, status: str = None):
        """Mark a writer as complete with optional status."""
        cls.get_instance().mark_complete(box_id, status)
    
    @classmethod
    def add_output(cls, line: str, buffered: bool = False):
        """Add output line."""
        cls.get_instance().add_output(line, buffered)
    
    @classmethod
    def flush_buffers(cls):
        """Flush any remaining buffers."""
        cls.get_instance().flush_buffers()
    
    @classmethod
    def start(cls):
        """Start layout."""
        cls.get_instance().start()
    
    @classmethod
    def close(cls):
        """Close layout."""
        if cls._instance:
            cls._instance.close()
    
    @classmethod
    def reset(cls):
        """Reset singleton."""
        if cls._instance:
            cls._instance.close()
        cls._instance = None

def get_dual_layout():
    """Get the dual layout."""
    return DualWriterLayout

