"""Phase definitions for workflow state machine."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Awaitable, Callable, Optional


@dataclass
class PhaseResult:
    """Result from executing a phase."""

    success: bool = True
    exit: bool = False
    exit_message: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    next_phase: int | None = None  # Jump to specific phase (for TIE loops)


@dataclass
class WorkflowContext:
    """Shared context passed to all phase handlers."""

    task_id: str
    task_file: str
    prompts_dir: Path
    resume_from: int
    writer_key: Optional[str] = None
    resume_alias: Optional[str] = None
    result: dict[str, Any] = field(default_factory=dict)
    final_result: dict[str, Any] = field(default_factory=dict)
    fresh_writer: bool = False  # Clear winner's session and start fresh
    fresh_judges: bool = False  # Start fresh judge sessions instead of resuming
    resume_prompt: Optional[str] = None  # Additional context for resumed agents

    @property
    def writer_prompt_path(self) -> Path:
        return self.prompts_dir / f"writer-prompt-{self.task_id}.md"

    @property
    def panel_prompt_path(self) -> Path:
        return self.prompts_dir / f"panel-prompt-{self.task_id}.md"


PhaseHandler = Callable[[WorkflowContext], Awaitable[PhaseResult]]


@dataclass
class Phase:
    """Definition of a workflow phase."""

    num: int
    name: str
    handler: PhaseHandler
    state_updates: dict[str, Any] = field(default_factory=dict)


PHASES: list[Phase] = []


def get_phases() -> list[Phase]:
    """Get all registered phases."""
    return PHASES
