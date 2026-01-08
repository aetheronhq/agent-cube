"""Parse and aggregate judge decisions from JSON files."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .config import PROJECT_ROOT


def normalize_decision(decision: str) -> str:
    """Normalize decision string to canonical form."""
    d = decision.strip().upper()
    if d in ("APPROVE", "APPROVED"):
        return "APPROVED"
    if d in ("REJECT", "REJECTED"):
        return "REJECTED"
    if d in ("REQUEST_CHANGE", "REQUEST_CHANGES", "CHANGES_REQUESTED"):
        return "REQUEST_CHANGES"
    if d in ("SKIP", "SKIPPED"):
        return "SKIPPED"
    return d


def normalize_winner(winner_str: str) -> str:
    """Normalize winner string to config key."""
    from .user_config import load_config

    if not winner_str:
        return "TIE"

    config = load_config()
    winner_lower = winner_str.lower()

    # Handle key formats
    for key in config.writer_order:
        if key in winner_lower or winner_lower.replace(" ", "_") == key:
            return key

    return "TIE"


@dataclass
class JudgeDecision:
    """Parsed decision from a judge."""

    judge: str
    task_id: str
    decision: str
    winner: str
    scores: Dict[str, float]
    blocker_issues: List[str]
    recommendation: str
    timestamp: str


def get_decision_file_path(
    judge_key: str, task_id: str, project_root: Optional[Union[str, Path]] = None, review_type: str = "decision"
) -> Path:
    """Get the path to a judge's decision JSON file."""
    from .decision_files import find_decision_file

    root = Path(project_root) if project_root else PROJECT_ROOT

    found = find_decision_file(judge_key, task_id, review_type, project_root=root)
    if found:
        return found

    # Check both underscore and hyphen variants (judge_1 vs judge-1)
    decisions_dir = root / ".prompts" / "decisions"
    for variant in [judge_key, judge_key.replace("_", "-")]:
        path = decisions_dir / f"{variant}-{task_id}-{review_type}.json"
        if path.exists():
            return path

    return decisions_dir / f"{judge_key}-{task_id}-{review_type}.json"


def parse_single_decision_file(filepath: Path) -> Optional[Dict[str, Any]]:
    """Parse a single decision JSON file and return raw data.

    Returns None if file doesn't exist or is invalid JSON.
    Use this when you need raw JSON data, not a JudgeDecision object.
    """
    if not filepath.exists():
        return None
    try:
        with open(filepath) as f:
            return json.load(f)
    except json.JSONDecodeError:
        return None


