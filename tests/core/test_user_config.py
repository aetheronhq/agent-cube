"""
Tests for cube.core.user_config module."""

import pytest
import yaml
from cube.core.user_config import (
    CubeConfig,
    WriterConfig,
    clear_config_cache,
    get_judge_config,
    get_writer_config,
    load_config,
    merge_config_data,
    resolve_judge_alias,
    resolve_writer_alias,
)


@pytest.fixture(autouse=True)
def reset_config():
    """Clear config cache before each test."""
    clear_config_cache()
    yield
    clear_config_cache()


@pytest.fixture
def mock_config_files(tmp_path, monkeypatch):
    """Create a minimal cube.yaml and mock find_config_files."""
    config_data = {
        "writers": {
            "writer_a": {"name": "opus", "model": "opus-4.5", "label": "Writer Opus", "color": "green"},
            "writer_b": {"name": "codex", "model": "gpt-5.1", "label": "Writer Codex", "color": "blue"},
        },
        "judges": {
            "judge_1": {"model": "opus-4.5", "label": "Judge 1", "color": "green"},
            "judge_2": {"model": "gpt-4", "label": "Judge 2", "color": "red"},
        },
        "writer_order": ["writer_a", "writer_b"],
    }
    config_path = tmp_path / "cube.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config_data, f)

    # Mock find_config_files to return this file as repo_config
    monkeypatch.setattr("cube.core.user_config.find_config_files", lambda: (None, None, config_path))

    return config_path


class TestUserConfig:
    def test_load_config_returns_cube_config(self, mock_config_files):
        """load_config() returns a CubeConfig dataclass."""
        config = load_config()
        assert isinstance(config, CubeConfig)
        assert "writer_a" in config.writers
        assert "judge_1" in config.judges

    def test_merge_config_data_shallow(self):
        """Override values replace base values."""
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}
        merged = merge_config_data(base, override)
        assert merged == {"a": 1, "b": 3, "c": 4}

    def test_merge_config_data_deep(self):
        """Nested dicts are merged recursively."""
        base = {"nested": {"x": 1, "y": 2}, "top": 0}
        override = {"nested": {"y": 3, "z": 4}}
        merged = merge_config_data(base, override)
        assert merged["nested"] == {"x": 1, "y": 3, "z": 4}
        assert merged["top"] == 0

    def test_get_writer_config_by_key(self, mock_config_files):
        """Get writer by exact key (writer_a, writer_b)."""
        writer = get_writer_config("writer_a")
        assert writer.key == "writer_a"
        assert writer.name == "opus"

    def test_get_writer_config_fallback(self, mock_config_files):
        """Unknown key falls back to first writer."""
        writer = get_writer_config("unknown_writer")
        assert writer.key == "writer_a"

    def test_get_judge_config_by_key(self, mock_config_files):
        """Get judge by exact key (judge_1, judge_2)."""
        judge = get_judge_config("judge_1")
        assert judge.key == "judge_1"
        assert judge.model == "opus-4.5"

    def test_get_judge_config_unknown_raises(self, mock_config_files):
        """Unknown judge key raises KeyError."""
        with pytest.raises(KeyError):
            get_judge_config("judge_unknown")

    def test_resolve_writer_alias_by_name(self, mock_config_files):
        """'opus', 'codex' resolve to correct writer."""
        writer = resolve_writer_alias("opus")
        assert writer.key == "writer_a"

        writer = resolve_writer_alias("codex")
        assert writer.key == "writer_b"

    def test_resolve_writer_alias_by_key(self, mock_config_files):
        """'writer_a', 'writer_b' resolve correctly."""
        writer = resolve_writer_alias("writer_a")
        assert writer.key == "writer_a"

    def test_resolve_writer_alias_unknown_raises(self, mock_config_files):
        """Unknown alias raises KeyError."""
        with pytest.raises(KeyError):
            resolve_writer_alias("unknown_alias")

    def test_resolve_judge_alias_hyphenated(self, mock_config_files):
        """'judge-1' resolves to judge_1."""
        judge = resolve_judge_alias("judge-1")
        assert judge.key == "judge_1"

    def test_clear_config_cache_forces_reload(self, mock_config_files, tmp_path):
        """After clear_config_cache(), next load_config() reloads from disk."""
        load_config()

        # Modify config file
        with open(mock_config_files, "a") as f:
            f.write(
                "\nwriters:\n" "  writer_new:\n" "    name: new\n" "    model: m\n" "    label: l\n" "    color: c\n"
            )

        clear_config_cache()
        config = load_config()
        assert "writer_new" in config.writers

    def test_writer_config_session_key(self):
        """WriterConfig.session_key() returns correct format."""
        wc = WriterConfig("k", "n", "m", "l", "c")
        assert wc.session_key("task1") == "K_task1"

    def test_writer_config_worktree_name(self):
        """WriterConfig.worktree_name() returns correct format."""
        wc = WriterConfig("k", "name", "m", "l", "c")
        assert wc.worktree_name("task1") == "writer-name-task1"

    def test_get_default_writer(self, mock_config_files):
        """get_default_writer() returns configured default."""
        from cube.core.user_config import get_default_writer

        assert get_default_writer() == "writer_a"

    def test_is_single_mode_default(self, mock_config_files):
        """is_single_mode_default() returns boolean."""
        from cube.core.user_config import is_single_mode_default

        assert is_single_mode_default() is False

    def test_get_cli_tool_for_model(self, mock_config_files):
        """get_cli_tool_for_model() returns tool name."""
        from cube.core.user_config import get_cli_tool_for_model

        assert get_cli_tool_for_model("any") == "cursor-agent"

    def test_get_prompter_model(self, mock_config_files):
        """get_prompter_model() returns model name."""
        from cube.core.user_config import get_prompter_model

        assert get_prompter_model() == "opus-4.5-thinking"

    def test_get_writer_slugs(self, mock_config_files):
        """get_writer_slugs() returns list of names."""
        from cube.core.user_config import get_writer_slugs

        assert get_writer_slugs() == ["opus", "codex"]

    def test_get_writer_aliases(self, mock_config_files):
        """get_writer_aliases() returns keys and names."""
        from cube.core.user_config import get_writer_aliases

        aliases = get_writer_aliases()
        assert "opus" in aliases
        assert "writer_a" in aliases

    def test_get_writer_by_key(self, mock_config_files):
        """get_writer_by_key() works like resolve_writer_alias."""
        from cube.core.user_config import get_writer_by_key

        assert get_writer_by_key("opus").key == "writer_a"

    def test_get_judge_configs(self, mock_config_files):
        """get_judge_configs() returns list of config objects."""
        from cube.core.user_config import get_judge_configs

        configs = get_judge_configs()
        assert len(configs) == 2
        assert configs[0].key == "judge_1"

    def test_get_judge_numbers(self, mock_config_files):
        """get_judge_numbers() returns keys."""
        from cube.core.user_config import get_judge_numbers

        assert "judge_1" in get_judge_numbers()

    def test_get_judge_aliases(self, mock_config_files):
        """get_judge_aliases() returns keys and hyphenated variants."""
        from cube.core.user_config import get_judge_aliases

        aliases = get_judge_aliases()
        assert "judge_1" in aliases
        assert "judge-1" in aliases
