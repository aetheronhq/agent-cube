import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cube.automation.dual_writers import launch_dual_writers
from cube.automation.judge_panel import launch_judge_panel
from cube.core.state import load_state
from cube.core.decision_parser import JudgeDecision

# Sample Agent Responses
WRITER_RESPONSE = [
    json.dumps({"type": "thinking", "text": "I am planning the code..."}),
    json.dumps({"type": "thinking", "text": "Still thinking..."}), 
    json.dumps({"type": "thinking", "text": "Almost there..."}),
    json.dumps({"type": "tool_call", "tool": "edit_file", "args": {"file": "test.py", "content": "print('hello')"}}),
    json.dumps({"type": "result", "output": "File edited"}),
    json.dumps({"type": "thinking", "text": "Checking correctness..."}),
    json.dumps({"type": "thinking", "text": "Running tests..."}),
    json.dumps({"type": "thinking", "text": "Tests passed..."}),
    json.dumps({"type": "thinking", "text": "Finalizing..."}),
    json.dumps({"type": "thinking", "text": "I am done."}),
    json.dumps({"type": "thinking", "text": "Really done."})
]

JUDGE_RESPONSE_APPROVE = [
    json.dumps({"type": "thinking", "text": "Reviewing the code..."}),
    json.dumps({"type": "thinking", "text": "Checking file 1..."}),
    json.dumps({"type": "thinking", "text": "Checking file 2..."}),
    json.dumps({"type": "thinking", "text": "Checking file 3..."}),
    json.dumps({"type": "thinking", "text": "Checking file 4..."}),
    json.dumps({"type": "thinking", "text": "Checking file 5..."}),
    json.dumps({"type": "thinking", "text": "Checking file 6..."}),
    json.dumps({"type": "thinking", "text": "Checking file 7..."}),
    json.dumps({"type": "thinking", "text": "Checking file 8..."}),
    json.dumps({"type": "thinking", "text": "Checking file 9..."}),
    json.dumps({"type": "thinking", "text": "Checking file 10..."}),
    json.dumps({"type": "tool_call", "tool": "write_decision", "args": {"vote": "APPROVE", "rationale": "Looks good"}}),
    json.dumps({"type": "result", "output": "Decision recorded"})
]

JUDGE_RESPONSE_CHANGES = [
    json.dumps({"type": "thinking", "text": "Found some issues..."}),
    json.dumps({"type": "tool_call", "tool": "write_decision", "args": {"vote": "REQUEST_CHANGES", "rationale": "Fix bug"}}),
    json.dumps({"type": "result", "output": "Decision recorded"})
]

@pytest.fixture
def mock_agent_runner():
    with patch("cube.automation.dual_writers.run_agent") as mock:
        yield mock

@pytest.fixture
def mock_git():
    with patch("cube.automation.dual_writers.create_worktree") as mock_wt, \
         patch("cube.automation.dual_writers.commit_and_push") as mock_cp, \
         patch("cube.automation.dual_writers.has_uncommitted_changes", return_value=False), \
         patch("cube.automation.dual_writers.has_unpushed_commits", return_value=False):
        
        mock_wt.return_value = Path("/tmp/mock-worktree")
        yield mock_wt

@pytest.fixture
def mock_panel_runner():
    with patch("cube.automation.judge_panel.run_agent") as mock:
        yield mock

@pytest.mark.asyncio
async def test_launch_dual_writers(mock_agent_runner, mock_git, tmp_path, mock_home):
    """Test that dual writers launch and update state correctly."""
    
    # Setup mocks
    async def agent_stream(*args, **kwargs):
        for line in WRITER_RESPONSE:
            yield line
    
    mock_agent_runner.side_effect = agent_stream
    
    # Mock subprocess.run globally since it's imported locally or used from stdlib
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="file1.txt")
        
        # Setup task
        task_id = "test-writers-task"
        prompt_file = tmp_path / "prompt.md"
        prompt_file.write_text("Do some work")
        
        # Run
        await launch_dual_writers(task_id, prompt_file)
        
        # Verify agent called twice (Writer A and Writer B)
        assert mock_agent_runner.call_count == 2
        
        # Verify state updated
        state = load_state(task_id)
        assert state is not None
        assert state.writers_complete is True
        assert state.current_phase == 2

@pytest.mark.skip(reason="Hangs - needs better mocking of DynamicLayout.start()")
@pytest.mark.asyncio
async def test_launch_judge_panel(mock_git, tmp_path, mock_home):
    """Test judge panel execution."""
    
    # Mock find_decision_file globally since it's imported locally
    with patch("cube.core.decision_files.find_decision_file", return_value=None):
        
        # Mock get_adapter in registry globally
        with patch("cube.core.adapters.registry.get_adapter") as mock_get_adapter:
            mock_adapter = MagicMock()
            
            # Mock the async run method
            async def adapter_stream(*args, **kwargs):
                for line in JUDGE_RESPONSE_APPROVE:
                    yield line
            
            mock_adapter.run = MagicMock(side_effect=adapter_stream)
            mock_adapter.check_installed.return_value = True
            
            mock_get_adapter.return_value = mock_adapter

            # Setup task state
            task_id = "test-panel-task"
            prompt_file = tmp_path / "prompt.md"
            prompt_file.write_text("Review this")
            
            # Run
            await launch_judge_panel(task_id, prompt_file)
            
            # Verify adapter.run was called for each judge
            assert mock_adapter.run.call_count >= 3

