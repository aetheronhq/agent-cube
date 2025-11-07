"""Teleprompter-style scrolling display for thinking stream."""

import sys
from collections import deque
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

class ThinkingTeleprompter:
    """Display thinking stream in a scrolling window using Rich."""
    
    def __init__(self, lines: int = 3, width: int = 80):
        self.lines = lines
        self.width = width
        self.buffer = deque(maxlen=lines * 2)
        self.current_line = ""
        self.started = False
        self.live = None
        self.console = Console()
    
    def add_token(self, text: str) -> None:
        """Add a thinking token and update display."""
        if not self.started:
            self.started = True
            self.live = Live(self._create_panel(), console=self.console, refresh_per_second=10)
            self.live.start()
        
        self.current_line += text
        
        should_flush = text.endswith(('.', '!', '?', '\n'))
        
        if should_flush and self.current_line.strip():
            wrapped = self._wrap_line(self.current_line.strip())
            for line in wrapped:
                self.buffer.append(line)
            
            if self.live:
                self.live.update(self._create_panel())
            
            self.current_line = ""
    
    def _wrap_line(self, text: str) -> list:
        """Wrap text to fit width, breaking on words."""
        if len(text) <= self.width - 4:
            return [text]
        
        words = text.split()
        lines = []
        current = []
        current_len = 0
        
        for word in words:
            word_len = len(word) + (1 if current else 0)
            if current_len + word_len > self.width - 4:
                if current:
                    lines.append(' '.join(current))
                    current = [word]
                    current_len = len(word)
                else:
                    lines.append(word[:self.width - 7] + "...")
                    current_len = 0
            else:
                current.append(word)
                current_len += word_len
        
        if current:
            lines.append(' '.join(current))
        
        return lines
    
    def _create_panel(self) -> Panel:
        """Create Rich panel with current buffer."""
        visible_lines = list(self.buffer)[-self.lines:]
        
        text = Text()
        for line in visible_lines:
            if len(line) > self.width - 4:
                line = line[:self.width - 7] + "..."
            text.append(line + "\n", style="dim")
        
        return Panel(
            text,
            title="[dim]💭 Thinking[/dim]",
            border_style="dim",
            padding=(0, 1)
        )
    
    def close(self) -> None:
        """Close the thinking display."""
        if self.started and self.live:
            if self.current_line.strip():
                self.buffer.append(self.current_line.strip())
                self.live.update(self._create_panel())
            self.live.stop()
            self.started = False

