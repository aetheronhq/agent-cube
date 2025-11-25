from __future__ import annotations

import logging
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from pydantic import BaseModel, model_validator

from cube.automation.dual_writers import launch_dual_writers
from cube.automation.judge_panel import launch_judge_panel
from cube.commands.feedback import send_feedback_async
from cube.core.config import JUDGE_MODELS, PROJECT_ROOT, WRITER_LETTERS, get_worktree_path
from cube.core.user_config import resolve_writer_alias, get_writer_aliases
from cube.core.decision_parser import JudgeDecision, aggregate_decisions, parse_all_decisions
from cube.core.session import load_session
from cube.core.state import WorkflowState, load_state

router = APIRouter(prefix="/tasks", tags=["tasks"])

logger = logging.getLogger(__name__)

STATE_DIR = Path.home() / ".cube" / "state"
LOGS_DIR = Path.home() / ".cube" / "logs"
PROMPTS_DIR = PROJECT_ROOT / ".prompts"


class TaskSummary(BaseModel):
    id: str
    current_phase: int
    path: str
    workflow_status: str
    updated_at: str | None = None


class TaskListResponse(BaseModel):
    tasks: list[TaskSummary]


class TaskLogsResponse(BaseModel):
    logs: list["LogEntry"]


class LogEntry(BaseModel):
    file: str
    content: str


class WriterRequest(BaseModel):
    prompt_file: str
    resume: bool = False


class PanelRequest(BaseModel):
    prompt_file: str
    resume: bool = False
    review_type: Literal["panel", "peer-review", "initial"] = "panel"


class FeedbackRequest(BaseModel):
    writer: str
    feedback_file: str | None = None
    feedback_text: str | None = None

    @model_validator(mode="after")
    def validate_payload(self) -> "FeedbackRequest":
        """Validate the feedback request payload.
        
        Check that exactly one of feedback_file or feedback_text is
        provided, and that the writer alias resolves to a valid writer.
        
        Returns:
            The validated FeedbackRequest instance
        
        Raises:
            ValueError: If payload is missing required fields or has invalid values
        """
        if bool(self.feedback_file) == bool(self.feedback_text):
            raise ValueError("Provide exactly one of feedback_file or feedback_text")
        try:
            resolve_writer_alias(self.writer)
        except KeyError:
            raise ValueError(
                f"Unknown writer '{self.writer}'. Choices: {', '.join(get_writer_aliases())}"
            )
        return self


@router.get("", response_model=TaskListResponse)
async def list_tasks() -> TaskListResponse:
    """Return a summary of all known tasks ordered by last update.
    
    Scan the state directory for task state files and return a list
    of task summaries with current phase, path, and workflow status.
    
    Returns:
        TaskListResponse containing list of TaskSummary objects
    """
    if not STATE_DIR.exists():
        return TaskListResponse(tasks=[])

    summaries: list[TaskSummary] = []

    for state_file in STATE_DIR.glob("*.json"):
        task_id = state_file.stem
        state = load_state(task_id)
        if not state:
            continue

        summaries.append(
            TaskSummary(
                id=state.task_id,
                current_phase=state.current_phase,
                path=state.path,
                workflow_status=_determine_status(state),
                updated_at=state.updated_at or None,
            )
        )

    summaries.sort(key=lambda item: _parse_timestamp(item.updated_at), reverse=True)
    return TaskListResponse(tasks=summaries)


@router.get("/{task_id}")
async def get_task(task_id: str) -> dict:
    """Return complete workflow state for a single task.
    
    Args:
        task_id: The task identifier to look up
    
    Returns:
        Dictionary containing full workflow state
    
    Raises:
        HTTPException: 404 if task not found
    """
    state = load_state(task_id)
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{task_id}' not found",
        )

    return asdict(state)


