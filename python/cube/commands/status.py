"""Status command - show workflow progress."""

from ..core.config import PROJECT_ROOT
from ..core.output import console, print_info, print_warning
from ..core.session import load_session


def status_command(task_id: str = None) -> None:
    """Show workflow status for a task or all active work."""

    if task_id:
        show_task_status(task_id)
    else:
        show_all_status()


def show_task_status(task_id: str):
    """Show detailed status for a specific task."""
    from ..core.state import get_progress, load_state
    from ..core.user_config import get_writer_by_key, load_config

    config = load_config()

    console.print(f"[cyan]📊 Status for Task: {task_id}[/cyan]")
    console.print()

    state = load_state(task_id)
    if state:
        console.print(f"[green]Progress:[/green] {get_progress(task_id)}")
        console.print(f"[green]Completed phases:[/green] {', '.join(map(str, state.completed_phases))}")
        if state.winner:
            try:
                winner_label = get_writer_by_key(state.winner).label
            except (KeyError, ValueError):
                winner_label = state.winner
            console.print(f"[green]Winner:[/green] {winner_label}")
        console.print()

    prompts_dir = PROJECT_ROOT / ".prompts"
    decisions_dir = prompts_dir / "decisions"

    console.print("[yellow]Phase 1-2: Writers[/yellow]")
    writers_active = False
    for writer_key in config.writer_order:
        wconfig = config.writers[writer_key]
        session_id = load_session(writer_key.upper(), task_id)
        if session_id:
            writers_active = True
        status_icon = "✅" if session_id else "❌"
        status_text = f"Session: {session_id[:8]}..." if session_id else "Not started"
        console.print(f"  {wconfig.label}: {status_icon} {status_text}")
    console.print()

    # Filter panel judges (exclude peer_review_only)
    panel_judges = [j for j in config.judges.values() if not j.peer_review_only]

    console.print("[yellow]Phase 3-4: Judge Panel[/yellow]")
    panel_sessions_count = 0
    for jconfig in panel_judges:
        session_id = load_session(jconfig.key.upper(), f"{task_id}_panel")
        if session_id:
            panel_sessions_count += 1
        console.print(f"    {jconfig.label}: {'✅' if session_id else '❌'}")
    console.print(f"  Sessions: {panel_sessions_count}/{len(panel_judges)}")
    console.print()

    console.print("[yellow]Phase 5: Decisions[/yellow]")
    decisions_count = 0
    for jconfig in panel_judges:
        decision_path = decisions_dir / f"{jconfig.key.replace('_', '-')}-{task_id}-decision.json"
        exists = decision_path.exists()
        if exists:
            decisions_count += 1
        console.print(f"    {jconfig.label}: {'✅' if exists else '❌'}")
    console.print(f"  Decision files: {decisions_count}/{len(panel_judges)}")

    aggregated = (decisions_dir / f"{task_id}-aggregated.json").exists()
    if aggregated:
        import json

        with open(decisions_dir / f"{task_id}-aggregated.json") as f:
            result = json.load(f)
        console.print()
        console.print("  [green]✅ Aggregated decision:[/green]")
        winner = result.get("winner", "?")
        try:
            winner_display = get_writer_by_key(winner).label
        except (KeyError, ValueError):
            winner_display = winner
        console.print(f"    Winner: {winner_display}")
        console.print(f"    Next action: {result.get('next_action', '?')}")

        score_parts = []
        for key in config.writer_order:
            wconfig = config.writers[key]
            raw_score = result.get(f"avg_score_{key}")
            try:
                score = float(raw_score) if raw_score is not None else None
            except (ValueError, TypeError):
                score = None
            if score is not None:
                score_parts.append(f"{wconfig.label}={score:.1f}")
        if score_parts:
            console.print(f"    Scores: {', '.join(score_parts)}")
    console.print()

    # Peer review check (any peer review session exists)
    peer_review_active = False
    for jconfig in config.judges.values():
        if load_session(jconfig.key.upper(), f"{task_id}_peer-review"):
            peer_review_active = True
            break

    if peer_review_active:
        console.print("[yellow]Phase 6-7: Peer Review[/yellow]")
        # Determine which judges are expected for peer review
        # If peer_review_only judges exist, they are the ones expected. Otherwise all judges.
        peer_judges = [j for j in config.judges.values() if j.peer_review_only]
        if not peer_judges:
            peer_judges = list(config.judges.values())

        peer_session_count = 0
        peer_decision_count = 0

        for jconfig in peer_judges:
            session_id = load_session(jconfig.key.upper(), f"{task_id}_peer-review")
            if session_id:
                peer_session_count += 1
            decision_path = decisions_dir / f"{jconfig.key.replace('_', '-')}-{task_id}-peer-review.json"
            if decision_path.exists():
                peer_decision_count += 1

        console.print(f"  Sessions: {peer_session_count}/{len(peer_judges)}")
        console.print(f"  Decisions: {peer_decision_count}/{len(peer_judges)}")
        console.print()

    if not writers_active and not panel_sessions_count:
        print_warning("No active work for this task")
        console.print()
        console.print("Start with:")
        console.print("  cube orchestrate auto <task-file>")
        console.print(f"  cube writers {task_id} <prompt-file>")


def show_all_status():
    """Show overview of all active work."""
    from ..core.session import get_sessions_dir

    sessions_dir = get_sessions_dir()

    if not sessions_dir.exists():
        print_warning("No sessions found")
        return

    session_files = list(sessions_dir.glob("*SESSION_ID.txt"))

    tasks = {}
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

    from ..core.user_config import load_config

    config = load_config()
    total_writers = len(config.writers)
    total_judges = len([j for j in config.judges.values() if not j.peer_review_only])

    console.print(f"[cyan]📊 Active Tasks: {len(tasks)}[/cyan]")
    console.print()

    for task_id, agents in tasks.items():
        writer_count = len(agents["writers"])
        judge_count = len(agents["judges"])

        status_line = f"[yellow]{task_id}[/yellow]"
        if writer_count:
            status_line += f" | Writers: {writer_count}/{total_writers}"
        if judge_count:
            status_line += f" | Judges: {judge_count}/{total_judges}"

        console.print(status_line)

    console.print()
    console.print("View detailed status:")
    console.print("  cube status <task-id>")
