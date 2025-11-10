"""Base layout class for thinking displays."""

from collections import deque
from threading import Lock
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.console import Console
from rich.text import Text
from typing import Dict

class BaseThinkingLayout:
    """Base class for thinking box layouts."""
    
    def __init__(self, boxes: Dict[str, str], lines_per_box: int = 3):
        """
        boxes: dict of {box_id: title} e.g. {"writer_a": "Writer A", "judge_1": "Judge 1"}
        lines_per_box: number of lines per box
        """
        self.boxes = boxes
        self.lines_per_box = lines_per_box
        self.width = 100
        self.buffers = {box_id: deque(maxlen=lines_per_box) for box_id in boxes}
        self.current_lines = {box_id: "" for box_id in boxes}
        self.output_lines = deque(maxlen=50)
        self.started = False
        self.live = None
        self.layout = None
        self.console = Console()
        self.lock = Lock()
    
    def start(self):
        """Start the live layout."""
        with self.lock:
            if self.started:
                return
            
            self.layout = Layout()
            
            regions = []
            for box_id in self.boxes:
                regions.append(Layout(name=box_id, size=self.lines_per_box + 2))
            regions.append(Layout(name="output", ratio=1))
            
            self.layout.split_column(*regions)
            
            for box_id, title in self.boxes.items():
                self.layout[box_id].update(self._create_panel(title, []))
            self.layout["output"].update("")
            
            self.live = Live(self.layout, console=self.console, refresh_per_second=4, screen=False)
            self.live.start()
            self.started = True
    
    def add_thinking(self, box_id: str, text: str) -> None:
        """Add thinking text to a specific box."""
        with self.lock:
            if not self.started:
                self.start()
            
            if box_id not in self.current_lines:
                return
            
            self.current_lines[box_id] += text
            
            if text.endswith(('.', '!', '?', '\n')) and self.current_lines[box_id].strip():
                line = self.current_lines[box_id].strip()
                if len(line) > 94:
                    line = line[:91] + "..."
                self.buffers[box_id].append(line)
                self.current_lines[box_id] = ""
                self._update()
    
    def add_output(self, line: str) -> None:
        """Add output line."""
        with self.lock:
            if not self.started:
                self.start()
            
            self.output_lines.append(line)
            self._update()
    
    def _create_panel(self, title: str, lines: list) -> Panel:
        """Create a panel."""
        text = Text()
        for line in lines:
            text.append(line + "\n", style="dim")
        
        while len(text.plain.split('\n')) < self.lines_per_box:
            text.append("\n")
        
        icon = "💭" if "Writer" in title or "Prompter" in title else "⚖️ "
        
        return Panel(
            text,
            title=f"[dim]{icon} {title}[/dim]",
            border_style="dim",
            padding=(0, 1),
            height=self.lines_per_box + 2
        )
    
    def _update(self) -> None:
        """Update all regions."""
        if not self.live or not self.layout:
            return
        
        for box_id, title in self.boxes.items():
            visible = list(self.buffers[box_id])[-self.lines_per_box:]
            self.layout[box_id].update(self._create_panel(title, visible))
        
        import os
        try:
            term_height = os.get_terminal_size().lines
            thinking_boxes_height = len(self.boxes) * (self.lines_per_box + 2) + 2
            available_lines = max(10, term_height - thinking_boxes_height - 5)
        except:
            available_lines = 20
        
        recent_output = list(self.output_lines)[-available_lines:]
        output_text = "\n".join(recent_output)
        
        from rich.text import Text
        text = Text.from_markup(output_text)
        
        self.layout["output"].update(text)
    
    def close(self) -> None:
        """Stop the live display."""
        with self.lock:
            if self.started and self.live:
                self.live.stop()
                self.started = False

