"""Triple judge layout for panel/peer-review commands."""

from collections import deque
from threading import Lock
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.console import Console
from rich.text import Text

class TripleJudgeLayout:
    """Fixed layout with 3 judge thinking boxes + output region."""
    
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
        
        self.lines_per_box = 2
        self.buffer_1 = deque(maxlen=self.lines_per_box)
        self.buffer_2 = deque(maxlen=self.lines_per_box)
        self.buffer_3 = deque(maxlen=self.lines_per_box)
        self.current_1 = ""
        self.current_2 = ""
        self.current_3 = ""
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
                Layout(name="judge1", size=4),
                Layout(name="judge2", size=4),
                Layout(name="judge3", size=4),
                Layout(name="output", ratio=1)
            )
            
            self.layout["judge1"].update(self._create_panel("Judge 1", []))
            self.layout["judge2"].update(self._create_panel("Judge 2", []))
            self.layout["judge3"].update(self._create_panel("Judge 3", []))
            self.layout["output"].update("")
            
            self.live = Live(self.layout, console=self.console, refresh_per_second=4, screen=False)
            self.live.start()
            self.started = True
    
    def add_thinking(self, judge_num: int, text: str) -> None:
        """Add thinking text from a judge."""
        with self._lock:
            if not self.started:
                self.start()
            
            buffer = [self.buffer_1, self.buffer_2, self.buffer_3][judge_num - 1]
            current = [self.current_1, self.current_2, self.current_3][judge_num - 1]
            
            if judge_num == 1:
                self.current_1 += text
                current = self.current_1
            elif judge_num == 2:
                self.current_2 += text
                current = self.current_2
            else:
                self.current_3 += text
                current = self.current_3
            
            if text.endswith(('.', '!', '?', '\n')) and current.strip():
                line = current.strip()
                if len(line) > 94:
                    line = line[:91] + "..."
                buffer.append(line)
                
                if judge_num == 1:
                    self.current_1 = ""
                elif judge_num == 2:
                    self.current_2 = ""
                else:
                    self.current_3 = ""
                
                self._update()
    
    def add_output(self, line: str) -> None:
        """Add output line."""
        with self._lock:
            if not self.started:
                self.start()
            
            self.output_lines.append(line)
            self._update()
    
    def _create_panel(self, title: str, lines: list) -> Panel:
        """Create panel for a judge."""
        text = Text()
        for line in lines:
            text.append(line + "\n", style="dim")
        
        while len(text.plain.split('\n')) < self.lines_per_box:
            text.append("\n")
        
        return Panel(
            text,
            title=f"[dim]⚖️  {title}[/dim]",
            border_style="dim",
            padding=(0, 1),
            height=self.lines_per_box + 2
        )
    
    def _update(self) -> None:
        """Update all regions."""
        if not self.live or not self.layout:
            return
        
        visible_1 = list(self.buffer_1)[-self.lines_per_box:]
        visible_2 = list(self.buffer_2)[-self.lines_per_box:]
        visible_3 = list(self.buffer_3)[-self.lines_per_box:]
        
        self.layout["judge1"].update(self._create_panel("Judge 1", visible_1))
        self.layout["judge2"].update(self._create_panel("Judge 2", visible_2))
        self.layout["judge3"].update(self._create_panel("Judge 3", visible_3))
        
        output_text = "\n".join(list(self.output_lines)[-20:])
        self.layout["output"].update(output_text)
    
    def close(self) -> None:
        """Stop display."""
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

def get_triple_layout() -> TripleJudgeLayout:
    """Get the global triple judge layout instance."""
    return TripleJudgeLayout()

