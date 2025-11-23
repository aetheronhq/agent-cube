"""Parse and aggregate judge decisions from JSON files."""

import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

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

def get_decision_file_path(judge_key: str, task_id: str) -> Path:
    """Get the path to a judge's decision JSON file."""
    from .decision_files import find_decision_file
    
    found = find_decision_file(judge_key, task_id, "decision")
    if found:
        return found
    
    return PROJECT_ROOT / ".prompts" / "decisions" / f"{judge_key.replace('_', '-')}-{task_id}-decision.json"

def parse_judge_decision(judge_key: str, task_id: str) -> Optional[JudgeDecision]:
    """Parse a single judge's decision JSON file with flexible format support."""
    decision_file = get_decision_file_path(judge_key, task_id)
    
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
        
        # Extract decision (try top-level, then nested)
        decision = data.get("decision")
        if not decision and "panel_recommendation" in data:
            decision = data["panel_recommendation"].get("final_decision", "APPROVED")
        if not decision:
            decision = "UNKNOWN"
        
        # Extract winner (try top-level, then nested, normalize format)
        winner = data.get("winner")
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
        
        # Extract total score (try multiple field names)
        total_a = scores_a.get("total_weighted") or scores_a.get("total")
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
            recommendation=recommendation[:200],  # Truncate long recommendations
            timestamp=data.get("timestamp", "")
        )
    except (json.JSONDecodeError, Exception) as e:
        raise RuntimeError(f"Invalid decision file for Judge {judge_key}: {e}\nFile: {decision_file}")

def parse_all_decisions(task_id: str) -> List[JudgeDecision]:
    """Parse all judge decisions for a task."""
    from .user_config import get_judge_configs
    
    decisions = []
    judge_configs = get_judge_configs()
    
    for jconfig in judge_configs:
        decision = parse_judge_decision(jconfig.key, task_id)
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


