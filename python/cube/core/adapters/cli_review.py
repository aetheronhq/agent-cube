"""Generic adapter for CLI-based review tools (CodeRabbit, Snyk, etc.)."""

import asyncio
import json
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, Optional

from .base import CLIAdapter, run_subprocess_streaming


class CLIReviewAdapter(CLIAdapter):
    """Adapter for running generic CLI review tools + LLM synthesis."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize with tool configuration."""
        tool_cmd = config.get("cmd")

        if not tool_cmd:
            raise ValueError("CLIReviewAdapter requires 'cmd' config")

        self.tool_cmd: str = tool_cmd
        self.tool_name = config.get("name") or self.tool_cmd.split()[0]
        self.writer_worktrees: Dict[str, Path] = {}
        self.task_id: Optional[str] = None

    def set_task_id(self, task_id: str) -> None:
        """Set task_id programmatically (required before run)."""
        self.task_id = task_id

    def set_writer_worktrees(self, worktrees: Dict[str, Path]) -> None:
        """Set writer worktree paths programmatically.

        Args:
            worktrees: Dict of {"Writer A": Path("/path/to/worktree-a"), ...}
        """
        self.writer_worktrees = worktrees

    async def run(
        self,
        worktree: Path,
        model: str,
        prompt: str,
        session_id: Optional[str] = None,
        resume: bool = False,
    ) -> AsyncGenerator[str, None]:
        """Run the review tool and synthesize results."""
        from ..agent import run_agent  # Import here to avoid circular dependency

        if not self.task_id:
            raise ValueError("CLIReviewAdapter requires task_id - call set_task_id() before run()")
        task_id = self.task_id

        orch_model = model

        if not self.writer_worktrees:
            yield json.dumps({"type": "assistant", "content": "ERROR: No writer worktrees configured for CLI review"})
            return

        # Run tool on writers with real-time streaming
        num_writers = len(self.writer_worktrees)
        if num_writers == 1:
            writer_name = list(self.writer_worktrees.keys())[0]
            yield json.dumps({"type": "assistant", "content": f"🔍 Running {self.tool_name} on {writer_name}..."})
        else:
            yield json.dumps(
                {"type": "assistant", "content": f"🔍 Running {self.tool_name} on {num_writers} writers in parallel..."}
            )

        reviews = {}
        output_buffers = {writer: [] for writer in self.writer_worktrees}
        line_counts = {writer: 0 for writer in self.writer_worktrees}
        errors = set()

        async def stream_tool_output(writer: str, wt_path: Path, queue: asyncio.Queue):
            """Run tool and push output to shared queue."""
            cmd_str = self.tool_cmd.replace("{{worktree}}", str(wt_path))
            import shlex

            cmd_args = shlex.split(cmd_str)
            last_error_line = None  # Capture actual error messages from output

            try:
                async for line in run_subprocess_streaming(cmd_args, wt_path, self.tool_name):
                    clean_line = line.strip()
                    if clean_line:
                        # Capture FIRST error-like line for better error messages
                        lower = clean_line.lower()
                        if not last_error_line and ("error" in lower or "rate limit" in lower or "failed" in lower):
                            last_error_line = clean_line[:200]
                        # Only append period if the line ends with alphanumeric (avoiding : , ) etc)
                        if clean_line and clean_line[-1].isalnum():
                            clean_line += "."
                        await queue.put((writer, "thinking", clean_line))
                    output_buffers[writer].append(line)
                    line_counts[writer] += 1
            except RuntimeError as e:
                # Use captured error line if available, otherwise generic message
                error_msg = last_error_line or str(e)
                output_buffers[writer].append(f"[TOOL ERROR] {error_msg}")
                await queue.put((writer, "error", error_msg))
            finally:
                await queue.put((writer, "done", None))

        # Create queue and start both tasks
        queue = asyncio.Queue()
        tasks = [stream_tool_output(w, p, queue) for w, p in self.writer_worktrees.items()]
        worker_tasks = [asyncio.create_task(t) for t in tasks]

        # Stream output as it arrives
        completed = set()
        while len(completed) < len(self.writer_worktrees):
            writer, msg_type, content = await queue.get()

            if msg_type == "thinking":
                yield json.dumps({"type": "assistant", "content": f"{writer}: {content}\n"})
            elif msg_type == "error":
                errors.add(writer)
                yield json.dumps(
                    {"type": "assistant", "content": f"❌ ERROR: {self.tool_name} failed on {writer}: {content}"}
                )
            elif msg_type == "done":
                completed.add(writer)
                if writer in errors:
                    if line_counts[writer] == 0:
                        status = f"❌ {self.tool_name} failed for {writer} before producing output"
                    else:
                        status = f"❌ {self.tool_name} completed with errors for {writer} ({line_counts[writer]} lines captured)"
                elif line_counts[writer] == 0:
                    status = f"⚠️  {self.tool_name} produced no output for {writer}"
                else:
                    status = f"✅ {self.tool_name} complete: {line_counts[writer]} lines from {writer}"
                yield json.dumps({"type": "assistant", "content": status})

        # Wait for tasks to finish
        await asyncio.gather(*worker_tasks, return_exceptions=True)

        # Build reviews dict and save to files
        review_files = {}
        reviews_dir = worktree / ".prompts" / "reviews"
        reviews_dir.mkdir(parents=True, exist_ok=True)

        for writer, lines in output_buffers.items():
            reviews[writer] = "\n".join(lines)

            # Save raw output to file - create slug from writer name
            writer_slug = writer.lower().replace(" ", "-")
            review_file = reviews_dir / f"{task_id}-{writer_slug}-{self.tool_name.lower()}.txt"
            review_file.write_text(reviews[writer])
            review_files[writer] = str(review_file)  # Absolute path for synthesis agent

        yield json.dumps(
            {"type": "assistant", "content": f"📁 Saved review output to {reviews_dir.relative_to(worktree)}"}
        )

        # 3. Run Synthesis Agent
        yield json.dumps({"type": "assistant", "content": f"🤖 Synthesizing decision with {orch_model}..."})

        synthesis_prompt = self._build_synthesis_prompt(prompt, reviews, review_files)

        async for line in run_agent(
            worktree=worktree, model=orch_model, prompt=synthesis_prompt, session_id=None, resume=False
        ):
            yield line

    def _build_synthesis_prompt(
        self, original_prompt: str, reviews: Dict[str, str], review_files: Dict[str, str]
    ) -> str:
        """Construct the synthesis prompt."""
        # Build dynamic review sections from whatever writers were reviewed
        review_sections = []
        file_sections = []
        for writer_name, review_content in reviews.items():
            review_sections.append(f"## Review: {writer_name}\n{review_content}")
            file_path = review_files.get(writer_name, "N/A")
            file_sections.append(f"- **{writer_name}:** `{file_path}`")

        reviews_text = "\n\n".join(review_sections) if review_sections else "No reviews available."
        files_text = "\n".join(file_sections) if file_sections else "- No review files available"

        # Extract just the essential context from original prompt
        import re

        judge_match = re.search(r"judge[_-]?(\d+|[a-zA-Z_]+)", original_prompt, re.IGNORECASE)
        judge_key = judge_match.group(0) if judge_match else "judge_4"

        # Find decision file path pattern
        decision_match = re.search(r"\.prompts/decisions/[^\s\]]+\.json", original_prompt)
        decision_path = (
            decision_match.group(0)
            if decision_match
            else f".prompts/decisions/{judge_key}-{self.task_id}-peer-review.json"
        )

        return f"""
You are synthesizing {self.tool_name} review results into a decision. DO NOT review the code yourself.

## Task: {self.task_id}
## Judge: {judge_key}
## Decision File: {decision_path}

## {self.tool_name} Review Output
{reviews_text}

## Review Output Files (for writer reference)
{files_text}

## Your ONLY Job
Read the review output above and create a decision JSON file. That's it.

**DO NOT:**
- Run git commands
- Read source code files
- Run tests
- Do your own code review

**DECISION CRITERIA:**
- APPROVED = The review shows NO issues (e.g., "Review completed ✔" with no problems listed)
- REQUEST_CHANGES = The review found ANY issues
- SKIPPED = The review tool failed (rate limit, error, empty output)

## Create this JSON file at {decision_path}
{{
  "judge": "{judge_key}",
  "task_id": "{self.task_id}",
  "review_type": "peer-review",
  "decision": "APPROVED" | "REQUEST_CHANGES" | "SKIPPED",
  "remaining_issues": [],
  "recommendation": "Brief summary of review result"
}}

Use write_file tool to save the JSON. Nothing else needed.
"""

    def check_installed(self) -> bool:
        import shutil

        cmd_base = self.tool_cmd.split()[0]
        return shutil.which(cmd_base) is not None

    def get_install_instructions(self) -> str:
        return f"Please install {self.tool_cmd.split()[0]} manually."
