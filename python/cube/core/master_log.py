"""Master logging for all agent activity."""

import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import contextlib

_master_log_instance: Optional["MasterLog"] = None
_master_log_lock = threading.Lock()


class MasterLog:
    """Centralized logging for all agent activity during a task."""
    
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.log_dir = Path.home() / ".cube" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / f"master-{task_id}.log"
        self._file_handle = None
        self._lock = threading.Lock()
    
    def __enter__(self):
        self._file_handle = open(self.log_file, "a", encoding="utf-8", buffering=1)
        self._write_entry("system", "master_log_start", {"task_id": self.task_id, "timestamp": datetime.now().isoformat()})
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self._write_entry("system", "master_log_error", {"error_type": exc_type.__name__, "error_message": str(exc_val)})
        self._write_entry("system", "master_log_end", {"task_id": self.task_id, "success": exc_type is None})
        if self._file_handle:
            self._file_handle.close()
        global _master_log_instance
        with _master_log_lock:
            _master_log_instance = None
    
    def _write_entry(self, agent: str, event_type: str, data: Dict[str, Any]):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "event_type": event_type,
            "data": data
        }
        with self._lock:
            if self._file_handle:
                self._file_handle.write(json.dumps(entry) + "\n")
    
    def write_raw_line(self, agent_id: str, line: str):
        """Log a raw output line from an agent."""
        self._write_entry(agent_id, "raw_output", {"line": line})
    
    def write_phase_start(self, phase: int, phase_name: str):
        """Log the start of a workflow phase."""
        self._write_entry("orchestrator", "phase_start", {"phase": phase, "phase_name": phase_name})
    
    def write_phase_end(self, phase: int, phase_name: str, success: bool):
        """Log the end of a workflow phase."""
        self._write_entry("orchestrator", "phase_end", {"phase": phase, "phase_name": phase_name, "success": success})
    
    def write_agent_start(self, agent_type: str, agent_name: str, agent_id: str, model: str, task_id: str, **kwargs):
        """Log an agent starting."""
        self._write_entry(agent_id, "agent_start", {
            "agent_type": agent_type,
            "agent_name": agent_name,
            "agent_id": agent_id,
            "model": model,
            "task_id": task_id,
            **kwargs
        })
    
    def write_agent_end(self, agent_id: str, success: bool, **kwargs):
        """Log an agent finishing."""
        self._write_entry(agent_id, "agent_end", {"success": success, **kwargs})
    
    def write_error(self, agent_id: str, error_type: str, error_message: str):
        """Log an error."""
        self._write_entry(agent_id, "error", {"error_type": error_type, "error_message": error_message})


@contextlib.contextmanager
def master_log_context(task_id: str):
    """Context manager for master logging during a task."""
    global _master_log_instance
    with _master_log_lock:
        if _master_log_instance is None:
            _master_log_instance = MasterLog(task_id)
        elif _master_log_instance.task_id != task_id:
            raise RuntimeError(f"MasterLog already active for task {_master_log_instance.task_id}")
        current_instance = _master_log_instance
        # Hold lock while entering context to prevent race condition
        with current_instance as log:
            yield log


def get_master_log() -> Optional[MasterLog]:
    """Get the current master log instance if one exists."""
    with _master_log_lock:
        return _master_log_instance
