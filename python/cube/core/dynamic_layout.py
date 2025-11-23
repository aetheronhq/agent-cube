"""Dynamic layout that adapts to any number of boxes."""

from .base_layout import BaseThinkingLayout
from typing import Dict

class DynamicLayout:
    """Universal layout for any number of thinking boxes."""
    
    _instance = None
    _boxes = None
    
    @classmethod
    def initialize(cls, boxes: Dict[str, str], lines_per_box: int = 2):
        """Initialize layout with specific boxes.
        
        Args:
            boxes: Dict of {key: label} e.g. {"judge_1": "Judge Sonnet", "writer_a": "Writer A"}
            lines_per_box: Number of lines per thinking box
        """
        cls._boxes = boxes
        cls._instance = BaseThinkingLayout(boxes, lines_per_box)
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise RuntimeError("DynamicLayout not initialized. Call initialize() first.")
        return cls._instance
    
    @classmethod
    def add_thinking(cls, key: str, text: str):
        """Add thinking to a box (buffers until punctuation)."""
        cls.get_instance().add_thinking(key, text)
    
    @classmethod
    def add_assistant_message(cls, key: str, content: str, label: str, color: str):
        """Add assistant message to main output (buffers per agent until punctuation).
        
        Buffers fragments and outputs complete sentences as:
        [color]label[/color] 💭 complete sentence.
        """
        cls.get_instance().add_assistant_message(key, content, label, color)
    
    @classmethod
    def add_tool_event(cls, line: str):
        """Add tool call/error to main output (immediate, no buffering)."""
        cls.get_instance().add_output(line)
    
    @classmethod
    def mark_complete(cls, key: str, status: str = None):
        """Mark a box as complete."""
        cls.get_instance().mark_complete(key, status)
    
    @classmethod
    def flush_buffers(cls):
        """Flush all buffers."""
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
        cls._boxes = None

def get_dynamic_layout():
    """Get the dynamic layout."""
    return DynamicLayout

