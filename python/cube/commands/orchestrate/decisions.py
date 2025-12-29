"""Decision handling for Agent Cube workflow."""

import json

from ...core.output import print_warning, print_info, console
from ...core.config import PROJECT_ROOT
from ..decide import decide_command


def run_decide_and_get_result(task_id: str) -> dict:
    """Run decide for panel decisions and return parsed result."""
    # Force panel review type - Phase 5 needs panel aggregation
    decide_command(task_id, review_type="panel")

    result_file = PROJECT_ROOT / ".prompts" / "decisions" / f"{task_id}-aggregated.json"
    with open(result_file) as f:
        return json.load(f)


def clear_peer_review_decisions(task_id: str) -> None:
    """Delete existing peer-review decision files to prevent append/concatenation.
    
    Some agents append to existing files instead of overwriting, causing
    invalid JSON with multiple root objects. Clear before each peer-review run.
    """
    from ...core.user_config import get_judge_configs
    from ...core.decision_parser import get_decision_file_path
    
    for judge in get_judge_configs():
        peer_file = get_decision_file_path(judge.key, task_id, review_type="peer-review")
        if peer_file.exists():
            peer_file.unlink()


def run_decide_peer_review(task_id: str, require_decisions: bool = True) -> dict:
    """Check peer review decisions and extract any remaining issues.
    
    Args:
        task_id: Identifier of the current task.
        require_decisions: When False, missing peer-review files won't raise
            warnings (useful before peer review runs).
    
    Only checks judges that have peer-review decision files (not all judges).
    """
    from ...core.user_config import get_judge_configs
    from ...core.decision_parser import get_decision_file_path

    all_issues = []
    approvals = 0
    decisions_found = 0
    judge_decisions = {}

    console.print(f"[cyan]📊 Checking peer review decisions for: {task_id}[/cyan]")
    console.print()

    judge_configs = get_judge_configs()
    judge_nums = [j.key for j in judge_configs]
    
    # Count judges that actually have peer-review files (not all judges)
    judges_with_files = []
    for judge_key in judge_nums:
        peer_file = get_decision_file_path(judge_key, task_id, review_type="peer-review")
        if peer_file.exists():
            judges_with_files.append(judge_key)
    total_judges = len(judges_with_files) if judges_with_files else 1

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
                    for issue in issues[:3]:
                        truncated = issue[:100] + "..." if len(issue) > 100 else issue
                        console.print(f"    • {truncated}")
                    if len(issues) > 3:
                        console.print(f"    [dim]... and {len(issues) - 3} more[/dim]")
                    all_issues.extend(issues)

                if decision == "APPROVED":
                    approvals += 1
                elif decision == "SKIPPED":
                    # Tool failure (rate limit, etc.) - not a code issue, count as non-blocking
                    approvals += 1
                    console.print(f"  [dim](tool skipped - not blocking)[/dim]")
                elif decision == "REQUEST_CHANGES":
                    if not issues:
                        console.print("  [yellow]⚠️  No issues listed (malformed decision)[/yellow]")
                        all_issues.append(f"Judge {judge_label} requested changes but didn't specify issues")

    console.print()

    if decisions_found == 0:
        if require_decisions:
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
