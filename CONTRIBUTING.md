# Contributing to Agent Cube

Thank you for your interest in contributing to Agent Cube! 🧊

## How to Contribute

### Reporting Issues

1. **Check existing issues** first to avoid duplicates
2. **Use the issue templates** when available
3. **Include reproduction steps** for bugs
4. **Provide system info**: OS, Python version, cursor-agent version

### Submitting Changes

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature`
3. **Make your changes**
4. **Run tests**: `pytest tests/`
5. **Submit a Pull Request**

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/agent-cube.git
cd agent-cube

# Install in development mode
cd python
pip install -e .

# Run tests
pytest tests/
```

### Code Style

- **Python**: Follow PEP 8
- **Type hints**: Use them for function signatures
- **Docstrings**: Required for public functions
- **No bare exceptions**: Always catch specific exception types

### Pull Request Guidelines

1. **Keep PRs focused** - one feature or fix per PR
2. **Update documentation** if needed
3. **Add tests** for new features
4. **Ensure CI passes** before requesting review

### Testing

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/cli/test_commands.py

# Run with coverage
pytest --cov=cube tests/
```

### Type Checking

We use mypy for static type checking. Run before committing:

```bash
mypy python/cube --ignore-missing-imports
```

Or with full dev setup:

```bash
pip install -e ".[dev]"
mypy python/cube
```

Common fixes:
- Use `Optional[str]` instead of `str = None`
- Add type hints to variables: `data: dict[str, Any] = {}`
- Handle Optional values before method calls

### Areas We Need Help

- **CLI Adapters**: Support for more AI CLIs (Claude Code, etc.)
- **Documentation**: Improve guides and examples
- **Tests**: Increase coverage
- **Bug Fixes**: Check open issues

## Code of Conduct

Be respectful, inclusive, and constructive. We're all here to build cool things together.

## Questions?

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and ideas

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

