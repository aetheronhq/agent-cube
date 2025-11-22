"""Generic adapter for CLI-based review tools (CodeRabbit, Snyk, etc.)."""

import asyncio
import os
from pathlib import Path
from typing import AsyncGenerator, Optional, Dict, Any

from ..cli_adapter import CLIAdapter, read_stream_with_buffer
from ..agent import run_agent
from ...models.types import StreamMessage

class CLIReviewAdapter(CLIAdapter):
    """Adapter for running generic CLI review tools + LLM synthesis."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize with tool configuration.
        
        Args:
            config: Dict containing 'review_tool' and 'orchestrator' settings
        """
        self.tool_config = config.get("review_tool", {})
        self.orch_config = config.get("orchestrator", {})
        
        if not self.tool_config or not self.orch_config:
            raise ValueError("CLIReviewAdapter requires 'review_tool' and 'orchestrator' config")
            
        self.tool_name = self.tool_config.get("name", "Unknown Tool")
        self.tool_cmd = self.tool_config.get("command")
        self.orch_model = self.orch_config.get("model", "claude-3-5-sonnet")
        self.prompt_template = self.orch_config.get("prompt_template", "judge-synthesis.md")
        
        if not self.tool_cmd:
            raise ValueError(f"No command specified for tool {self.tool_name}")

    async def run(
        self,
        worktree: Path,
        model: str,
        prompt: str,  # Contains task context
        session_id: Optional[str] = None,
        resume: bool = False,
    ) -> AsyncGenerator[str, None]:
        """Run the review tool and synthesize results."""
        
        # 1. Parse the prompt to find writer branches
        # The prompt usually contains: "Writer A's branch: writer-sonnet/task-id"
        branches = self._extract_branches(prompt)
        if not branches:
            yield '{"type": "error", "content": "Could not identify writer branches from prompt"}'
            return

        reviews = {}
        
        # 2. Run tool for each writer
        for writer, branch in branches.items():
            yield f'{{"type": "thinking", "content": "Running {self.tool_name} on {writer} ({branch})..."}}'
            
            # Checkout branch
            if not await self._checkout_branch(worktree, branch):
                yield f'{{"type": "error", "content": "Failed to checkout {branch}"}}'
                continue
                
            # Run tool
            output = await self._run_tool(worktree)
            reviews[writer] = output
            
            yield f'{{"type": "thinking", "content": "Completed {self.tool_name} review for {writer}"}}'

        # 3. Run Synthesis Agent
        yield f'{{"type": "thinking", "content": "Synthesizing decision with {self.orch_model}..."}}'
        
        synthesis_prompt = self._build_synthesis_prompt(prompt, reviews)
        
        # Delegate to standard agent runner
        # Note: We stream the JSON chunks directly from the agent
        async for line in run_agent(
            worktree=worktree,  # Context doesn't matter much for synthesis
            model=self.orch_model,
            prompt=synthesis_prompt,
            session_id=None, # Synthesis is stateless
            resume=False
        ):
            yield line

    async def _run_tool(self, cwd: Path) -> str:
        """Execute the configured CLI command."""
        # Replace {{worktree}} placeholder
        cmd_str = self.tool_cmd.replace("{{worktree}}", str(cwd))
        
        # Split into args (naive splitting, could be improved)
        import shlex
        cmd_args = shlex.split(cmd_str)
        
        process = await asyncio.create_subprocess_exec(
            *cmd_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=cwd,
            env=os.environ.copy()
        )
        
        stdout, _ = await process.communicate()
        return stdout.decode("utf-8", errors="replace")

    async def _checkout_branch(self, worktree: Path, branch: str) -> bool:
        """Checkout a git branch in the worktree."""
        process = await asyncio.create_subprocess_exec(
            "git", "checkout", branch,
            cwd=worktree,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        return await process.wait() == 0

    def _extract_branches(self, prompt: str) -> Dict[str, str]:
        """Extract branch names from the judge prompt."""
        # Simple heuristic: look for "Writer A's branch: <name>" pattern
        # This relies on the standard prompt format
        import re
        branches = {}
        
        # Matches: "**Writer A's branch:** `writer-sonnet/task-id`"
        # Or: "Writer A Branch: writer-sonnet/task-id"
        for writer in ["A", "B"]:
            pattern = f"Writer {writer}.*branch:.*[`'\"]?([a-zA-Z0-9/_.-]+)[`'\"]?"
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                branches[f"Writer {writer}"] = match.group(1).strip()
                
        return branches

    def _build_synthesis_prompt(self, original_prompt: str, reviews: Dict[str, str]) -> str:
        """Construct the prompt for the synthesizer agent."""
        # Load template if it exists (TODO: Implement template loading)
        # For now, use a built-in template
        
        return f"""
You are a technical judge synthesizing results from {self.tool_name}.

## Task Context
{original_prompt}

## {self.tool_name} Review: Writer A
{reviews.get('Writer A', 'No output')}

## {self.tool_name} Review: Writer B
{reviews.get('Writer B', 'No output')}

## Your Job
1. Analyze the issues found by {self.tool_name} for each writer.
2. Determine which implementation is better (fewer/less critical issues).
3. Output a JSON decision file following the standard format.

## JSON Format
{{
  "decision": "APPROVED" | "REQUEST_CHANGES",
  "winner": "A" | "B" | "TIE",
  "scores": {{
    "writer_a": {{ "total_weighted": <0-10> }},
    "writer_b": {{ "total_weighted": <0-10> }}
  }},
  "blocker_issues": ["list", "of", "critical", "issues"],
  "recommendation": "Explanation of the decision..."
}}

Output ONLY valid JSON.
"""

    def check_installed(self) -> bool:
        """Check if the tool command is available."""
        import shutil
        cmd_base = self.tool_cmd.split()[0]
        return shutil.which(cmd_base) is not None

    def get_install_instructions(self) -> str:
        """Return generic install instructions."""
        return f"Please install {self.tool_name} manually."

