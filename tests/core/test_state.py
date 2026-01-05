"""Tests for cube.core.state module."""

import json
from pathlib import Path

import pytest
from cube.core.state import (
    WorkflowState,
    clear_state,
    get_progress,
    get_state_file,
    load_state,
    save_state,
    update_phase,
    validate_resume,
)


@pytest.fixture
def mock_home(tmp_path, monkeypatch):
    """Override HOME to use temp directory for state files."""
    home = tmp_path / "home"
    (home / ".cube" / "state").mkdir(parents=True)
    monkeypatch.setattr(Path, "home", lambda: home)
    return home


@pytest.fixture
def sample_state():
    """Sample WorkflowState for testing."""
    return WorkflowState(
        task_id="test-task",
        current_phase=2,
        path="SYNTHESIS",
        completed_phases=[1, 2],
        winner="writer_a",
        writers_complete=True,
        panel_complete=False,
    )


class TestGetStateFile:
    """Tests for get_state_file function."""

    def test_returns_correct_path_format(self, mock_home):
        """State file path follows ~/.cube/state/<task_id>.json format."""
        result = get_state_file("my-task")
        expected = mock_home / ".cube" / "state" / "my-task.json"
        assert result == expected

    def test_creates_state_directory(self, mock_home):
        """State directory is created if it does not exist."""
        state_dir = mock_home / ".cube" / "state"
        state_dir.rmdir()
        (mock_home / ".cube").rmdir()

        result = get_state_file("new-task")
        assert result.parent.exists()

    def test_handles_special_characters_in_task_id(self, mock_home):
        """Task IDs with special characters work correctly."""
        result = get_state_file("task-with-dashes_and_underscores")
        assert result.name == "task-with-dashes_and_underscores.json"


class TestLoadState:
    """Tests for load_state function."""

    def test_returns_none_for_nonexistent_file(self, mock_home):
        """Returns None when state file does not exist."""
        result = load_state("nonexistent-task")
        assert result is None

    def test_loads_valid_state_file(self, mock_home):
        """Loads state correctly from valid JSON file."""
        state_data = {
            "task_id": "test-task",
            "current_phase": 3,
            "path": "FEEDBACK",
            "completed_phases": [1, 2, 3],
            "winner": "writer_b",
            "writers_complete": True,
            "panel_complete": True,
        }
        state_file = mock_home / ".cube" / "state" / "test-task.json"
        state_file.write_text(json.dumps(state_data))

        result = load_state("test-task")

        assert result is not None
        assert result.task_id == "test-task"
        assert result.current_phase == 3
        assert result.path == "FEEDBACK"
        assert result.completed_phases == [1, 2, 3]
        assert result.winner == "writer_b"
        assert result.writers_complete is True
        assert result.panel_complete is True

    def test_returns_none_for_corrupted_json(self, mock_home, capsys):
        """Returns None for corrupted JSON file."""
        state_file = mock_home / ".cube" / "state" / "corrupted-task.json"
        state_file.write_text("{invalid json content")

        result = load_state("corrupted-task")
        assert result is None

    def test_handles_missing_optional_fields(self, mock_home):
        """Handles state files with missing optional fields."""
        state_data = {
            "task_id": "minimal-task",
            "current_phase": 1,
            "path": "SYNTHESIS",
            "completed_phases": [1],
        }
        state_file = mock_home / ".cube" / "state" / "minimal-task.json"
        state_file.write_text(json.dumps(state_data))

        result = load_state("minimal-task")

        assert result is not None
        assert result.winner is None
        assert result.writers_complete is False
        assert result.panel_complete is False


class TestSaveState:
    """Tests for save_state function."""

    def test_saves_state_to_file(self, mock_home, sample_state):
        """State is saved correctly to JSON file."""
        save_state(sample_state)

        state_file = mock_home / ".cube" / "state" / "test-task.json"
        assert state_file.exists()

        data = json.loads(state_file.read_text())
        assert data["task_id"] == "test-task"
        assert data["current_phase"] == 2
        assert data["path"] == "SYNTHESIS"
        assert data["winner"] == "writer_a"

    def test_updates_timestamp_on_save(self, mock_home, sample_state):
        """Timestamp is updated when state is saved."""
        original_timestamp = sample_state.updated_at
        save_state(sample_state)

        assert sample_state.updated_at != original_timestamp

    def test_save_and_load_roundtrip(self, mock_home, sample_state):
        """State survives save/load roundtrip."""
        save_state(sample_state)
        loaded = load_state("test-task")

        assert loaded is not None
        assert loaded.task_id == sample_state.task_id
        assert loaded.current_phase == sample_state.current_phase
        assert loaded.path == sample_state.path
        assert loaded.winner == sample_state.winner


