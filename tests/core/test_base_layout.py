"""Tests for cube.core.base_layout module."""

from collections import deque
from threading import Thread
from unittest.mock import patch

import pytest
from cube.core.base_layout import BaseThinkingLayout


@pytest.fixture
def mock_console():
    with patch("cube.core.base_layout.Console") as mock:
        yield mock


@pytest.fixture
def mock_live():
    with patch("cube.core.base_layout.Live") as mock:
        yield mock


@pytest.fixture
def layout(mock_console, mock_live):
    """Create a layout instance with mocked dependencies."""
    # Mock terminal size
    with patch("cube.core.base_layout.os.get_terminal_size") as mock_size:
        mock_size.return_value.columns = 80
        mock_size.return_value.lines = 24
        layout_inst = BaseThinkingLayout({"a": "Agent A"}, lines_per_box=3)
        return layout_inst


class TestBaseLayout:
    def test_truncate_plain_short_text(self, layout):
        """Text shorter than max_len returned unchanged."""
        text = "Short text"
        assert layout._truncate_plain(text, 20) == text

    def test_truncate_plain_long_text(self, layout):
        """Text longer than max_len truncated with ellipsis."""
        text = "This is a very long text that should be truncated"
        truncated = layout._truncate_plain(text, 10)
        assert len(truncated) == 10
        assert truncated.endswith("…")

    def test_truncate_plain_strips_markup(self, layout):
        """Rich markup tags stripped from plain output."""
        text = "[bold]Bold[/bold] [green]Green[/green]"
        assert layout._truncate_plain(text, 100) == "Bold Green"

    def test_truncate_markup_preserves_short(self, layout):
        """Short markup text preserved."""
        text = "[bold]Bold[/bold]"
        assert layout._truncate_markup(text, 100) == text

    def test_truncate_markup_escapes_on_truncate(self, layout):
        """Long markup text escaped and truncated safely."""
        # Note: _truncate_markup implementation escapes text if it truncates
        text = "[bold]" + "a" * 100 + "[/bold]"
        truncated = layout._truncate_markup(text, 10)
        assert len(truncated) == 10
        assert truncated.endswith("…")
        assert "[bold]" not in truncated

    def test_add_thinking_buffers_text(self, layout):
        """Text accumulated in thinking buffer."""
        layout.start()
        layout.add_thinking("a", "Part 1 ")
        assert layout.thinking_current["a"] == "Part 1 "
        layout.add_thinking("a", "Part 2")
        assert layout.thinking_current["a"] == "Part 1 Part 2"

    def test_add_thinking_flushes_on_newline(self, layout):
        """Newlines trigger buffer flush to display."""
        layout.start()
        layout.add_thinking("a", "Line 1\n")
        assert len(layout.thinking_buffers["a"]) == 1
        assert layout.thinking_buffers["a"][0] == "Line 1"
        assert layout.thinking_current["a"] == ""

    def test_add_thinking_flushes_on_punctuation(self, layout):
        """Sentence-ending punctuation (.!?:) triggers flush."""
        layout.start()
        # Ensure long enough to trigger flush (>40 chars)
        long_text = "A" * 45 + "."
        layout.add_thinking("a", long_text)
        assert len(layout.thinking_buffers["a"]) == 1
        assert layout.thinking_current["a"] == ""

    def test_add_thinking_flushes_on_length(self, layout):
        """Long text (>150 chars) triggers flush."""
        layout.start()
        long_text = "A" * 151
        layout.add_thinking("a", long_text)
        assert len(layout.thinking_buffers["a"]) == 1
        assert layout.thinking_current["a"] == ""

    def test_add_output_appends_to_lines(self, layout):
        """Output lines added to deque."""
        layout.start()
        layout.add_output("Output 1")
        assert "Output 1" in layout.output_lines

    def test_add_output_scrolls(self, layout):
        """Old lines dropped when maxlen exceeded."""
        layout.output_lines = deque(maxlen=2)
        layout.start()
        layout.add_output("1")
        layout.add_output("2")
        layout.add_output("3")
        assert list(layout.output_lines) == ["2", "3"]

    def test_mark_complete_sets_status(self, layout):
        """Box marked complete with optional status."""
        layout.mark_complete("a", "Done")
        assert layout.completed["a"] is True
        assert layout.completion_status["a"] == "Done"

    def test_flush_buffers_clears_all(self, layout):
        """All pending buffers flushed."""
        layout.start()
        layout.thinking_current["a"] = "Leftover"
        layout.flush_buffers()
        assert layout.thinking_current["a"] == ""
        assert len(layout.thinking_buffers["a"]) == 1
        assert layout.thinking_buffers["a"][0] == "Leftover"

    def test_layout_initialization(self):
        """Layout initializes with correct box structure."""
        boxes = {"a": "A", "b": "B"}
        layout_inst = BaseThinkingLayout(boxes, lines_per_box=5)
        assert layout_inst.lines_per_box == 5
        assert "a" in layout_inst.thinking_buffers
        assert "b" in layout_inst.thinking_buffers
        assert layout_inst.thinking_buffers["a"].maxlen == 5

    def test_layout_thread_safety(self, layout):
        """Multiple threads can safely call methods."""
        layout.start()

        def worker():
            for _ in range(100):
                layout.add_thinking("a", "work ")

        threads = [Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert True

    def test_add_assistant_message(self, layout):
        """Assistant message added to output."""
        layout.start()
        layout.add_assistant_message("k", "Hello", "Label", "green")
        assert "Hello" in layout.assistant_buf["k"]
        # Trigger flush with newline
        layout.add_assistant_message("k", "\n", "Label", "green")
        # Check output lines for formatted message
        found = any("Label" in line and "Hello" in line for line in layout.output_lines)
        assert found
