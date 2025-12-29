"""Single agent layout for feedback/resume commands."""

from threading import Lock
from typing import Dict, Optional

from .base_layout import BaseThinkingLayout

class SingleAgentLayout(BaseThinkingLayout):
    """Fixed layout with one thinking box + output region."""
    
    _instance: Optional['SingleAgentLayout'] = None
    _lock = Lock()

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
                cls._instance.close()
                cls._instance = None
    
    @classmethod
    def start(cls) -> None:
        with cls._lock:
            if cls._instance:
                cls._instance.start()
