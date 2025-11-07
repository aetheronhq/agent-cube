"""Parse and aggregate judge decisions from JSON files."""

import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from .config import PROJECT_ROOT

@dataclass
class JudgeDecision:
    """Parsed decision from a judge."""
    judge: int
    task_id: str
    decision: str
    winner: str
    scores_a: float
    scores_b: float
    blocker_issues: List[str]
    recommendation: str
    timestamp: str

def get_decision_file_path(judge_num: int, task_id: str) -> Path:
    """Get the path to a judge's decision JSON file."""
    return PROJECT_ROOT / ".prompts" / "decisions" / f"judge-{judge_num}-{task_id}-decision.json"

def parse_judge_decision(judge_num: int, task_id: str) -> Optional[JudgeDecision]:
    """Parse a single judge's decision JSON file."""
    decision_file = get_decision_file_path(judge_num, task_id)
    
    if not decision_file.exists():
        return None
    
    try:
        with open(decision_file) as f:
            data = json.load(f)
        
        return JudgeDecision(
            judge=data["judge"],
            task_id=data["task_id"],
            decision=data["decision"],
            winner=data["winner"],
            scores_a=data["scores"]["writer_a"]["total_weighted"],
            scores_b=data["scores"]["writer_b"]["total_weighted"],
            blocker_issues=data.get("blocker_issues", []),
            recommendation=data["recommendation"],
            timestamp=data.get("timestamp", "")
        )
    except (json.JSONDecodeError, KeyError, Exception) as e:
        raise RuntimeError(f"Invalid decision file for Judge {judge_num}: {e}")

def parse_all_decisions(task_id: str) -> List[JudgeDecision]:
    """Parse all judge decisions for a task."""
    decisions = []
    
    for judge_num in [1, 2, 3]:
        decision = parse_judge_decision(judge_num, task_id)
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
    
    a_wins = sum(1 for d in decisions if d.winner == "A")
    b_wins = sum(1 for d in decisions if d.winner == "B")
    ties = sum(1 for d in decisions if d.winner == "TIE")
    
    avg_score_a = sum(d.scores_a for d in decisions) / len(decisions)
    avg_score_b = sum(d.scores_b for d in decisions) / len(decisions)
    
    all_blockers = []
    for d in decisions:
        all_blockers.extend(d.blocker_issues)
    
    winner = "B" if b_wins > a_wins else ("A" if a_wins > b_wins else "TIE")
    
    if approvals >= 2 and not all_blockers:
        next_action = "MERGE"
    elif approvals >= 2 and all_blockers:
        next_action = "SYNTHESIS"
    elif request_changes >= 2:
        next_action = "FEEDBACK"
    else:
        next_action = "REVIEW"
    
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


