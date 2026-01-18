# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""
Environment metadata detection for test execution context.

This module provides functionality to capture comprehensive metadata about
the test execution environment, including:

- Git repository information (commit, branch, status, remote)
- CI/CD platform detection (GitHub Actions, GitLab CI, Jenkins, etc.)
- Runtime environment (hostname, platform, Python version)
- Project identification (from git, pyproject.toml, or environment)

Example usage:

    >>> from juxlib.metadata import capture_metadata
    >>> metadata = capture_metadata()
    >>> print(f"Git commit: {metadata.git_commit}")
    >>> print(f"CI provider: {metadata.ci_provider}")
    >>> print(f"Project: {metadata.project_name}")
"""

# Public API will be exported here once implemented
# from .models import EnvironmentMetadata
# from .detection import capture_metadata

__all__: list[str] = []
