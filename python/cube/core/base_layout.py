"""Base layout class for thinking displays."""

import os
import time
from collections import deque
from threading import Lock
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.console import Console
from rich.text import Text
from typing import Dict, Optional


class BaseThinkingLayout:
    """Thinking boxes at top + scrolling log output below."""
    
    def __init__(self, boxes: Dict[str, str], lines_per_box: int = 3):
        self.boxes = boxes
        self.lines_per_box = lines_per_box
        self.thinking_buffers = {box_id: deque(maxlen=lines_per_box) for box_id in boxes}
        self.thinking_current = {box_id: "" for box_id in boxes}
        self.output_lines = deque(maxlen=500)
        self.assistant_buf = {}
        self.assistant_meta = {}
        self.completed = {box_id: False for box_id in boxes}
        self.completion_status = {box_id: None for box_id in boxes}
        
        self.console = Console()
        self.live = None
        self.layout = None
        self.started = False
        self.lock = Lock()
    
    def _term_width(self) -> int:
        try:
            return os.get_terminal_size().columns
        except Exception:
            return 100
    
    def _term_height(self) -> int:
        try:
            return os.get_terminal_size().lines
        except Exception:
            return 40
    
    def _visual_len(self, text: str) -> int:
        if '[' not in text:
            return len(text)
        from rich.text import Text as RichText
        return len(RichText.from_markup(text).plain)
    
    def _truncate(self, text: str, max_len: int) -> str:
        visual_len = self._visual_len(text)
        if visual_len <= max_len:
            return text
        
        if '[' not in text:
            return text[:max_len - 1] + "…"
        
        from rich.text import Text as RichText
        plain = RichText.from_markup(text).plain
        return plain[:max_len - 1] + "…"
    
    def start(self):
        with self.lock:
            if self.started:
                return
            
            self.layout = Layout()
            regions = [Layout(name=box_id, size=self.lines_per_box + 2) for box_id in self.boxes]
            regions.append(Layout(name="output", ratio=1))
            self.layout.split_column(*regions)
            
            for box_id, title in self.boxes.items():
                self.layout[box_id].update(self._make_panel(box_id, title))
            self.layout["output"].update("")
            
            self.live = Live(self.layout, console=self.console, refresh_per_second=4, transient=True)
            self.live.start()
            self.started = True
    
    def _make_panel(self, box_id: str, title: str) -> Panel:
        text = Text()
        
        if self.completed.get(box_id):
            status = self.completion_status.get(box_id) or "Completed"
            text.append(f"✅ {status}\n", style="green")
            for _ in range(self.lines_per_box - 1):
                text.append("\n")
            border = "green"
            icon = "💭" if "Writer" in title or "Prompter" in title else "⚖️"
            title_fmt = f"[green]{icon} {title} ✓[/green]"
        else:
            lines = list(self.thinking_buffers[box_id])[-self.lines_per_box:]
            for line in lines:
                text.append(line + "\n", style="dim")
            for _ in range(self.lines_per_box - len(lines)):
                text.append("\n")
            border = "dim"
            icon = "💭" if "Writer" in title or "Prompter" in title else "⚖️"
            title_fmt = f"[dim]{icon} {title}[/dim]"
        
        return Panel(text, title=title_fmt, border_style=border, padding=(0, 1), height=self.lines_per_box + 2)
    
    def _refresh(self):
        if not self.live or not self.layout:
            return
        
        for box_id, title in self.boxes.items():
            self.layout[box_id].update(self._make_panel(box_id, title))
        
        # Calculate available lines for output
        boxes_height = len(self.boxes) * (self.lines_per_box + 2)
        available = max(5, self._term_height() - boxes_height - 3)
        
        # Take last N lines, truncate each to terminal width
        width = self._term_width() - 2
        recent = list(self.output_lines)[-available:]
        lines = [self._truncate(line, width) for line in recent]
        
        self.layout["output"].update(Text.from_markup("\n".join(lines)))
    
    def add_thinking(self, box_id: str, text: str) -> None:
        with self.lock:
            if not self.started:
                self.start()
            if box_id not in self.thinking_current:
                return
            
            self.thinking_current[box_id] += text
            buf = self.thinking_current[box_id]
            width = self._term_width() - 4  # Just borders
            
            # Handle embedded newlines - flush each complete line
            while '\n' in buf:
                line, buf = buf.split('\n', 1)
                if line.strip():
                    self.thinking_buffers[box_id].append(self._truncate(line.strip(), width))
                self.thinking_current[box_id] = buf
            
            # Flush remaining buffer on sentence end or length limit
            ends = buf.rstrip().endswith(('.', '!', '?', ':'))
            if (len(buf) > 40 and ends) or len(buf) > 150:
                self.thinking_buffers[box_id].append(self._truncate(buf.strip(), width))
                self.thinking_current[box_id] = ""
            
            self._refresh()
    
    def add_assistant_message(self, key: str, content: str, label: str, color: str) -> None:
        with self.lock:
            if not self.started:
                self.start()
            if not content:
                return
            
            if key not in self.assistant_buf:
                self.assistant_buf[key] = ""
            self.assistant_meta[key] = (label, color)
            self.assistant_buf[key] += content
            
            buf = self.assistant_buf[key]
            width = self._term_width() - len(label) - 6  # Label + emoji + borders
            
            # Handle embedded newlines - flush each complete line
            while '\n' in buf:
                line, buf = buf.split('\n', 1)
                if line.strip():
                    truncated = self._truncate(line.strip(), width)
                    self.output_lines.append(f"[{color}]{label}[/{color}] 💭 {truncated}")
                self.assistant_buf[key] = buf
            
            # Flush remaining buffer on sentence end or length limit
            ends = buf.rstrip().endswith(('.', '!', '?', ':'))
            if (len(buf) > 50 and ends) or len(buf) > 300:
                truncated = self._truncate(buf.strip(), width)
                self.output_lines.append(f"[{color}]{label}[/{color}] 💭 {truncated}")
                self.assistant_buf[key] = ""
            
            self._refresh()
    
    def add_output(self, line: str) -> None:
        with self.lock:
            if not self.started:
                self.start()
            self.output_lines.append(line)
            self._refresh()
    
    def mark_complete(self, box_id: str, status: Optional[str] = None) -> None:
        with self.lock:
            if box_id in self.completed:
                self.completed[box_id] = True
                self.completion_status[box_id] = status
                self._refresh()
    
    def flush_buffers(self) -> None:
        with self.lock:
            for key, buf in list(self.assistant_buf.items()):
                if buf.strip():
                    label, color = self.assistant_meta.get(key, (key, "white"))
                    width = self._term_width() - len(label) - 6
                    truncated = self._truncate(buf.strip(), width)
                    self.output_lines.append(f"[{color}]{label}[/{color}] 💭 {truncated}")
                    self.assistant_buf[key] = ""
            
            for box_id, buf in self.thinking_current.items():
                if buf.strip():
                    width = self._term_width() - 4
                    self.thinking_buffers[box_id].append(self._truncate(buf.strip(), width))
                    self.thinking_current[box_id] = ""
            self._refresh()
    
    def close(self) -> None:
        with self.lock:
            if self.started and self.live:
                self.live.stop()
                self.started = False
                for line in self.output_lines:
                    self.console.print(Text.from_markup(line))
