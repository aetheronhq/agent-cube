"""Single agent layout for feedback/resume commands."""

from .base_layout import BaseThinkingLayout

class SingleAgentLayout(BaseThinkingLayout):
    """Fixed layout with one thinking box + output region."""
    
    def __init__(self, title: str = "Agent"):
        boxes = {"agent": title}
        super().__init__(boxes, lines_per_box=3)
    
    def add_thinking(self, text: str) -> None:
        """Add thinking text."""
        super().add_thinking("agent", text)

