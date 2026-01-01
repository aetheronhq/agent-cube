"""Run a single agent with any model."""

import asyncio
from pathlib import Path
import typer

from ..core.agent import run_agent
from ..core.output import print_error, print_info, console
from ..core.config import PROJECT_ROOT
from ..core.user_config import load_config
from ..core.adapters.registry import get_adapter
from ..core.parsers.registry import get_parser
from ..automation.stream import format_stream_message

async def run_single_agent(
    model: str,
    prompt_text: str,
    worktree: Path
) -> None:
    """Run a single agent and stream output."""
    from ..core.single_layout import SingleAgentLayout
    
    config = load_config()
    cli_name = config.cli_tools.get(model, "cursor-agent")
    
    adapter = get_adapter(cli_name)
    if not adapter.check_installed():
        print_error(f"{cli_name} not installed (needed for {model})")
        console.print()
        console.print(adapter.get_install_instructions())
        raise RuntimeError(f"{cli_name} not installed")
    
    parser = get_parser(cli_name)
    layout = SingleAgentLayout
    layout.initialize(f"{model}")
    
    console.print(f"[cyan]🤖 Running {model} with {cli_name}[/cyan]")
    console.print()
    
    layout.start()
    
    stream = run_agent(
        worktree,
        model,
        prompt_text,
        session_id=None,
        resume=False
    )
    
    async for line in stream:
        msg = parser.parse(line)
        if msg:
            formatted = format_stream_message(msg, "Agent", "cyan")
            if formatted:
                if formatted.startswith("[thinking]"):
                    thinking_text = formatted.replace("[thinking]", "").replace("[/thinking]", "")
                    layout.add_thinking(thinking_text)
                elif msg.type == "assistant" and msg.content:
                    layout.add_assistant_message(msg.content, "Agent", "cyan")
                else:
                    layout.add_output(formatted)
    
    layout.close()
    console.print()
    console.print("[green]✅ Completed[/green]")

def run_command(
    model: str,
    prompt: str,
    directory: str = "."
) -> None:
    """Run a single agent with specified model.
    
    Examples:
        cube run gemini-2.5-pro "Explain this codebase"
        cube run sonnet-4.5-thinking "Add tests for auth.ts"
        cube run grok "Review the API design" --directory apps/api
    """
    config = load_config()
    
    if model not in config.cli_tools:
        print_error(f"Unknown model: {model}")
        console.print()
        console.print("Available models:")
        for m in config.cli_tools.keys():
            cli = config.cli_tools[m]
            console.print(f"  [cyan]{m}[/cyan] ({cli})")
        raise typer.Exit(1)
    
    worktree = PROJECT_ROOT / directory
    if not worktree.exists():
        print_error(f"Directory not found: {directory}")
        raise typer.Exit(1)
    
    print_info(f"Model: {model}")
    print_info(f"Directory: {worktree}")
    print_info(f"Prompt: {prompt[:100]}...")
    console.print()
    
    try:
        asyncio.run(run_single_agent(model, prompt, worktree))
    except RuntimeError as e:
        print_error(str(e))
        raise typer.Exit(1)

