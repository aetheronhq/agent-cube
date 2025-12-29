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
    
    def __init__(self, title: str = "Agent"):
        boxes = {"agent": title}
        super().__init__(boxes, lines_per_box=3)
    
    def add_thinking(self, text: str, box_id: str = "agent") -> None:  # type: ignore[override]
        super().add_thinking(box_id, text)

