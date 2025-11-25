"""Utility functions for orchestration."""

import subprocess
from pathlib import Path

from ...core.output import print_error, print_success, print_warning, console
from ...core.config import PROJECT_ROOT

def extract_task_id_from_file(task_file: str) -> str:
    """Extract task ID from filename."""
    name = Path(task_file).stem
    
    if not name:
        raise ValueError(f"Cannot extract task ID from: {task_file}")
    
    if name.startswith("writer-prompt-"):
        task_id = name.replace("writer-prompt-", "")
    elif name.startswith("task-"):
        task_id = name.replace("task-", "")
    else:
        parts = name.split("-")
        if len(parts) > 0 and parts[0].isdigit():
            task_id = name
        else:
            task_id = name
    
    if not task_id or task_id.startswith("-") or task_id.endswith("-"):
        raise ValueError(f"Invalid task ID extracted: '{task_id}' from {task_file}")
    
    return task_id

async def create_pr(task_id: str, winner: str):
    """Create PR automatically."""
    from ...core.user_config import get_writer_by_key_or_letter
    
    winner_cfg = get_writer_by_key_or_letter(winner)
    branch = f"writer-{winner_cfg.name}/{task_id}"
    
    console.print(f"[green]✅ Creating PR from: {branch}[/green]")
    console.print()
    
    try:
        result = subprocess.run(
            [
                "gh", "pr", "create",
                "--base", "main",
                "--head", branch,
                "--title", f"feat: {task_id}",
                "--body", f"Autonomous implementation via Agent Cube\n\nWinner: Writer {winner}\nBranch: {branch}\n\nReview decisions in `.prompts/decisions/{task_id}-*.json`"
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            pr_url = result.stdout.strip().split('\n')[-1]
            print_success(f"✅ PR created: {pr_url}")
        else:
            print_warning("⚠️  PR creation failed (maybe already exists?)")
            console.print()
            console.print(f"[dim]{result.stderr}[/dim]")
            console.print()
            console.print("Create manually:")
            console.print(f"  gh pr create --base main --head {branch} --title 'feat: {task_id}'")
    
    except FileNotFoundError:
        print_warning("⚠️  gh CLI not installed")
        console.print()
        console.print("Install: https://cli.github.com")
        console.print()
        console.print("Or create PR manually:")
        console.print(f"  gh pr create --base main --head {branch} --title 'feat: {task_id}'")
    
    console.print()
    print_success("🎉 Autonomous workflow complete!")
