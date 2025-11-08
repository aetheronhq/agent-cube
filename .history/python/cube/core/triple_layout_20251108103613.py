"""Triple judge layout for panel/peer-review commands."""

from .base_layout import BaseThinkingLayout

class TripleJudgeLayout(BaseThinkingLayout):
    """Fixed layout with 3 judge thinking boxes + output region."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            boxes = {
                "judge_1": "Judge 1",
                "judge_2": "Judge 2",
                "judge_3": "Judge 3"
            }
            BaseThinkingLayout.__init__(cls._instance, boxes, lines_per_box=2)
        return cls._instance
    
    def add_thinking(self, judge_num: int, text: str) -> None:
        """Add thinking from a specific judge."""
        box_id = f"judge_{judge_num}"
        super().add_thinking(box_id, text)
    
    @classmethod
    def reset(cls):
        """Reset singleton."""
        if cls._instance:
            cls._instance.close()
        cls._instance = None

def get_triple_layout() -> TripleJudgeLayout:
    """Get the global triple judge layout instance."""
    return TripleJudgeLayout()

