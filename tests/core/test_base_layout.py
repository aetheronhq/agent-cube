"""Tests for cube.core.base_layout module.

Note: These tests avoid actually starting the Rich Live display by testing
internal state and methods directly. Tests that need to verify display behavior
are designed to work without terminal interaction.
"""

from cube.core.base_layout import BaseThinkingLayout


class TestTruncatePlain:
    """Tests for _truncate_plain method."""

    def test_short_text_unchanged(self):
        """Text shorter than max_len returned unchanged."""
        layout = BaseThinkingLayout({"agent": "Agent"}, lines_per_box=3)
        result = layout._truncate_plain("short text", 50)
        assert result == "short text"

    def test_long_text_truncated(self):
        """Text longer than max_len truncated with ellipsis."""
        layout = BaseThinkingLayout({"agent": "Agent"}, lines_per_box=3)
        long_text = "a" * 100
        result = layout._truncate_plain(long_text, 50)

        assert len(result) == 50
        assert result.endswith("…")

    def test_strips_markup(self):
        """Rich markup tags stripped from plain output."""
        layout = BaseThinkingLayout({"agent": "Agent"}, lines_per_box=3)
        result = layout._truncate_plain("[bold]Hello[/bold] [green]World[/green]", 100)
        assert "[" not in result
        assert "bold" not in result
        assert "Hello" in result
        assert "World" in result

    def test_handles_invalid_markup(self):
        """Invalid markup is handled gracefully."""
        layout = BaseThinkingLayout({"agent": "Agent"}, lines_per_box=3)
        result = layout._truncate_plain("[invalid markup text", 100)
        assert result is not None

    def test_exact_length_unchanged(self):
        """Text exactly at max_len is unchanged."""
        layout = BaseThinkingLayout({"agent": "Agent"}, lines_per_box=3)
        text = "x" * 50
        result = layout._truncate_plain(text, 50)
        assert result == text


class TestTruncateMarkup:
    """Tests for _truncate_markup method."""

    def test_short_markup_preserved(self):
        """Short markup text preserved."""
        layout = BaseThinkingLayout({"agent": "Agent"}, lines_per_box=3)
        result = layout._truncate_markup("[green]OK[/green]", 100)
        assert "[green]" in result
        assert "[/green]" in result

    def test_long_markup_escaped_and_truncated(self):
        """Long markup text escaped and truncated safely."""
        layout = BaseThinkingLayout({"agent": "Agent"}, lines_per_box=3)
        long_markup = "[green]" + "a" * 100 + "[/green]"
        result = layout._truncate_markup(long_markup, 50)

        assert len(result) <= 50
        assert result.endswith("…")

    def test_invalid_markup_escaped(self):
        """Invalid markup is escaped."""
        layout = BaseThinkingLayout({"agent": "Agent"}, lines_per_box=3)
        result = layout._truncate_markup("[invalid [nested] markup", 100)
        assert result is not None


class TestLayoutInitialization:
    """Tests for layout initialization."""

    def test_initializes_with_correct_boxes(self):
        """Layout initializes with correct box structure."""
        layout = BaseThinkingLayout(
            {
                "writer_a": "Writer Opus",
                "writer_b": "Writer Codex",
            },
            lines_per_box=3,
        )

        assert "writer_a" in layout.boxes
        assert "writer_b" in layout.boxes
        assert layout.boxes["writer_a"] == "Writer Opus"
        assert layout.boxes["writer_b"] == "Writer Codex"

    def test_initializes_buffers_for_all_boxes(self):
        """Buffers initialized for all boxes."""
        layout = BaseThinkingLayout(
            {
                "writer_a": "Writer Opus",
                "writer_b": "Writer Codex",
            },
            lines_per_box=3,
        )

        assert "writer_a" in layout.thinking_buffers
        assert "writer_b" in layout.thinking_buffers
        assert "writer_a" in layout.thinking_current
        assert "writer_b" in layout.thinking_current

    def test_initializes_completed_flags(self):
        """Completed flags initialized to False."""
        layout = BaseThinkingLayout(
            {
                "writer_a": "Writer Opus",
                "writer_b": "Writer Codex",
            },
            lines_per_box=3,
        )

        assert layout.completed["writer_a"] is False
        assert layout.completed["writer_b"] is False

    def test_lines_per_box_configurable(self):
        """lines_per_box is configurable."""
        layout = BaseThinkingLayout({"a": "A"}, lines_per_box=5)
        assert layout.lines_per_box == 5
        assert layout.thinking_buffers["a"].maxlen == 5

    def test_not_started_by_default(self):
        """Layout is not started by default."""
        layout = BaseThinkingLayout({"agent": "Agent"}, lines_per_box=3)
        assert layout.started is False

    def test_output_lines_has_maxlen(self):
        """Output lines deque has maxlen of 500."""
        layout = BaseThinkingLayout({"agent": "Agent"}, lines_per_box=3)
        assert layout.output_lines.maxlen == 500


class TestMakePanel:
    """Tests for _make_panel method."""

    def test_panel_for_active_box(self):
        """Panel created for active box."""
        layout = BaseThinkingLayout({"agent": "Agent"}, lines_per_box=3)
        layout.thinking_buffers["agent"].append("Thinking...")
        panel = layout._make_panel("agent", "Agent")

        assert panel is not None
        assert "Agent" in str(panel.title)

    def test_panel_for_completed_box(self):
        """Panel shows completion status."""
        layout = BaseThinkingLayout({"agent": "Agent"}, lines_per_box=3)
        layout.completed["agent"] = True
        layout.completion_status["agent"] = "Done"

        panel = layout._make_panel("agent", "Agent")

        assert "✓" in str(panel.title)

    def test_panel_shows_writer_icon(self):
        """Writer boxes show thought bubble icon."""
        layout = BaseThinkingLayout({"writer_a": "Writer Test"}, lines_per_box=3)
        panel = layout._make_panel("writer_a", "Writer Test")

        assert "💭" in str(panel.title)

    def test_panel_shows_judge_icon(self):
        """Judge boxes show balance scale icon."""
        layout = BaseThinkingLayout({"judge_1": "Judge Test"}, lines_per_box=3)
        panel = layout._make_panel("judge_1", "Judge Test")

        assert "⚖️" in str(panel.title)


