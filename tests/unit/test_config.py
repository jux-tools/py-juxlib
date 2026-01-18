# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""Tests for juxlib.config module."""

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from juxlib.config import (
    ConfigSchema,
    ConfigurationManager,
    ConfigValidationError,
    StorageMode,
    get_default_config_path,
)


class TestStorageMode:
    """Tests for StorageMode enum."""

    def test_storage_mode_values(self) -> None:
        """StorageMode should have expected values."""
        assert StorageMode.LOCAL.value == "local"
        assert StorageMode.API.value == "api"
        assert StorageMode.BOTH.value == "both"
        assert StorageMode.CACHE.value == "cache"

    def test_storage_mode_from_string(self) -> None:
        """StorageMode should be creatable from string."""
        assert StorageMode("local") == StorageMode.LOCAL
        assert StorageMode("api") == StorageMode.API
        assert StorageMode("both") == StorageMode.BOTH
        assert StorageMode("cache") == StorageMode.CACHE


class TestConfigSchema:
    """Tests for ConfigSchema class."""

    def test_get_schema_returns_dict(self) -> None:
        """get_schema should return a dictionary."""
        schema = ConfigSchema.get_schema()

        assert isinstance(schema, dict)
        assert len(schema) > 0

    def test_get_schema_returns_copy(self) -> None:
        """get_schema should return a copy, not the original."""
        schema1 = ConfigSchema.get_schema()
        schema2 = ConfigSchema.get_schema()

        assert schema1 is not schema2

    def test_get_field_returns_field_info(self) -> None:
        """get_field should return field information."""
        field = ConfigSchema.get_field("jux_enabled")

        assert field is not None
        assert field["type"] == "bool"
        assert field["default"] is False

    def test_get_field_returns_none_for_unknown(self) -> None:
        """get_field should return None for unknown keys."""
        assert ConfigSchema.get_field("unknown_key") is None

    def test_get_default_returns_default_value(self) -> None:
        """get_default should return default value."""
        assert ConfigSchema.get_default("jux_enabled") is False
        assert ConfigSchema.get_default("jux_api_timeout") == 30

    def test_get_default_raises_for_unknown(self) -> None:
        """get_default should raise KeyError for unknown keys."""
        with pytest.raises(KeyError):
            ConfigSchema.get_default("unknown_key")

    def test_get_type_returns_type(self) -> None:
        """get_type should return type string."""
        assert ConfigSchema.get_type("jux_enabled") == "bool"
        assert ConfigSchema.get_type("jux_storage_mode") == "enum"
        assert ConfigSchema.get_type("jux_api_url") == "str"
        assert ConfigSchema.get_type("jux_key_path") == "path"
        assert ConfigSchema.get_type("jux_api_timeout") == "int"

    def test_get_type_raises_for_unknown(self) -> None:
        """get_type should raise KeyError for unknown keys."""
        with pytest.raises(KeyError):
            ConfigSchema.get_type("unknown_key")

    def test_list_keys_returns_all_keys(self) -> None:
        """list_keys should return all configuration keys."""
        keys = ConfigSchema.list_keys()

        assert isinstance(keys, list)
        assert "jux_enabled" in keys
        assert "jux_storage_mode" in keys
        assert "jux_api_url" in keys


class TestXDGFunctions:
    """Tests for XDG utility functions."""

    def test_get_xdg_config_home_on_macos(self) -> None:
        """get_xdg_config_home should return Library path on macOS."""
        with patch.object(sys, "platform", "darwin"):
            # Need to reimport to get fresh function with patched platform
            from juxlib.config.manager import get_xdg_config_home as fresh_func

            result = fresh_func()
            assert "Library" in str(result) or ".config" in str(result)

    def test_get_xdg_data_home_on_macos(self) -> None:
        """get_xdg_data_home should return Library path on macOS."""
        with patch.object(sys, "platform", "darwin"):
            from juxlib.config.manager import get_xdg_data_home as fresh_func

            result = fresh_func()
            assert "Library" in str(result) or ".local" in str(result)

    def test_get_default_config_path(self) -> None:
        """get_default_config_path should return jux config path."""
        path = get_default_config_path()

        assert isinstance(path, Path)
        assert "jux" in str(path)
        assert path.name == "config.ini"


