"""Generic adapter for CLI-based review tools (CodeRabbit, Snyk, etc.)."""

import asyncio
import os
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
            yield '{"type": "assistant", "content": "ERROR: No writer worktrees configured for CLI review"}'
            return

        # Run tool in parallel for both writers with real-time streaming
        yield f'{{"type": "assistant", "content": "🔍 Running {self.tool_name} on both writers in parallel..."}}'
        
        reviews = {}
        output_buffers = {"Writer A": [], "Writer B": []}
        line_counts = {"Writer A": 0, "Writer B": 0}
        
        async def stream_tool_output(writer: str, wt_path: Path, queue: asyncio.Queue):
            """Run tool and push output to shared queue."""
            cmd_str = self.tool_cmd.replace("{{worktree}}", str(wt_path))
            import shlex
            cmd_args = shlex.split(cmd_str)
            
            try:
                async for line in run_subprocess_streaming(cmd_args, wt_path, self.tool_name):
                    clean_line = line.strip().replace('"', '\\"').replace('\\', '\\\\')
                    if clean_line:
                        if not clean_line.endswith(('.', '!', '?')):
                            clean_line += '.'
                        await queue.put((writer, "thinking", clean_line))
                    output_buffers[writer].append(line)
                    line_counts[writer] += 1
            except RuntimeError as e:
                await queue.put((writer, "error", str(e)))
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
                yield f'{{"type": "thinking", "content": "[{self.tool_name}/{writer}] {content}"}}'
            elif msg_type == "error":
                yield f'{{"type": "assistant", "content": "❌ ERROR: {self.tool_name} failed on {writer}: {content}"}}'
                completed.add(writer)
            elif msg_type == "done":
                completed.add(writer)
                if line_counts[writer] == 0:
                    yield f'{{"type": "assistant", "content": "⚠️  {self.tool_name} produced no output for {writer}"}}'
                else:
                    yield f'{{"type": "assistant", "content": "✅ {self.tool_name} complete: {line_counts[writer]} lines from {writer}"}}'
        
        # Wait for tasks to finish
        await asyncio.gather(*worker_tasks, return_exceptions=True)
        
        # Build reviews dict
        for writer in self.writer_worktrees.keys():
            reviews[writer] = "\n".join(output_buffers[writer])

        # 3. Run Synthesis Agent
        # Important milestone -> main output
        yield f'{{"type": "assistant", "content": "🤖 Synthesizing decision with {orch_model}..."}}'
        
        synthesis_prompt = self._build_synthesis_prompt(prompt, reviews)
        
        async for line in run_agent(
            worktree=worktree,
            model=orch_model,
            prompt=synthesis_prompt,
            session_id=None,
            resume=False
        ):
            yield line

    def _build_synthesis_prompt(self, original_prompt: str, reviews: Dict[str, str]) -> str:
        """Construct the synthesis prompt."""
        return f"""
You are a technical judge synthesizing results from a CLI review tool.

## Task Context
{original_prompt}

## Review: Writer A
{reviews.get('Writer A', 'No output')}

## Review: Writer B
{reviews.get('Writer B', 'No output')}

## Your Job
1. Analyze the issues found in the reviews above.
2. Determine which implementation is better based ONLY on the review output.
3. Output a JSON decision file.

**CRITICAL: Do NOT use any tools (read_file, shell, etc.). Make your decision SOLELY based on the review output provided above.**

**If reviews contain errors or are empty:**
- Use decision: "REQUEST_CHANGES"  
- Use winner: "TIE"
- Set blocker_issues to explain the tool failure
- Do NOT approve when reviews failed

## JSON Format
{{
  "decision": "APPROVED" | "REQUEST_CHANGES",
  "winner": "A" | "B" | "TIE",
  "scores": {{
    "writer_a": {{ "total_weighted": <0-10> }},
    "writer_b": {{ "total_weighted": <0-10> }}
  }},
  "blocker_issues": ["list", "of", "critical", "issues"],
  "recommendation": "Explanation..."
}}

Output ONLY valid JSON.
"""

    def check_installed(self) -> bool:
        import shutil
        cmd_base = self.tool_cmd.split()[0]
        return shutil.which(cmd_base) is not None

    def get_install_instructions(self) -> str:
        return f"Please install {self.tool_cmd.split()[0]} manually."
