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
        self.output_lines = deque(maxlen=1000)
        self.output_buffer = ""  # Buffer for assistant deltas in main output
        self.started = False
        self.live = None
        self.layout = None
        self.console = Console()
        self.lock = Lock()
        self.last_update_time = 0
        self.min_update_interval = 0.1
        self.completed = {box_id: False for box_id in boxes}
        self.completion_status = {box_id: None for box_id in boxes}
        self.last_activity = {box_id: 0 for box_id in boxes}
    
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
                self.layout[box_id].update(self._create_panel(title, [], box_id))
            self.layout["output"].update("")
            
            self.live = Live(
                self.layout, 
                console=self.console, 
                refresh_per_second=2,
                screen=False,
                transient=True
            )
            self.live.start()
            self.started = True
    
    def add_thinking(self, box_id: str, text: str) -> None:
        """Add thinking text to a specific box."""
        with self.lock:
            if not self.started:
                self.start()
            
            if box_id not in self.current_lines:
                return
            
            self.last_activity[box_id] = time.time()
            
            self.current_lines[box_id] += text
            
            if text.endswith(('.', '!', '?', '\n')) and self.current_lines[box_id].strip():
                line = self.current_lines[box_id].strip()
                if len(line) > 94:
                    line = line[:91] + "..."
                self.buffers[box_id].append(line)
                self.current_lines[box_id] = ""
                self._update()
    
    def mark_complete(self, box_id: str, status: Optional[str] = None) -> None:
        """Mark a box as complete with optional status message.
        
        Args:
            box_id: Box to mark complete
            status: Optional status to display (e.g., "APPROVED", "Winner", "3 commits")
        """
        with self.lock:
            if box_id in self.completed:
                self.completed[box_id] = True
                self.completion_status[box_id] = status
                self._update()
    
    def add_output(self, line: str, buffered: bool = False) -> None:
        """Add output line.
        
        Args:
            line: Formatted output line
            buffered: If True, buffer until punctuation (for assistant deltas)
                     If False, show immediately (for tool calls, errors)
        """
        with self.lock:
            if not self.started:
                self.start()
            
            if buffered:
                self.output_buffer += line
                if line.endswith(('.', '!', '?', '\n')) and self.output_buffer.strip():
                    self.output_lines.append(self.output_buffer.strip())
                    self.output_buffer = ""
                    self._update()
            else:
                self.output_lines.append(line)
                self._update()
    
    def flush_buffers(self) -> None:
        """Flush any remaining buffered content."""
        with self.lock:
            # Flush output buffer
            if self.output_buffer.strip():
                self.output_lines.append(self.output_buffer.strip())
                self.output_buffer = ""
            
            # Flush thinking buffers
            for box_id, current_text in self.current_lines.items():
                if current_text.strip():
                    line = current_text.strip()
                    if len(line) > 94:
                        line = line[:91] + "..."
                    self.buffers[box_id].append(line)
                    self.current_lines[box_id] = ""
            
            self._update()
    
    def _create_panel(self, title: str, lines: list, box_id: str) -> Panel:
        """Create a panel."""
        text = Text()
        
        if self.completed.get(box_id, False):
            status = self.completion_status.get(box_id)
            if status:
                text.append("✅ ", style="green bold")
                text.append(f"{status}\n", style="green")
            else:
                text.append("✅ Completed\n", style="green bold")
            
            for _ in range(self.lines_per_box - 1):
                text.append("\n")
        else:
            # Show last N lines only (auto-scroll to bottom)
            display_lines = lines[-self.lines_per_box:] if len(lines) > self.lines_per_box else lines
            for line in display_lines:
                text.append(line + "\n", style="dim")
            
            # Pad to fill box height
            current_height = len(display_lines)
            for _ in range(self.lines_per_box - current_height):
                text.append("\n")
        
        icon = "💭" if "Writer" in title or "Prompter" in title else "⚖️ "
        
        if self.completed.get(box_id, False):
            border_style = "green"
            title_text = f"[green]{icon} {title} ✓[/green]"
        else:
            border_style = "dim"
            title_text = f"[dim]{icon} {title}[/dim]"
        
        return Panel(
            text,
            title=title_text,
            border_style=border_style,
            padding=(0, 1),
            height=self.lines_per_box + 2
        )
    
    def _update(self) -> None:
        """Update all regions."""
        if not self.live or not self.layout:
            return
        
        current_time = time.time()
        if current_time - self.last_update_time < self.min_update_interval:
            return
        
        self.last_update_time = current_time
        
        for box_id, title in self.boxes.items():
            visible = list(self.buffers[box_id])[-self.lines_per_box:]
            self.layout[box_id].update(self._create_panel(title, visible, box_id))
        
        try:
            term_height = os.get_terminal_size().lines
            thinking_boxes_height = len(self.boxes) * (self.lines_per_box + 2) + 2
            available_lines = max(20, term_height - thinking_boxes_height - 5)
        except:
            available_lines = 30
        
        recent_output = list(self.output_lines)[-available_lines:]
        output_text = "\n".join(recent_output)
        
        from rich.text import Text
        text = Text.from_markup(output_text)
        
        self.layout["output"].update(text)
    
    def close(self) -> None:
        """Stop the live display and print all output to scrollback."""
        with self.lock:
            if self.started and self.live:
                self.live.stop()
                self.started = False
                
                if self.output_lines:
                    from rich.text import Text
                    for line in self.output_lines:
                        self.console.print(Text.from_markup(line))

