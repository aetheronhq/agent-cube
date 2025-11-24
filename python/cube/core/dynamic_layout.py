"""Dynamic layout that adapts to any number of boxes."""

from .base_layout import BaseThinkingLayout
from typing import Dict, Optional

class DynamicLayout:
    """Universal layout for any number of thinking boxes (singleton with proper cleanup)."""
    
    _instance: Optional[BaseThinkingLayout] = None
    
    @classmethod
    def initialize(cls, boxes: Dict[str, str], lines_per_box: int = 2):
        """Initialize layout with specific boxes (closes previous instance if exists).
        
        Args:
            boxes: Dict of {key: label} e.g. {"judge_1": "Judge Sonnet", "writer_a": "Writer A"}
            lines_per_box: Number of lines per thinking box
        """
        # Close previous instance to avoid multiple Live() displays
        if cls._instance:
            cls._instance.close()
        
        cls._instance = BaseThinkingLayout(boxes, lines_per_box)
    
    @classmethod
    def add_thinking(cls, key: str, text: str):
        """Add thinking to a box (buffers until punctuation)."""
        if cls._instance:
            cls._instance.add_thinking(key, text)
    
    @classmethod
    def add_assistant_message(cls, key: str, content: str, label: str, color: str):
        """Add assistant message to main output (buffers per agent until punctuation)."""
        if cls._instance:
            cls._instance.add_assistant_message(key, content, label, color)
    
    @classmethod
    def add_output(cls, line: str):
        """Add to main output (immediate)."""
        if cls._instance:
            cls._instance.add_output(line)
    
    @classmethod
    def mark_complete(cls, key: str, status: str = None):
        """Mark a box as complete."""
        if cls._instance:
            cls._instance.mark_complete(key, status)
    
    @classmethod
    def flush_buffers(cls):
        """Flush all buffers."""
        if cls._instance:
            cls._instance.flush_buffers()
    
    @classmethod
    def start(cls):
        """Start layout."""
        if cls._instance:
            cls._instance.start()
    
    @classmethod
    def close(cls):
        """Close layout."""
        if cls._instance:
            cls._instance.close()
            cls._instance = None

