# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""Environment metadata capture.

This module provides the main entry point for capturing comprehensive
environment metadata including system information, git repository state,
and CI/CD provider details.

Example usage:
    from juxlib.metadata import capture_metadata

    # Basic capture
    metadata = capture_metadata()
    print(f"Running on: {metadata.hostname}")

    # With custom environment variables
    metadata = capture_metadata(include_env_vars=["MY_VAR", "ANOTHER_VAR"])

    # With tool versions
    import pytest
    metadata = capture_metadata(tool_versions={"pytest": pytest.__version__})
"""

from __future__ import annotations

import getpass
import os
import platform
import socket
import sys
from datetime import UTC, datetime

from .ci import detect_ci_provider
from .git import capture_git_info
from .models import EnvironmentMetadata
from .project import detect_project_name


def capture_metadata(
    include_env_vars: list[str] | None = None,
    tool_versions: dict[str, str] | None = None,
    project_name: str | None = None,
) -> EnvironmentMetadata:
    """Capture current environment metadata.

    Gathers comprehensive information about the execution environment:
    - System information (hostname, username, platform, Python version)
    - Git repository state (if in a repository)
    - CI/CD provider details (if running in CI)
    - Custom tool versions (pytest, behave, etc.)
    - Specified environment variables

    Args:
        include_env_vars: List of environment variable names to capture.
                         CI-specific variables are captured automatically.
                         If None, only CI variables are captured.
        tool_versions: Dict of tool names to version strings.
                      Example: {"pytest": "8.0.0", "behave": "1.2.6"}
        project_name: Override auto-detected project name.
                     If None, project name is auto-detected.

    Returns:
        EnvironmentMetadata instance with current environment information
    """
    # Capture basic system information
    hostname = socket.gethostname()
    username = getpass.getuser()
    platform_info = platform.platform()
    python_version = sys.version

    # Generate ISO 8601 timestamp in UTC
    timestamp = datetime.now(UTC).isoformat()

    # Auto-detect or use provided project name
    detected_project_name = project_name if project_name else detect_project_name()

    # Auto-detect git metadata
    git_info = capture_git_info()

    # Auto-detect CI provider and metadata
    ci_info = detect_ci_provider()

    # Merge CI env vars with explicitly requested ones
    env_dict: dict[str, str] | None = None
    if ci_info.env_vars or include_env_vars:
        env_dict = ci_info.env_vars.copy() if ci_info.env_vars else {}
        if include_env_vars:
            for var_name in include_env_vars:
                if var_name in os.environ:
                    # User-requested vars take precedence over CI auto-detected
                    env_dict[var_name] = os.environ[var_name]
        # Keep empty dict if user explicitly requested vars (even if none found)
        if not env_dict and not include_env_vars:
            env_dict = None

    return EnvironmentMetadata(
        hostname=hostname,
        username=username,
        platform=platform_info,
        python_version=python_version,
        timestamp=timestamp,
        project_name=detected_project_name,
        tool_versions=tool_versions or {},
        env=env_dict,
        git_commit=git_info.commit,
        git_branch=git_info.branch,
        git_status=git_info.status,
        git_remote=git_info.remote,
        ci_provider=ci_info.provider,
        ci_build_id=ci_info.build_id,
        ci_build_url=ci_info.build_url,
    )
