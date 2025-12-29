"""Parse and aggregate judge decisions from JSON files."""

import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Union

from .config import PROJECT_ROOT

@dataclass
class JudgeDecision:
    """Parsed decision from a judge."""
    judge: str
    task_id: str
    decision: str
    winner: str
    scores_a: float
    scores_b: float
    blocker_issues: List[str]
    recommendation: str
    timestamp: str

def get_decision_file_path(
    judge_key: str, 
    task_id: str,
    project_root: Optional[Union[str, Path]] = None,
    review_type: str = "decision"
) -> Path:
    """Get the path to a judge's decision JSON file."""
    from .decision_files import find_decision_file
    
    root = Path(project_root) if project_root else PROJECT_ROOT
    
    found = find_decision_file(judge_key, task_id, review_type, project_root=root)
    if found:
        return found
    
    return root / ".prompts" / "decisions" / f"{judge_key.replace('_', '-')}-{task_id}-{review_type}.json"


def parse_single_decision_file(filepath: Path) -> Optional[Dict[str, Any]]:
    """Parse a single decision JSON file and return raw data.
    
    Returns None if file doesn't exist or is invalid JSON.
    Use this when you need raw JSON data, not a JudgeDecision object.
    """
    if not filepath.exists():
        return None
    try:
        with open(filepath) as f:
            result: Dict[str, Any] = json.load(f)
            return result
    except json.JSONDecodeError:
        return None


def parse_judge_decision(
    judge_key: str, 
    task_id: str,
    project_root: Optional[Union[str, Path]] = None,
    review_type: str = "decision"
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
        if isinstance(winner, str):
            winner_lower = winner.lower()
            if "writer_a" in winner_lower or winner_lower == "a":
                winner = "writer_a"
            elif "writer_b" in winner_lower or winner_lower == "b":
                winner = "writer_b"
            else:
                winner = "TIE"
        
        # Extract scores (try standard location, then nested reviews)
        scores_a = data.get("scores", {}).get("writer_a", {})
        scores_b = data.get("scores", {}).get("writer_b", {})
        
        # If scores not in standard location, try nested reviews
        if not scores_a and "reviews" in data:
            scores_a = data["reviews"].get("writer_a", {}).get("scores", {})
            scores_b = data["reviews"].get("writer_b", {}).get("scores", {})
        
        # Extract total score (try multiple field names and locations)
        total_a = scores_a.get("total_weighted") or scores_a.get("total")
        if total_a is None and "total_score" in data:
            total_a = data["total_score"].get("writer_a")
        if total_a is None:
            # Calculate from individual scores
            total_a = sum([
                scores_a.get("kiss_compliance", 0),
                scores_a.get("architecture", 0),
                scores_a.get("type_safety", 0),
                scores_a.get("tests", 0),
                scores_a.get("production_ready", 0)
            ]) / 5.0
        
        total_b = scores_b.get("total_weighted") or scores_b.get("total")
        if total_b is None and "total_score" in data:
            total_b = data["total_score"].get("writer_b")
        if total_b is None:
            # Calculate from individual scores
            total_b = sum([
                scores_b.get("kiss_compliance", 0),
                scores_b.get("architecture", 0),
                scores_b.get("type_safety", 0),
                scores_b.get("tests", 0),
                scores_b.get("production_ready", 0)
            ]) / 5.0
        
        # Extract blocker issues (try multiple locations)
        blockers = data.get("blocker_issues", [])
        # Also check remaining_issues (used in peer-review)
        remaining = data.get("remaining_issues", [])
        if remaining and isinstance(remaining, list):
            blockers = blockers + remaining
        if not blockers and "reviews" in data:
            blockers_a = data["reviews"].get("writer_a", {}).get("critical_issues", [])
            blockers_b = data["reviews"].get("writer_b", {}).get("critical_issues", [])
            blockers = blockers_a + blockers_b
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
            scores_a=float(total_a),
            scores_b=float(total_b),
            blocker_issues=blockers,
            recommendation=recommendation,
            timestamp=data.get("timestamp", "")
        )
    except (json.JSONDecodeError, Exception) as e:
        raise RuntimeError(f"Invalid decision file for Judge {judge_key}: {e}\nFile: {decision_file}")

def parse_all_decisions(
    task_id: str,
    project_root: Optional[Union[str, Path]] = None,
    review_type: str = "decision"
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
        return {
            "consensus": False,
            "winner": None,
            "next_action": "ERROR",
            "message": "No decisions found"
        }
    
    approvals = sum(1 for d in decisions if d.decision == "APPROVED")
    request_changes = sum(1 for d in decisions if d.decision == "REQUEST_CHANGES")
    rejections = sum(1 for d in decisions if d.decision == "REJECTED")
    
    # Normalize winner field (supports "A", "writer_a", "Writer A", etc.)
    a_wins = sum(1 for d in decisions if d.winner and d.winner.upper() in ["A", "WRITER_A", "WRITER A"])
    b_wins = sum(1 for d in decisions if d.winner and d.winner.upper() in ["B", "WRITER_B", "WRITER B"])
    ties = sum(1 for d in decisions if d.winner and d.winner.upper() == "TIE")
    
    avg_score_a = sum(d.scores_a for d in decisions) / len(decisions)
    avg_score_b = sum(d.scores_b for d in decisions) / len(decisions)
    
    all_blockers = []
    for d in decisions:
        all_blockers.extend(d.blocker_issues)
    
    winner = "writer_b" if b_wins > a_wins else ("writer_a" if a_wins > b_wins else "TIE")
    
    has_clear_winner = (a_wins >= 2 or b_wins >= 2)
    
    if winner == "TIE":
        next_action = "FEEDBACK"  # Both writers need changes
    elif has_clear_winner and all_blockers:
        next_action = "SYNTHESIS"  # Winner needs changes
    elif has_clear_winner and not all_blockers:
        next_action = "MERGE"  # Winner is ready
    elif approvals >= 2 and not all_blockers:
        next_action = "MERGE"  # Majority approved
    else:
        # Fallback: not has_clear_winner or other edge cases
        next_action = "FEEDBACK"
    
    return {
        "consensus": approvals >= 2,
        "winner": winner,
        "avg_score_a": round(avg_score_a, 2),
        "avg_score_b": round(avg_score_b, 2),
        "votes": {
            "approve": approvals,
            "request_changes": request_changes,
            "reject": rejections
        },
        "winner_votes": {
            "a": a_wins,
            "b": b_wins,
            "tie": ties
        },
        "blocker_issues": all_blockers,
        "next_action": next_action,
        "decisions": decisions
    }


def get_peer_review_status(
    task_id: str,
    project_root: Optional[Union[str, Path]] = None,
    require_decisions: bool = True
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
            jconfig.key, task_id, 
            project_root=project_root, 
            review_type="peer-review"
        )
        
        data = parse_single_decision_file(decision_file)
        if data is None:
            continue
            
        decisions_found += 1
        decision = data.get("decision", "UNKNOWN")
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
        "judge_decisions": judge_decisions
    }
