"""Dual writer layout using Rich Layout for fixed regions."""

from collections import deque
from threading import Lock
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.console import Console
from rich.text import Text

class DualWriterLayout:
    """Fixed layout with Writer A/B thinking boxes + output region."""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self):
        if self.initialized:
            return
        
        self.lines_per_box = 3
        self.buffer_a = deque(maxlen=self.lines_per_box)
        self.buffer_b = deque(maxlen=self.lines_per_box)
        self.current_a = ""
        self.current_b = ""
        self.output_lines = deque(maxlen=50)
        self.started = False
        self.live = None
        self.layout = None
        self.console = Console()
        self.initialized = True
    
    def start(self):
        """Start the live layout."""
        with self._lock:
            if self.started:
                return
            
            self.layout = Layout()
            self.layout.split_column(
                Layout(name="writer_a", size=5),
                Layout(name="writer_b", size=5),
                Layout(name="output", ratio=1)
            )
            
            self.layout["writer_a"].update(self._create_panel("Writer A", []))
            self.layout["writer_b"].update(self._create_panel("Writer B", []))
            self.layout["output"].update("")
            
            self.live = Live(self.layout, console=self.console, refresh_per_second=4, screen=False)
            self.live.start()
            self.started = True
    
    def add_thinking(self, writer: str, text: str) -> None:
        """Add thinking text from Writer A or B."""
        with self._lock:
            if not self.started:
                self.start()
            
            if writer == "A":
                self.current_a += text
                if text.endswith(('.', '!', '?', '\n')) and self.current_a.strip():
                    line = self.current_a.strip()
                    if len(line) > 94:
                        line = line[:91] + "..."
                    self.buffer_a.append(line)
                    self.current_a = ""
                    self._update()
            else:
                self.current_b += text
                if text.endswith(('.', '!', '?', '\n')) and self.current_b.strip():
                    line = self.current_b.strip()
                    if len(line) > 94:
                        line = line[:91] + "..."
                    self.buffer_b.append(line)
                    self.current_b = ""
                    self._update()
    
    def add_output(self, line: str) -> None:
        """Add output line below the thinking boxes."""
        with self._lock:
            if not self.started:
                self.start()
            
            self.output_lines.append(line)
            self._update()
    
    def _create_panel(self, title: str, lines: list) -> Panel:
        """Create a panel for a writer."""
        text = Text()
        for line in lines:
            text.append(line + "\n", style="dim")
        
        while len(text.plain) < self.lines_per_box:
            text.append("\n")
        
        return Panel(
            text,
            title=f"[dim]💭 {title}[/dim]",
            border_style="dim",
            padding=(0, 1),
            height=self.lines_per_box + 2
        )
    
    def _update(self) -> None:
        """Update all regions."""
        if not self.live or not self.layout:
            return
        
        visible_a = list(self.buffer_a)[-self.lines_per_box:]
        visible_b = list(self.buffer_b)[-self.lines_per_box:]
        
        self.layout["writer_a"].update(self._create_panel("Writer A", visible_a))
        self.layout["writer_b"].update(self._create_panel("Writer B", visible_b))
        
        output_text = "\n".join(list(self.output_lines)[-20:])
        self.layout["output"].update(output_text)
    
    def close(self) -> None:
        """Stop the live display."""
        with self._lock:
            if self.started and self.live:
                self.live.stop()
                self.started = False
    
    @classmethod
    def reset(cls):
        """Reset singleton."""
        if cls._instance and cls._instance.live:
            cls._instance.close()
        cls._instance = None

def get_dual_layout() -> DualWriterLayout:
    """Get the global dual layout instance."""
    return DualWriterLayout()

