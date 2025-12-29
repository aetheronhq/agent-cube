"""Session ID tracking and storage."""

import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple
import time

from .config import get_sessions_dir

def save_session(session_type: str, task_id: str, session_id: str, metadata: Optional[str] = None) -> None:
    """Save a session ID to a file."""
    sessions_dir = get_sessions_dir()
    sessions_dir.mkdir(exist_ok=True)
    
    session_file = sessions_dir / f"{session_type}_{task_id}_SESSION_ID.txt"
    session_file.write_text(session_id)
    
    if metadata:
        meta_file = sessions_dir / f"{session_type}_{task_id}_SESSION_ID.txt.meta"
        meta_file.write_text(f"# {metadata}\n")

def load_session(session_type: str, task_id: str) -> Optional[str]:
    """Load a session ID from a file."""
    sessions_dir = get_sessions_dir()
    session_file = sessions_dir / f"{session_type}_{task_id}_SESSION_ID.txt"
    
    if not session_file.exists():
        return None
    
    return session_file.read_text().strip()

def list_sessions() -> List[Tuple[str, str, Optional[str]]]:
    """List all sessions with their IDs and metadata."""
    sessions_dir = get_sessions_dir()
    
    if not sessions_dir.exists():
        return []
    
    sessions = []
    for session_file in sessions_dir.glob("*_SESSION_ID.txt"):
        name = session_file.stem.replace("_SESSION_ID", "")
        session_id = session_file.read_text().strip()
        
        meta_file = session_file.with_suffix(".txt.meta")
        metadata = None
        if meta_file.exists():
            metadata = meta_file.read_text().strip().replace("# ", "")
        
        sessions.append((name, session_id, metadata))
    
    return sessions

def session_exists(session_type: str, task_id: str) -> bool:
    """Check if a session file exists."""
    sessions_dir = get_sessions_dir()
    session_file = sessions_dir / f"{session_type}_{task_id}_SESSION_ID.txt"
    return session_file.exists()

class SessionWatcher:
    """Background watcher to save session IDs immediately when they appear in logs."""
    
    def __init__(self, log_file: Path, session_file: Path, metadata: str):
        self.log_file = log_file
        self.session_file = session_file
        self.metadata = metadata
        self.stop_event = threading.Event()
        self.thread: Optional[threading.Thread] = None
    
    def start(self) -> None:
        """Start watching the log file for session ID."""
        self.thread = threading.Thread(target=self._watch, daemon=True)
        self.thread.start()
    
    def stop(self) -> None:
        """Stop the watcher thread."""
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=1.0)
    
    def _watch(self) -> None:
        """Watch the log file for session ID."""
        while not self.log_file.exists() and not self.stop_event.is_set():
            time.sleep(0.1)
        
        if self.stop_event.is_set():
            return
        
        session_id = None
        while not session_id and not self.stop_event.is_set():
            try:
                content = self.log_file.read_text()
                import json
                for line in content.splitlines():
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if "session_id" in data:
                            session_id = data["session_id"]
                            break
                    except json.JSONDecodeError:
                        continue
            except Exception:
                pass
            
            if not session_id:
                time.sleep(0.1)
        
        if session_id and not self.stop_event.is_set():
            self.session_file.parent.mkdir(exist_ok=True)
            self.session_file.write_text(session_id)
            
            meta_file = Path(str(self.session_file) + ".meta")
            meta_file.write_text(f"# {self.metadata}\n")