class TestThinkingBufferBehavior:
    """Tests for thinking buffer behavior without starting display."""

    def test_buffer_appends_truncated_lines(self):
        """Buffer accepts truncated lines."""
        layout = BaseThinkingLayout({"agent": "Agent"}, lines_per_box=3)
        layout.thinking_buffers["agent"].append("Line 1")
        layout.thinking_buffers["agent"].append("Line 2")

        assert len(layout.thinking_buffers["agent"]) == 2
        assert "Line 1" in list(layout.thinking_buffers["agent"])

    def test_buffer_respects_maxlen(self):
        """Buffer respects maxlen and drops old lines."""
        layout = BaseThinkingLayout({"agent": "Agent"}, lines_per_box=3)
        for i in range(5):
            layout.thinking_buffers["agent"].append(f"Line {i}")

        assert len(layout.thinking_buffers["agent"]) == 3
        assert "Line 0" not in list(layout.thinking_buffers["agent"])
        assert "Line 4" in list(layout.thinking_buffers["agent"])

    def test_current_buffer_accumulation(self):
        """Current buffer accumulates partial text."""
        layout = BaseThinkingLayout({"agent": "Agent"}, lines_per_box=3)
        layout.thinking_current["agent"] = "Hello "
        layout.thinking_current["agent"] += "World"

        assert layout.thinking_current["agent"] == "Hello World"


class TestOutputLinesBehavior:
    """Tests for output lines behavior without starting display."""

    def test_output_deque_appends(self):
        """Output lines can be appended."""
        layout = BaseThinkingLayout({"agent": "Agent"}, lines_per_box=3)
        layout.output_lines.append("Line 1")
        layout.output_lines.append("Line 2")

        assert "Line 1" in list(layout.output_lines)
        assert "Line 2" in list(layout.output_lines)

    def test_output_deque_scrolls(self):
        """Output deque scrolls when maxlen exceeded."""
        layout = BaseThinkingLayout({"agent": "Agent"}, lines_per_box=3)
        for i in range(600):
            layout.output_lines.append(f"Line {i}")

        assert len(layout.output_lines) == 500
        assert "Line 0" not in list(layout.output_lines)
        assert "Line 599" in list(layout.output_lines)


class TestAssistantBufferBehavior:
    """Tests for assistant message buffer behavior."""

    def test_assistant_buffer_accumulates(self):
        """Assistant buffer accumulates content."""
        layout = BaseThinkingLayout({"agent": "Agent"}, lines_per_box=3)
        layout.assistant_buf["key1"] = "Hello "
        layout.assistant_buf["key1"] += "World"

        assert layout.assistant_buf["key1"] == "Hello World"

    def test_assistant_meta_stores_info(self):
        """Assistant meta stores label and color."""
        layout = BaseThinkingLayout({"agent": "Agent"}, lines_per_box=3)
        layout.assistant_meta["key1"] = ("My Label", "cyan")

        label, color = layout.assistant_meta["key1"]
        assert label == "My Label"
        assert color == "cyan"


class TestCompletionState:
    """Tests for completion state management."""

    def test_completion_default_false(self):
        """Completed is False by default."""
        layout = BaseThinkingLayout({"agent": "Agent"}, lines_per_box=3)
        assert layout.completed["agent"] is False

    def test_completion_can_be_set(self):
        """Completed can be set to True."""
        layout = BaseThinkingLayout({"agent": "Agent"}, lines_per_box=3)
        layout.completed["agent"] = True
        assert layout.completed["agent"] is True

    def test_completion_status_default_none(self):
        """Completion status is None by default."""
        layout = BaseThinkingLayout({"agent": "Agent"}, lines_per_box=3)
        assert layout.completion_status["agent"] is None

    def test_completion_status_can_be_set(self):
        """Completion status can be set."""
        layout = BaseThinkingLayout({"agent": "Agent"}, lines_per_box=3)
        layout.completion_status["agent"] = "Success!"
        assert layout.completion_status["agent"] == "Success!"


class TestTerminalDimensions:
    """Tests for terminal dimension methods."""

    def test_term_width_returns_int(self):
        """_term_width returns an integer."""
        layout = BaseThinkingLayout({"agent": "Agent"}, lines_per_box=3)
        result = layout._term_width()
        assert isinstance(result, int)
        assert result > 0

    def test_term_height_returns_int(self):
        """_term_height returns an integer."""
        layout = BaseThinkingLayout({"agent": "Agent"}, lines_per_box=3)
        result = layout._term_height()
        assert isinstance(result, int)
        assert result > 0


class TestLockExists:
    """Tests for thread safety lock."""

    def test_lock_exists(self):
        """Layout has a lock for thread safety."""
        layout = BaseThinkingLayout({"agent": "Agent"}, lines_per_box=3)
        assert hasattr(layout, "lock")

    def test_lock_is_acquirable(self):
        """Lock can be acquired and released."""
        layout = BaseThinkingLayout({"agent": "Agent"}, lines_per_box=3)
        with layout.lock:
            pass


class TestCloseWithoutStart:
    """Tests for close() without start()."""

    def test_close_without_start_is_safe(self):
        """Calling close() without start is safe."""
        layout = BaseThinkingLayout({"agent": "Agent"}, lines_per_box=3)
        layout.close()
