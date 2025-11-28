# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- CONTRIBUTING.md with development setup and pull request guidelines
- CODE_OF_CONDUCT.md (Contributor Covenant v2.1)
- CHANGELOG.md with version history

## [1.1.0] - 2025-11-25

### Added
- CodeRabbit CLI integration as judge option
- Configurable prompter model selection
- Resume without task file using `--resume` flag
- Dynamic layout system with configurable writers and judges
- State management and resume capabilities
- Pluggable CLI adapters for different LLM tools
- Parser plugins for different output formats
- Layout adapters for display customization

### Changed
- Configuration now driven by `cube.yaml` for writers and judges
- Improved architecture with ports & adapters pattern

### Fixed
- Gemini timeout detection through parser improvements
- Bare except clauses replaced with proper error handling
- Orchestration reliability improvements

## [1.0.0] - 2025-11-01

### Added
- Initial release of Agent Cube
- Dual writer competitive development workflow
- Three-judge panel system for solution selection
- Autonomous orchestration with `cube auto` command
- Git worktree isolation for parallel agent execution
- State management for workflow tracking
- Streaming output for real-time monitoring
- CLI adapters for cursor-agent and gemini
- Session management and resume capabilities
- Master logging system
- Phase-based workflow organization
- Parallel execution of independent tasks
- Automated PR creation
- Synthesis of best solutions from dual writers
- Peer review cycle with LLM panel
- Human-in-the-loop validation

[Unreleased]: https://github.com/aetheronhq/agent-cube/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/aetheronhq/agent-cube/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/aetheronhq/agent-cube/releases/tag/v1.0.0
