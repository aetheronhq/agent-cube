# Contributing to Agent Cube

Thank you for your interest in contributing to Agent Cube! This document provides guidelines for contributing to the project.

## Development Setup

1. **Prerequisites:**
   - Python 3.11 or higher
   - [cursor-agent CLI](https://cursor.com)
   - Git

2. **Installation:**
   
   Follow the [Installation Guide](INSTALL.md) to set up Agent Cube, then install development dependencies:

   ```bash
   git clone https://github.com/aetheronhq/agent-cube.git
   cd agent-cube
   ./install.sh
   ```

3. **Verify your setup:**

   ```bash
   cube version
   pytest tests/
   ```

## Running Tests

Run the full test suite:

```bash
pytest tests/
```

Run specific test files:

```bash
pytest tests/cli/test_commands.py
```

Run with verbose output:

```bash
pytest tests/ -v
```

Expected output: All tests should pass with no errors.

## Code Style

Agent Cube follows these coding standards:

- **Python 3.11+** required
- **Type hints** required for all functions and methods
- **Docstrings** required (Google style) for public APIs
- **Linting:** Run `ruff check .` before committing

Check your code before committing:

```bash
# Run linter
ruff check .

# Auto-fix issues where possible
ruff check . --fix
```

## Pull Request Process

1. **Fork the repository** and create your feature branch:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** with tests:
   - Write clear, focused commits
   - Add tests for new functionality
   - Update documentation as needed

3. **Run tests and linter:**

   ```bash
   pytest tests/
   ruff check .
   ```

4. **Submit a pull request** against the `main` branch:
   - Provide a clear description of the changes
   - Reference any related issues
   - Ensure CI checks pass

5. **Respond to review feedback** promptly

## Issue Reporting

We use [GitHub Issues](https://github.com/aetheronhq/agent-cube/issues) for bug reports and feature requests.

### Bug Reports

When reporting bugs, please include:

- **What you expected** to happen
- **What actually happened**
- **How to reproduce** the issue (minimal example)
- **Environment details:**
  - Python version (`python --version`)
  - Operating system
  - Stack trace or error message

Example:

```
**Expected:** `cube auto task.md` should start dual writers

**Actual:** Command fails with "cursor-agent not found"

**Steps to reproduce:**
1. Install cube via ./install.sh
2. Run cube auto test.md
3. Error appears

**Environment:**
- Python 3.11.5
- macOS 14.0
- cursor-agent not installed
```

### Feature Requests

When requesting features, please describe:

- **Use case:** What problem are you trying to solve?
- **Proposed solution:** How would this feature help?
- **Why it matters:** How does this benefit other users?

## Questions?

- **Documentation:** See [docs/QUICK_START.md](docs/QUICK_START.md) and [AGENT_CUBE.md](AGENT_CUBE.md)
- **Discussions:** Use [GitHub Discussions](https://github.com/aetheronhq/agent-cube/discussions)
- **Issues:** For bugs or feature requests

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

---

**Thank you for contributing to Agent Cube!** 🧊✨