def parse_judge_decision(
    judge_key: str, task_id: str, project_root: Optional[Union[str, Path]] = None, review_type: str = "decision"
) -> Optional[JudgeDecision]:
    """Parse a single judge's decision JSON file with flexible format support."""
    decision_file = get_decision_file_path(judge_key, task_id, project_root=project_root, review_type=review_type)

    if not decision_file.exists():
        return None

    try:
        with open(decision_file) as f:
            data = json.load(f)

        # Extract judge key (flexible field names)
        judge_id = data.get("judge")
        if judge_id is None:
            judge_id = data.get("judge_id", judge_key)

        # Ensure judge_id is a string
        if not isinstance(judge_id, str):
            judge_id = str(judge_id)

        # Extract decision (try top-level, then nested, then infer)
        decision = data.get("decision")
        if not decision and "panel_recommendation" in data:
            decision = data["panel_recommendation"].get("final_decision", "APPROVED")
        if not decision and (data.get("vote") or data.get("winner")):
            decision = "APPROVED"  # If they voted, assume approved
        if not decision:
            decision = "UNKNOWN"
        if not decision:
            decision = "UNKNOWN"

        # Extract winner (try winner, vote, or nested fields)
        winner = data.get("winner") or data.get("vote")
        if not winner and "panel_recommendation" in data:
            winner = data["panel_recommendation"].get("selected_writer", "TIE")
        if not winner and "comparison" in data:
            winner = data["comparison"].get("better_implementation", "TIE")

        # Normalize winner format to writer keys
        winner = normalize_winner(winner)

        from .user_config import load_config

        config = load_config()

        scores = {}
        for writer_key in config.writer_order:
            writer_scores = data.get("scores", {}).get(writer_key, {})

            # If scores not in standard location, try nested reviews
            if not writer_scores and "reviews" in data:
                writer_scores = data["reviews"].get(writer_key, {}).get("scores", {})

            total = writer_scores.get("total_weighted") or writer_scores.get("total")
            if total is None and "total_score" in data:
                total = data["total_score"].get(writer_key)

            if total is None:
                # Calculate from individual scores
                score_components = [
                    writer_scores.get("kiss_compliance", 0),
                    writer_scores.get("architecture", 0),
                    writer_scores.get("type_safety", 0),
                    writer_scores.get("tests", 0),
                    writer_scores.get("production_ready", 0),
                ]
                total = sum(score_components) / len(score_components) if score_components else 0
            scores[writer_key] = float(total)

        # Extract blocker issues (try multiple locations)
        blockers = data.get("blocker_issues", [])
        # Also check remaining_issues (used in peer-review)
        remaining = data.get("remaining_issues", [])
        if remaining and isinstance(remaining, list):
            blockers = blockers + remaining
        if not blockers and "reviews" in data:
            blockers_all = []
            for writer_key in config.writer_order:
                blockers_all.extend(data["reviews"].get(writer_key, {}).get("critical_issues", []))
            blockers = blockers_all
        if not isinstance(blockers, list):
            blockers = [str(blockers)] if blockers else []

        # Extract recommendation (try multiple locations)
        recommendation = data.get("recommendation")
        if not recommendation and "panel_recommendation" in data:
            recommendation = data["panel_recommendation"].get("reasoning", "No recommendation provided")
        if not recommendation and "comparison" in data:
            recommendation = data["comparison"].get("rationale", "No recommendation provided")
        if not recommendation and "summary" in data:
            recommendation = data.get("summary")
        if not recommendation and "rationale" in data:
            recommendation = data.get("rationale")

        # If recommendation is too short and we have blockers, include them
        if (not recommendation or len(recommendation) < 50) and blockers:
            issues_text = "\n".join(f"• {b}" for b in blockers[:5])
            if recommendation:
                recommendation = f"{recommendation}\n\nIssues:\n{issues_text}"
            else:
                recommendation = f"Issues to address:\n{issues_text}"

        if not recommendation:
            recommendation = "No recommendation provided"

        return JudgeDecision(
            judge=judge_id,
            task_id=data.get("task_id", task_id),
            decision=decision,
            winner=winner,
            scores=scores,
            blocker_issues=blockers,
            recommendation=recommendation,
            timestamp=data.get("timestamp", ""),
        )
    except (json.JSONDecodeError, Exception) as e:
        raise RuntimeError(f"Invalid decision file for Judge {judge_key}: {e}\nFile: {decision_file}")


def parse_all_decisions(
    task_id: str, project_root: Optional[Union[str, Path]] = None, review_type: str = "decision"
) -> List[JudgeDecision]:
    """Parse all judge decisions for a task.

    Args:
        task_id: Task identifier
        project_root: Optional project root path
        review_type: 'decision' for panel, 'peer-review' for peer review
    """
    from .user_config import get_judge_configs

    decisions = []
    judge_configs = get_judge_configs()

    for jconfig in judge_configs:
        decision = parse_judge_decision(jconfig.key, task_id, project_root=project_root, review_type=review_type)
        if decision:
            decisions.append(decision)

    return decisions


