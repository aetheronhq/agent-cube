"""Tests for single-writer mode."""

from unittest.mock import patch, MagicMock
import pytest
from typer.testing import CliRunner
from pathlib import Path

from cube.cli import app

runner = CliRunner()

@pytest.fixture
def task_file(tmp_path: Path) -> Path:
    f = tmp_path / "task-123.md"
    f.write_text("Test task")
    return f

def test_help_output():
    """--help should show new options."""
    result = runner.invoke(app, ["auto", "--help"])
    assert result.exit_code == 0
    assert "--single" in result.stdout
    assert "--writer" in result.stdout

@patch("cube.cli.orchestrate_auto_command")
def test_single_flag_implies_single_mode(mock_orchestrate: MagicMock, task_file: Path):
    """--single flag should enable single-writer mode."""
    result = runner.invoke(app, ["auto", str(task_file), "--single"])
    assert result.exit_code == 0
    mock_orchestrate.assert_called_once()
    call_args = mock_orchestrate.call_args[1]
    assert call_args['single_mode'] is True
    assert call_args['writer_key'] == "writer_a" # default

@patch("cube.cli.orchestrate_auto_command")
def test_writer_flag_implies_single_mode(mock_orchestrate: MagicMock, task_file: Path):
    """--writer flag should imply single mode and set writer_key."""
    result = runner.invoke(app, ["auto", str(task_file), "--writer", "opus"])
    assert result.exit_code == 0
    mock_orchestrate.assert_called_once()
    call_args = mock_orchestrate.call_args[1]
    assert call_args['single_mode'] is True
    assert call_args['writer_key'] == "writer_a" # 'opus' is writer_a

@patch("cube.cli.orchestrate_auto_command")
def test_writer_b_alias(mock_orchestrate: MagicMock, task_file: Path):
    """--writer b should resolve to writer_b."""
    result = runner.invoke(app, ["auto", str(task_file), "--writer", "b"])
    assert result.exit_code == 0
    mock_orchestrate.assert_called_once()
    call_args = mock_orchestrate.call_args[1]
    assert call_args['single_mode'] is True
    assert call_args['writer_key'] == "writer_b"

@patch("cube.cli.orchestrate_auto_command")
def test_default_is_dual_mode(mock_orchestrate: MagicMock, task_file: Path):
    """Default behavior should be dual-writer mode."""
    result = runner.invoke(app, ["auto", str(task_file)])
    assert result.exit_code == 0
    mock_orchestrate.assert_called_once()
    call_args = mock_orchestrate.call_args[1]
    assert call_args['single_mode'] is False
    assert call_args['writer_key'] is None

def test_invalid_writer_alias(task_file: Path):
    """Invalid writer aliases should raise an error."""
    result = runner.invoke(app, ["auto", str(task_file), "--writer", "invalid-writer"])
    assert result.exit_code != 0
    assert "Unknown writer: invalid-writer" in result.stdout
