# Task: Add Open Source Project Files

**Priority:** P2 (Minor)
**Complexity:** Low
**Files:** Create 3 new files

## Problem

Missing standard open source project files:
- `CONTRIBUTING.md` - How to contribute
- `CODE_OF_CONDUCT.md` - Community standards
- `CHANGELOG.md` - Version history

## Requirements

### 1. CONTRIBUTING.md

Create `CONTRIBUTING.md` with:

- [ ] How to set up development environment
- [ ] How to run tests
- [ ] Code style guidelines
- [ ] Pull request process
- [ ] Issue reporting guidelines

```markdown
# Contributing to Agent Cube

## Development Setup

1. Clone the repo
2. Run `./install.sh`
3. ...

## Running Tests

```bash
pytest tests/
```

## Code Style

- Python 3.11+
- Type hints required
- Google-style docstrings
- Run `ruff check .` before committing

## Pull Requests

1. Fork the repo
2. Create a feature branch
3. Make changes with tests
4. Submit PR against `main`
```

### 2. CODE_OF_CONDUCT.md

Use Contributor Covenant v2.1 (standard):
- https://www.contributor-covenant.org/version/2/1/code_of_conduct/

### 3. CHANGELOG.md

Create `CHANGELOG.md` with Keep a Changelog format:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- CodeRabbit CLI integration as judge
- Configurable prompter model
- Resume without task file

### Fixed
- Gemini timeout detection
- Bare except clauses

## [1.1.0] - 2025-11-25

### Added
- Dynamic layout system
- Config-driven writers/judges
- State management and resume

## [1.0.0] - 2025-11-01

### Added
- Initial release
- Dual writer workflow
- Judge panel
- Autonomous orchestration
```

## Verification

- [ ] All 3 files exist in project root
- [ ] CONTRIBUTING.md has accurate setup instructions
- [ ] CODE_OF_CONDUCT.md has contact info filled in
- [ ] CHANGELOG.md covers recent versions

## Notes

- Keep CONTRIBUTING.md updated as tooling changes
- Update CHANGELOG.md with each release
- Consider adding a PR template (`.github/PULL_REQUEST_TEMPLATE.md`)

