"""Generic adapter for CLI-based review tools (CodeRabbit, Snyk, etc.)."""

import asyncio
import json
import os
import re
from pathlib import Path
from typing import AsyncGenerator, Optional, Dict, Any

from ..cli_adapter import CLIAdapter, run_subprocess_streaming

class CLIReviewAdapter(CLIAdapter):
    """Adapter for running generic CLI review tools + LLM synthesis."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize with tool configuration."""
        self.tool_cmd = config.get("cmd")
        
        if not self.tool_cmd:
            raise ValueError("CLIReviewAdapter requires 'cmd' config")
            
        self.tool_name = config.get("name") or self.tool_cmd.split()[0]
        self.writer_worktrees = {}  # Set via set_writer_worktrees() before run()
    
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
        
        # Use the passed model as the orchestrator
        orch_model = model
        
        if not self.writer_worktrees:
            yield json.dumps({"type": "assistant", "content": "ERROR: No writer worktrees configured for CLI review"})
            return

        # Run tool in parallel for both writers with real-time streaming
        yield json.dumps({"type": "assistant", "content": f"🔍 Running {self.tool_name} on both writers in parallel..."})
        
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
                        if not clean_line.endswith(('.', '!', '?')):
                            clean_line += '.'
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
                yield json.dumps({"type": "thinking", "content": f"[{self.tool_name}/{writer}] {content}"})
            elif msg_type == "error":
                errors.add(writer)
                yield json.dumps({"type": "assistant", "content": f"❌ ERROR: {self.tool_name} failed on {writer}: {content}"})
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
        
        # Extract task_id from prompt if possible
        # Handles: **Task:** `quick`, Task: rand, task_id: test-task
        task_match = re.search(r'\*?\*?[Tt]ask[_\s]*(?:[Ii][Dd])?:?\*?\*?\s*["\'\`]?([a-zA-Z0-9_-]+)', prompt)
        task_id = task_match.group(1) if task_match else "review"
        
        for writer, lines in output_buffers.items():
            reviews[writer] = "\n".join(lines)
            
            # Save raw output to file
            writer_slug = "writer-a" if "A" in writer else "writer-b"
            review_file = reviews_dir / f"{task_id}-{writer_slug}-{self.tool_name.lower()}.txt"
            review_file.write_text(reviews[writer])
            review_files[writer] = f".prompts/reviews/{review_file.name}"
            
        yield json.dumps({"type": "assistant", "content": f"📁 Saved review output to {reviews_dir.relative_to(worktree)}"})

        # 3. Run Synthesis Agent
        yield json.dumps({"type": "assistant", "content": f"🤖 Synthesizing decision with {orch_model}..."})
        
        synthesis_prompt = self._build_synthesis_prompt(prompt, reviews, review_files)
        
        async for line in run_agent(
            worktree=worktree,
            model=orch_model,
            prompt=synthesis_prompt,
            session_id=None,
            resume=False
        ):
            yield line

    def _build_synthesis_prompt(self, original_prompt: str, reviews: Dict[str, str], review_files: Dict[str, str]) -> str:
        """Construct the synthesis prompt."""
        writer_a_file = review_files.get('Writer A', 'N/A')
        writer_b_file = review_files.get('Writer B', 'N/A')
        
        return f"""
You are a technical judge synthesizing results from a CLI review tool ({self.tool_name}).

## Task Context
{original_prompt}

## Review Output Files (IMPORTANT - reference these in your decision)
- **Writer A:** `{writer_a_file}`
- **Writer B:** `{writer_b_file}`

These files contain the FULL {self.tool_name} output including "Prompt for AI Agent" sections.
The winning writer should read their file to address all issues.

## Review: Writer A
{reviews.get('Writer A', 'No output')}

## Review: Writer B
{reviews.get('Writer B', 'No output')}

## Your Job
1. Analyze ALL issues found in the reviews above for BOTH writers.
2. Determine which implementation is better based ONLY on the review output.
3. Output a JSON decision file that includes the review file paths.

**CRITICAL REQUIREMENTS:**
- Do NOT use any tools (read_file, shell, etc.)
- Make your decision SOLELY based on the review output provided above
- Include the `review_output_files` field so the writer knows where to find full details

**If reviews contain errors or are empty:**
- Use decision: "REQUEST_CHANGES"  
- Use winner: "TIE"
- Set blocker_issues to explain the tool failure

## JSON Format
{{
  "decision": "APPROVED" | "REQUEST_CHANGES",
  "winner": "A" | "B" | "TIE",
  "scores": {{
    "writer_a": {{ "total_weighted": <0-100> }},
    "writer_b": {{ "total_weighted": <0-100> }}
  }},
  "review_output_files": {{
    "writer_a": "{writer_a_file}",
    "writer_b": "{writer_b_file}"
  }},
  "blocker_issues": ["list", "of", "critical", "issues", "from", "the", "review"],
  "recommendation": "Brief explanation. Tell winner to read their review file for full details."
}}

**IMPORTANT:** 
- The `review_output_files` paths let the writer find the FULL {self.tool_name} output
- The output includes "Prompt for AI Agent" sections with detailed fix instructions
- Blocker issues should be a SHORT summary; full details are in the review files

Output ONLY valid JSON.
"""

    def check_installed(self) -> bool:
        import shutil
        cmd_base = self.tool_cmd.split()[0]
        return shutil.which(cmd_base) is not None

    def get_install_instructions(self) -> str:
        return f"Please install {self.tool_cmd.split()[0]} manually."
