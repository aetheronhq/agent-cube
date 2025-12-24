"""Orchestration package exports."""

import importlib.util
from pathlib import Path

from .decisions import run_decide_and_get_result, run_decide_peer_review
from .phases import run_synthesis, run_peer_review, run_minor_fixes, generate_dual_feedback
from .prompts import generate_orchestrator_prompt, generate_writer_prompt, generate_panel_prompt
from .pr import create_pr
from .workflow import _orchestrate_auto_impl

_ENTRY_PATH = Path(__file__).resolve().parent.parent / "orchestrate.py"
_ENTRY_SPEC = importlib.util.spec_from_file_location("cube.commands._orchestrate_entry", _ENTRY_PATH)
if _ENTRY_SPEC and _ENTRY_SPEC.loader:
    _entry_module = importlib.util.module_from_spec(_ENTRY_SPEC)
    _ENTRY_SPEC.loader.exec_module(_entry_module)

    orchestrate_prompt_command = _entry_module.orchestrate_prompt_command
    orchestrate_auto_command = _entry_module.orchestrate_auto_command
    extract_task_id_from_file = _entry_module.extract_task_id_from_file
else:
    raise ImportError(f"Unable to load orchestrate entry module from {_ENTRY_PATH}")

__all__ = [
    "orchestrate_prompt_command",
    "orchestrate_auto_command",
    "extract_task_id_from_file",
    "run_decide_and_get_result",
    "run_decide_peer_review",
    "run_synthesis",
    "run_peer_review",
    "run_minor_fixes",
    "generate_dual_feedback",
    "generate_orchestrator_prompt",
    "generate_writer_prompt",
    "generate_panel_prompt",
    "create_pr",
    "_orchestrate_auto_impl",
]
