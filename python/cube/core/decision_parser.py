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
    primary_path = PROJECT_ROOT / ".prompts" / "decisions" / f"judge-{judge_num}-{task_id}-decision.json"
    
    if primary_path.exists():
        return primary_path
    
    from .config import WORKTREE_BASE
    gemini_path = WORKTREE_BASE.parent / ".prompts" / "decisions" / f"judge-{judge_num}-{task_id}-decision.json"
    
    if gemini_path.exists():
        import shutil
        primary_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(gemini_path, primary_path)
        return primary_path
    
    return primary_path

def parse_judge_decision(judge_num: int, task_id: str) -> Optional[JudgeDecision]:
    """Parse a single judge's decision JSON file."""
    decision_file = get_decision_file_path(judge_num, task_id)
    
    if not decision_file.exists():
        return None
    
    try:
        with open(decision_file) as f:
            data = json.load(f)
        
        scores_a = data.get("scores", {}).get("writer_a", {})
        scores_b = data.get("scores", {}).get("writer_b", {})
        
        total_a = scores_a.get("total_weighted")
        if total_a is None:
            total_a = sum([
                scores_a.get("kiss_compliance", 0),
                scores_a.get("architecture", 0),
                scores_a.get("type_safety", 0),
                scores_a.get("tests", 0),
                scores_a.get("production_ready", 0)
            ]) / 5.0
        
        total_b = scores_b.get("total_weighted")
        if total_b is None:
            total_b = sum([
                scores_b.get("kiss_compliance", 0),
                scores_b.get("architecture", 0),
                scores_b.get("type_safety", 0),
                scores_b.get("tests", 0),
                scores_b.get("production_ready", 0)
            ]) / 5.0
        
        blockers = data.get("blocker_issues", [])
        if not isinstance(blockers, list):
            blockers = [str(blockers)] if blockers else []
        
        return JudgeDecision(
            judge=data.get("judge", judge_num),
            task_id=data.get("task_id", task_id),
            decision=data.get("decision", "UNKNOWN"),
            winner=data.get("winner", "TIE"),
            scores_a=float(total_a),
            scores_b=float(total_b),
            blocker_issues=blockers,
            recommendation=data.get("recommendation", "No recommendation provided"),
            timestamp=data.get("timestamp", "")
        )
    except (json.JSONDecodeError, Exception) as e:
        raise RuntimeError(f"Invalid decision file for Judge {judge_num}: {e}\nFile: {decision_file}")

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
    
    has_clear_winner = (a_wins >= 2 or b_wins >= 2)
    
    if winner == "TIE":
        next_action = "FEEDBACK"
    elif approvals >= 2 and not all_blockers:
        next_action = "MERGE"
    elif has_clear_winner and all_blockers:
        next_action = "SYNTHESIS"
    elif has_clear_winner and not all_blockers:
        next_action = "MERGE"
    elif not has_clear_winner:
        next_action = "FEEDBACK"
    else:
        next_action = "SYNTHESIS"
    
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


