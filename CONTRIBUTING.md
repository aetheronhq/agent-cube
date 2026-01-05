# Contributing to Agent Cube

Thank you for your interest in contributing to Agent Cube! 🧊

## Development Setup

1. Follow the [Installation Guide](INSTALL.md) to set up Agent Cube
2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
3. Verify setup:
   ```bash
   pytest tests/
   ```

**Prerequisites:**
- Python 3.11+
- [cursor-agent CLI](https://cursor.com)

## Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/cli/test_commands.py

# Run with verbose output
pytest tests/ -v
```

## Code Style

- **Python 3.11+** required
- **Type hints** required for function signatures
- **Docstrings** for public functions (Google style)
- **Linter**: Run `ruff check .` before committing

```bash
# Check code style
ruff check .

# Auto-fix issues
ruff check . --fix
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make changes with tests
4. Run tests and linter:
   ```bash
   pytest tests/
   ruff check .
   ```
5. Submit PR against `main` branch
6. Respond to review feedback

## Reporting Issues

Use [GitHub Issues](https://github.com/aetheronhq/agent-cube/issues) to report bugs or request features.

**For bugs, include:**
- What you expected to happen
- What actually happened
- Steps to reproduce
- Python version, OS, stack trace

**For features, include:**
- Use case description
- Why it would be helpful

## Questions?

- [GitHub Issues](https://github.com/aetheronhq/agent-cube/issues) - Bugs and feature requests
- [GitHub Discussions](https://github.com/aetheronhq/agent-cube/discussions) - Questions and ideas

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
