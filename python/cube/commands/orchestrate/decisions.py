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
    """Check peer review decisions and extract any remaining issues."""
    from ...core.decision_parser import get_peer_review_status, get_decision_file_path
    from ...core.user_config import get_judge_configs
    
    console.print(f"[cyan]📊 Checking peer review decisions for: {task_id}[/cyan]")
    console.print()
    
    result = get_peer_review_status(task_id, require_decisions=require_decisions)
    
    # Display per-judge status
    for judge_key, decision in result["judge_decisions"].items():
        judge_label = judge_key.replace("_", "-")
        console.print(f"Judge {judge_label}: {decision}")

    console.print()
    
    judge_configs = get_judge_configs()

    if result["decisions_found"] == 0:
        if require_decisions:
            print_warning("No peer review decisions found!")
            peer_review_judges = [j for j in judge_configs if j.peer_review_only]
            if peer_review_judges:
                console.print("Expected files from peer-review judges:")
                for judge_cfg in peer_review_judges:
                    judge_label = judge_cfg.key.replace("_", "-")
                    fpath = get_decision_file_path(judge_cfg.key, task_id, review_type="peer-review")
                    console.print(f"  {fpath.relative_to(PROJECT_ROOT)}")
            else:
                console.print("No peer_review_only judges configured - all judges:")
                for jc in judge_configs:
                    judge_label = jc.key.replace("_", "-")
                    fpath = get_decision_file_path(jc.key, task_id, review_type="peer-review")
                    console.print(f"  {fpath.relative_to(PROJECT_ROOT)}")
            console.print()
        return result
    
    peer_review_judges = [j for j in judge_configs if j.peer_review_only]
    total_peer_judges = len(peer_review_judges) if peer_review_judges else len(judge_configs)
    
    console.print(f"Decisions: {result['decisions_found']}/{total_peer_judges}, Approvals: {result['approvals']}/{result['decisions_found']}")
    
    if result["approved"]:
        console.print()
        print_info("All judges approved!")
    elif result["approvals"] > 0:
        console.print()
        print_warning(f"Not unanimous: {result['approvals']}/{result['decisions_found']} approved, {len(result['remaining_issues'])} issue(s)")
    
    return result

