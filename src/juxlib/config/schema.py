# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""Configuration schema definitions.

This module defines the configuration schema for Jux tools, including
storage modes, field types, defaults, and validation rules.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, ClassVar


class StorageMode(Enum):
    """Storage modes for signed reports.

    Determines how reports are stored and published:
    - LOCAL: Store locally only (no network)
    - API: Publish to API only (no local copy)
    - BOTH: Store locally AND publish to API
    - CACHE: Store locally, publish when available (offline queue)
    """

    LOCAL = "local"
    API = "api"
    BOTH = "both"
    CACHE = "cache"


class ConfigSchema:
    """Configuration schema definition.

    Defines all configuration keys, their types, defaults, and validation rules.
    The schema supports:
    - Type definitions (bool, int, str, path, enum)
    - Default values
    - Required dependencies between settings
    - Descriptions for documentation
    """

    _SCHEMA: ClassVar[dict[str, dict[str, Any]]] = {
        # Core settings
        "jux_enabled": {
            "type": "bool",
            "default": False,
            "description": "Enable Jux plugin functionality",
        },
        "jux_sign": {
            "type": "bool",
            "default": False,
            "description": "Enable report signing",
            "requires": ["jux_key_path"],
        },
        "jux_publish": {
            "type": "bool",
            "default": False,
            "description": "Enable API publishing",
            "requires": ["jux_api_url"],
        },
        # Storage settings
        "jux_storage_mode": {
            "type": "enum",
            "enum_class": StorageMode,
            "default": "local",
            "choices": ["local", "api", "both", "cache"],
            "description": "Storage mode for reports",
        },
        "jux_storage_path": {
            "type": "path",
            "default": None,
            "description": "Custom storage directory path",
        },
        # Signing settings
        "jux_key_path": {
            "type": "path",
            "default": None,
            "description": "Path to signing key (PEM format)",
        },
        "jux_cert_path": {
            "type": "path",
            "default": None,
            "description": "Path to X.509 certificate",
        },
        # API settings
        "jux_api_url": {
            "type": "str",
            "default": None,
            "description": "Jux API base URL (e.g., https://jux.example.com/api/v1)",
        },
        "jux_bearer_token": {
            "type": "str",
            "default": None,
            "description": "Bearer token for remote API authentication",
        },
        "jux_api_timeout": {
            "type": "int",
            "default": 30,
            "description": "API request timeout in seconds",
        },
        "jux_api_max_retries": {
            "type": "int",
            "default": 3,
            "description": "Maximum retry attempts for transient failures",
        },
    }

    @classmethod
    def get_schema(cls) -> dict[str, dict[str, Any]]:
        """Get the configuration schema.

        Returns:
            Copy of the schema dictionary
        """
        return cls._SCHEMA.copy()

    @classmethod
    def get_field(cls, key: str) -> dict[str, Any] | None:
        """Get schema definition for a specific field.

        Args:
            key: Configuration key

        Returns:
            Field schema or None if not found
        """
        return cls._SCHEMA.get(key)

    @classmethod
    def get_default(cls, key: str) -> Any:
        """Get default value for a configuration key.

        Args:
            key: Configuration key

        Returns:
            Default value or None

        Raises:
            KeyError: If key not in schema
        """
        if key not in cls._SCHEMA:
            raise KeyError(f"Unknown configuration key: {key}")
        return cls._SCHEMA[key].get("default")

    @classmethod
    def get_type(cls, key: str) -> str:
        """Get type for a configuration key.

        Args:
            key: Configuration key

        Returns:
            Type string (bool, int, str, path, enum)

        Raises:
            KeyError: If key not in schema
        """
        if key not in cls._SCHEMA:
            raise KeyError(f"Unknown configuration key: {key}")
        field_type: str = cls._SCHEMA[key]["type"]
        return field_type

    @classmethod
    def list_keys(cls) -> list[str]:
        """List all configuration keys.

        Returns:
            List of all configuration key names
        """
        return list(cls._SCHEMA.keys())
