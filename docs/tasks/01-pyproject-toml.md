# Task: Add pyproject.toml for Proper Python Packaging

**Priority:** P0 (Critical)
**Complexity:** Low
**Files:** New file `pyproject.toml`

## Problem

The project has no `pyproject.toml` or `setup.py`, making it impossible to:
- `pip install .` the package
- Publish to PyPI
- Declare dependencies properly
- Define entry points for CLI

## Requirements

### Functional Requirements

- [ ] Create `pyproject.toml` in project root
- [ ] Use modern PEP 621 format with `[project]` table
- [ ] Define `cube` CLI entry point pointing to `cube.cli:app`
- [ ] List all runtime dependencies from current imports
- [ ] Include optional dev/test dependencies
- [ ] Set Python version requirement (>=3.11)

### Package Metadata

```toml
[project]
name = "agent-cube"
version = "1.1.0"  # Match __version__ in __init__.py
description = "Autonomous multi-agent coding workflow"
authors = [{name = "Aetheron", email = "..."}]
license = {text = "MIT"}
readme = "README.md"
requires-python = ">=3.11"
```

### Dependencies to Include

From scanning imports:
- `typer` - CLI framework
- `rich` - Terminal UI
- `pyyaml` - Config parsing
- `fastapi` - Web framework (for web UI)
- `uvicorn[standard]` - ASGI server
- `aiofiles` - Async file ops

### Entry Points

```toml
[project.scripts]
cube = "cube.cli:app"
```

### Build System

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["python/cube"]
```

## Verification

- [ ] `pip install -e .` works
- [ ] `cube --version` works after install
- [ ] All imports resolve correctly
- [ ] `pip install .` creates working package

## Notes

- Keep `install.sh` for development setup
- Consider adding `[project.optional-dependencies]` for dev tools
