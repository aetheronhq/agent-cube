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
from cube.core.config import JUDGE_MODELS, PROJECT_ROOT, get_worktree_path
from cube.core.user_config import resolve_writer_alias, get_writer_aliases, get_writer_config
from cube.core.decision_parser import JudgeDecision, aggregate_decisions, parse_all_decisions
from cube.core.session import load_session
from cube.core.state import WorkflowState, load_state

MAX_FILE_PREVIEW_SIZE = 10 * 1024  # 10 KB preview limit for UI

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
    """Return a summary of all known tasks ordered by last update."""
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
    """Return complete workflow state for a single task."""
    state = load_state(task_id)
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task '{task_id}' not found",
        )

    return asdict(state)


@router.get("/{task_id}/logs", response_model=TaskLogsResponse)
async def get_task_logs(task_id: str) -> TaskLogsResponse:
    """Return available log files for the given task."""
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
    "/{task_id}/prompts",
    status_code=status.HTTP_200_OK,
)
async def get_task_prompts(task_id: str) -> dict[str, Any]:
    """Return prompts generated for a task."""
    state = load_state(task_id)
    prompts_dir = Path(state.project_root) / ".prompts" if state and state.project_root else PROMPTS_DIR
    
    prompts = {}
    
    # Known prompt files with semantic keys
    known_prompts = {
        "writer": f"writer-prompt-{task_id}.md",
        "panel": f"panel-prompt-{task_id}.md",
        "synthesis": f"synthesis-{task_id}.md",
        "peer_review": f"peer-review-{task_id}.md",
        "feedback_a": f"feedback/writer-a-{task_id}.md",
        "feedback_b": f"feedback/writer-b-{task_id}.md",
    }
    
    for key, filename in known_prompts.items():
        filepath = prompts_dir / filename
        if filepath.exists():
            try:
                prompts[key] = {
                    "filename": filename,
                    "content": filepath.read_text()[:MAX_FILE_PREVIEW_SIZE],
                    "truncated": filepath.stat().st_size > MAX_FILE_PREVIEW_SIZE,
                }
            except (OSError, IOError):
                pass
    
    # Also scan for any other .md files containing the task_id
    if prompts_dir.exists():
        for filepath in prompts_dir.glob(f"*{task_id}*.md"):
            if not filepath.is_file():
                continue
            filename = filepath.name
            # Skip if already captured as a known prompt
            if filename in known_prompts.values():
                continue
            # Generate a key from the filename
            key = filepath.stem.replace(f"-{task_id}", "").replace(task_id, "").strip("-_") or "custom"
            if key in prompts:
                key = f"{key}_{filepath.stem[:8]}"
            try:
                prompts[key] = {
                    "filename": filename,
                    "content": filepath.read_text()[:MAX_FILE_PREVIEW_SIZE],
                    "truncated": filepath.stat().st_size > MAX_FILE_PREVIEW_SIZE,
                }
            except (OSError, IOError):
                pass
        
        # Check feedback subdirectory for any matching files
        feedback_dir = prompts_dir / "feedback"
        if feedback_dir.exists():
            for filepath in feedback_dir.glob(f"*{task_id}*.md"):
                if not filepath.is_file():
                    continue
                filename = f"feedback/{filepath.name}"
                if filename in known_prompts.values():
                    continue
                key = f"feedback_{filepath.stem.replace(f'-{task_id}', '').replace(task_id, '').strip('-_')}"
                try:
                    prompts[key] = {
                        "filename": filename,
                        "content": filepath.read_text()[:MAX_FILE_PREVIEW_SIZE],
                        "truncated": filepath.stat().st_size > MAX_FILE_PREVIEW_SIZE,
                    }
                except (OSError, IOError):
                    pass
    
    return {"prompts": prompts}


