# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""Environment metadata detection module.

This module provides comprehensive environment metadata capture for test
reports and execution tracking. It detects:
- System information (hostname, username, platform, Python version)
- Git repository state (commit, branch, status, remote)
- CI/CD provider details (provider name, build ID, build URL)
- Project name (with multiple fallback strategies)

The metadata is designed to be embedded in JUnit XML reports and signed
with XMLDSig for integrity verification.

Example usage:

    >>> from juxlib.metadata import capture_metadata
    >>>
    >>> # Basic capture
    >>> metadata = capture_metadata()
    >>> print(f"Running on: {metadata.hostname}")
    >>>
    >>> # With tool versions
    >>> import pytest
    >>> metadata = capture_metadata(tool_versions={"pytest": pytest.__version__})
    >>>
    >>> # Convert to dict or JSON
    >>> data = metadata.to_dict()
    >>> json_str = metadata.to_json(indent=2)
"""

from .ci import CIInfo, detect_ci_provider, is_ci_environment
from .detection import capture_metadata
from .git import GitInfo, capture_git_info, is_git_repository
from .models import EnvironmentMetadata
from .project import detect_project_name

__all__ = [  # noqa: RUF022 - intentionally grouped by category
    # Main entry point
    "capture_metadata",
    # Data models
    "EnvironmentMetadata",
    "GitInfo",
    "CIInfo",
    # Detection functions
    "detect_project_name",
    "capture_git_info",
    "is_git_repository",
    "detect_ci_provider",
    "is_ci_environment",
]
