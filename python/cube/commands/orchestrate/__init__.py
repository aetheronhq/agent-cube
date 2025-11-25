"""Orchestrate command - split into modules."""

from .phases import orchestrate_auto_command
from .prompts import orchestrate_prompt_command
from .utils import extract_task_id_from_file

__all__ = [
    'orchestrate_auto_command',
    'orchestrate_prompt_command',
    'extract_task_id_from_file'
]
