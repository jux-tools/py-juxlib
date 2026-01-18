# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""
Configuration management with multi-source loading.

This module provides a flexible configuration system that loads settings
from multiple sources with clear precedence rules:

1. Explicit values (highest priority)
2. Command-line arguments
3. Environment variables (JUX_* prefix)
4. Configuration files (jux.ini, pyproject.toml)
5. Default values (lowest priority)

Features:
- Schema-based validation with type coercion
- Source tracking for debugging
- Dependency checking between settings
- XDG-compliant file locations

Example usage:

    >>> from juxlib.config import ConfigurationManager, StorageMode
    >>>
    >>> config = ConfigurationManager()
    >>> config.load_from_env()
    >>> config.load_from_file(Path("~/.config/jux/config.ini"))
    >>>
    >>> api_url = config.get("jux_api_url")
    >>> storage_mode = config.get("jux_storage_mode")  # Returns StorageMode enum
"""

# Public API: ConfigurationManager, ConfigSchema, StorageMode
# (exports added when modules are implemented)

__all__: list[str] = []
