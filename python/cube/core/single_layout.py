"""Single-agent layout for sequential agent runs.

This module provides a simplified layout for scenarios with only one agent,
removing the need to manage box IDs.

When to use:
    - Single agent execution (run.py, feedback.py, resume.py)
    - Prompter agent display
    - Any sequential single-agent workflow

Related modules:
    - base_layout.py: Parent class with full functionality
    - dynamic_layout.py: For parallel multi-agent displays

Example:
    layout = SingleAgentLayout(title="Prompter")
    layout.start()
    layout.add_thinking("Generating prompt...")
    layout.close()
"""

from threading import RLock
from typing import Dict, Optional

from .base_layout import BaseThinkingLayout


class SingleAgentLayout(BaseThinkingLayout):
    """Simplified layout for single-agent displays.
    
    A convenience subclass that pre-configures a single thinking box,
    removing the need to specify box_id in add_thinking() calls.
    
    Args:
        title: Display title for the thinking box (default: "Agent")
    
    Example:
        layout = SingleAgentLayout("My Agent")
        layout.start()
        layout.add_thinking("Processing request...")
        layout.mark_complete("agent", "Complete")
        layout.close()
    """
    
    _instance: Optional['SingleAgentLayout'] = None
    _lock = RLock()

    @classmethod
    def initialize(cls, title: str = "Agent"):
        with cls._lock:
            if cls._instance:
                cls._instance.close()
            cls._instance = cls({"agent": title}, lines_per_box=3)
        return cls._instance

    def __init__(self, boxes: Dict[str, str], lines_per_box: int = 3):
        super().__init__(boxes, lines_per_box)
    
    @classmethod
    def add_thinking(cls, text: str) -> None:
        """Add thinking text."""
        with cls._lock:
            if cls._instance:
                # Base class expects box_id, which is always 'agent' here
                cls._instance.add_thinking("agent", text)

    @classmethod
    def update_thinking(cls, text: str) -> None:
        """Alias for add_thinking for consistency."""
        cls.add_thinking(text)

    @classmethod
    def add_assistant_message(cls, content: str, label: str, color: str) -> None:
        with cls._lock:
            if cls._instance:
                # Base class expects key, which is always 'agent' here
                cls._instance.add_assistant_message("agent", content, label, color)

    @classmethod
    def add_output(cls, line: str) -> None:
        with cls._lock:
            if cls._instance:
                cls._instance.add_output(line)
    
    @classmethod
    def mark_complete(cls, status: Optional[str] = None) -> None:
        with cls._lock:
            if cls._instance:
                cls._instance.mark_complete("agent", status)

    @classmethod
    def close(cls) -> None:
        with cls._lock:
            if cls._instance:
                # Call parent class's close method to avoid recursion
                BaseThinkingLayout.close(cls._instance)
                cls._instance = None
    
    @classmethod
    def start(cls) -> None:
        with cls._lock:
            if cls._instance:
                # Call parent class's start method to avoid recursion
                BaseThinkingLayout.start(cls._instance)