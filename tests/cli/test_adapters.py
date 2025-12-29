import json
from unittest.mock import AsyncMock, patch, MagicMock
import pytest
from cube.core.adapters import CursorAdapter
from cube.core.adapters.claude_code import ClaudeCodeAdapter
from cube.core.adapters.registry import list_adapters, get_adapter
from cube.core.parsers.registry import get_parser
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


def test_claude_code_adapter_registered():
    """Claude Code adapter should be registered."""
    assert "claude-code" in list_adapters()


def test_claude_code_adapter_instance():
    """Claude Code adapter should be instantiable."""
    adapter = get_adapter("claude-code")
    assert isinstance(adapter, ClaudeCodeAdapter)
    assert adapter.get_install_instructions()


def test_claude_code_parser_registered():
    """Claude Code parser should be registered."""
    parser = get_parser("claude-code")
    assert parser is not None
    assert parser.supports_resume() == True


def test_claude_code_parser_parses_init():
    """Claude Code parser should parse init messages."""
    parser = get_parser("claude-code")
    line = '{"type":"system","subtype":"init","model":"claude-sonnet-4","session_id":"abc123"}'
    msg = parser.parse(line)
    assert msg is not None
    assert msg.type == "system"
    assert msg.subtype == "init"
    assert msg.model == "claude-sonnet-4"
    assert msg.session_id == "abc123"


def test_claude_code_parser_parses_assistant():
    """Claude Code parser should parse assistant messages."""
    parser = get_parser("claude-code")
    line = '{"type":"assistant","message":{"content":[{"type":"text","text":"Hello world"}]}}'
    msg = parser.parse(line)
    assert msg is not None
    assert msg.type == "assistant"
    assert msg.content == "Hello world"


def test_claude_code_parser_parses_tool_use():
    """Claude Code parser should parse tool use messages."""
    parser = get_parser("claude-code")
    line = '{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Read","input":{"file_path":"/path/to/file"}}]}}'
    msg = parser.parse(line)
    assert msg is not None
    assert msg.type == "tool_call"
    assert msg.subtype == "started"
    assert msg.tool_name == "read"
    assert msg.tool_args["path"] == "/path/to/file"


def test_claude_code_parser_parses_result():
    """Claude Code parser should parse result messages."""
    parser = get_parser("claude-code")
    line = '{"type":"result","subtype":"success","duration_ms":1234,"session_id":"abc123"}'
    msg = parser.parse(line)
    assert msg is not None
    assert msg.type == "result"
    assert msg.subtype == "success"
    assert msg.duration_ms == 1234
