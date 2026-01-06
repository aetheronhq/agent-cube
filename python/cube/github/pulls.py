import json
import subprocess
from dataclasses import dataclass


@dataclass
class PRData:
    number: int
    title: str
    body: str
    diff: str
    head_branch: str
    base_branch: str
    commits: list[str]
    existing_reviews: list[dict]


def fetch_pr(pr_number: int) -> PRData:
    """Fetch PR metadata via gh CLI."""
    # Get PR details
    result = subprocess.run(
        ["gh", "api", f"repos/{{owner}}/{{repo}}/pulls/{pr_number}"], capture_output=True, text=True, check=True
    )
    data = json.loads(result.stdout)

    # Get diff
    diff_result = subprocess.run(
        ["gh", "api", f"repos/{{owner}}/{{repo}}/pulls/{pr_number}", "-H", "Accept: application/vnd.github.diff"],
        capture_output=True,
        text=True,
        check=True,
    )

    # Get existing reviews (to avoid duplicates)
    reviews_result = subprocess.run(
        ["gh", "api", f"repos/{{owner}}/{{repo}}/pulls/{pr_number}/reviews"], capture_output=True, text=True, check=True
    )

    # Get commits list
    commits_result = subprocess.run(
        ["gh", "api", f"repos/{{owner}}/{{repo}}/pulls/{pr_number}/commits"], capture_output=True, text=True, check=True
    )
    commits_data = json.loads(commits_result.stdout)

    return PRData(
        number=pr_number,
        title=data["title"],
        body=data.get("body", ""),
        diff=diff_result.stdout,
        head_branch=data["head"]["ref"],
        base_branch=data["base"]["ref"],
        commits=[c["sha"][:7] for c in commits_data],
        existing_reviews=json.loads(reviews_result.stdout),
    )
