"""Tests for configuration support."""

from pathlib import Path

from sloppy.config import Config, find_config_file, get_default_ignores, load_config


def test_config_defaults():
    """Test that config has sensible defaults."""
    config = Config()
    assert config.ignore == []
    assert config.disable == []
    assert config.severity == "low"
    assert config.max_score is None
    assert config.format == "detailed"
    assert config.ci is False


def test_config_from_dict():
    """Test creating config from a dictionary."""
    data = {
        "ignore": ["tests/*", "docs/*"],
        "disable": ["magic_number", "todo_placeholder"],
        "severity": "medium",
        "max-score": 50,
        "format": "compact",
        "ci": True,
    }
    config = Config.from_dict(data)

    assert config.ignore == ["tests/*", "docs/*"]
    assert config.disable == ["magic_number", "todo_placeholder"]
    assert config.severity == "medium"
    assert config.max_score == 50
    assert config.format == "compact"
    assert config.ci is True


def test_load_config_from_pyproject(tmp_path):
    """Test loading config from pyproject.toml."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """
[tool.sloppy]
ignore = ["venv/*", ".git/*"]
disable = ["debug_print"]
severity = "high"
max-score = 100
"""
    )

    config = load_config(pyproject)

    assert "venv/*" in config.ignore
    assert "debug_print" in config.disable
    assert config.severity == "high"
    assert config.max_score == 100


def test_load_config_missing_section(tmp_path):
    """Test loading config when [tool.sloppy] section is missing."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """
[project]
name = "myproject"
"""
    )

    config = load_config(pyproject)

    # Should return default config
    assert config.ignore == []
    assert config.disable == []


def test_load_config_no_file():
    """Test loading config when file doesn't exist."""
    config = load_config(Path("/nonexistent/pyproject.toml"))

    # Should return default config
    assert config.ignore == []
    assert config.severity == "low"


def test_find_config_file(tmp_path):
    """Test finding pyproject.toml in parent directories."""
    # Create nested directory structure
    subdir = tmp_path / "src" / "mypackage"
    subdir.mkdir(parents=True)

    # Create pyproject.toml in root
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[tool.sloppy]\n")

    # Should find it from subdir
    found = find_config_file(subdir)
    assert found == pyproject


def test_default_ignores():
    """Test that default ignores are reasonable."""
    defaults = get_default_ignores()

    assert "__pycache__" in defaults
    assert ".git" in defaults
    assert ".venv" in defaults
    assert "node_modules" in defaults


def test_merge_cli_args():
    """Test merging CLI arguments into config."""
    config = Config(
        ignore=["config_ignore"],
        disable=["config_disable"],
        severity="low",
    )

    class MockArgs:
        ignore = ["cli_ignore"]
        disable = ["cli_disable"]
        severity = "medium"
        strict = False
        lenient = False
        max_score = 75
        format = "compact"
        ci = True

    config.merge_cli_args(MockArgs())

    # CLI values should be appended/override
    assert "config_ignore" in config.ignore
    assert "cli_ignore" in config.ignore
    assert "config_disable" in config.disable
    assert "cli_disable" in config.disable
    assert config.severity == "medium"
    assert config.max_score == 75
    assert config.format == "compact"
    assert config.ci is True
