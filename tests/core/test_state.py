"""Tests for cube.core.state module."""

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
    monkeypatch.setenv("HOME", str(home))
    return home


@pytest.fixture
def sample_state(mock_home):
    """Create a sample workflow state."""
    return WorkflowState(
        task_id="test-task",
        current_phase=1,
        path="SYNTHESIS",
        completed_phases=[1],
        project_root="/tmp/project",
        winner="writer_a",
    )


class TestState:
    def test_get_state_file_path(self, mock_home):
        """Returns ~/.cube/state/<task_id>.json path."""
        path = get_state_file("my-task")
        expected = mock_home / ".cube" / "state" / "my-task.json"
        assert path == expected

    def test_save_and_load_state(self, mock_home, sample_state):
        """State roundtrips correctly through save/load."""
        save_state(sample_state)
        loaded = load_state(sample_state.task_id)

        assert loaded is not None
        assert loaded.task_id == sample_state.task_id
        assert loaded.current_phase == sample_state.current_phase
        assert loaded.winner == sample_state.winner
        assert loaded.updated_at != ""  # Should be set

    def test_load_state_nonexistent(self, mock_home):
        """Returns None for missing state file."""
        assert load_state("nonexistent") is None

    def test_load_state_corrupted_json(self, mock_home):
        """Returns None for corrupted state file."""
        state_file = get_state_file("corrupt")
        state_file.write_text("{invalid_json")

        assert load_state("corrupt") is None

    def test_update_phase_creates_new(self, mock_home, monkeypatch, tmp_path):
        """Creates new state if none exists."""
        monkeypatch.setattr("cube.core.config.PROJECT_ROOT", tmp_path)
        state = update_phase("new-task", 1, path="SYNTHESIS")

        assert state.task_id == "new-task"
        assert state.current_phase == 1
        assert state.path == "SYNTHESIS"
        assert state.project_root == str(tmp_path)

        # Verify saved
        loaded = load_state("new-task")
        assert loaded is not None

    def test_update_phase_updates_existing(self, mock_home, monkeypatch, tmp_path):
        """Updates existing state correctly."""
        monkeypatch.setattr("cube.core.config.PROJECT_ROOT", tmp_path)

        # Initial
        update_phase("existing-task", 1, path="SYNTHESIS")

        # Update
        state = update_phase("existing-task", 2, winner="writer_b")

        assert state.current_phase == 2
        assert state.winner == "writer_b"
        assert 1 in state.completed_phases
        assert 2 in state.completed_phases

    def test_update_phase_adds_to_completed(self, mock_home, monkeypatch, tmp_path):
        """Phase added to completed_phases list."""
        monkeypatch.setattr("cube.core.config.PROJECT_ROOT", tmp_path)
        state = update_phase("phases-task", 1, path="TEST")
        assert 1 in state.completed_phases

        state = update_phase("phases-task", 3, path="TEST")
        assert 1 in state.completed_phases
        assert 3 in state.completed_phases
        assert state.completed_phases == [1, 3]

    def test_deduplicates_completed_phases(self, mock_home, monkeypatch, tmp_path):
        """Completed phases are deduplicated."""
        monkeypatch.setattr("cube.core.config.PROJECT_ROOT", tmp_path)
        update_phase("dedup-task", 1, path="TEST")
        update_phase("dedup-task", 1, path="TEST")
        state = update_phase("dedup-task", 2, path="TEST")

        assert state.completed_phases == [1, 2]

    def test_update_phase_preserves_kwargs(self, mock_home, monkeypatch, tmp_path):
        """Extra kwargs (winner, path, etc.) are saved."""
        monkeypatch.setattr("cube.core.config.PROJECT_ROOT", tmp_path)
        state = update_phase("kwargs-task", 1, winner="writer_a", next_action="review")

        assert state.winner == "writer_a"
        assert state.next_action == "review"

    def test_validate_resume_no_state(self, mock_home):
        """Resuming without state is allowed."""
        valid, msg = validate_resume("no-state", 1)
        assert valid is True

    def test_validate_resume_with_state(self, mock_home, sample_state):
        """Resuming with existing state is allowed."""
        save_state(sample_state)
        valid, msg = validate_resume(sample_state.task_id, 2)
        assert valid is True

    def test_clear_state_removes_file(self, mock_home, sample_state):
        """State file is deleted."""
        save_state(sample_state)
        path = get_state_file(sample_state.task_id)
        assert path.exists()

        clear_state(sample_state.task_id)
        assert not path.exists()

    def test_clear_state_missing_file_no_error(self, mock_home):
        """No error when clearing nonexistent state."""
        clear_state("missing")  # Should not raise

    def test_get_progress_not_started(self, mock_home):
        """Returns 'Not started' for unknown task."""
        assert get_progress("unknown") == "Not started"

    def test_get_progress_with_state(self, mock_home, sample_state):
        """Returns formatted progress string."""
        save_state(sample_state)
        progress = get_progress(sample_state.task_id)
        assert "Phase 1/10" in progress
        assert "10%" in progress
        assert "SYNTHESIS" in progress