@router.get(
    "/{task_id}/decisions",
    status_code=status.HTTP_200_OK,
)
async def get_task_decisions(task_id: str) -> dict[str, Any]:
    """Return decision data for a task (panel + peer-review)."""
    # Get project_root from task state if available
    state = load_state(task_id)
    project_root = state.project_root if state else None
    
    all_decisions = []
    
    try:
        # Get panel decisions
        panel_decisions = parse_all_decisions(task_id, project_root=project_root, review_type="decision")
        if panel_decisions:
            all_decisions.append(_build_single_decision_payload(panel_decisions, "panel"))
        
        # Get peer-review decisions
        peer_decisions = parse_all_decisions(task_id, project_root=project_root, review_type="peer-review")
        if peer_decisions:
            all_decisions.append(_build_single_decision_payload(peer_decisions, "peer-review"))
            
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Failed to read decisions for task %s", task_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading decisions: {exc}",
        ) from exc

    if not all_decisions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No decisions found for task '{task_id}'",
        )

    return {"decisions": all_decisions}


@router.post("/{task_id}/writers")
async def start_writers(
    task_id: str,
    request: WriterRequest,
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    """Launch dual writers in the background for the given task."""
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
    """Launch judge panel agents in the background."""
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
    """Queue feedback to resume a writer session."""
    writer_cfg = resolve_writer_alias(request.writer)
    session_id = load_session(writer_cfg.key.upper(), task_id)

    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session not found for writer '{writer_cfg.name}' and task '{task_id}'",
        )

    feedback_path = _resolve_feedback_path(task_id, request)
    project_name = PROJECT_ROOT.name
    worktree = get_worktree_path(project_name, writer_cfg.name, task_id)

    if not worktree.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Worktree not found for writer '{writer_cfg.name}' and task '{task_id}'",
        )

    logger.info(
        "Scheduling feedback for writer %s (task=%s, session=%s, feedback=%s)",
        writer_cfg.name,
        task_id,
        session_id,
        feedback_path,
    )

    background_tasks.add_task(
        send_feedback_async,
        writer_cfg.name,
        task_id,
        feedback_path,
        session_id,
        worktree,
    )

    return {
        "status": "started",
        "task_id": task_id,
        "message": f"Feedback sent to {writer_cfg.label}",
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


def _build_single_decision_payload(
    judge_decisions: list[JudgeDecision],
    decision_type: str = "panel"
) -> dict[str, Any]:
    """Build a single decision payload from judge decisions."""
    serialized_votes = [_serialize_judge_decision(decision) for decision in judge_decisions]

    summary = aggregate_decisions(judge_decisions)
    winner = summary.get("winner")
    
    timestamps = [decision.timestamp for decision in judge_decisions if decision.timestamp]
    latest_timestamp = max(timestamps) if timestamps else datetime.utcnow().isoformat()

    decision_payload: dict[str, Any] = {
        "type": decision_type,
        "judges": serialized_votes,
        "timestamp": latest_timestamp,
    }

    if winner:
        decision_payload["winner"] = winner

    return decision_payload


def _build_decision_payload(
    judge_decisions: list[JudgeDecision],
) -> list[dict[str, Any]]:
    """Legacy wrapper for backward compatibility."""
    if not judge_decisions:
        return []
    return [_build_single_decision_payload(judge_decisions, "panel")]


def _serialize_judge_decision(decision: JudgeDecision) -> dict[str, Any]:
    from cube.core.user_config import get_judge_config
    
    vote_value = _resolve_vote(decision)
    
    # Get proper label and model from config
    try:
        judge_cfg = get_judge_config(decision.judge)
        label = judge_cfg.label
        model_name = judge_cfg.model
    except (KeyError, ValueError, AttributeError):
        label = decision.judge.replace("_", " ").title()
        model_name = JUDGE_MODELS.get(decision.judge, f"judge-{decision.judge}")

    scores = decision.scores

    return {
        "judge": decision.judge,
        "label": label,
        "model": model_name,
        "vote": vote_value,
        "rationale": decision.recommendation,
        "blockers": decision.blocker_issues or [],
        "scores": scores,
    }


def _resolve_vote(decision: JudgeDecision) -> str:
    from cube.core.user_config import load_config
    config = load_config()
    if decision.winner in config.writer_order:
        return decision.winner
    elif decision.winner == "TIE":
        return "TIE"

    normalized_decision = (decision.decision or "").upper()
    if normalized_decision in {"APPROVE", "APPROVED"}:
        return "APPROVE"
    if normalized_decision == "REQUEST_CHANGES":
        return "REQUEST_CHANGES"
    return "COMMENT"
