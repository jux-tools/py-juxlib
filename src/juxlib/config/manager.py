# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""Configuration manager with multi-source loading.

This module provides the ConfigurationManager class that handles loading,
validating, and accessing configuration from multiple sources with clear
precedence rules.
"""

from __future__ import annotations

import configparser
import contextlib
import os
import sys
import tomllib
from pathlib import Path
from typing import Any

from .schema import ConfigSchema, StorageMode


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""


def get_xdg_config_home() -> Path:
    """Get XDG config home directory.

    Returns:
        Path to config directory (~/.config on Linux, ~/Library/Application Support on macOS)
    """
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support"
    # Linux/other platforms - type: ignore needed because mypy sees darwin platform
    xdg_config = os.environ.get("XDG_CONFIG_HOME")  # type: ignore[unreachable]
    if xdg_config:
        return Path(xdg_config)
    return Path.home() / ".config"


def get_xdg_data_home() -> Path:
    """Get XDG data home directory.

    Returns:
        Path to data directory (~/.local/share on Linux, ~/Library/Application Support on macOS)
    """
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support"
    # Linux/other platforms - type: ignore needed because mypy sees darwin platform
    xdg_data = os.environ.get("XDG_DATA_HOME")  # type: ignore[unreachable]
    if xdg_data:
        return Path(xdg_data)
    return Path.home() / ".local" / "share"


def get_default_config_path() -> Path:
    """Get default configuration file path.

    Returns:
        Path to default config file (XDG-compliant)
    """
    return get_xdg_config_home() / "jux" / "config.ini"


class ConfigurationManager:
    """Manages configuration from multiple sources.

    Configuration sources are loaded with the following precedence
    (highest to lowest):
    1. Explicit values set via set()
    2. Command-line arguments (if loaded via load_from_dict)
    3. Environment variables (JUX_* prefix)
    4. Configuration files (INI or TOML)
    5. Default values from schema

    Example:
        >>> config = ConfigurationManager()
        >>> config.load_from_env()
        >>> config.load_from_file(Path("~/.config/jux/config.ini"))
        >>>
        >>> api_url = config.get("jux_api_url")
        >>> storage_mode = config.get("jux_storage_mode")
    """

    def __init__(self) -> None:
        """Initialize configuration manager with defaults."""
        self._config: dict[str, Any] = {}
        self._sources: dict[str, str] = {}
        self._load_defaults()

    def _load_defaults(self) -> None:
        """Load default values from schema."""
        schema = ConfigSchema.get_schema()
        for key, field_info in schema.items():
            default = field_info.get("default")
            if default is not None:
                if field_info["type"] == "enum":
                    enum_class = field_info.get("enum_class", StorageMode)
                    default = enum_class(default)
                elif field_info["type"] == "path" and isinstance(default, str):
                    default = Path(default).expanduser()
            self._config[key] = default
            self._sources[key] = "default"

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.

        Args:
            key: Configuration key
            default: Default value if key not set (only used for None values)

        Returns:
            Configuration value

        Raises:
            KeyError: If key doesn't exist in schema
        """
        if key not in ConfigSchema.get_schema():
            raise KeyError(f"Unknown configuration key: {key}")

        value = self._config.get(key)
        if value is None and default is not None:
            return default
        return value

    def set(self, key: str, value: Any, source: str = "explicit") -> None:
        """Set configuration value with validation.

        Args:
            key: Configuration key
            value: Configuration value
            source: Source of the configuration (for debugging)

        Raises:
            KeyError: If key doesn't exist in schema
            ConfigValidationError: If value doesn't match expected type
        """
        schema = ConfigSchema.get_schema()
        if key not in schema:
            raise KeyError(f"Unknown configuration key: {key}")

        field_info = schema[key]
        validated_value = self._validate_value(key, value, field_info)

        self._config[key] = validated_value
        self._sources[key] = source

    def _validate_value(self, key: str, value: Any, field_info: dict[str, Any]) -> Any:
        """Validate and convert configuration value.

        Args:
            key: Configuration key
            value: Value to validate
            field_info: Schema field information

        Returns:
            Validated and converted value

        Raises:
            ConfigValidationError: If validation fails
        """
        field_type = field_info["type"]

        # Handle None values
        if value is None:
            return None

        # Type-specific validation
        if field_type == "bool":
            return self._parse_bool(value)
        elif field_type == "enum":
            return self._parse_enum(key, value, field_info)
        elif field_type == "path":
            return self._parse_path(value)
        elif field_type == "int":
            return self._parse_int(value)
        elif field_type == "str":
            return str(value)
        else:
            return value

    def _parse_int(self, value: Any) -> int:
        """Parse integer value from string or int.

        Args:
            value: Value to parse

        Returns:
            Integer value

        Raises:
            ConfigValidationError: If value can't be parsed
        """
        if isinstance(value, int) and not isinstance(value, bool):
            return value

        if isinstance(value, str):
            try:
                return int(value)
            except ValueError as e:
                raise ConfigValidationError(
                    f"Invalid integer value: {value}. Expected: numeric string or int"
                ) from e

        raise ConfigValidationError(
            f"Invalid integer value type: {type(value).__name__}. Expected: int or str"
        )

    def _parse_bool(self, value: Any) -> bool:
        """Parse boolean value from string or bool.

        Args:
            value: Value to parse

        Returns:
            Boolean value

        Raises:
            ConfigValidationError: If value can't be parsed
        """
        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            lower_value = value.lower()
            if lower_value in ("true", "1", "yes", "on"):
                return True
            elif lower_value in ("false", "0", "no", "off"):
                return False
            else:
                raise ConfigValidationError(
                    f"Invalid boolean value: {value}. "
                    "Expected: true/false, 1/0, yes/no, on/off"
                )

        raise ConfigValidationError(
            f"Invalid boolean value type: {type(value).__name__}. Expected: bool or str"
        )

    def _parse_enum(
        self, key: str, value: Any, field_info: dict[str, Any]
    ) -> StorageMode:
        """Parse enum value from string or enum.

        Args:
            key: Configuration key
            value: Value to parse
            field_info: Schema field information

        Returns:
            Enum value

        Raises:
            ConfigValidationError: If value is invalid
        """
        enum_class = field_info.get("enum_class", StorageMode)

        # Handle string values (case-insensitive)
        if isinstance(value, str):
            try:
                value_lower = value.lower()
                for choice in field_info.get("choices", []):
                    if choice.lower() == value_lower:
                        result = enum_class(choice)
                        # Currently only StorageMode is supported
                        assert isinstance(result, StorageMode)
                        return result
                raise ValueError(f"Invalid choice: {value}")
            except ValueError as e:
                choices = ", ".join(field_info.get("choices", []))
                raise ConfigValidationError(
                    f"Invalid value for {key}: {value}. Valid choices: {choices}"
                ) from e

        # Handle enum instance
        if isinstance(value, StorageMode):
            return value

        raise ConfigValidationError(
            f"Invalid value type for {key}: {type(value).__name__}. "
            f"Expected: str or {enum_class.__name__}"
        )

    def _parse_path(self, value: Any) -> Path:
        """Parse path value with expansion.

        Args:
            value: Value to parse

        Returns:
            Path object with ~ expanded

        Raises:
            ConfigValidationError: If value is invalid
        """
        if isinstance(value, Path):
            return value.expanduser()

        if isinstance(value, str):
            return Path(value).expanduser()

        raise ConfigValidationError(
            f"Invalid path value type: {type(value).__name__}. Expected: str or Path"
        )

    def load_from_dict(self, values: dict[str, Any], source: str = "dict") -> None:
        """Load configuration from dictionary.

        Invalid values are silently skipped during batch loading.

        Args:
            values: Configuration key-value pairs
            source: Source identifier for debugging
        """
        schema = ConfigSchema.get_schema()
        for key, value in values.items():
            if key in schema:
                with contextlib.suppress(ConfigValidationError):
                    self.set(key, value, source)

    def load_from_env(self) -> None:
        """Load configuration from environment variables.

        Environment variables should use the JUX_* prefix with uppercase
        names matching the configuration keys. For example:
        - JUX_ENABLED=true
        - JUX_API_URL=https://api.example.com
        - JUX_STORAGE_MODE=cache
        """
        schema = ConfigSchema.get_schema()
        for key in schema:
            env_var = key.upper()
            if env_var in os.environ:
                with contextlib.suppress(ConfigValidationError):
                    self.set(key, os.environ[env_var], f"env:{env_var}")

    def load_from_file(self, path: Path | str) -> bool:
        """Load configuration from INI file.

        The INI file should have a [jux] section with keys matching
        the configuration schema (without the jux_ prefix).

        Example INI file:
            [jux]
            enabled = true
            api_url = https://api.example.com
            storage_mode = cache

        Args:
            path: Path to configuration file

        Returns:
            True if file was loaded, False if file doesn't exist
        """
        path = Path(path).expanduser()
        if not path.exists():
            return False

        parser = configparser.ConfigParser()
        parser.read(path)

        if "jux" in parser:
            section = parser["jux"]
            for ini_key, value in section.items():
                config_key = f"jux_{ini_key}"
                if config_key in ConfigSchema.get_schema():
                    with contextlib.suppress(ConfigValidationError):
                        self.set(config_key, value, f"file:{path}")

        return True

    def load_from_toml(self, path: Path | str) -> bool:
        """Load configuration from TOML file (pyproject.toml).

        Looks for configuration in the [tool.jux] section.

        Example pyproject.toml:
            [tool.jux]
            enabled = true
            api_url = "https://api.example.com"
            storage_mode = "cache"

        Args:
            path: Path to TOML file (typically pyproject.toml)

        Returns:
            True if file was loaded, False if file doesn't exist or has no [tool.jux]
        """
        path = Path(path).expanduser()
        if not path.exists():
            return False

        try:
            with path.open("rb") as f:
                data = tomllib.load(f)
        except tomllib.TOMLDecodeError:
            return False

        tool_section = data.get("tool", {}).get("jux", {})
        if not tool_section:
            return False

        for toml_key, value in tool_section.items():
            config_key = f"jux_{toml_key}"
            if config_key in ConfigSchema.get_schema():
                with contextlib.suppress(ConfigValidationError):
                    self.set(config_key, value, f"toml:{path}")

        return True

    def validate(self, strict: bool = False) -> list[str]:
        """Validate configuration.

        Checks for dependency violations between settings. For example,
        if jux_sign is enabled, jux_key_path must be set.

        Args:
            strict: If True, return errors for missing dependencies

        Returns:
            List of validation warnings/errors
        """
        errors: list[str] = []
        schema = ConfigSchema.get_schema()

        if strict:
            for key, field_info in schema.items():
                if "requires" in field_info:
                    value = self._config.get(key)
                    if value:  # If this feature is enabled
                        for required_key in field_info["requires"]:
                            required_value = self._config.get(required_key)
                            if not required_value:
                                errors.append(
                                    f"{key} is enabled but {required_key} is not set"
                                )

        return errors

    def get_source(self, key: str) -> str:
        """Get source of configuration value.

        Useful for debugging to understand where a value came from.

        Args:
            key: Configuration key

        Returns:
            Source identifier (e.g., "default", "env:JUX_API_URL", "file:/path")

        Raises:
            KeyError: If key doesn't exist
        """
        if key not in self._sources:
            raise KeyError(f"Configuration key not found: {key}")
        return self._sources[key]

    def dump(self, include_sources: bool = False) -> dict[str, Any]:
        """Dump current configuration.

        Args:
            include_sources: If True, include source information for each value

        Returns:
            Configuration dictionary. If include_sources is True, values are
            dicts with 'value' and 'source' keys.
        """
        if include_sources:
            return {
                key: {"value": value, "source": self._sources[key]}
                for key, value in self._config.items()
            }
        return self._config.copy()

    def reset(self) -> None:
        """Reset configuration to defaults."""
        self._config.clear()
        self._sources.clear()
        self._load_defaults()
