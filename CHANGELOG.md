# Changelog

All notable changes to Agent Cube will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial open source release
- Dual-writer parallel execution with configurable AI models
- Judge panel for code review and winner selection
- Synthesis workflow for combining best ideas from both writers
- Web UI for monitoring workflow progress
- CLI tools: `cube auto`, `cube status`, `cube panel`, `cube peer-review`
- Support for multiple LLM backends via adapters
- Git worktree isolation for parallel development

### Changed
- Compute workflow path at runtime from peer review decisions (no stale state)

### Fixed
- Block PR creation when peer review has outstanding issues
- CLI now shows decision status consistently with web UI
- Peer-review alias correctly runs peer review on MERGE path

## [0.1.0] - 2024-12-24

### Added
- Initial release with core dual-writer workflow
- Judge panel with configurable judges
- Basic CLI interface

