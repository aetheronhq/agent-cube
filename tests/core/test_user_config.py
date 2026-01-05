"""Tests for cube.core.user_config module."""

from pathlib import Path

import pytest
from cube.core.user_config import (
    CubeConfig,
    JudgeConfig,
    WriterConfig,
    clear_config_cache,
    find_config_files,
    get_judge_config,
    get_writer_config,
    load_config,
    merge_config_data,
    resolve_judge_alias,
    resolve_writer_alias,
)


@pytest.fixture(autouse=True)
def reset_config():
    """Clear config cache before and after each test."""
    clear_config_cache()
    yield
    clear_config_cache()


@pytest.fixture
def mock_config(tmp_path, monkeypatch):
    """Create a minimal cube.yaml for testing."""
    config_content = """
writers:
  writer_a:
    name: "opus"
    model: "opus-4.5"
    label: "Writer Opus"
    color: "green"
  writer_b:
    name: "codex"
    model: "gpt-5.1"
    label: "Writer Codex"
    color: "blue"

judges:
  judge_1:
    model: "opus-4.5"
    label: "Judge Opus"
    color: "green"
  judge_2:
    model: "gpt-5.1"
    label: "Judge Codex"
    color: "yellow"

behavior:
  auto_commit: true
  auto_push: false
  default_mode: "dual"
  default_writer: "writer_a"
"""
    config_path = tmp_path / "cube.yaml"
    config_path.write_text(config_content)
    monkeypatch.chdir(tmp_path)

    (tmp_path / ".git").mkdir()

    return config_path


class TestMergeConfigData:
    """Tests for merge_config_data function."""

    def test_shallow_merge_overrides(self):
        """Override values replace base values."""
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}

        result = merge_config_data(base, override)

        assert result == {"a": 1, "b": 3, "c": 4}

    def test_deep_merge_nested_dicts(self):
        """Nested dicts are merged recursively."""
        base = {
            "writers": {
                "writer_a": {"name": "opus", "model": "opus-4.5"},
            }
        }
        override = {
            "writers": {
                "writer_a": {"model": "opus-5.0"},
                "writer_b": {"name": "codex", "model": "gpt-5.1"},
            }
        }

        result = merge_config_data(base, override)

        assert result["writers"]["writer_a"]["name"] == "opus"
        assert result["writers"]["writer_a"]["model"] == "opus-5.0"
        assert result["writers"]["writer_b"]["name"] == "codex"

    def test_override_replaces_non_dict_with_dict(self):
        """Non-dict value is replaced by dict."""
        base = {"key": "string_value"}
        override = {"key": {"nested": "dict"}}

        result = merge_config_data(base, override)

        assert result["key"] == {"nested": "dict"}

    def test_does_not_mutate_base(self):
        """Base dict is not mutated."""
        base = {"a": 1, "b": {"c": 2}}
        override = {"b": {"c": 3}}

        merge_config_data(base, override)

        assert base["b"]["c"] == 2


class TestLoadConfig:
    """Tests for load_config function."""

    def test_returns_cube_config(self, mock_config):
        """load_config() returns a CubeConfig dataclass."""
        config = load_config()
        assert isinstance(config, CubeConfig)

    def test_loads_writers(self, mock_config):
        """Writers are loaded correctly."""
        config = load_config()

        assert "writer_a" in config.writers
        assert "writer_b" in config.writers
        assert config.writers["writer_a"].name == "opus"
        assert config.writers["writer_b"].name == "codex"

    def test_loads_judges(self, mock_config):
        """Judges are loaded correctly."""
        config = load_config()

        assert "judge_1" in config.judges
        assert "judge_2" in config.judges
        assert config.judges["judge_1"].label == "Judge Opus"

    def test_loads_behavior_settings(self, mock_config):
        """Behavior settings are loaded correctly."""
        config = load_config()

        assert config.auto_commit is True
        assert config.auto_push is False
        assert config.default_mode == "dual"
        assert config.default_writer == "writer_a"

    def test_caches_config(self, mock_config):
        """Config is cached after first load."""
        config1 = load_config()
        config2 = load_config()

        assert config1 is config2


class TestClearConfigCache:
    """Tests for clear_config_cache function."""

    def test_forces_reload(self, tmp_path, monkeypatch):
        """After clear_config_cache(), next load_config() reloads from disk."""
        config_content = """
writers:
  writer_a:
    name: "opus"
    model: "opus-4.5"
    label: "Writer Opus"
    color: "green"

judges:
  judge_1:
    model: "opus-4.5"
    label: "Judge 1"
    color: "green"
"""
        config_path = tmp_path / "cube.yaml"
        config_path.write_text(config_content)
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        config1 = load_config()
        assert config1.writers["writer_a"].label == "Writer Opus"

        updated_content = config_content.replace("Writer Opus", "Updated Label")
        config_path.write_text(updated_content)

        clear_config_cache()
        config2 = load_config()

        assert config2.writers["writer_a"].label == "Updated Label"
        assert config1 is not config2


class TestGetWriterConfig:
    """Tests for get_writer_config function."""

    def test_get_by_exact_key(self, mock_config):
        """Get writer by exact key (writer_a, writer_b)."""
        writer_a = get_writer_config("writer_a")
        writer_b = get_writer_config("writer_b")

        assert writer_a.key == "writer_a"
        assert writer_a.name == "opus"
        assert writer_b.key == "writer_b"
        assert writer_b.name == "codex"

    def test_fallback_for_unknown_key(self, mock_config):
        """Unknown key falls back to first writer."""
        result = get_writer_config("unknown_writer")

        assert result.key == "writer_a"


