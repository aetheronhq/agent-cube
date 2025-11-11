"""Task management and workflow control endpoints."""

import asyncio
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from ...core.state import load_state, get_state_file
from ...core.config import get_sessions_dir
from ...automation.dual_writers import launch_dual_writers
from ...automation.judge_panel import launch_judge_panel

router = APIRouter()


class WriterRequest(BaseModel):
    """Request to start dual writers."""
    prompt_file: str


class PanelRequest(BaseModel):
    """Request to start judge panel."""
    prompt_file: str
    review_type: str = "initial"


class FeedbackRequest(BaseModel):
    """Request to send feedback to a writer."""
    writer: str
    feedback: str


class TaskSummary(BaseModel):
    """Summary of a task."""
    id: str
    phase: int
    path: str
    status: str
    updated_at: str


class TaskDetail(BaseModel):
    """Detailed task information."""
    task_id: str
    current_phase: int
    path: str
    completed_phases: List[int]
    winner: Optional[str]
    next_action: Optional[str]
    writers_complete: bool
    panel_complete: bool
    synthesis_complete: bool
    peer_review_complete: bool
    updated_at: str


class LogEntry(BaseModel):
    """Log file entry."""
    file: str
    content: str


@router.get("/tasks")
async def list_tasks():
    """List all tasks from state files."""
    state_dir = Path.home() / ".cube" / "state"
    
    if not state_dir.exists():
        return {"tasks": []}
    
    tasks = []
    for state_file in sorted(state_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        task_id = state_file.stem
        state = load_state(task_id)
        
        if state:
            tasks.append(TaskSummary(
                id=task_id,
                phase=state.current_phase,
                path=state.path,
                status="active" if state.current_phase < 10 else "completed",
                updated_at=state.updated_at
            ))
    
    return {"tasks": tasks}


@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """Get detailed task state."""
    state = load_state(task_id)
    
    if not state:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    return TaskDetail(
        task_id=state.task_id,
        current_phase=state.current_phase,
        path=state.path,
        completed_phases=state.completed_phases,
        winner=state.winner,
        next_action=state.next_action,
        writers_complete=state.writers_complete,
        panel_complete=state.panel_complete,
        synthesis_complete=state.synthesis_complete,
        peer_review_complete=state.peer_review_complete,
        updated_at=state.updated_at
    )


@router.get("/tasks/{task_id}/logs")
async def get_task_logs(task_id: str):
    """Get agent logs for a task."""
    logs_dir = Path.home() / ".cube" / "logs"
    
    if not logs_dir.exists():
        return {"logs": []}
    
    logs = []
    
    for log_file in sorted(logs_dir.glob(f"*{task_id}*.json")):
        try:
            content = log_file.read_text()
            logs.append(LogEntry(
                file=log_file.name,
                content=content
            ))
        except Exception:
            continue
    
    return {"logs": logs}


def run_writers_background(task_id: str, prompt_file: Path):
    """Background task to run dual writers."""
    try:
        asyncio.run(launch_dual_writers(task_id, prompt_file, resume_mode=False))
    except Exception as e:
        print(f"Error running writers: {e}")


def run_panel_background(task_id: str, prompt_file: Path, review_type: str):
    """Background task to run judge panel."""
    try:
        asyncio.run(launch_judge_panel(task_id, prompt_file, review_type=review_type, resume_mode=False))
    except Exception as e:
        print(f"Error running panel: {e}")


@router.post("/tasks/{task_id}/writers")
async def start_writers(
    task_id: str,
    request: WriterRequest,
    background_tasks: BackgroundTasks
):
    """Start dual writers for a task."""
    prompt_path = Path(request.prompt_file)
    
    if not prompt_path.exists():
        raise HTTPException(status_code=404, detail=f"Prompt file not found: {request.prompt_file}")
    
    background_tasks.add_task(
        run_writers_background,
        task_id,
        prompt_path
    )
    
    return {
        "status": "started",
        "task_id": task_id,
        "message": "Dual writers launching in background"
    }


@router.post("/tasks/{task_id}/panel")
async def start_panel(
    task_id: str,
    request: PanelRequest,
    background_tasks: BackgroundTasks
):
    """Start judge panel for a task."""
    prompt_path = Path(request.prompt_file)
    
    if not prompt_path.exists():
        raise HTTPException(status_code=404, detail=f"Prompt file not found: {request.prompt_file}")
    
    background_tasks.add_task(
        run_panel_background,
        task_id,
        prompt_path,
        request.review_type
    )
    
    return {
        "status": "started",
        "task_id": task_id,
        "message": f"Judge panel launching in background (review_type: {request.review_type})"
    }


@router.post("/tasks/{task_id}/feedback")
async def send_feedback(task_id: str, request: FeedbackRequest, background_tasks: BackgroundTasks):
    """Send feedback to a writer."""
    from ...commands.feedback import send_feedback_async
    from ...core.session import load_session
    from ...core.config import PROJECT_ROOT, get_worktree_path, WRITER_LETTERS
    
    if request.writer not in ["sonnet", "codex"]:
        raise HTTPException(status_code=400, detail="Writer must be 'sonnet' or 'codex'")
    
    writer_letter = WRITER_LETTERS[request.writer]
    session_id = load_session(f"WRITER_{writer_letter}", task_id)
    
    if not session_id:
        raise HTTPException(status_code=404, detail=f"No session found for writer {request.writer}")
    
    project_name = Path(PROJECT_ROOT).name
    worktree = get_worktree_path(project_name, request.writer, task_id)
    
    if not worktree.exists():
        raise HTTPException(status_code=404, detail=f"Worktree not found for writer {request.writer}")
    
    temp_feedback_path = Path(PROJECT_ROOT) / ".prompts" / f"temp-feedback-{task_id}-{request.writer}.md"
    temp_feedback_path.parent.mkdir(parents=True, exist_ok=True)
    temp_feedback_path.write_text(request.feedback)
    
    def run_feedback_background():
        try:
            asyncio.run(send_feedback_async(request.writer, task_id, temp_feedback_path, session_id, worktree))
        except Exception as e:
            print(f"Error sending feedback: {e}")
    
    background_tasks.add_task(run_feedback_background)
    
    return {
        "status": "sent",
        "task_id": task_id,
        "writer": request.writer,
        "message": f"Feedback being sent to writer {request.writer} in background"
    }
