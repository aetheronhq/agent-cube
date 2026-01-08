"""Writer metadata storage."""

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

from .config import PROJECT_ROOT


@dataclass
class WriterMetadata:
    """Metadata about the writer that created a branch."""

    name: str
    model: str
    label: str
    color: str
    key: str


def _get_metadata_path(writer_name: str, task_id: str) -> Path:
    """Get path for writer metadata file."""
    return PROJECT_ROOT / ".prompts" / "writers" / f"{writer_name}-{task_id}.json"


def save_writer_metadata(writer_name: str, task_id: str, metadata: WriterMetadata) -> None:
    """Save writer metadata to .prompts/writers/."""
    path = _get_metadata_path(writer_name, task_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(metadata), indent=2))


def load_writer_metadata(writer_name: str, task_id: str) -> Optional[WriterMetadata]:
    """Load writer metadata if it exists."""
    path = _get_metadata_path(writer_name, task_id)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        return WriterMetadata(**data)
    except (json.JSONDecodeError, TypeError, KeyError):
        return None
