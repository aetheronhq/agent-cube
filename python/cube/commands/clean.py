"""Clean command - remove completed/old sessions and artifacts."""

import typer
from pathlib import Path
from datetime import datetime, timedelta
from ..core.output import print_success, print_info, print_warning, console
from ..core.config import PROJECT_ROOT, get_sessions_dir

def clean_command(
    task_id: str = None,
    old: bool = False,
    all_tasks: bool = False,
    dry_run: bool = False
) -> None:
    """Clean up completed or stale sessions and artifacts.
    
    Examples:
        cube clean 05-task           # Clean specific task
        cube clean --old             # Clean sessions >7 days
        cube clean --all             # Clean all completed
        cube clean 05-task --dry-run # Preview what would be deleted
    """
    
    sessions_dir = get_sessions_dir()
    prompts_dir = PROJECT_ROOT / ".prompts"
    
    if not sessions_dir.exists():
        print_info("No sessions to clean")
        return
    
    to_remove = []
    
    if task_id:
        session_files = list(sessions_dir.glob(f"*{task_id}*SESSION_ID.txt"))
        meta_files = list(sessions_dir.glob(f"*{task_id}*SESSION_ID.txt.meta"))
        to_remove.extend(session_files)
        to_remove.extend(meta_files)
        
        temp_prompts = list(prompts_dir.glob(f"temp-*{task_id}*.md"))
        to_remove.extend(temp_prompts)
        
        state_file = Path.home() / ".cube" / "state" / f"{task_id}.json"
        if state_file.exists():
            to_remove.append(state_file)
    
    elif old:
        cutoff = datetime.now() - timedelta(days=7)
        
        for session_file in sessions_dir.glob("*SESSION_ID.txt"):
            if session_file.stat().st_mtime < cutoff.timestamp():
                to_remove.append(session_file)
                meta = session_file.parent / f"{session_file.name}.meta"
                if meta.exists():
                    to_remove.append(meta)
    
    elif all_tasks:
        decisions_dir = prompts_dir / "decisions"
        
        if decisions_dir.exists():
            for decision_file in decisions_dir.glob("*-aggregated.json"):
                task_name = decision_file.stem.replace("-aggregated", "")
                
                session_files = list(sessions_dir.glob(f"*{task_name}*SESSION_ID.txt"))
                meta_files = list(sessions_dir.glob(f"*{task_name}*SESSION_ID.txt.meta"))
                
                to_remove.extend(session_files)
                to_remove.extend(meta_files)
    
    if not to_remove:
        print_info("Nothing to clean")
        return
    
    console.print(f"[yellow]Will remove {len(to_remove)} file(s):[/yellow]")
    console.print()
    
    for f in to_remove[:10]:
        console.print(f"  {f.name}")
    
    if len(to_remove) > 10:
        console.print(f"  ... and {len(to_remove) - 10} more")
    
    console.print()
    
    if dry_run:
        print_info("Dry run - no files deleted")
        return
    
    if not typer.confirm("Proceed with deletion?"):
        print_info("Cancelled")
        return
    
    for f in to_remove:
        try:
            f.unlink()
        except (FileNotFoundError, PermissionError, OSError) as e:
            pass
    
    print_success(f"Removed {len(to_remove)} file(s)")

