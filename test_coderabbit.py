import asyncio
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add python path
sys.path.insert(0, 'python')

from cube.core.adapters.cli_review_adapter import CLIReviewAdapter

# Mock run_agent to avoid real LLM calls
async def mock_run_agent(worktree, model, prompt, session_id, resume):
    print(f"\n[MOCK LLM] Received Prompt (length {len(prompt)}):")
    print(f"[MOCK LLM] Model: {model}")
    print("-" * 40)
    print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
    print("-" * 40)
    
    # Verify prompt contains our mock output
    if "SQL Injection vulnerability" in prompt:
        print("✅ Prompt contains tool output!")
    else:
        print("❌ Prompt MISSING tool output!")
        
    yield '{"decision": "REQUEST_CHANGES", "winner": "B"}'

async def test_coderabbit_flow():
    print("🚀 Starting CodeRabbit Integration Test")
    
    # Mock config
    config = {
        "cmd": f"{os.getcwd()}/mock-rabbit.sh",
        "name": "MockRabbit"
    }
    
    adapter = CLIReviewAdapter(config)
    
    # Mock checkout to succeed
    with patch.object(CLIReviewAdapter, '_checkout_branch', return_value=True):
        # Patch run_agent
        with patch('cube.core.agent.run_agent', side_effect=mock_run_agent):
            
            # Test Prompt with branch info
            prompt = (
                "Review the following task.\n"
                "Writer A's branch: writer-sonnet/test-task\n"
                "Writer B's branch: writer-codex/test-task"
            )
            
            print("\nRunning adapter...")
            async for line in adapter.run(
                worktree=Path(os.getcwd()),
                model="composer-1",
                prompt=prompt
            ):
                print(f"[Stream] {line}")

if __name__ == "__main__":
    asyncio.run(test_coderabbit_flow())