@router.get("/{task_id}/logs", response_model=TaskLogsResponse)
async def get_task_logs(task_id: str) -> TaskLogsResponse:
    """Return available log files for the given task.
    
    Find and read all log files matching the task ID from the logs
    directory, returning their contents for display.
    
    Args:
        task_id: The task identifier to get logs for
    
    Returns:
        TaskLogsResponse containing list of LogEntry objects
    
    Raises:
        HTTPException: 404 if logs directory or task logs not found
    """
    if not LOGS_DIR.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Logs directory not found",
        )

    matching = sorted(
        file
        for file in LOGS_DIR.glob(f"*{task_id}*")
        if file.is_file() and file.suffix in {".log", ".json", ".txt"}
    )

    if not matching:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No logs found for task '{task_id}'",
        )

    log_entries: list[LogEntry] = []

    for log_file in matching:
        try:
            content = log_file.read_text(encoding="utf-8")
        except OSError as exc:
            logger.warning("Failed to read log file %s: %s", log_file, exc)
            continue

        log_entries.append(LogEntry(file=log_file.name, content=content))

    if not log_entries:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to read logs for task '{task_id}'",
        )

    return TaskLogsResponse(logs=log_entries)


@router.get(
    "/{task_id}/decisions",
    status_code=status.HTTP_200_OK,
)
async def get_task_decisions(task_id: str) -> dict[str, Any]:
    """Return decision data for a task.
    
    Parse and aggregate all judge decisions for the task, returning
    votes, rationales, and overall winner determination.
    
    Args:
        task_id: The task identifier to get decisions for
    
    Returns:
        Dictionary containing aggregated decision data
    
    Raises:
        HTTPException: 404 if no decisions found, 500 on read errors
    """
    try:
        judge_decisions = parse_all_decisions(task_id)
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Failed to read decisions for task %s", task_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading decisions: {exc}",
        ) from exc

    if not judge_decisions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No decisions found for task '{task_id}'",
        )

    response = _build_decision_payload(judge_decisions)
    return {"decisions": response}


@router.post("/{task_id}/writers")
async def start_writers(
    task_id: str,
    request: WriterRequest,
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    """Launch dual writers in the background for the given task.
    
    Schedule the dual writer workflow to run asynchronously, returning
    immediately with a status message.
    
    Args:
        task_id: The task identifier
        request: Writer configuration with prompt file and resume flag
        background_tasks: FastAPI background task manager
    
    Returns:
        Status dictionary with task_id and message
    
    Raises:
        HTTPException: 404 if prompt file not found
    """
    prompt_path = _resolve_project_path(request.prompt_file)

    if not prompt_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt file not found: {request.prompt_file}",
        )

    logger.info(
        "Scheduling dual writers for task %s using prompt %s (resume=%s)",
        task_id,
        prompt_path,
        request.resume,
    )

    background_tasks.add_task(
        launch_dual_writers,
        task_id,
        prompt_path,
        request.resume,
    )

    return {
        "status": "started",
        "task_id": task_id,
        "message": "Dual writers launching in background",
    }


@router.post("/{task_id}/panel")
async def start_panel(
    task_id: str,
    request: PanelRequest,
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    """Launch judge panel agents in the background.
    
    Schedule the judge panel workflow to run asynchronously with the
    specified review type (panel or peer-review).
    
    Args:
        task_id: The task identifier
        request: Panel configuration with prompt file and review type
        background_tasks: FastAPI background task manager
    
    Returns:
        Status dictionary with task_id and message
    
    Raises:
        HTTPException: 404 if prompt file not found
    """
    prompt_path = _resolve_project_path(request.prompt_file)

    if not prompt_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt file not found: {request.prompt_file}",
        )

    logger.info(
        "Scheduling judge panel for task %s using prompt %s (review_type=%s, resume=%s)",
        task_id,
        prompt_path,
        request.review_type,
        request.resume,
    )

    background_tasks.add_task(
        launch_judge_panel,
        task_id,
        prompt_path,
        request.review_type,
        request.resume,
    )

    return {
        "status": "started",
        "task_id": task_id,
        "message": "Judge panel launching in background",
    }


