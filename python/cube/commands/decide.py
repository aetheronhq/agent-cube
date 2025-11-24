"""Decide command - aggregate judge decisions."""

import json
import typer
from pathlib import Path

from ..core.decision_parser import parse_all_decisions, aggregate_decisions, get_decision_file_path
from ..core.output import print_error, print_success, print_warning, print_info, console
from ..core.config import PROJECT_ROOT
from ..core.session import load_session
from ..core.state import update_phase

def decide_command(task_id: str, review_type: str = "auto") -> None:
    """Aggregate judge decisions and determine next action.
    
    Args:
        review_type: 'auto' (latest), 'panel', or 'peer-review'
    """
    from ..core.decision_files import find_decision_file
    
    from ..core.user_config import get_judge_configs
    judge_configs = get_judge_configs()
    judge_nums = [j.key for j in judge_configs]
    
    if review_type == "auto":
        has_peer = any(find_decision_file(j, task_id, "peer-review") for j in judge_nums)
        actual_type = "peer-review" if has_peer else "panel"
        console.print(f"[dim]Auto-detected: {actual_type} review[/dim]")
    else:
        actual_type = review_type
    
    if actual_type == "peer-review":
        console.print(f"[cyan]📊 Analyzing peer review decisions for: {task_id}[/cyan]")
        console.print()
        
        from ..commands.orchestrate import run_decide_peer_review
        result = run_decide_peer_review(task_id)
        
        console.print()
        if result["approved"]:
            print_success("✅ Peer review approved - ready for PR!")
        else:
            print_warning("⚠️  Peer review needs more work")
        
        return
    
    console.print(f"[cyan]📊 Analyzing panel decisions for: {task_id}[/cyan]")
    console.print()
    
    decisions = parse_all_decisions(task_id)
    
    if not decisions:
        print_error("No decision files found")
        console.print()
        console.print("Expected decision files:")
        for judge_key in judge_nums:
            decision_file = get_decision_file_path(judge_key, task_id)
            console.print(f"  {decision_file}")
        console.print()
        
        console.print("Missing decisions from:")
        for judge_key in judge_nums:
            decision_file = get_decision_file_path(judge_key, task_id)
            if not decision_file.exists():
                session_id = load_session(f"JUDGE_{judge_key}", f"{task_id}_panel")
                if session_id:
                    judge_label = judge_key.replace("_", "-")
                    console.print(f"  [yellow]Judge {judge_label}[/yellow] (session: {session_id})")
                    console.print(f"    Resume: [cyan]cube resume {judge_label} {task_id} \"Write decision file\"[/cyan]")
                    
                    from ..core.user_config import get_judge_config
                    jconfig = get_judge_config(judge_key)
                    if "gemini" in jconfig.model.lower():
                        console.print("    [dim]Note: Gemini may need help finding PROJECT_ROOT[/dim]")
                        console.print(f"    [dim]Tell it: Write to {PROJECT_ROOT}/.prompts/decisions/{judge_key.replace('_', '-')}-{task_id}-decision.json[/dim]")
                else:
                    judge_label = judge_key.replace("_", "-")
                    console.print(f"  [red]Judge {judge_label}[/red] (no session)")
        
        raise typer.Exit(1)
    
    total_judges = len(judge_nums)
    if len(decisions) < total_judges:
        # Normalize judge keys for comparison (handle "1" vs "judge_1" etc)
        found_judges = set()
        for d in decisions:
            found_judges.add(str(d.judge))
            # Also add with judge_ prefix if it's a number
            if str(d.judge).isdigit():
                found_judges.add(f"judge_{d.judge}")
        
        missing = [j for j in judge_nums if j not in found_judges]
        if missing:
            missing_labels = []
            for j in missing:
                try:
                    from ..core.user_config import get_judge_config
                    jconfig = get_judge_config(j)
                    missing_labels.append(jconfig.label)
                except:
                    missing_labels.append(j)
            print_warning(f"Only {len(decisions)}/{total_judges} decisions found. Missing: {', '.join(missing_labels)}")
            console.print()
    
    for d in decisions:
        # Get judge label (handle key, number, or already a label)
        judge_label = str(d.judge)
        try:
            from ..core.user_config import get_judge_config
            # Try as-is first
            jconfig = get_judge_config(judge_label)
            judge_label = jconfig.label
        except:
            # Try adding judge_ prefix if it's just a number
            try:
                if judge_label.isdigit():
                    jconfig = get_judge_config(f"judge_{judge_label}")
                    judge_label = jconfig.label
            except:
                pass
        
        color = "green" if d.decision == "APPROVED" else ("yellow" if d.decision == "REQUEST_CHANGES" else "red")
        console.print(f"[{color}]{judge_label}:[/{color}] {d.decision} → Winner: {d.winner} (A: {d.scores_a}, B: {d.scores_b})")
    
    console.print()
    console.print("━" * 60)
    
    result = aggregate_decisions(decisions)
    
    if result["consensus"]:
        print_success(f"Consensus: APPROVED ({result['votes']['approve']}/{len(decisions)})")
    else:
        print_warning(f"No consensus: {result['votes']['approve']} approve, {result['votes']['request_changes']} request changes, {result['votes']['reject']} reject")
    
    console.print()
    
    # Format winner display
    winner_display = result['winner']
    if winner_display == "writer_a":
        winner_display = "A"
    elif winner_display == "writer_b":
        winner_display = "B"
    
    console.print(f"[bold]🏆 Winner: Writer {winner_display}[/bold]")
    console.print(f"📊 Average Scores: A={result['avg_score_a']:.1f}, B={result['avg_score_b']:.1f}")
    console.print()
    
    if result["blocker_issues"]:
        print_warning(f"{len(result['blocker_issues'])} blocker issue(s) found:")
        for issue in result["blocker_issues"]:
            console.print(f"  • {issue}")
        console.print()
    
    console.print("━" * 60)
    console.print()
    
    action_color = "green" if result["next_action"] == "MERGE" else "yellow"
    console.print(f"[bold {action_color}]Next Action: {result['next_action']}[/bold {action_color}]")
    console.print()
    
    if result["next_action"] == "MERGE":
        from ..core.user_config import get_writer_by_key_or_letter
        winner_cfg = get_writer_by_key_or_letter(result["winner"])
        console.print("[green]✅ Ready for PR![/green]")
        console.print()
        console.print("Create pull request:")
        console.print(f"  git checkout writer-{winner_cfg.name}/{task_id}")
        console.print(f"  git push -u origin writer-{winner_cfg.name}/{task_id}")
        console.print(f"  gh pr create --base main --title 'feat: {task_id}' --fill")
    
    elif result["next_action"] == "SYNTHESIS":
        from ..core.user_config import get_writer_by_key_or_letter
        winner_cfg = get_writer_by_key_or_letter(result["winner"])
        console.print("Synthesis needed (winner has blockers):")
        console.print(f"  1. Create: .prompts/synthesis-{task_id}.md")
        console.print(f"  2. Run: cube feedback {winner_cfg.name} {task_id} .prompts/synthesis-{task_id}.md")
        console.print(f"  3. After fixes: cube peer-review {task_id} .prompts/peer-review-{task_id}.md")
    
    elif result["next_action"] == "FEEDBACK":
        console.print("Major changes needed:")
        console.print(f"  1. Create feedback for both writers")
        console.print(f"  2. Resume with: cube feedback <writer> {task_id} .prompts/feedback-{task_id}.md")
    
    console.print()
    
    save_path = PROJECT_ROOT / ".prompts" / "decisions" / f"{task_id}-aggregated.json"
    save_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print_success(f"Aggregated decision saved: {save_path}")
    update_phase(
        task_id,
        5,
        path=result["next_action"],
        winner=result["winner"],
        next_action=result["next_action"],
        panel_complete=True
    )

