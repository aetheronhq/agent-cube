"""Triple judge layout for panel/peer-review commands."""

from .base_layout import BaseThinkingLayout

class TripleJudgeLayout:
    """Fixed layout with 3 judge thinking boxes + output region."""
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            boxes = {
                "judge_1": "Judge 1",
                "judge_2": "Judge 2",
                "judge_3": "Judge 3"
            }
            cls._instance = BaseThinkingLayout(boxes, lines_per_box=2)
        return cls._instance
    
    @classmethod
    def add_thinking(cls, judge_num: int, text: str):
        """Add thinking from a specific judge."""
        box_id = f"judge_{judge_num}"
        cls.get_instance().add_thinking(box_id, text)
    
    @classmethod
    def mark_complete(cls, judge_num: int, status: str = None):
        """Mark a judge as complete with optional status."""
        box_id = f"judge_{judge_num}"
        cls.get_instance().mark_complete(box_id, status)
    
    @classmethod
    def add_output(cls, line: str):
        """Add output line."""
        cls.get_instance().add_output(line)
    
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


