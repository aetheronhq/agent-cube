"""Phase definitions for workflow state machine."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Awaitable, Optional


class WorkflowType(str, Enum):
    SINGLE = "SINGLE"
    DUAL = "DUAL"
    SYNTHESIS = "SYNTHESIS"
    MERGE = "MERGE"
    FEEDBACK = "FEEDBACK"


@dataclass
class PhaseResult:
    """Result from executing a phase."""

    success: bool = True
    next_workflow: Optional[WorkflowType] = None
    exit: bool = False
    exit_message: str = ""
    data: dict[str, Any] = field(default_factory=dict)


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


SINGLE_WORKFLOW: list[Phase] = []
DUAL_WORKFLOW: list[Phase] = []
SYNTHESIS_WORKFLOW: list[Phase] = []
MERGE_WORKFLOW: list[Phase] = []
FEEDBACK_WORKFLOW: list[Phase] = []


def get_workflow(workflow_type: WorkflowType | str) -> list[Phase]:
    """Get the phase list for a workflow type."""
    if isinstance(workflow_type, str):
        workflow_type = WorkflowType(workflow_type)

    workflows = {
        WorkflowType.SINGLE: SINGLE_WORKFLOW,
        WorkflowType.DUAL: DUAL_WORKFLOW,
        WorkflowType.SYNTHESIS: SYNTHESIS_WORKFLOW,
        WorkflowType.MERGE: MERGE_WORKFLOW,
        WorkflowType.FEEDBACK: FEEDBACK_WORKFLOW,
    }
    return workflows.get(workflow_type, [])


def get_max_phase(workflow_type: WorkflowType | str) -> int:
    """Get the maximum phase number for a workflow."""
    workflow = get_workflow(workflow_type)
    if not workflow:
        return 0
    return workflow[-1].num


def register_phase(workflow_type: WorkflowType, phase: Phase) -> None:
    """Register a phase to a workflow."""
    workflow = get_workflow(workflow_type)
    workflow.append(phase)
    workflow.sort(key=lambda p: p.num)