class TestConfigurationManager:
    """Tests for ConfigurationManager class."""

    def test_init_loads_defaults(self) -> None:
        """ConfigurationManager should load defaults on init."""
        config = ConfigurationManager()

        assert config.get("jux_enabled") is False
        assert config.get("jux_api_timeout") == 30
        assert config.get("jux_storage_mode") == StorageMode.LOCAL

    def test_get_returns_value(self) -> None:
        """get should return configuration value."""
        config = ConfigurationManager()

        assert config.get("jux_enabled") is False

    def test_get_with_default_for_none(self) -> None:
        """get should return default for None values."""
        config = ConfigurationManager()

        assert config.get("jux_api_url") is None
        assert config.get("jux_api_url", "https://default.com") == "https://default.com"

    def test_get_raises_for_unknown_key(self) -> None:
        """get should raise KeyError for unknown keys."""
        config = ConfigurationManager()

        with pytest.raises(KeyError):
            config.get("unknown_key")

    def test_set_updates_value(self) -> None:
        """set should update configuration value."""
        config = ConfigurationManager()

        config.set("jux_enabled", True)

        assert config.get("jux_enabled") is True

    def test_set_validates_bool(self) -> None:
        """set should validate boolean values."""
        config = ConfigurationManager()

        config.set("jux_enabled", "true")
        assert config.get("jux_enabled") is True

        config.set("jux_enabled", "false")
        assert config.get("jux_enabled") is False

        config.set("jux_enabled", "1")
        assert config.get("jux_enabled") is True

        config.set("jux_enabled", "0")
        assert config.get("jux_enabled") is False

    def test_set_validates_bool_invalid(self) -> None:
        """set should raise for invalid boolean values."""
        config = ConfigurationManager()

        with pytest.raises(ConfigValidationError, match="Invalid boolean"):
            config.set("jux_enabled", "invalid")

    def test_set_validates_int(self) -> None:
        """set should validate integer values."""
        config = ConfigurationManager()

        config.set("jux_api_timeout", 60)
        assert config.get("jux_api_timeout") == 60

        config.set("jux_api_timeout", "45")
        assert config.get("jux_api_timeout") == 45

    def test_set_validates_int_invalid(self) -> None:
        """set should raise for invalid integer values."""
        config = ConfigurationManager()

        with pytest.raises(ConfigValidationError, match="Invalid integer"):
            config.set("jux_api_timeout", "not_a_number")

    def test_set_validates_enum(self) -> None:
        """set should validate enum values."""
        config = ConfigurationManager()

        config.set("jux_storage_mode", "api")
        assert config.get("jux_storage_mode") == StorageMode.API

        config.set("jux_storage_mode", "CACHE")
        assert config.get("jux_storage_mode") == StorageMode.CACHE

        config.set("jux_storage_mode", StorageMode.BOTH)
        assert config.get("jux_storage_mode") == StorageMode.BOTH

    def test_set_validates_enum_invalid(self) -> None:
        """set should raise for invalid enum values."""
        config = ConfigurationManager()

        with pytest.raises(ConfigValidationError, match="Invalid value"):
            config.set("jux_storage_mode", "invalid_mode")

    def test_set_validates_path(self) -> None:
        """set should validate and expand path values."""
        config = ConfigurationManager()

        config.set("jux_key_path", "/tmp/key.pem")
        assert config.get("jux_key_path") == Path("/tmp/key.pem")

        config.set("jux_key_path", Path("/tmp/other.pem"))
        assert config.get("jux_key_path") == Path("/tmp/other.pem")

    def test_set_expands_home_in_path(self) -> None:
        """set should expand ~ in path values."""
        config = ConfigurationManager()

        config.set("jux_key_path", "~/keys/key.pem")
        result = config.get("jux_key_path")

        assert isinstance(result, Path)
        assert "~" not in str(result)

    def test_set_validates_str(self) -> None:
        """set should accept string values."""
        config = ConfigurationManager()

        config.set("jux_api_url", "https://api.example.com")

        assert config.get("jux_api_url") == "https://api.example.com"

    def test_set_tracks_source(self) -> None:
        """set should track the source of values."""
        config = ConfigurationManager()

        config.set("jux_enabled", True, source="test")

        assert config.get_source("jux_enabled") == "test"

    def test_set_raises_for_unknown_key(self) -> None:
        """set should raise KeyError for unknown keys."""
        config = ConfigurationManager()

        with pytest.raises(KeyError):
            config.set("unknown_key", "value")

    def test_set_allows_none(self) -> None:
        """set should allow None values."""
        config = ConfigurationManager()

        config.set("jux_api_url", None)

        assert config.get("jux_api_url") is None

    def test_load_from_dict(self) -> None:
        """load_from_dict should load values from dictionary."""
        config = ConfigurationManager()

        config.load_from_dict(
            {
                "jux_enabled": True,
                "jux_api_url": "https://api.example.com",
            }
        )

        assert config.get("jux_enabled") is True
        assert config.get("jux_api_url") == "https://api.example.com"

    def test_load_from_dict_skips_invalid(self) -> None:
        """load_from_dict should skip invalid values."""
        config = ConfigurationManager()

        config.load_from_dict(
            {
                "jux_enabled": "invalid",
                "jux_api_url": "https://api.example.com",
            }
        )

        # Invalid value should be skipped
        assert config.get("jux_enabled") is False  # Default
        # Valid value should be set
        assert config.get("jux_api_url") == "https://api.example.com"

    def test_load_from_dict_skips_unknown_keys(self) -> None:
        """load_from_dict should skip unknown keys."""
        config = ConfigurationManager()

        # Should not raise
        config.load_from_dict(
            {
                "unknown_key": "value",
                "jux_enabled": True,
            }
        )

        assert config.get("jux_enabled") is True

    def test_load_from_env(self) -> None:
        """load_from_env should load from environment variables."""
        config = ConfigurationManager()

        with patch.dict(os.environ, {"JUX_ENABLED": "true", "JUX_API_TIMEOUT": "60"}):
            config.load_from_env()

        assert config.get("jux_enabled") is True
        assert config.get("jux_api_timeout") == 60
        assert "env:JUX_ENABLED" in config.get_source("jux_enabled")

    def test_load_from_env_skips_invalid(self) -> None:
        """load_from_env should skip invalid env values."""
        config = ConfigurationManager()

        with patch.dict(os.environ, {"JUX_ENABLED": "invalid"}):
            config.load_from_env()

        # Invalid value should be skipped
        assert config.get("jux_enabled") is False

    def test_load_from_file(self, tmp_path: Path) -> None:
        """load_from_file should load from INI file."""
        config_file = tmp_path / "config.ini"
        config_file.write_text("""
[jux]
enabled = true
api_url = https://api.example.com
storage_mode = cache
""")

        config = ConfigurationManager()
        result = config.load_from_file(config_file)

        assert result is True
        assert config.get("jux_enabled") is True
        assert config.get("jux_api_url") == "https://api.example.com"
        assert config.get("jux_storage_mode") == StorageMode.CACHE

    def test_load_from_file_returns_false_for_missing(self) -> None:
        """load_from_file should return False for missing file."""
        config = ConfigurationManager()

        result = config.load_from_file(Path("/nonexistent/config.ini"))

        assert result is False

    def test_load_from_file_skips_invalid(self, tmp_path: Path) -> None:
        """load_from_file should skip invalid values."""
        config_file = tmp_path / "config.ini"
        config_file.write_text("""
[jux]
enabled = invalid
api_url = https://api.example.com
""")

        config = ConfigurationManager()
        config.load_from_file(config_file)

        assert config.get("jux_enabled") is False  # Default
        assert config.get("jux_api_url") == "https://api.example.com"

    def test_load_from_toml(self, tmp_path: Path) -> None:
        """load_from_toml should load from TOML file."""
        toml_file = tmp_path / "pyproject.toml"
        toml_file.write_text("""
[tool.jux]
enabled = true
api_url = "https://api.example.com"
api_timeout = 60
""")

        config = ConfigurationManager()
        result = config.load_from_toml(toml_file)

        assert result is True
        assert config.get("jux_enabled") is True
        assert config.get("jux_api_url") == "https://api.example.com"
        assert config.get("jux_api_timeout") == 60

    def test_load_from_toml_returns_false_for_missing(self) -> None:
        """load_from_toml should return False for missing file."""
        config = ConfigurationManager()

        result = config.load_from_toml(Path("/nonexistent/pyproject.toml"))

        assert result is False

    def test_load_from_toml_returns_false_for_no_section(self, tmp_path: Path) -> None:
        """load_from_toml should return False if no [tool.jux] section."""
        toml_file = tmp_path / "pyproject.toml"
        toml_file.write_text("""
[project]
name = "my-project"
""")

        config = ConfigurationManager()
        result = config.load_from_toml(toml_file)

        assert result is False

    def test_validate_returns_empty_by_default(self) -> None:
        """validate should return empty list by default."""
        config = ConfigurationManager()

        errors = config.validate()

        assert errors == []

    def test_validate_strict_checks_dependencies(self) -> None:
        """validate with strict=True should check dependencies."""
        config = ConfigurationManager()
        config.set("jux_sign", True)  # Requires jux_key_path

        errors = config.validate(strict=True)

        assert len(errors) > 0
        assert any("jux_key_path" in err for err in errors)

    def test_validate_strict_no_errors_when_satisfied(self) -> None:
        """validate with strict=True should pass when dependencies satisfied."""
        config = ConfigurationManager()
        config.set("jux_sign", True)
        config.set("jux_key_path", "/path/to/key.pem")

        errors = config.validate(strict=True)

        assert not any("jux_key_path" in err for err in errors)

    def test_get_source_returns_source(self) -> None:
        """get_source should return source identifier."""
        config = ConfigurationManager()

        assert config.get_source("jux_enabled") == "default"

    def test_get_source_raises_for_unknown(self) -> None:
        """get_source should raise KeyError for unknown keys."""
        config = ConfigurationManager()

        with pytest.raises(KeyError):
            config.get_source("unknown_key")

    def test_dump_returns_config(self) -> None:
        """dump should return configuration dictionary."""
        config = ConfigurationManager()
        config.set("jux_enabled", True)

        result = config.dump()

        assert isinstance(result, dict)
        assert result["jux_enabled"] is True

    def test_dump_with_sources(self) -> None:
        """dump with include_sources should include source info."""
        config = ConfigurationManager()
        config.set("jux_enabled", True, source="test")

        result = config.dump(include_sources=True)

        assert result["jux_enabled"]["value"] is True
        assert result["jux_enabled"]["source"] == "test"

    def test_reset_restores_defaults(self) -> None:
        """reset should restore default values."""
        config = ConfigurationManager()
        config.set("jux_enabled", True)
        config.set("jux_api_url", "https://api.example.com")

        config.reset()

        assert config.get("jux_enabled") is False
        assert config.get("jux_api_url") is None


class TestModuleExports:
    """Tests for module exports."""

    def test_all_exports_accessible(self) -> None:
        """All __all__ exports should be accessible."""
        from juxlib import config

        expected = [
            "ConfigurationManager",
            "ConfigSchema",
            "StorageMode",
            "ConfigValidationError",
            "get_default_config_path",
            "get_xdg_config_home",
            "get_xdg_data_home",
        ]

        for name in expected:
            assert hasattr(config, name), f"{name} not accessible"
