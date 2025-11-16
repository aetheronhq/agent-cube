"""CodeRabbit decision file generation.

Generates standard judge decision JSON files from CodeRabbit review output.
Includes scoring, winner selection, and blocker identification.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from .config import PROJECT_ROOT


def categorize_issue(message: str) -> str:
    """Map issue message to score category using keyword matching.
    
    Args:
        message: Issue message from CodeRabbit
    
    Returns:
        Category name (one of: type_safety, production_ready, tests, 
        kiss_compliance, architecture)
    """
    message_lower = message.lower()
    
    # Type safety
    if any(kw in message_lower for kw in ["type", "null", "undefined", "any"]):
        return "type_safety"
    
    # Production ready
    elif any(kw in message_lower for kw in ["security", "vulnerability", "injection", "error handling"]):
        return "production_ready"
    
    # Tests
    elif any(kw in message_lower for kw in ["test", "coverage", "assertion"]):
        return "tests"
    
    # KISS compliance
    elif any(kw in message_lower for kw in ["complex", "abstraction", "over"]):
        return "kiss_compliance"
    
    # Default
    else:
        return "architecture"


def calculate_scores(issues: List[dict]) -> dict:
    """Calculate scores for all categories based on issues.
    
    Args:
        issues: List of issue dicts with keys: file, line, severity, message
    
    Returns:
        Dict with category scores and total_weighted
    """
    # Start with perfect scores
    category_scores = {
        "kiss_compliance": 10.0,
        "architecture": 10.0,
        "type_safety": 10.0,
        "tests": 10.0,
        "production_ready": 10.0
    }
    
    # Apply deductions
    for issue in issues:
        severity = issue.get("severity", "info")
        message = issue.get("message", "")
        
        # Determine deduction amount
        if severity == "error":
            deduction = 2.0
        elif severity == "warning":
            deduction = 0.5
        else:  # info
            deduction = 0.1
        
        # Determine which category to deduct from
        category = categorize_issue(message)
        category_scores[category] = max(0.0, category_scores[category] - deduction)
    
    # Calculate total weighted (average of all categories)
    total = sum(category_scores.values()) / len(category_scores)
    category_scores["total_weighted"] = round(total, 1)
    
    return category_scores


def determine_winner(score_a: float, score_b: float) -> str:
    """Determine winner based on total weighted scores.
    
    Args:
        score_a: Writer A's total weighted score
        score_b: Writer B's total weighted score
    
    Returns:
        "A", "B", or "TIE"
    """
    diff = abs(score_a - score_b)
    
    if diff < 0.5:
        return "TIE"
    elif score_a > score_b:
        return "A"
    else:
        return "B"


def extract_blockers(issues: List[dict]) -> List[str]:
    """Extract blocker issues (errors only) and format them.
    
    Args:
        issues: List of issue dicts with keys: writer, file, line, severity, message
    
    Returns:
        List of formatted blocker strings
    """
    blockers = []
    
    for issue in issues:
        if issue.get("severity") == "error":
            writer = issue.get("writer", "?").lower()
            file = issue.get("file", "unknown")
            line = issue.get("line", 0)
            message = issue.get("message", "")
            
            blocker = f"writer-{writer}/{file}:{line} - {message}"
            blockers.append(blocker)
    
    return blockers


def determine_decision(blockers: List[str]) -> str:
    """Determine decision value based on blocker count.
    
    Args:
        blockers: List of blocker issue strings
    
    Returns:
        "APPROVED", "REQUEST_CHANGES", or "REJECTED"
    """
    blocker_count = len(blockers)
    
    if blocker_count == 0:
        return "APPROVED"
    elif blocker_count > 10:
        return "REJECTED"
    else:
        return "REQUEST_CHANGES"


def generate_recommendation(
    winner: str,
    scores_a: dict,
    scores_b: dict,
    issues_a: List[dict],
    issues_b: List[dict]
) -> str:
    """Generate recommendation text explaining the decision.
    
    Args:
        winner: "A", "B", or "TIE"
        scores_a: Writer A's scores dict
        scores_b: Writer B's scores dict
        issues_a: Writer A's issues list
        issues_b: Writer B's issues list
    
    Returns:
        Recommendation string
    """
    if winner == "TIE":
        return "Both implementations have similar code quality based on static analysis"
    
    winner_score = scores_a["total_weighted"] if winner == "A" else scores_b["total_weighted"]
    loser_score = scores_b["total_weighted"] if winner == "A" else scores_a["total_weighted"]
    
    winner_errors = sum(1 for i in (issues_a if winner == "A" else issues_b) if i.get("severity") == "error")
    loser_errors = sum(1 for i in (issues_b if winner == "A" else issues_a) if i.get("severity") == "error")
    
    return (
        f"Writer {winner} preferred: higher code quality score "
        f"({winner_score} vs {loser_score}), fewer critical issues "
        f"({winner_errors} errors vs {loser_errors} errors)"
    )


def generate_decision(
    judge_num: int,
    task_id: str,
    writer_a_issues: List[dict],
    writer_b_issues: List[dict]
) -> dict:
    """Generate judge decision from CodeRabbit review output.
    
    This is the main entry point for decision generation. It orchestrates
    all the helper functions to produce a complete decision dict.
    
    Args:
        judge_num: Judge number (3 for CodeRabbit)
        task_id: Task identifier (e.g., "01-example-task")
        writer_a_issues: List of issues found in writer A's code
        writer_b_issues: List of issues found in writer B's code
    
    Returns:
        Decision dict matching standard judge format
    
    Example issue dict:
        {
            "file": "api.ts",
            "line": 42,
            "severity": "error",
            "message": "Potential null pointer dereference"
        }
    
    Example output:
        {
            "judge": 3,
            "task_id": "01-example-task",
            "timestamp": "2025-11-16T10:30:00Z",
            "decision": "REQUEST_CHANGES",
            "winner": "A",
            "scores": {
                "writer_a": {"kiss_compliance": 9, ..., "total_weighted": 7.8},
                "writer_b": {"kiss_compliance": 8, ..., "total_weighted": 6.2}
            },
            "blocker_issues": ["writer-b/api.ts:55 - Missing error handling"],
            "recommendation": "Writer A preferred: ..."
        }
    """
    # Calculate scores for both writers
    scores_a = calculate_scores(writer_a_issues)
    scores_b = calculate_scores(writer_b_issues)
    
    # Determine winner
    winner = determine_winner(scores_a["total_weighted"], scores_b["total_weighted"])
    
    # Tag issues with writer and extract blockers
    all_issues = [
        {"writer": "A", **issue} for issue in writer_a_issues
    ] + [
        {"writer": "B", **issue} for issue in writer_b_issues
    ]
    
    blockers = extract_blockers(all_issues)
    
    # Determine decision value
    decision_value = determine_decision(blockers)
    
    # Generate recommendation
    recommendation = generate_recommendation(
        winner, scores_a, scores_b, writer_a_issues, writer_b_issues
    )
    
    # Assemble decision dict
    return {
        "judge": judge_num,
        "task_id": task_id,
        "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "decision": decision_value,
        "winner": winner,
        "scores": {
            "writer_a": scores_a,
            "writer_b": scores_b
        },
        "blocker_issues": blockers,
        "recommendation": recommendation
    }


def write_decision_file(decision: dict, task_id: str, judge_num: int) -> Path:
    """Write decision to JSON file in standard location.
    
    Args:
        decision: Decision dict from generate_decision()
        task_id: Task identifier
        judge_num: Judge number
    
    Returns:
        Path to written file
    
    File location:
        .prompts/decisions/judge-{judge_num}-{task_id}-decision.json
    """
    decisions_dir = PROJECT_ROOT / ".prompts" / "decisions"
    decisions_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"judge-{judge_num}-{task_id}-decision.json"
    filepath = decisions_dir / filename
    
    with open(filepath, 'w') as f:
        json.dump(decision, f, indent=2)
    
    return filepath


# Test script
if __name__ == "__main__":
    # Sample test data
    writer_a_issues = [
        {"file": "api.ts", "line": 42, "severity": "error", "message": "Potential null pointer dereference"},
        {"file": "utils.ts", "line": 15, "severity": "warning", "message": "Unused variable 'temp'"},
        {"file": "types.ts", "line": 8, "severity": "info", "message": "Consider using const instead of let"}
    ]
    
    writer_b_issues = [
        {"file": "api.ts", "line": 55, "severity": "error", "message": "Missing error handling"},
        {"file": "api.ts", "line": 60, "severity": "error", "message": "SQL injection vulnerability"},
        {"file": "utils.ts", "line": 20, "severity": "warning", "message": "Complex function, consider refactoring"}
    ]
    
    # Generate decision
    decision = generate_decision(
        judge_num=3,
        task_id="01-test",
        writer_a_issues=writer_a_issues,
        writer_b_issues=writer_b_issues
    )
    
    # Print results
    print(json.dumps(decision, indent=2))
    
    # Write to file
    filepath = write_decision_file(decision, "01-test", 3)
    print(f"\nDecision written to: {filepath}")