@router.post("/{task_id}/feedback")
async def send_feedback(
    task_id: str,
    request: FeedbackRequest,
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    """Queue feedback to resume a writer session.
    
    Send feedback content to a specific writer, resuming their session
    to continue work on the task.
    
    Args:
        task_id: The task identifier
        request: Feedback request with writer and content
        background_tasks: FastAPI background task manager
    
    Returns:
        Status dictionary with task_id and message
    
    Raises:
        HTTPException: 404 if session, feedback file, or worktree not found
    """
    writer_cfg = resolve_writer_alias(request.writer)
    writer = writer_cfg.name
    writer_letter = WRITER_LETTERS[writer]
    session_id = load_session(f"WRITER_{writer_letter}", task_id)

    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session not found for writer '{writer}' and task '{task_id}'",
        )

    feedback_path = _resolve_feedback_path(task_id, request)
    project_name = PROJECT_ROOT.name
    worktree = get_worktree_path(project_name, writer, task_id)

    if not worktree.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Worktree not found for writer '{writer}' and task '{task_id}'",
        )

    logger.info(
        "Scheduling feedback for writer %s (task=%s, session=%s, feedback=%s)",
        writer,
        task_id,
        session_id,
        feedback_path,
    )

    background_tasks.add_task(
        send_feedback_async,
        writer,
        task_id,
        feedback_path,
        session_id,
        worktree,
    )

    return {
        "status": "started",
        "task_id": task_id,
        "message": f"Feedback sent to writer {writer}",
    }


def _resolve_project_path(path_str: str) -> Path:
    path = Path(path_str)
    if not path.is_absolute():
        path = (PROJECT_ROOT / path_str).resolve()
    return path


def _resolve_feedback_path(task_id: str, request: FeedbackRequest) -> Path:
    if request.feedback_file:
        path = _resolve_project_path(request.feedback_file)
        if not path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feedback file not found: {request.feedback_file}",
            )
        return path

    assert request.feedback_text is not None

    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)

    filename = f"feedback-{task_id}-{uuid4().hex}.md"
    path = PROMPTS_DIR / filename
    path.write_text(request.feedback_text, encoding="utf-8")
    return path


def _determine_status(state: WorkflowState) -> str:
    if state.peer_review_complete:
        return "peer-review-complete"
    if state.synthesis_complete:
        return "synthesis-complete"
    if state.panel_complete:
        return "panel-complete"
    if state.writers_complete:
        return "writers-complete"
    return "in-progress"


def _parse_timestamp(value: str | None) -> datetime:
    if not value:
        return datetime.min
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return datetime.min


def _build_decision_payload(
    judge_decisions: list[JudgeDecision],
) -> list[dict[str, Any]]:
    if not judge_decisions:
        return []

    serialized_votes = [_serialize_judge_decision(decision) for decision in judge_decisions]

    summary = aggregate_decisions(judge_decisions)
    winner = summary.get("winner")
    winner_letter = winner if winner in {"A", "B"} else None

    timestamps = [decision.timestamp for decision in judge_decisions if decision.timestamp]
    latest_timestamp = max(timestamps) if timestamps else datetime.utcnow().isoformat()

    decision_payload: dict[str, Any] = {
        "type": "panel",
        "judges": serialized_votes,
        "timestamp": latest_timestamp,
    }

    if winner_letter:
        decision_payload["winner"] = winner_letter

    return [decision_payload]


def _serialize_judge_decision(decision: JudgeDecision) -> dict[str, Any]:
    model_name = JUDGE_MODELS.get(decision.judge, f"judge-{decision.judge}")
    vote_value = _resolve_vote(decision)

    return {
        "judge": decision.judge,
        "model": model_name,
        "vote": vote_value,
        "rationale": decision.recommendation,
    }


def _resolve_vote(decision: JudgeDecision) -> str:
    if decision.winner in {"A", "B"}:
        return decision.winner

    normalized_decision = (decision.decision or "").upper()
    if normalized_decision in {"APPROVE", "APPROVED"}:
        return "APPROVE"
    if normalized_decision == "REQUEST_CHANGES":
        return "REQUEST_CHANGES"
    return "COMMENT"
