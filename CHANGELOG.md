# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- CONTRIBUTING.md, CODE_OF_CONDUCT.md, and CHANGELOG.md files
- Open source project documentation

## [1.2.0] - 2026-02-07

### Added
- Single writer mode (`cube auto --single`, configurable via `default_mode`)
- `cube auto --fix` fetches failed CI/GHA logs and includes them in the fix prompt
- `cube prv <pr>` shortcut for `cube peer-review --pr`
- claude-code adapter (claude CLI) alongside cursor-agent and gemini adapters
- mypy type checking via pre-commit hook
- TIE loop fix: on judge draw, writers receive targeted feedback before re-judging (max 2 retries)
- PR fix correctly identifies task worktree branch (not current workspace branch)

### Fixed
- `-p` prompt now correctly forwarded to synthesis (Phase 6) and minor fixes (Phase 9) on resume
- `cube pr` gives clear error when result is TIE instead of crashing with "Unknown writer"
- `cube auto --fix` no longer exits early when CI is failing but there are no PR comments
- Judge sessions gracefully fall back to fresh mode when no prior session exists
- Output truncation preserves colors and only triggers at 3× terminal width
- Worktree push no longer fails on detached HEAD branches

### Changed
- Default models updated to Sonnet 4.6 (writers/judges) and GPT-5.3 Codex High (Codex judge)
- Gemini 3.1 Pro replaces Gemini 3 Pro as third judge
- `cube auto --fix` PR detection prioritises most recent open PR for the task branch

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
