"""Install command."""

import os
import sys
from pathlib import Path
import typer

from ..core.output import print_info, print_success, print_warning, print_error

def install_command() -> None:
    """Install cube-py CLI to PATH."""
    print_info("Installing cube-py CLI...")
    
    local_bin = Path.home() / ".local" / "bin"
    
    if not local_bin.exists():
        print_warning("Creating ~/.local/bin directory")
        local_bin.mkdir(parents=True, exist_ok=True)
    
    target = local_bin / "cube-py"
    
    if target.exists() or target.is_symlink():
        print_warning("Removing existing cube-py installation")
        target.unlink()
    
    python_path = Path(sys.executable)
    cube_module = Path(__file__).parent.parent
    
    script_content = f"""#!/bin/bash
{python_path} -m cube.cli "$@"
"""
    
    target.write_text(script_content)
    target.chmod(0o755)
    
    print_success(f"Cube-py CLI installed to {target}")
    
    path_env = os.environ.get("PATH", "")
    if str(local_bin) not in path_env:
        print_warning("~/.local/bin is not in your PATH")
        console.print()
        console.print("Add this line to your ~/.zshrc or ~/.bashrc:")
        console.print(f'[yellow]export PATH="$HOME/.local/bin:$PATH"[/yellow]')
        console.print()
        console.print("Then run: source ~/.zshrc (or ~/.bashrc)")
    else:
        print_success("~/.local/bin is already in your PATH")
        console.print()
        console.print("You can now run: [green]cube-py --help[/green]")

