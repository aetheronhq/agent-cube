"""Single agent layout for feedback/resume commands."""

from collections import deque
from threading import Lock
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.console import Console
from rich.text import Text

class SingleAgentLayout:
    """Fixed layout with one thinking box + output region."""
    
    def __init__(self, title: str = "Agent"):
        self.title = title
        self.lines = 3
        self.buffer = deque(maxlen=self.lines)
        self.current_line = ""
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
            self.layout.split_column(
                Layout(name="thinking", size=5),
                Layout(name="output", ratio=1)
            )
            
            self.layout["thinking"].update(self._create_panel([]))
            self.layout["output"].update("")
            
            self.live = Live(self.layout, console=self.console, refresh_per_second=4, screen=False)
            self.live.start()
            self.started = True
    
    def add_thinking(self, text: str) -> None:
        """Add thinking text."""
        with self.lock:
            if not self.started:
                self.start()
            
            self.current_line += text
            if text.endswith(('.', '!', '?', '\n')) and self.current_line.strip():
                line = self.current_line.strip()
                if len(line) > 94:
                    line = line[:91] + "..."
                self.buffer.append(line)
                self.current_line = ""
                self._update()
    
    def add_output(self, line: str) -> None:
        """Add output line."""
        with self.lock:
            if not self.started:
                self.start()
            
            self.output_lines.append(line)
            self._update()
    
    def _create_panel(self, lines: list) -> Panel:
        """Create panel."""
        text = Text()
        for line in lines:
            text.append(line + "\n", style="dim")
        
        while len(text.plain.split('\n')) < self.lines:
            text.append("\n")
        
        return Panel(
            text,
            title=f"[dim]💭 {self.title}[/dim]",
            border_style="dim",
            padding=(0, 1),
            height=self.lines + 2
        )
    
    def _update(self) -> None:
        """Update regions."""
        if not self.live or not self.layout:
            return
        
        visible = list(self.buffer)[-self.lines:]
        self.layout["thinking"].update(self._create_panel(visible))
        
        output_text = "\n".join(list(self.output_lines)[-20:])
        self.layout["output"].update(output_text)
    
    def close(self) -> None:
        """Stop display."""
        with self.lock:
            if self.started and self.live:
                self.live.stop()
                self.started = False

