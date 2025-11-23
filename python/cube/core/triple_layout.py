"""Triple judge layout for panel/peer-review commands."""

from .base_layout import BaseThinkingLayout

class TripleJudgeLayout:
    """Dynamic layout for judge thinking boxes + output region."""
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            from ..core.user_config import get_judge_configs
            judges = get_judge_configs()
            boxes = {j.key: j.label for j in judges}
            cls._instance = BaseThinkingLayout(boxes, lines_per_box=2)
        return cls._instance
    
    @classmethod
    def add_thinking(cls, judge_key: str, text: str):
        """Add thinking from a specific judge."""
        cls.get_instance().add_thinking(judge_key, text)
    
    @classmethod
    def add_assistant_message(cls, key: str, content: str, label: str, color: str):
        """Add assistant message (buffered per agent)."""
        cls.get_instance().add_assistant_message(key, content, label, color)
    
    @classmethod
    def mark_complete(cls, judge_key: str, status: str = None):
        """Mark a judge as complete with optional status."""
        cls.get_instance().mark_complete(judge_key, status)
    
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

def get_triple_layout():
    """Get the triple layout."""
    return TripleJudgeLayout