class TestUpdatePhase:
    """Tests for update_phase function."""

    def test_creates_new_state_if_none_exists(self, mock_home, monkeypatch):
        """Creates new state when no existing state."""
        monkeypatch.setattr("cube.core.config.get_project_root", lambda: mock_home)

        result = update_phase("new-task", 1, path="SYNTHESIS")

        assert result.task_id == "new-task"
        assert result.current_phase == 1
        assert result.path == "SYNTHESIS"
        assert 1 in result.completed_phases

    def test_updates_existing_state(self, mock_home, sample_state, monkeypatch):
        """Updates existing state correctly."""
        monkeypatch.setattr("cube.core.config.get_project_root", lambda: mock_home)
        save_state(sample_state)

        result = update_phase("test-task", 3, path="FEEDBACK")

        assert result.current_phase == 3
        assert result.path == "FEEDBACK"
        assert 3 in result.completed_phases

    def test_adds_phase_to_completed(self, mock_home, sample_state, monkeypatch):
        """Phase is added to completed_phases list."""
        monkeypatch.setattr("cube.core.config.get_project_root", lambda: mock_home)
        save_state(sample_state)

        result = update_phase("test-task", 5)

        assert 5 in result.completed_phases
        assert 1 in result.completed_phases
        assert 2 in result.completed_phases

    def test_deduplicates_completed_phases(self, mock_home, sample_state, monkeypatch):
        """Duplicate phases are not added twice."""
        monkeypatch.setattr("cube.core.config.get_project_root", lambda: mock_home)
        save_state(sample_state)

        result = update_phase("test-task", 2)

        assert result.completed_phases.count(2) == 1

    def test_preserves_kwargs(self, mock_home, monkeypatch):
        """Extra kwargs are saved to state."""
        monkeypatch.setattr("cube.core.config.get_project_root", lambda: mock_home)

        result = update_phase("new-task", 1, path="MERGE", winner="writer_b", writers_complete=True)

        assert result.winner == "writer_b"
        assert result.writers_complete is True


class TestValidateResume:
    """Tests for validate_resume function."""

    def test_allows_resume_without_state(self, mock_home):
        """Resuming without existing state is allowed."""
        valid, message = validate_resume("nonexistent-task", 1)
        assert valid is True
        assert message == ""

    def test_allows_resume_with_state(self, mock_home, sample_state):
        """Resuming with existing state is allowed."""
        save_state(sample_state)

        valid, message = validate_resume("test-task", 3)
        assert valid is True
        assert message == ""

    def test_allows_skipping_ahead(self, mock_home, sample_state):
        """Allows skipping ahead in phases."""
        save_state(sample_state)

        valid, message = validate_resume("test-task", 10)
        assert valid is True


class TestClearState:
    """Tests for clear_state function."""

    def test_removes_state_file(self, mock_home, sample_state):
        """State file is deleted when cleared."""
        save_state(sample_state)
        state_file = mock_home / ".cube" / "state" / "test-task.json"
        assert state_file.exists()

        clear_state("test-task")

        assert not state_file.exists()

    def test_no_error_for_missing_file(self, mock_home):
        """No error when clearing nonexistent state."""
        clear_state("nonexistent-task")


class TestGetProgress:
    """Tests for get_progress function."""

    def test_returns_not_started_for_unknown_task(self, mock_home):
        """Returns 'Not started' for unknown task."""
        result = get_progress("unknown-task")
        assert result == "Not started"

    def test_returns_formatted_progress(self, mock_home, sample_state):
        """Returns formatted progress string with state."""
        save_state(sample_state)

        result = get_progress("test-task")

        assert "Phase 2/10" in result
        assert "20%" in result
        assert "SYNTHESIS" in result


class TestWorkflowState:
    """Tests for WorkflowState dataclass."""

    def test_post_init_sets_timestamp(self):
        """Timestamp is set automatically if not provided."""
        state = WorkflowState(
            task_id="test",
            current_phase=1,
            path="SYNTHESIS",
            completed_phases=[],
        )
        assert state.updated_at != ""

    def test_default_values(self):
        """Default values are set correctly."""
        state = WorkflowState(
            task_id="test",
            current_phase=1,
            path="SYNTHESIS",
            completed_phases=[],
        )
        assert state.winner is None
        assert state.next_action is None
        assert state.writers_complete is False
        assert state.panel_complete is False
        assert state.synthesis_complete is False
        assert state.peer_review_complete is False
        assert state.mode == "dual"
        assert state.writer_key is None
