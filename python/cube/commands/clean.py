"""Clean command - remove completed/old sessions and artifacts."""

import typer
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from ..core.output import print_success, print_info, print_warning, print_error, console
from ..core.config import PROJECT_ROOT, get_sessions_dir, WORKTREE_BASE

def clean_command(
    task_id: str = None,
    old: bool = False,
    all_tasks: bool = False,
    full: bool = False,
    dry_run: bool = False
) -> None:
    """Clean up completed or stale sessions and artifacts.
    
    Examples:
        cube clean 05-task           # Clean specific task (sessions, state, temp prompts)
        cube clean 05-task --full    # Full reset (+ worktrees, branches, decisions, logs)
        cube clean --old             # Clean sessions >7 days
        cube clean --all             # Clean all completed
        cube clean 05-task --dry-run # Preview what would be deleted
    """
    
    sessions_dir = get_sessions_dir()
    prompts_dir = PROJECT_ROOT / ".prompts"
    decisions_dir = prompts_dir / "decisions"
    logs_dir = Path.home() / ".cube" / "logs"
    
    if not sessions_dir.exists():
        print_info("No sessions directory found")
    
    to_remove = []
    worktrees_to_remove = []
    branches_to_remove = []
    
    if task_id:
        # Session files
        if sessions_dir.exists():
            session_files = list(sessions_dir.glob(f"*{task_id}*SESSION_ID.txt"))
            meta_files = list(sessions_dir.glob(f"*{task_id}*SESSION_ID.txt.meta"))
            to_remove.extend(session_files)
            to_remove.extend(meta_files)
        
        # Temp prompts
        temp_prompts = list(prompts_dir.glob(f"temp-*{task_id}*.md"))
        to_remove.extend(temp_prompts)
        
        # State file
        state_file = Path.home() / ".cube" / "state" / f"{task_id}.json"
        if state_file.exists():
            to_remove.append(state_file)
        
        if full:
            # Decision files
            if decisions_dir.exists():
                decision_files = list(decisions_dir.glob(f"*{task_id}*.json"))
                to_remove.extend(decision_files)
            
            # Prompt files (writer prompt, panel prompt, synthesis, feedback, etc.)
            prompt_files = list(prompts_dir.glob(f"*{task_id}*.md"))
            to_remove.extend(prompt_files)
            
            # Log files
            if logs_dir.exists():
                log_files = list(logs_dir.glob(f"*{task_id}*"))
                to_remove.extend(log_files)
            
            # Git worktrees
            project_name = PROJECT_ROOT.name
            worktree_base = WORKTREE_BASE / project_name
            if worktree_base.exists():
                for wt in worktree_base.iterdir():
                    if task_id in wt.name and wt.is_dir():
                        worktrees_to_remove.append(wt)
            
            # Git branches (local)
            try:
                result = subprocess.run(
                    ["git", "branch", "--list", f"*{task_id}*"],
                    capture_output=True, text=True, cwd=PROJECT_ROOT
                )
                for line in result.stdout.strip().split('\n'):
                    branch = line.strip().lstrip('* ')
                    if branch and task_id in branch:
                        branches_to_remove.append(branch)
            except Exception:
                pass
    
    elif old:
        cutoff = datetime.now() - timedelta(days=7)
        
        if sessions_dir.exists():
            for session_file in sessions_dir.glob("*SESSION_ID.txt"):
                if session_file.stat().st_mtime < cutoff.timestamp():
                    to_remove.append(session_file)
                    meta = session_file.parent / f"{session_file.name}.meta"
                    if meta.exists():
                        to_remove.append(meta)
    
    elif all_tasks:
        if decisions_dir.exists():
            for decision_file in decisions_dir.glob("*-aggregated.json"):
                task_name = decision_file.stem.replace("-aggregated", "")
                
                if sessions_dir.exists():
                    session_files = list(sessions_dir.glob(f"*{task_name}*SESSION_ID.txt"))
                    meta_files = list(sessions_dir.glob(f"*{task_name}*SESSION_ID.txt.meta"))
                    to_remove.extend(session_files)
                    to_remove.extend(meta_files)
    
    total_items = len(to_remove) + len(worktrees_to_remove) + len(branches_to_remove)
    
    if total_items == 0:
        print_info("Nothing to clean")
        return
    
    console.print(f"[yellow]Will remove:[/yellow]")
    console.print()
    
    if to_remove:
        console.print(f"[cyan]Files ({len(to_remove)}):[/cyan]")
        for f in to_remove[:10]:
            console.print(f"  {f.name}")
        if len(to_remove) > 10:
            console.print(f"  ... and {len(to_remove) - 10} more")
        console.print()
    
    if worktrees_to_remove:
        console.print(f"[cyan]Worktrees ({len(worktrees_to_remove)}):[/cyan]")
        for wt in worktrees_to_remove:
            console.print(f"  {wt.name}")
        console.print()
    
    if branches_to_remove:
        console.print(f"[cyan]Branches ({len(branches_to_remove)}):[/cyan]")
        for branch in branches_to_remove:
            console.print(f"  {branch}")
        console.print()
    
    if dry_run:
        print_info("Dry run - nothing deleted")
        return
    
    if not typer.confirm("Proceed with deletion?"):
        print_info("Cancelled")
        return
    
    # Remove files
    removed_count = 0
    for f in to_remove:
        try:
            f.unlink()
            removed_count += 1
        except OSError:
            pass
    
    # Remove worktrees
    for wt in worktrees_to_remove:
        try:
            subprocess.run(
                ["git", "worktree", "remove", str(wt), "--force"],
                capture_output=True, cwd=PROJECT_ROOT
            )
            removed_count += 1
        except Exception:
            # Fallback: remove directory
            import shutil
            try:
                shutil.rmtree(wt)
                removed_count += 1
            except Exception:
                print_warning(f"Failed to remove worktree: {wt.name}")
    
    # Remove branches
    for branch in branches_to_remove:
        try:
            subprocess.run(
                ["git", "branch", "-D", branch],
                capture_output=True, cwd=PROJECT_ROOT
            )
            removed_count += 1
        except Exception:
            print_warning(f"Failed to remove branch: {branch}")
    
    print_success(f"Removed {removed_count} item(s)")
    
    if full and branches_to_remove:
        console.print()
        console.print("[dim]Note: Remote branches not deleted. To delete them:[/dim]")
        for branch in branches_to_remove:
            console.print(f"[dim]  git push origin --delete {branch}[/dim]")
