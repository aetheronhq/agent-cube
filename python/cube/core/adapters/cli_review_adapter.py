"""Generic adapter for CLI-based review tools (CodeRabbit, Snyk, etc.)."""

import asyncio
import os
from pathlib import Path
from typing import AsyncGenerator, Optional, Dict, Any

from ..cli_adapter import CLIAdapter, read_stream_with_buffer

class CLIReviewAdapter(CLIAdapter):
    """Adapter for running generic CLI review tools + LLM synthesis."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize with tool configuration."""
        self.tool_cmd = config.get("cmd")
        
        if not self.tool_cmd:
            raise ValueError("CLIReviewAdapter requires 'cmd' config")
            
        self.tool_name = config.get("name") or self.tool_cmd.split()[0]
        self.branches = None
    
    def set_branches(self, branches: Dict[str, str]) -> None:
        """Set writer branches programmatically.
        
        Args:
            branches: Dict of {"Writer A": "writer-sonnet/task-id", "Writer B": "writer-codex/task-id"}
        """
        self.branches = branches

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
        
        # 1. Get branches (programmatic if set, otherwise extract from prompt)
        if self.branches:
            branches = self.branches
        else:
            branches = self._extract_branches(prompt)
            if not branches:
                yield '{"type": "error", "content": "Could not identify writer branches from prompt"}'
                return

        reviews = {}
        
        # 2. Run tool for each writer
        for writer, branch in branches.items():
            yield f'{{"type": "thinking", "content": "Running {self.tool_name} on {writer} ({branch})..."}}'
            
            if not await self._checkout_branch(worktree, branch):
                yield f'{{"type": "error", "content": "Failed to checkout {branch}"}}'
                continue
            
            yield f'{{"type": "thinking", "content": "Checked out {branch}, executing tool..."}}'
            
            output_buffer = []
            line_count = 0
            async for line in self._run_tool_stream(worktree):
                line_count += 1
                # Stream tool output as thinking to show progress
                # Escape JSON chars for the yield string
                clean_line = line.strip().replace('"', '\\"').replace('\\', '\\\\')
                if clean_line:
                    yield f'{{"type": "thinking", "content": "[{self.tool_name}] {clean_line}"}}'
                output_buffer.append(line)
            
            review_text = "\n".join(output_buffer)
            reviews[writer] = review_text
            yield f'{{"type": "thinking", "content": "Tool produced {line_count} lines ({len(review_text)} chars) for {writer}"}}'

        # 3. Run Synthesis Agent
        yield f'{{"type": "thinking", "content": "Synthesizing decision with {orch_model}..."}}'
        
        synthesis_prompt = self._build_synthesis_prompt(prompt, reviews)
        
        async for line in run_agent(
            worktree=worktree,
            model=orch_model,
            prompt=synthesis_prompt,
            session_id=None,
            resume=False
        ):
            yield line

    async def _run_tool_stream(self, cwd: Path) -> AsyncGenerator[str, None]:
        """Execute the configured CLI command and stream output."""
        cmd_str = self.tool_cmd.replace("{{worktree}}", str(cwd))
        import shlex
        cmd_args = shlex.split(cmd_str)
        
        process = await asyncio.create_subprocess_exec(
            *cmd_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=cwd,
            env=os.environ.copy()
        )
        
        if process.stdout:
            async for line in read_stream_with_buffer(process.stdout):
                yield line
        
        await process.wait()

    async def _checkout_branch(self, worktree: Path, branch: str) -> bool:
        """Checkout a git branch."""
        process = await asyncio.create_subprocess_exec(
            "git", "checkout", branch,
            cwd=worktree,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        return await process.wait() == 0

    def _extract_branches(self, prompt: str) -> Dict[str, str]:
        """Extract branch names from prompt."""
        import re
        branches = {}
        for writer in ["A", "B"]:
            # Matches: **Writer A Branch:** `writer-sonnet/task-id`
            # Matches: Writer A's branch: writer-sonnet/task-id
            pattern = f"Writer {writer}.*?branch:.*?([a-zA-Z0-9/_.-]+)"
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                raw_branch = match.group(1)
                # Clean up any accidentally captured quotes/backticks
                branches[f"Writer {writer}"] = raw_branch.strip("`'\" ")
        return branches

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

**CRITICAL: Do NOT use any tools (read_file, shell, etc.). Make your decision SOLELY based on the review output provided above. If reviews are empty, output a TIE decision.**

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
