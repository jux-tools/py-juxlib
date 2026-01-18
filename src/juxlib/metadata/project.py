# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""Project name detection.

This module provides functions for detecting the project name using
multiple fallback strategies:
1. Git remote URL - Extract repository name
2. pyproject.toml - Read project name from Python metadata
3. Environment variable - Check JUX_PROJECT_NAME
4. Directory basename - Fall back to current directory name
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from .git import get_remote_url


def _extract_name_from_git_remote() -> str | None:
    """Extract project name from git remote URL.

    Handles various URL formats:
    - https://github.com/owner/repo.git -> repo
    - git@github.com:owner/repo.git -> repo
    - ssh://user@host:port/path/repo.git -> repo

    Returns:
        Repository name or None if not available
    """
    remote_url = get_remote_url()
    if not remote_url:
        return None

    # Extract repo name from URL (handles .git suffix)
    match = re.search(r"/([^/]+?)(\.git)?$", remote_url)
    if match:
        return match.group(1)

    # Handle git@host:owner/repo format
    match = re.search(r":([^/]+/)?([^/]+?)(\.git)?$", remote_url)
    if match:
        return match.group(2)

    return None


def _read_pyproject_name() -> str | None:
    """Read project name from pyproject.toml.

    Checks both PEP 621 [project] section and [tool.poetry] section.

    Returns:
        Project name or None if not found
    """
    pyproject_path = Path.cwd() / "pyproject.toml"
    if not pyproject_path.exists():
        return None

    try:
        import tomllib

        with pyproject_path.open("rb") as f:
            data = tomllib.load(f)

        # Try [project] section first (PEP 621)
        if "project" in data and "name" in data["project"]:
            return str(data["project"]["name"])

        # Fall back to [tool.poetry] section
        if (
            "tool" in data
            and "poetry" in data["tool"]
            and "name" in data["tool"]["poetry"]
        ):
            return str(data["tool"]["poetry"]["name"])

    except Exception:
        pass

    return None


def _get_env_project_name() -> str | None:
    """Get project name from environment variable.

    Returns:
        Value of JUX_PROJECT_NAME environment variable or None
    """
    return os.getenv("JUX_PROJECT_NAME")


def _get_directory_name() -> str:
    """Get current directory name as fallback project name.

    Returns:
        Current directory basename (always returns a string)
    """
    return Path.cwd().name


def detect_project_name() -> str:
    """Detect project name using multiple strategies.

    Tries strategies in order:
    1. Git remote URL - Extract repository name
    2. pyproject.toml - Read project name from Python metadata
    3. Environment variable - Check JUX_PROJECT_NAME
    4. Directory basename - Fall back to current directory name

    Returns:
        Project name (never None, always returns a string)
    """
    # Strategy 1: Git remote URL
    name = _extract_name_from_git_remote()
    if name:
        return name

    # Strategy 2: pyproject.toml
    name = _read_pyproject_name()
    if name:
        return name

    # Strategy 3: Environment variable
    name = _get_env_project_name()
    if name:
        return name

    # Strategy 4: Directory basename (always works)
    return _get_directory_name()
