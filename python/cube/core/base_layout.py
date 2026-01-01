"""Base layout class for Rich terminal displays with thinking boxes.

This module provides the core implementation for terminal UI layouts that show
real-time "thinking" indicators for LLM agents alongside scrolling output.

When to use:
    - Inherit from BaseThinkingLayout for custom specialized layouts
    - Instantiate directly when you need full control over box configuration

Related modules:
    - dynamic_layout.py: Singleton wrapper for process-wide shared layouts
    - single_layout.py: Convenience subclass for single-agent displays

Example:
    boxes = {"<writer_key>": "<Writer Label>", "judge_1": "Judge 1"}
    layout = BaseThinkingLayout(boxes, lines_per_box=3)
    layout.start()
    layout.add_thinking("<writer_key>", "Analyzing the code...")
    layout.add_output("[green]Progress:[/green] Step 1 complete")
    layout.close()
"""

import os
from collections import deque
from threading import Lock
from typing import Dict, Optional

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import Text


class BaseThinkingLayout:
    """Rich Live display with thinking boxes and scrolling output.

    Displays one or more "thinking boxes" at the top of the terminal showing
    real-time LLM thinking, with a scrolling output region below.

    Attributes:
        boxes: Dict mapping box_id to display title
        lines_per_box: Number of lines per thinking box
        started: Whether the Live display is active

    Thread Safety:
        All public methods are thread-safe via internal locking.

    Example:
        layout = BaseThinkingLayout({"agent": "My Agent"})
        layout.start()
        layout.add_thinking("agent", "Processing...")
        layout.mark_complete("agent", "Done")
        layout.close()
    """

    def __init__(self, boxes: Dict[str, str], lines_per_box: int = 3):
        self.boxes = boxes
        self.lines_per_box = lines_per_box
        self.thinking_buffers = {box_id: deque(maxlen=lines_per_box) for box_id in boxes}
        self.thinking_current = {box_id: "" for box_id in boxes}
        self.output_lines = deque(maxlen=500)
        self.assistant_buf = {}
        self.assistant_meta = {}
        self.completed = {box_id: False for box_id in boxes}
        self.completion_status: Dict[str, Optional[str]] = {box_id: None for box_id in boxes}

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

    def _truncate_plain(self, text: str, max_len: int) -> str:
        from rich.errors import MarkupError

        try:
            rich_text = Text.from_markup(text)
            plain = rich_text.plain
        except MarkupError:
            plain = text
            for tag in ["bold", "cyan", "green", "red", "dim", "thinking"]:
                plain = plain.replace(f"[{tag}]", "").replace(f"[/{tag}]", "")
            plain = plain.replace("\\[", "[").replace("\\]", "]")

        if len(plain) <= max_len:
            return plain
        return plain[: max_len - 1] + "…"

    def _truncate_markup(self, text: str, max_len: int) -> str:
        from rich.errors import MarkupError
        from rich.markup import escape

        try:
            rich_text = Text.from_markup(text)
            if len(rich_text.plain) <= max_len:
                return text
            return escape(rich_text.plain[: max_len - 1]) + "…"
        except MarkupError:
            escaped = escape(text)
            if len(escaped) <= max_len:
                return escaped
            return escaped[: max_len - 1] + "…"

    def _assistant_line_width(self, label: str) -> int:
        return self._term_width() - len(label) - 10

    def start(self):
        """Initialize and start the layout display rendering.

        Set up terminal state, create Rich layout regions for each thinking
        box, and begin the live display loop. Must be called before any
        content methods (add_thinking, add_output, add_assistant_message).
        """
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
            lines = list(self.thinking_buffers[box_id])[-self.lines_per_box :]
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
        lines = [self._truncate_markup(line, width) for line in recent]

        self.layout["output"].update(Text.from_markup("\n".join(lines)))

    def add_thinking(self, box_id: str, text: str) -> None:
        """Add thinking text to a specific thinking box.

        Buffer text until a complete sentence is detected (ending with
        punctuation or newline), then flush to the box's line buffer for
        display. Used for streaming AI model thinking output.

        Args:
            box_id: The identifier of the thinking box (e.g., "writer_a")
            text: Text chunk to add (may be partial sentence)
        """
        with self.lock:
            if not self.started:
                self.start()
            if box_id not in self.thinking_current:
                return

            self.thinking_current[box_id] += text
            buf = self.thinking_current[box_id]
            width = self._term_width() - 4  # Just borders

            # Handle embedded newlines - flush each complete line
            while "\n" in buf:
                line, buf = buf.split("\n", 1)
                if line.strip():
                    self.thinking_buffers[box_id].append(self._truncate_plain(line.strip(), width))
                self.thinking_current[box_id] = buf

            # Flush remaining buffer on sentence end or length limit
            ends = buf.rstrip().endswith((".", "!", "?", ":"))
            if (len(buf) > 40 and ends) or len(buf) > 150:
                self.thinking_buffers[box_id].append(self._truncate_plain(buf.strip(), width))
                self.thinking_current[box_id] = ""

            self._refresh()

    def add_assistant_message(self, key: str, content: str, label: str, color: str) -> None:
        """Add a buffered assistant message to the output region.

        Messages are buffered and flushed on sentence boundaries to prevent
        overwhelming the terminal with rapid updates. Displayed with a
        colored label prefix.

        Args:
            key: Unique identifier for this message stream
            content: The assistant message content to buffer
            label: Display label for the agent (e.g., "Writer A")
            color: Rich color name for the label (e.g., "green")
        """
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
            width = self._assistant_line_width(label)

            # Handle embedded newlines - flush each complete line
            while "\n" in buf:
                line, buf = buf.split("\n", 1)
                if line.strip():
                    truncated = self._truncate_markup(line.strip(), width)
                    self.output_lines.append(f"[{color}]{label}[/{color}] 💭 {truncated}")
                self.assistant_buf[key] = buf

            # Flush remaining buffer on sentence end or length limit
            ends = buf.rstrip().endswith((".", "!", "?", ":"))
            if (len(buf) > 50 and ends) or len(buf) > 300:
                truncated = self._truncate_markup(buf.strip(), width)
                self.output_lines.append(f"[{color}]{label}[/{color}] 💭 {truncated}")
                self.assistant_buf[key] = ""

            self._refresh()

    def add_output(self, line: str) -> None:
        """Add a message to the main output region.

        Output messages appear in the scrolling output area below the
        thinking boxes and are immediately visible. Unlike thinking text
        and assistant messages, output is not buffered.

        Args:
            line: The message line to display
        """
        with self.lock:
            if not self.started:
                self.start()
            self.output_lines.append(line)
            self._refresh()

    def mark_complete(self, box_id: str, status: Optional[str] = None) -> None:
        """Mark a thinking box as complete.

        Change the box's visual state to indicate processing is finished,
        displaying a green checkmark and optional status message.

        Args:
            box_id: The identifier of the box to mark complete
            status: Optional completion status message to display
        """
        with self.lock:
            if box_id in self.completed:
                self.completed[box_id] = True
                self.completion_status[box_id] = status
                self._refresh()

    def flush_buffers(self) -> None:
        """Flush all pending text buffers to the display.

        Force immediate display of any buffered assistant messages and
        thinking text. Called automatically when boxes complete and can
        be called manually to ensure all content is visible.
        """
        with self.lock:
            for key, buf in list(self.assistant_buf.items()):
                if buf.strip():
                    label, color = self.assistant_meta.get(key, (key, "white"))
                    width = self._assistant_line_width(label)
                    truncated = self._truncate_markup(buf.strip(), width)
                    self.output_lines.append(f"[{color}]{label}[/{color}] 💭 {truncated}")
                    self.assistant_buf[key] = ""

            for box_id, buf in self.thinking_current.items():
                if buf.strip():
                    width = self._term_width() - 10
                    self.thinking_buffers[box_id].append(self._truncate_plain(buf.strip(), width))
                    self.thinking_current[box_id] = ""
            self._refresh()

    def close(self) -> None:
        """Stop the layout and print final output.

        Flush all buffers, stop the Rich live display, restore terminal
        state, and print accumulated output lines to the console. Should
        be called when workflow is complete or interrupted.
        """
        with self.lock:
            if self.started and self.live:
                self.live.stop()
                self.started = False
                for line in self.output_lines:
                    self.console.print(Text.from_markup(line))
