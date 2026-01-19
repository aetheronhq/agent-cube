"""Data models for Cube CLI."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class WriterInfo:
    """Information about a writer agent."""

    key: str  # Config key: writer_a, writer_b
    name: str
    model: str
    color: str
    label: str
    task_id: str
    worktree: Path
    branch: str
    session_id: Optional[str] = None


@dataclass
class JudgeInfo:
    """Information about a judge agent."""

    key: str
    model: str
    color: str
    label: str
    task_id: str
    review_type: str
    session_id: Optional[str] = None
    adapter_config: Optional[dict] = None


@dataclass
class SessionInfo:
    """Information about a saved session."""

    name: str
    session_id: str
    metadata: Optional[str] = None


@dataclass
class StreamMessage:
    """Parsed message from cursor-agent JSON stream."""

    type: str
    subtype: Optional[str] = None
    model: Optional[str] = None
    session_id: Optional[str] = None
    content: Optional[str] = None
    tool_name: Optional[str] = None
    tool_args: Optional[dict] = None
    duration_ms: Optional[int] = None
    exit_code: Optional[int] = None
    resumed: Optional[bool] = None
