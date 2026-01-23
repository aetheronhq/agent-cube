"""Decision handling for Agent Cube workflow."""

import json

from ...core.config import PROJECT_ROOT
from ...core.output import console, print_info, print_warning
from ..decide import decide_command
from .phases import _normalize_issue


def run_decide_and_get_result(task_id: str) -> dict:
    """Run decide for panel decisions and return parsed result."""
    decide_command(task_id, review_type="panel")

    result_file = PROJECT_ROOT / ".prompts" / "decisions" / f"{task_id}-aggregated.json"
    with open(result_file) as f:
        return json.load(f)


def clear_peer_review_decisions(task_id: str) -> None:
    """Delete existing peer-review decision files to prevent append/concatenation.

    Some agents append to existing files instead of overwriting, causing
    invalid JSON with multiple root objects. Clear before each peer-review run.
    """
    from ...core.decision_parser import get_decision_file_path
    from ...core.user_config import get_judge_configs

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
    from ...core.decision_parser import get_decision_file_path, get_peer_review_status, parse_single_decision_file
    from ...core.user_config import get_judge_configs

    console.print(f"[cyan]📊 Checking peer review decisions for: {task_id}[/cyan]")
    console.print()

    result = get_peer_review_status(task_id, require_decisions=require_decisions)

    judge_configs = get_judge_configs()
    peer_review_judges = [j for j in judge_configs if j.peer_review_only]
    # If more decisions found than peer_review_only judges, all judges ran
    peer_only_count = len(peer_review_judges) if peer_review_judges else 0
    if result["decisions_found"] > peer_only_count:
        # All judges ran (single writer mode or run_all_judges=True)
        total_peer_judges = len(judge_configs)
    else:
        total_peer_judges = peer_only_count if peer_only_count else len(judge_configs)

    for judge_key, decision in result["judge_decisions"].items():
        judge_label = judge_key.replace("_", "-")
        console.print(f"Judge {judge_label}: {decision}")

        decision_file = get_decision_file_path(judge_key, task_id, review_type="peer-review")
        data = parse_single_decision_file(decision_file)
        if data:
            remaining = data.get("remaining_issues", [])
            blockers = data.get("blocker_issues", [])
            issues = remaining + blockers

            if issues:
                console.print(f"  Issues: {len(issues)}")
                for issue in issues[:3]:
                    issue_str = _normalize_issue(issue)
                    truncated = issue_str[:100] + "..." if len(issue_str) > 100 else issue_str
                    console.print(f"    • {truncated}")
                if len(issues) > 3:
                    console.print(f"    [dim]... and {len(issues) - 3} more[/dim]")

            if decision == "SKIPPED":
                console.print("  [dim](tool skipped - not blocking)[/dim]")
            elif decision == "REQUEST_CHANGES" and not issues:
                console.print("  [yellow]⚠️  No issues listed (malformed decision)[/yellow]")

    console.print()

    if result["decisions_found"] == 0:
        if require_decisions:
            print_warning("No peer review decisions found!")
            if peer_review_judges:
                console.print("Expected files from peer-review judges:")
                for judge_cfg in peer_review_judges:
                    judge_label = judge_cfg.key.replace("_", "-")
                    console.print(f"  .prompts/decisions/{judge_label}-{task_id}-peer-review.json")
            else:
                console.print("No peer_review_only judges configured - all judges:")
                for jconfig in judge_configs:
                    judge_label = jconfig.key.replace("_", "-")
                    console.print(f"  .prompts/decisions/{judge_label}-{task_id}-peer-review.json")
            console.print()
        return {"approved": False, "remaining_issues": [], "decisions_found": 0, "approvals": 0, "judge_decisions": {}}

    console.print(
        f"Decisions: {result['decisions_found']}/{total_peer_judges}, Approvals: {result['approvals']}/{result['decisions_found']}"
    )

    # Check if we have all expected decisions
    all_decisions_in = result["decisions_found"] >= total_peer_judges

    if result["approved"] and all_decisions_in:
        console.print()
        print_info("All judges approved!")
    elif result["approved"] and not all_decisions_in:
        console.print()
        missing = total_peer_judges - result["decisions_found"]
        print_warning(f"Missing {missing} judge decision(s) - cannot approve yet")

        found_keys = set(result["judge_decisions"].keys())
        missing_judges = [j for j in judge_configs if j.key not in found_keys]
        if missing_judges:
            console.print()
            console.print("[dim]Run missing judges:[/dim]")
            for j in missing_judges:
                console.print(f"  [cyan]cube peer-review {task_id} --judge {j.key} --fresh[/cyan]")

        result["approved"] = False  # Override - don't approve with missing decisions
    elif result["approvals"] > 0:
        console.print()
        print_warning(
            f"Not unanimous: {result['approvals']}/{result['decisions_found']} approved, {len(result['remaining_issues'])} issue(s) to address"
        )

    return result
