"""CodeRabbit decision file generation utilities.

Transforms parsed CodeRabbit review issues into standardized judge decision
artifacts, including scoring, winner selection, blocker extraction, and final
recommendations.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from .config import PROJECT_ROOT

CATEGORY_ORDER: tuple[str, ...] = (
    "kiss_compliance",
    "architecture",
    "type_safety",
    "tests",
    "production_ready",
)

CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "type_safety": ["type", "null", "undefined", "any"],
    "production_ready": ["security", "vulnerability", "injection", "error handling"],
    "tests": ["test", "coverage", "assertion"],
    "kiss_compliance": ["complex", "abstraction", "over-engineering", "over engineering"],
}

SEVERITY_DEDUCTIONS: Dict[str, float] = {
    "error": 2.0,
    "warning": 0.5,
    "info": 0.1,
}


def categorize_issue(message: str) -> str:
    """Map an issue message to a scoring category using keyword matching."""
    message_lower = (message or "").lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in message_lower for keyword in keywords):
            return category

    return "architecture"


def calculate_scores(issues: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calculate category scores for a single writer."""
    category_scores: Dict[str, float] = {category: 10.0 for category in CATEGORY_ORDER}

    for issue in issues:
        severity = str(issue.get("severity", "info")).lower()
        deduction = SEVERITY_DEDUCTIONS.get(severity, SEVERITY_DEDUCTIONS["info"])
        message = str(issue.get("message", ""))
        category = categorize_issue(message)
        category_scores[category] = max(0.0, category_scores[category] - deduction)

    for category in CATEGORY_ORDER:
        category_scores[category] = round(category_scores[category], 1)

    total = sum(category_scores[category] for category in CATEGORY_ORDER) / len(CATEGORY_ORDER)
    category_scores["total_weighted"] = round(total, 1)

    return category_scores


def determine_winner(score_a: float, score_b: float) -> str:
    """Determine the winning writer based on weighted scores."""
    diff = abs(score_a - score_b)

    if diff < 0.5:
        return "TIE"
    if score_a > score_b:
        return "A"
    return "B"


def extract_blockers(issues: List[Dict[str, Any]]) -> List[str]:
    """Extract and format blocker issues (severity error only)."""
    blockers: List[str] = []

    for issue in issues:
        severity = str(issue.get("severity", "")).lower()
        if severity != "error":
            continue

        writer = str(issue.get("writer", "?")).lower() or "?"
        file_path = issue.get("file") or "unknown"
        line_raw = issue.get("line")
        line_number = line_raw if isinstance(line_raw, int) and line_raw >= 0 else 0
        message = issue.get("message") or "Unspecified issue"

        blocker = f"writer-{writer}/{file_path}:{line_number} - {message}"
        blockers.append(blocker)

    return blockers


def determine_decision(blockers: List[str]) -> str:
    """Determine the decision status based on blocker count."""
    blocker_count = len(blockers)

    if blocker_count == 0:
        return "APPROVED"
    if blocker_count > 10:
        return "REJECTED"
    return "REQUEST_CHANGES"


def generate_recommendation(
    winner: str,
    scores_a: Dict[str, float],
    scores_b: Dict[str, float],
    issues_a: List[Dict[str, Any]],
    issues_b: List[Dict[str, Any]],
) -> str:
    """Generate a concise recommendation explaining the decision."""
    if winner == "TIE":
        return "Both implementations have similar code quality based on static analysis"

    winner_scores = scores_a if winner == "A" else scores_b
    loser_scores = scores_b if winner == "A" else scores_a
    winner_issues = issues_a if winner == "A" else issues_b
    loser_issues = issues_b if winner == "A" else issues_a

    winner_errors = sum(1 for issue in winner_issues if str(issue.get("severity", "")).lower() == "error")
    loser_errors = sum(1 for issue in loser_issues if str(issue.get("severity", "")).lower() == "error")

    return (
        f"Writer {winner} preferred: higher code quality score "
        f"({winner_scores['total_weighted']} vs {loser_scores['total_weighted']}), "
        f"fewer critical issues ({winner_errors} errors vs {loser_errors} errors)"
    )


def generate_decision(
    judge_num: int,
    task_id: str,
    writer_a_issues: List[Dict[str, Any]],
    writer_b_issues: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Generate the full decision payload for the CodeRabbit judge."""
    scores_a = calculate_scores(writer_a_issues)
    scores_b = calculate_scores(writer_b_issues)
    winner = determine_winner(scores_a["total_weighted"], scores_b["total_weighted"])

    tagged_issues = [{"writer": "a", **issue} for issue in writer_a_issues] + [
        {"writer": "b", **issue} for issue in writer_b_issues
    ]
    blockers = extract_blockers(tagged_issues)
    decision_value = determine_decision(blockers)

    recommendation = generate_recommendation(
        winner=winner,
        scores_a=scores_a,
        scores_b=scores_b,
        issues_a=writer_a_issues,
        issues_b=writer_b_issues,
    )

    timestamp = (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )

    return {
        "judge": judge_num,
        "task_id": task_id,
        "timestamp": timestamp,
        "decision": decision_value,
        "winner": winner,
        "scores": {
            "writer_a": scores_a,
            "writer_b": scores_b,
        },
        "blocker_issues": blockers,
        "recommendation": recommendation,
    }


def write_decision_file(decision: Dict[str, Any], task_id: str, judge_num: int) -> Path:
    """Persist a decision dict into the standard decisions directory."""
    decisions_dir = PROJECT_ROOT / ".prompts" / "decisions"
    decisions_dir.mkdir(parents=True, exist_ok=True)

    filename = f"judge-{judge_num}-{task_id}-decision.json"
    filepath = decisions_dir / filename

    with filepath.open("w", encoding="utf-8") as file:
        json.dump(decision, file, indent=2)

    return filepath


if __name__ == "__main__":
    WRITER_A_ISSUES = [
        {"file": "api.ts", "line": 42, "severity": "error", "message": "Potential null pointer dereference"},
        {"file": "utils.ts", "line": 15, "severity": "warning", "message": "Unused variable 'temp'"},
        {"file": "types.ts", "line": 8, "severity": "info", "message": "Consider using const instead of let"},
    ]

    WRITER_B_ISSUES = [
        {"file": "api.ts", "line": 55, "severity": "error", "message": "Missing error handling"},
        {"file": "api.ts", "line": 60, "severity": "error", "message": "SQL injection vulnerability"},
        {"file": "utils.ts", "line": 20, "severity": "warning", "message": "Complex function, consider refactoring"},
    ]

    decision_output = generate_decision(
        judge_num=3,
        task_id="01-test",
        writer_a_issues=WRITER_A_ISSUES,
        writer_b_issues=WRITER_B_ISSUES,
    )
    print(json.dumps(decision_output, indent=2))

    decision_path = write_decision_file(decision_output, "01-test", 3)
    print(f"\nDecision written to: {decision_path}")
