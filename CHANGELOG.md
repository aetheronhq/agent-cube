# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- CONTRIBUTING.md, CODE_OF_CONDUCT.md, and CHANGELOG.md files
- Open source project documentation

## [1.1.0] - 2025-11-25

### Added
- CodeRabbit CLI integration as judge option
- Configurable prompter model
- Resume without task file (`--resume` flag)
- Dynamic layout system with configurable writers/judges
- State management and resume capabilities
- Web UI for monitoring workflow progress

### Fixed
- Gemini timeout detection (parser improvements)
- Bare except clauses (better error handling)
- Orchestration reliability improvements

### Changed
- Config-driven writer/judge configuration (`cube.yaml`)

## [1.0.0] - 2025-11-01

### Added
- Initial release of Agent Cube
- Dual writer competitive development workflow
- Three-judge panel system
- Autonomous orchestration with `cube auto` command
- Git worktree isolation for parallel development
- State management and streaming output
- CLI adapters: cursor-agent, gemini
- Ports & adapters architecture
