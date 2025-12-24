"""Decision handling for orchestration workflow."""

import json
from pathlib import Path

from ...core.config import PROJECT_ROOT
from ...core.output import console, print_info, print_warning
from ...core.user_config import get_judge_configs
from ...core.decision_parser import get_decision_file_path
from ..decide import decide_command


def run_decide_and_get_result(task_id: str) -> dict:
    """Run decide and return parsed result."""
    decide_command(task_id)

    result_file = PROJECT_ROOT / ".prompts" / "decisions" / f"{task_id}-aggregated.json"
    with open(result_file) as f:
        return json.load(f)


def run_decide_peer_review(task_id: str) -> dict:
    """Check peer review decisions and extract any remaining issues."""
    decisions_dir = PROJECT_ROOT / ".prompts" / "decisions"
    all_issues = []
    approvals = 0
    decisions_found = 0
    judge_decisions = {}

    console.print(f"[cyan]📊 Checking peer review decisions for: {task_id}[/cyan]")
    console.print()

    has_request_changes = False
    judge_configs = get_judge_configs()
    judge_nums = [j.key for j in judge_configs]
    total_judges = len(judge_nums)

    for judge_key in judge_nums:
        peer_file = get_decision_file_path(judge_key, task_id, review_type="peer-review")

        if peer_file.exists():
            decisions_found += 1
            with open(peer_file) as f:
                data = json.load(f)
                decision = data.get("decision", "UNKNOWN")
                remaining = data.get("remaining_issues", [])
                blockers = data.get("blocker_issues", [])
                issues = remaining + blockers

                judge_decisions[f"{judge_key}_decision"] = decision

                judge_label = judge_key.replace("_", "-")
                console.print(f"Judge {judge_label}: {decision}")
                if issues:
                    console.print(f"  Issues: {len(issues)}")
                    all_issues.extend(issues)

                if decision == "APPROVED":
                    approvals += 1
                elif decision == "REQUEST_CHANGES":
                    has_request_changes = True
                    if not issues:
                        console.print(f"  [yellow]⚠️  No issues listed (malformed decision)[/yellow]")
                        all_issues.append(f"Judge {judge_label} requested changes but didn't specify issues")

    console.print()

    if decisions_found == 0:
        print_warning("No peer review decisions found!")
        console.print("Expected files:")
        for judge_key in judge_nums:
            judge_label = judge_key.replace("_", "-")
            console.print(f"  .prompts/decisions/{judge_label}-{task_id}-peer-review.json")
        console.print()
        return {"approved": False, "remaining_issues": [], "decisions_found": 0, "approvals": 0}

    console.print(f"Decisions: {decisions_found}/{total_judges}, Approvals: {approvals}/{decisions_found}")

    approved = approvals == decisions_found

    if approved:
        console.print()
        print_info("All judges approved!")
    elif approvals > 0:
        console.print()
        print_warning(f"Not unanimous: {approvals}/{decisions_found} approved, {len(all_issues)} issue(s) to address")

    result = {
        "approved": approved,
        "remaining_issues": all_issues,
        "decisions_found": decisions_found,
        "approvals": approvals
    }
    result.update(judge_decisions)
    return result
