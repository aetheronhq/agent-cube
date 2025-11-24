"""Dynamic layout that adapts to any number of boxes."""

from .base_layout import BaseThinkingLayout
from typing import Dict

class DynamicLayout:
    """Universal layout for any number of thinking boxes (instance-based, not singleton)."""
    
    def __init__(self, boxes: Dict[str, str], lines_per_box: int = 2):
        """Initialize layout with specific boxes.
        
        Args:
            boxes: Dict of {key: label} e.g. {"judge_1": "Judge Sonnet", "writer_a": "Writer A"}
            lines_per_box: Number of lines per thinking box
        """
        self.layout = BaseThinkingLayout(boxes, lines_per_box)
    
    def add_thinking(self, key: str, text: str):
        """Add thinking to a box (buffers until punctuation)."""
        self.layout.add_thinking(key, text)
    
    def add_assistant_message(self, key: str, content: str, label: str, color: str):
        """Add assistant message to main output (buffers per agent until punctuation)."""
        self.layout.add_assistant_message(key, content, label, color)
    
    def add_output(self, line: str, buffered: bool = False):
        """Add to main output (immediate)."""
        self.layout.add_output(line, buffered)
    
    def mark_complete(self, key: str, status: str = None):
        """Mark a box as complete."""
        self.layout.mark_complete(key, status)
    
    def flush_buffers(self):
        """Flush all buffers."""
        self.layout.flush_buffers()
    
    def start(self):
        """Start layout."""
        self.layout.start()
    
    def close(self):
        """Close layout."""
        self.layout.close()

