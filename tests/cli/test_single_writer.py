"""Tests for single-writer mode CLI options."""

import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, "python")

from cube.cli import app
from cube.core.user_config import (
    resolve_writer_alias, 
    get_default_writer, 
    is_single_mode_default,
    clear_config_cache
)

runner = CliRunner()


class TestWriterAliasResolution:
    """Test writer alias resolution."""
    
    def test_resolve_writer_a_key(self):
        """writer_a key should resolve."""
        clear_config_cache()
        writer = resolve_writer_alias("writer_a")
        assert writer.key == "writer_a"
    
    def test_resolve_writer_b_key(self):
        """writer_b key should resolve."""
        clear_config_cache()
        writer = resolve_writer_alias("writer_b")
        assert writer.key == "writer_b"
    
    def test_resolve_hyphenated_key(self):
        """writer-a should resolve to writer_a."""
        clear_config_cache()
        writer = resolve_writer_alias("writer-a")
        assert writer.key == "writer_a"
    
    def test_resolve_letter_a(self):
        """Letter 'a' should resolve to first writer."""
        clear_config_cache()
        writer = resolve_writer_alias("a")
        assert writer.key == "writer_a"
    
    def test_resolve_letter_b(self):
        """Letter 'b' should resolve to second writer."""
        clear_config_cache()
        writer = resolve_writer_alias("b")
        assert writer.key == "writer_b"
    
    def test_resolve_letter_uppercase(self):
        """Letter 'A' (uppercase) should also resolve."""
        clear_config_cache()
        writer = resolve_writer_alias("A")
        assert writer.key == "writer_a"
    
    def test_resolve_unknown_raises(self):
        """Unknown writer alias should raise KeyError."""
        clear_config_cache()
        with pytest.raises(KeyError, match="Unknown writer"):
            resolve_writer_alias("unknown_writer")


class TestConfigDefaults:
    """Test config default values."""
    
    def test_default_writer(self):
        """get_default_writer should return writer_a by default."""
        clear_config_cache()
        assert get_default_writer() == "writer_a"
    
    def test_single_mode_default_false(self):
        """is_single_mode_default should be False by default."""
        clear_config_cache()
        assert is_single_mode_default() is False


class TestAutoCommandHelp:
    """Test that auto command help shows single-writer options."""
    
    def test_auto_help_shows_single_flag(self):
        """--single flag should appear in auto help."""
        result = runner.invoke(app, ["auto", "--help"])
        assert "--single" in result.output
    
    def test_auto_help_shows_writer_flag(self):
        """--writer flag should appear in auto help."""
        result = runner.invoke(app, ["auto", "--help"])
        assert "--writer" in result.output
        assert "-w" in result.output
    
    def test_auto_help_describes_single_mode(self):
        """Help should describe single-writer workflow."""
        result = runner.invoke(app, ["auto", "--help"])
        assert "single writer" in result.output.lower() or "Single Writer" in result.output


class TestSingleWriterValidation:
    """Test validation of single-writer CLI options."""
    
    def test_writer_flag_invalid_alias(self):
        """Invalid writer alias should produce error."""
        result = runner.invoke(app, ["auto", "fake-task.md", "--writer", "invalid"])
        assert result.exit_code != 0
        assert "Unknown writer" in result.output or "Error" in result.output
