"""Singleton layout wrapper for parallel agent displays.

This module provides a class-level singleton wrapper around BaseThinkingLayout,
enabling process-wide shared display state for parallel agent execution.

When to use:
    - Parallel writer agents (dual_writers.py)
    - Judge panels with multiple concurrent judges
    - Any scenario where multiple callers need shared display state

Why a singleton:
    Rich Live displays don't support multiple concurrent instances. DynamicLayout
    ensures only one Live display exists, with proper cleanup between uses.

Related modules:
    - base_layout.py: Core implementation (wrapped, not inherited)
    - single_layout.py: For single-agent sequential runs

Example:
    DynamicLayout.initialize({"writer_a": "Writer A", "writer_b": "Writer B"})
    DynamicLayout.start()
    DynamicLayout.add_thinking("writer_a", "Working...")
    DynamicLayout.mark_complete("writer_a", "Done")
    DynamicLayout.close()
"""

from .base_layout import BaseThinkingLayout
from typing import Dict, Optional


class DynamicLayout:
    """Process-wide singleton for parallel agent thinking displays.
    
    Wraps BaseThinkingLayout with class-level state to enable shared display
    across multiple callers (threads/coroutines) during parallel execution.
    
    All methods are class methods operating on shared state. Call initialize()
    before use, and close() when done to clean up resources.
    
    Note:
        Previous instances are automatically closed when initialize() is called,
        preventing multiple Rich Live displays from conflicting.
    
    Example:
        DynamicLayout.initialize({"judge_1": "Judge 1", "judge_2": "Judge 2"})
        DynamicLayout.add_thinking("judge_1", "Reviewing code...")
        DynamicLayout.close()
    """
    
    _instance: Optional[BaseThinkingLayout] = None
    
    @classmethod
    def initialize(cls, boxes: Dict[str, str], lines_per_box: int = 2, task_name: str = None):
        """Initialize layout with specific boxes (closes previous instance if exists).
        
        Args:
            boxes: Dict of {key: label} e.g. {"judge_1": "Judge Sonnet", "writer_a": "Writer A"}
            lines_per_box: Number of lines per thinking box
            task_name: Optional task name to display in sticky header
        """
        # Close previous instance to avoid multiple Live() displays
        if cls._instance:
            cls._instance.close()
        
        cls._instance = BaseThinkingLayout(boxes, lines_per_box, task_name=task_name)
    
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