def aggregate_decisions(decisions: List[JudgeDecision]) -> Dict[str, Any]:
    """Aggregate judge decisions into final verdict."""
    if not decisions:
        return {"consensus": False, "winner": None, "next_action": "ERROR", "message": "No decisions found"}

    from .user_config import load_config

    config = load_config()

    approvals = sum(1 for d in decisions if normalize_decision(d.decision) == "APPROVED")
    request_changes = sum(1 for d in decisions if normalize_decision(d.decision) == "REQUEST_CHANGES")
    rejections = sum(1 for d in decisions if normalize_decision(d.decision) == "REJECTED")

    # Normalize winner field
    winner_votes = {key: 0 for key in config.writer_order}
    winner_votes["TIE"] = 0

    for d in decisions:
        winner_key = normalize_winner(d.winner)
        if winner_key in winner_votes:
            winner_votes[winner_key] += 1

    avg_scores = {}
    for key in config.writer_order:
        scores = [d.scores.get(key, 0) for d in decisions]
        avg_scores[f"avg_score_{key}"] = round(sum(scores) / len(decisions), 2)

    all_blockers = []
    for d in decisions:
        all_blockers.extend(d.blocker_issues)

    # Determine winner by votes
    sorted_winners = sorted(winner_votes.items(), key=lambda item: item[1], reverse=True)

    # If no votes (e.g. all empty or invalid), default to TIE
    if not sorted_winners or sorted_winners[0][1] == 0:
        winner = "TIE"
        has_clear_winner = False
    else:
        winner = sorted_winners[0][0]
        has_clear_winner = sorted_winners[0][1] >= 2

    # Determine next action - always SYNTHESIS
    # all_approved flag indicates synthesis phase can skip itself
    # TIE case handled in synthesis phase (generates feedback, prompts re-run)
    all_approved = False
    if winner == "TIE":
        next_action = "SYNTHESIS"  # TIE - phase 6 handles feedback
    elif has_clear_winner and all_blockers:
        next_action = "SYNTHESIS"  # Winner needs changes
    elif has_clear_winner and not all_blockers:
        next_action = "SYNTHESIS"  # Winner ready - synthesis will skip
        all_approved = True
    elif approvals >= 2 and not all_blockers:
        next_action = "SYNTHESIS"  # Majority approved - synthesis will skip
        all_approved = True
    else:
        next_action = "SYNTHESIS"  # Edge case - phase 6 will handle

    result = {
        "consensus": approvals >= 2,
        "winner": winner,
        "votes": {"approve": approvals, "request_changes": request_changes, "reject": rejections},
        "winner_votes": winner_votes,
        "blocker_issues": all_blockers,
        "next_action": next_action,
        "all_approved": all_approved,
        "decisions": decisions,
    }
    result.update(avg_scores)
    return result


def get_peer_review_status(
    task_id: str, project_root: Optional[Union[str, Path]] = None, require_decisions: bool = True
) -> Dict[str, Any]:
    """Get peer review approval status and remaining issues.

    Args:
        task_id: Task identifier
        project_root: Optional project root path
        require_decisions: If True, warn when no decisions found (unused here, handled by caller)

    Returns:
        {
            "approved": bool,
            "remaining_issues": List[str],
            "decisions_found": int,
            "approvals": int,
            "judge_decisions": Dict[str, str]  # judge_key -> decision
        }
    """
    from .user_config import get_judge_configs

    all_issues = []
    approvals = 0
    decisions_found = 0
    judge_decisions = {}

    judge_configs = get_judge_configs()

    for jconfig in judge_configs:
        decision_file = get_decision_file_path(
            jconfig.key, task_id, project_root=project_root, review_type="peer-review"
        )

        data = parse_single_decision_file(decision_file)
        if data is None:
            continue

        decisions_found += 1
        decision = normalize_decision(data.get("decision", "UNKNOWN"))
        remaining = data.get("remaining_issues", [])
        blockers = data.get("blocker_issues", [])
        issues = remaining + blockers

        judge_decisions[jconfig.key] = decision

        if issues:
            all_issues.extend(issues)

        if decision == "APPROVED":
            approvals += 1
        elif decision == "SKIPPED":
            approvals += 1  # Tool failure, not a code issue

    return {
        "approved": approvals == decisions_found and decisions_found > 0,
        "remaining_issues": all_issues,
        "decisions_found": decisions_found,
        "approvals": approvals,
        "judge_decisions": judge_decisions,
    }
