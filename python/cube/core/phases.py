"""Phase alias utilities for resume commands."""

from __future__ import annotations

import re
from typing import Dict, List, Sequence

PhaseAliasGroup = tuple[int, Sequence[str]]


_PHASE_ALIAS_GROUPS: List[PhaseAliasGroup] = [
    (1, ("writer-prompt", "prompt", "prep")),
    (2, ("writers", "dual-writers", "execution")),
    (3, ("panel-prompt", "judges-prompt", "review-prompt")),
    (4, ("panel", "judges", "review")),
    (5, ("feedback-prompt", "decide", "decisions", "aggregate")),
    (6, ("synthesis", "feedback", "pr")),
    (7, ("peer-review", "peer", "peer-panel")),
    (8, ("final-decision", "final", "approval")),
    (9, ("minor-fixes", "fixes", "patch")),
    (10, ("final-peer", "peer-review-2", "peer2")),
]

PHASE_ALIASES: Dict[str, int] = {
    alias: number
    for number, aliases in _PHASE_ALIAS_GROUPS
    for alias in aliases
}

MAX_PHASE = 10


def normalize_alias(value: str) -> str:
    """Normalize user input to match alias keys."""
    return value.strip().lower().replace("_", "-").replace(" ", "-")


def resolve_phase_identifier(value: str) -> int:
    """Resolve a phase number from numeric or alias input."""
    normalized = normalize_alias(value)

    if normalized.isdigit():
        phase = int(normalized)
    else:
        phase_match = re.fullmatch(r"phase-?(\d+)", normalized)
        if phase_match:
            phase = int(phase_match.group(1))
        else:
            phase = PHASE_ALIASES.get(normalized, 0)

    if phase < 1 or phase > MAX_PHASE:
        alias_list = ", ".join(sorted(PHASE_ALIASES.keys()))
        raise ValueError(
            f"Unknown phase '{value}'. Use 1-{MAX_PHASE} or alias ({alias_list})."
        )

    return phase


def format_phase_aliases() -> str:
    """Return a short summary string of primary aliases for help text."""
    return ", ".join(f"{aliases[0]}={number}" for number, aliases in _PHASE_ALIAS_GROUPS)


