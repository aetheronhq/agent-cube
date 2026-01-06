import json
import subprocess
from dataclasses import dataclass


@dataclass
class ReviewComment:
    path: str
    line: int
    body: str
    severity: str = "info"


@dataclass
class Review:
    decision: str  # "APPROVE" | "REQUEST_CHANGES" | "COMMENT"
    summary: str
    comments: list[ReviewComment]


def post_review(pr_number: int, review: Review) -> bool:
    """Post a review to GitHub."""
    body = f"## 🤖 Agent Cube Review\n\n{review.summary}"

    comments_json = json.dumps(
        [{"path": c.path, "line": c.line, "body": f"[{c.severity.upper()}] {c.body}"} for c in review.comments]
    )

    # Construct arguments separately to avoid shell injection issues if they were passed in a shell=True context
    # (though subprocess.run with list handles arguments safely)
    args = [
        "gh",
        "api",
        f"repos/{{owner}}/{{repo}}/pulls/{pr_number}/reviews",
        "-X",
        "POST",
        "-f",
        f"event={review.decision}",
        "-f",
        f"body={body}",
        "-f",
        f"comments={comments_json}",
    ]

    result = subprocess.run(args, capture_output=True, text=True)

    if result.returncode != 0:
        # It might be useful to log the error, but for now we just return False per spec
        # You might want to print stderr if debugging is needed
        pass

    return result.returncode == 0
