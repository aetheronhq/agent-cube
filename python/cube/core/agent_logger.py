"""Generic agent logging for all agent runs."""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import AsyncIterator, Optional, Callable

from .session import SessionWatcher


def get_logs_dir() -> Path:
    """Get the logs directory, creating it if needed."""
    logs_dir = Path.home() / ".cube" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def create_log_filename(agent_type: str, agent_name: str, task_id: str, suffix: str = "") -> str:
    """Create a standardized log filename.
    
    Args:
        agent_type: Type of agent (writer, judge, synth, feedback)
        agent_name: Name/key of the agent (opus, codex, judge_1, etc.)
        task_id: Task identifier
        suffix: Optional suffix (e.g., review type for judges)
    
    Returns:
        Filename like: writer-opus-my-task-1234567890.json
    """
    timestamp = int(datetime.now().timestamp())
    parts = [agent_type, agent_name, task_id]
    if suffix:
        parts.append(suffix)
    parts.append(str(timestamp))
    return "-".join(parts) + ".json"


class AgentLogger:
    """Context manager for logging agent output to files.
    
    Usage:
        logger = AgentLogger("writer", "opus", "my-task")
        async with logger.logging_context():
            async for line in agent_stream:
                logger.write_line(line)
                # Process line...
    """
    
    def __init__(
        self,
        agent_type: str,
        agent_name: str,
        task_id: str,
        suffix: str = "",
        session_key: Optional[str] = None,
        session_task_key: Optional[str] = None,
        metadata: Optional[str] = None
    ):
        """Initialize the agent logger.
        
        Args:
            agent_type: Type of agent (writer, judge, synth, feedback)
            agent_name: Name/key of the agent
            task_id: Task identifier
            suffix: Optional suffix for log filename
            session_key: Key for session storage (e.g., "WRITER_A", "JUDGE_1")
            session_task_key: Task key for session storage (e.g., "my-task")
            metadata: Optional metadata string for session file
        """
        self.agent_type = agent_type
        self.agent_name = agent_name
        self.task_id = task_id
        self.suffix = suffix
        self.session_key = session_key
        self.session_task_key = session_task_key or task_id
        self.metadata = metadata or f"{agent_type}-{agent_name} - {task_id} - {datetime.now()}"
        
        self.logs_dir = get_logs_dir()
        self.log_filename = create_log_filename(agent_type, agent_name, task_id, suffix)
        self.log_file = self.logs_dir / self.log_filename
        
        self._file_handle = None
        self._watcher: Optional[SessionWatcher] = None
        self._line_count = 0
    
    @property
    def line_count(self) -> int:
        """Number of lines written."""
        return self._line_count
    
    async def __aenter__(self):
        """Start logging context."""
        # Create session watcher if session key provided
        if self.session_key:
            from .config import get_sessions_dir
            session_file = get_sessions_dir() / f"{self.session_key}_{self.session_task_key}_SESSION_ID.txt"
            self._watcher = SessionWatcher(self.log_file, session_file, self.metadata)
            self._watcher.start()
        
        # Open log file
        self._file_handle = open(self.log_file, 'w')
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close logging context."""
        if self._file_handle:
            self._file_handle.close()
            self._file_handle = None
        
        if self._watcher:
            self._watcher.stop()
            self._watcher = None
    
    def write_line(self, line: str) -> None:
        """Write a line to the log file."""
        if self._file_handle:
            self._line_count += 1
            self._file_handle.write(line + '\n')
            self._file_handle.flush()


@asynccontextmanager
async def agent_logging_context(
    agent_type: str,
    agent_name: str,
    task_id: str,
    suffix: str = "",
    session_key: Optional[str] = None,
    session_task_key: Optional[str] = None,
    metadata: Optional[str] = None
) -> AsyncIterator[AgentLogger]:
    """Async context manager for agent logging.
    
    Usage:
        async with agent_logging_context("writer", "opus", "my-task") as logger:
            async for line in stream:
                logger.write_line(line)
    """
    logger = AgentLogger(
        agent_type=agent_type,
        agent_name=agent_name,
        task_id=task_id,
        suffix=suffix,
        session_key=session_key,
        session_task_key=session_task_key,
        metadata=metadata
    )
    async with logger:
        yield logger

