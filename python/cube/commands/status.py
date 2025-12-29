"""Status command - show workflow progress."""

from pathlib import Path
from typing import Optional
from ..core.output import print_info, print_success, print_warning, console
from ..core.config import PROJECT_ROOT
from ..core.session import load_session

def status_command(task_id: Optional[str] = None) -> None:
    """Show workflow status for a task or all active work."""
    
    if task_id:
        show_task_status(task_id)
    else:
        show_all_status()

def show_task_status(task_id: str):
    """Show detailed status for a specific task."""
    from ..core.state import load_state, get_progress
    
    console.print(f"[cyan]📊 Status for Task: {task_id}[/cyan]")
    console.print()
    
    state = load_state(task_id)
    if state:
        console.print(f"[green]Progress:[/green] {get_progress(task_id)}")
        console.print(f"[green]Completed phases:[/green] {', '.join(map(str, state.completed_phases))}")
        if state.winner:
            console.print(f"[green]Winner:[/green] Writer {state.winner}")
        console.print()
    

    
    prompts_dir = PROJECT_ROOT / ".prompts"
    decisions_dir = prompts_dir / "decisions"
    
    writer_a_session = load_session("WRITER_A", task_id)
    writer_b_session = load_session("WRITER_B", task_id)
    
    judge_1_panel = load_session("JUDGE_1", f"{task_id}_panel")
    judge_2_panel = load_session("JUDGE_2", f"{task_id}_panel")
    judge_3_panel = load_session("JUDGE_3", f"{task_id}_panel")
    
    judge_1_peer = load_session("JUDGE_1", f"{task_id}_peer-review")
    judge_2_peer = load_session("JUDGE_2", f"{task_id}_peer-review")
    judge_3_peer = load_session("JUDGE_3", f"{task_id}_peer-review")
    
    decision_1 = (decisions_dir / f"judge_1-{task_id}-decision.json").exists()
    decision_2 = (decisions_dir / f"judge_2-{task_id}-decision.json").exists()
    decision_3 = (decisions_dir / f"judge_3-{task_id}-decision.json").exists()
    
    peer_1 = (decisions_dir / f"judge_1-{task_id}-peer-review.json").exists()
    peer_2 = (decisions_dir / f"judge_2-{task_id}-peer-review.json").exists()
    peer_3 = (decisions_dir / f"judge_3-{task_id}-peer-review.json").exists()
    
    aggregated = (decisions_dir / f"{task_id}-aggregated.json").exists()
    
    console.print("[yellow]Phase 1-2: Writers[/yellow]")
    console.print(f"  Writer A: {'✅' if writer_a_session else '❌'} {f'Session: {writer_a_session[:8]}...' if writer_a_session else 'Not started'}")
    console.print(f"  Writer B: {'✅' if writer_b_session else '❌'} {f'Session: {writer_b_session[:8]}...' if writer_b_session else 'Not started'}")
    console.print()
    
    console.print("[yellow]Phase 3-4: Judge Panel[/yellow]")
    panel_count = sum([judge_1_panel is not None, judge_2_panel is not None, judge_3_panel is not None])
    console.print(f"  Sessions: {panel_count}/3")
    console.print(f"    Judge 1: {'✅' if judge_1_panel else '❌'}")
    console.print(f"    Judge 2: {'✅' if judge_2_panel else '❌'}")
    console.print(f"    Judge 3: {'✅' if judge_3_panel else '❌'}")
    console.print()
    
    console.print("[yellow]Phase 5: Decisions[/yellow]")
    decision_count = sum([decision_1, decision_2, decision_3])
    console.print(f"  Decision files: {decision_count}/3")
    console.print(f"    Judge 1: {'✅' if decision_1 else '❌'}")
    console.print(f"    Judge 2: {'✅' if decision_2 else '❌'}")
    console.print(f"    Judge 3: {'✅' if decision_3 else '❌'}")
    
    if aggregated:
        import json
        with open(decisions_dir / f"{task_id}-aggregated.json") as f:
            result = json.load(f)
        console.print()
        console.print(f"  [green]✅ Aggregated decision:[/green]")
        console.print(f"    Winner: Writer {result.get('winner', '?')}")
        console.print(f"    Next action: {result.get('next_action', '?')}")
        console.print(f"    Scores: A={result.get('avg_score_a', 0):.1f}, B={result.get('avg_score_b', 0):.1f}")
    console.print()
    
    if judge_1_peer or judge_2_peer or judge_3_peer:
        console.print("[yellow]Phase 6-7: Peer Review[/yellow]")
        peer_session_count = sum([judge_1_peer is not None, judge_2_peer is not None, judge_3_peer is not None])
        peer_decision_count = sum([peer_1, peer_2, peer_3])
        console.print(f"  Sessions: {peer_session_count}/3")
        console.print(f"  Decisions: {peer_decision_count}/3")
        console.print()
    
    if not any([writer_a_session, writer_b_session, judge_1_panel]):
        print_warning("No active work for this task")
        console.print()
        console.print("Start with:")
        console.print(f"  cube orchestrate auto <task-file>")
        console.print(f"  cube writers {task_id} <prompt-file>")

def show_all_status():
    """Show overview of all active work."""
    from ..core.session import get_sessions_dir
    
    sessions_dir = get_sessions_dir()
    
    if not sessions_dir.exists():
        print_warning("No sessions found")
        return
    
    session_files = list(sessions_dir.glob("*SESSION_ID.txt"))
    
    tasks: dict[str, dict[str, list[str]]] = {}
    for sf in session_files:
        parts = sf.stem.replace("_SESSION_ID", "").split("_")
        if len(parts) >= 2:
            agent_type = parts[0]
            task_id = "_".join(parts[1:])
            
            if task_id not in tasks:
                tasks[task_id] = {"writers": [], "judges": []}
            
            if agent_type.startswith("WRITER"):
                tasks[task_id]["writers"].append(agent_type)
            elif agent_type.startswith("JUDGE"):
                tasks[task_id]["judges"].append(agent_type)
    
    if not tasks:
        print_info("No active tasks")
        return
    
    console.print(f"[cyan]📊 Active Tasks: {len(tasks)}[/cyan]")
    console.print()
    
    for task_id, agents in tasks.items():
        writer_count = len(agents["writers"])
        judge_count = len(agents["judges"])
        
        status_line = f"[yellow]{task_id}[/yellow]"
        if writer_count:
            status_line += f" | Writers: {writer_count}/2"
        if judge_count:
            status_line += f" | Judges: {judge_count}/3"
        
        console.print(status_line)
    
    console.print()
    console.print("View detailed status:")
    console.print("  cube status <task-id>")