class TestGetJudgeConfig:
    """Tests for get_judge_config function."""

    def test_get_by_exact_key(self, mock_config):
        """Get judge by exact key (judge_1, judge_2)."""
        judge_1 = get_judge_config("judge_1")
        judge_2 = get_judge_config("judge_2")

        assert judge_1.key == "judge_1"
        assert judge_1.label == "Judge Opus"
        assert judge_2.key == "judge_2"
        assert judge_2.label == "Judge Codex"

    def test_unknown_key_raises(self, mock_config):
        """Unknown judge key raises KeyError."""
        with pytest.raises(KeyError, match="Unknown judge key"):
            get_judge_config("judge_999")


class TestResolveWriterAlias:
    """Tests for resolve_writer_alias function."""

    def test_resolve_by_name(self, mock_config):
        """Resolve by writer name (opus, codex)."""
        opus = resolve_writer_alias("opus")
        codex = resolve_writer_alias("codex")

        assert opus.key == "writer_a"
        assert codex.key == "writer_b"

    def test_resolve_by_key(self, mock_config):
        """Resolve by writer key (writer_a, writer_b)."""
        result = resolve_writer_alias("writer_a")

        assert result.key == "writer_a"
        assert result.name == "opus"

    def test_case_insensitive(self, mock_config):
        """Alias resolution is case-insensitive."""
        opus_lower = resolve_writer_alias("opus")
        opus_upper = resolve_writer_alias("OPUS")

        assert opus_lower.key == opus_upper.key

    def test_unknown_alias_raises(self, mock_config):
        """Unknown alias raises KeyError."""
        with pytest.raises(KeyError, match="Unknown writer"):
            resolve_writer_alias("unknown_alias")


class TestResolveJudgeAlias:
    """Tests for resolve_judge_alias function."""

    def test_resolve_by_key(self, mock_config):
        """Resolve by judge key (judge_1, judge_2)."""
        result = resolve_judge_alias("judge_1")

        assert result.key == "judge_1"
        assert result.label == "Judge Opus"

    def test_resolve_hyphenated(self, mock_config):
        """Resolve hyphenated key (judge-1 -> judge_1)."""
        result = resolve_judge_alias("judge-1")

        assert result.key == "judge_1"

    def test_resolve_by_label(self, mock_config):
        """Resolve by judge label."""
        result = resolve_judge_alias("Judge Opus")

        assert result.key == "judge_1"

    def test_unknown_alias_raises(self, mock_config):
        """Unknown alias raises KeyError."""
        with pytest.raises(KeyError, match="Unknown judge"):
            resolve_judge_alias("unknown_judge")


class TestWriterConfig:
    """Tests for WriterConfig dataclass."""

    def test_session_key_format(self):
        """WriterConfig.session_key() returns correct format."""
        writer = WriterConfig(
            key="writer_a",
            name="opus",
            model="opus-4.5",
            label="Writer Opus",
            color="green",
        )

        result = writer.session_key("my-task")

        assert result == "WRITER_A_my-task"

    def test_worktree_name_format(self):
        """WriterConfig.worktree_name() returns correct format."""
        writer = WriterConfig(
            key="writer_a",
            name="opus",
            model="opus-4.5",
            label="Writer Opus",
            color="green",
        )

        result = writer.worktree_name("my-task")

        assert result == "writer-opus-my-task"


class TestJudgeConfig:
    """Tests for JudgeConfig dataclass."""

    def test_session_key_format(self):
        """JudgeConfig.session_key() returns correct format."""
        judge = JudgeConfig(
            key="judge_1",
            model="opus-4.5",
            label="Judge Opus",
            color="green",
        )

        result = judge.session_key("my-task", "panel")

        assert result == "JUDGE_1_my-task_panel"

    def test_default_type_is_llm(self):
        """Default judge type is 'llm'."""
        judge = JudgeConfig(
            key="judge_1",
            model="opus-4.5",
            label="Judge 1",
            color="green",
        )

        assert judge.type == "llm"

    def test_cli_review_type(self):
        """CLI review type can be set."""
        judge = JudgeConfig(
            key="judge_4",
            model="gpt-5.2",
            label="CodeRabbit",
            color="magenta",
            type="cli-review",
            cmd="coderabbit review",
        )

        assert judge.type == "cli-review"
        assert judge.cmd == "coderabbit review"

    def test_peer_review_only_default(self):
        """peer_review_only defaults to False."""
        judge = JudgeConfig(
            key="judge_1",
            model="opus-4.5",
            label="Judge 1",
            color="green",
        )

        assert judge.peer_review_only is False


class TestFindConfigFiles:
    """Tests for find_config_files function."""

    def test_finds_repo_config(self, tmp_path, monkeypatch):
        """Finds cube.yaml in repo root."""
        config_path = tmp_path / "cube.yaml"
        config_path.write_text("version: 1.0")
        (tmp_path / ".git").mkdir()
        monkeypatch.chdir(tmp_path)

        base, global_cfg, repo = find_config_files()

        assert repo == config_path

    def test_finds_global_config(self, tmp_path, monkeypatch):
        """Finds ~/.cube/cube.yaml."""
        home = tmp_path / "home"
        cube_dir = home / ".cube"
        cube_dir.mkdir(parents=True)
        global_config = cube_dir / "cube.yaml"
        global_config.write_text("version: 1.0")

        monkeypatch.setattr(Path, "home", lambda: home)
        monkeypatch.chdir(tmp_path)

        base, global_cfg, repo = find_config_files()

        assert global_cfg == global_config

    def test_returns_none_for_missing(self, tmp_path, monkeypatch):
        """Returns None for missing config files."""
        empty_home = tmp_path / "empty_home"
        empty_home.mkdir()
        monkeypatch.setattr(Path, "home", lambda: empty_home)
        monkeypatch.chdir(tmp_path)

        base, global_cfg, repo = find_config_files()

        assert global_cfg is None
        assert repo is None
