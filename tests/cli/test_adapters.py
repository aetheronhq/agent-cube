import json
from unittest.mock import AsyncMock, patch, MagicMock
import pytest
from cube.core.adapters import CursorAdapter
from pathlib import Path

@pytest.mark.asyncio
async def test_cursor_adapter_run():
    adapter = CursorAdapter()
    
    with patch("cube.core.adapters.cursor.CursorAdapter.check_logged_in", return_value=True), \
         patch("asyncio.create_subprocess_exec") as mock_exec:
        
        # Mock process
        mock_process = AsyncMock()
        mock_process.wait.return_value = 0
        mock_process.stdout = AsyncMock()
        
        # Setup stream - read_stream_with_buffer calls read(n)
        # We need to return bytes chunks
        mock_process.stdout.read.side_effect = [
            b'{"type": "thinking", "text": "hello"}\n',
            b'{"type": "result", "output": "world"}\n',
            b'' # End of stream
        ]
        
        mock_exec.return_value = mock_process
        
        # Run
        worktree = Path("/tmp")
        results = []
        async for line in adapter.run(worktree, "claude-3.5-sonnet", "prompt"):
            results.append(line)
            
        # Verify command structure
        mock_exec.assert_called_once()
        args = mock_exec.call_args[0]
        assert "cursor-agent" in args
        assert "--model" in args
        assert "claude-3.5-sonnet" in args
        assert "prompt" in args
        
        # Verify output
        # read_stream_with_buffer might combine or split differently depending on buffer size,
        # but here we provided clean lines with newlines.
        assert len(results) == 2
        assert 'thinking' in results[0]
        assert 'result' in results[1]

@pytest.mark.asyncio
async def test_cursor_adapter_not_logged_in():
    adapter = CursorAdapter()
    with patch("cube.core.adapters.cursor.CursorAdapter.check_logged_in", return_value=False):
        with pytest.raises(RuntimeError, match="not logged in"):
            async for _ in adapter.run(Path("/tmp"), "model", "prompt"):
                pass

