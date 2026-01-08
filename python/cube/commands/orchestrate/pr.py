"""PR creation for Agent Cube workflow."""

import subprocess

from ...core.config import PROJECT_ROOT
from ...core.output import console, print_success, print_warning


async def create_pr(task_id: str, winner: str):
    """Create PR automatically."""
    from ...core.user_config import get_writer_by_key_or_metadata

    winner_cfg = get_writer_by_key_or_metadata(winner, task_id)
    branch = f"writer-{winner_cfg.name}/{task_id}"

    console.print(f"[green]✅ Creating PR from: {branch}[/green]")
    console.print()

    try:
        result = subprocess.run(
            [
                "gh",
                "pr",
                "create",
                "--base",
                "main",
                "--head",
                branch,
                "--title",
                f"feat: {task_id}",
                "--body",
                f"Autonomous implementation via Agent Cube\n\nWinner: Writer {winner}\nBranch: {branch}\n\nReview decisions in `.prompts/decisions/{task_id}-*.json`",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            pr_url = result.stdout.strip().split("\n")[-1]
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
