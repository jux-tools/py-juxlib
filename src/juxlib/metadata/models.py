# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""Environment metadata data models.

This module defines the data structures for representing environment metadata
captured during execution. The metadata includes system information, git
repository state, and CI/CD provider details.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class EnvironmentMetadata:
    """Environment metadata for execution context.

    Captures comprehensive environment information including:
    - System information (hostname, username, platform, Python version)
    - Project information (name, timestamp)
    - Git repository state (commit, branch, status, remote)
    - CI/CD provider details (provider name, build ID, build URL)
    - Tool-specific versions (extensible for pytest, behave, etc.)
    - Custom environment variables

    Attributes:
        hostname: Machine hostname
        username: Current user name
        platform: Platform description (OS, version, architecture)
        python_version: Python interpreter version string
        timestamp: ISO 8601 timestamp in UTC
        project_name: Project name (auto-detected or configured)
        tool_versions: Dict of tool names to version strings
        env: Dict of captured environment variables (optional)
        git_commit: Git commit hash (if in a repository)
        git_branch: Git branch name (if in a repository)
        git_status: "clean" or "dirty" (if in a repository)
        git_remote: Git remote URL (sanitized, if available)
        ci_provider: CI provider name (github, gitlab, jenkins, etc.)
        ci_build_id: CI build identifier
        ci_build_url: URL to the CI build
    """

    hostname: str
    username: str
    platform: str
    python_version: str
    timestamp: str
    project_name: str
    tool_versions: dict[str, str] = field(default_factory=dict)
    env: dict[str, str] | None = None
    git_commit: str | None = None
    git_branch: str | None = None
    git_status: str | None = None
    git_remote: str | None = None
    ci_provider: str | None = None
    ci_build_id: str | None = None
    ci_build_url: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert metadata to dictionary.

        Removes None values and empty tool_versions for cleaner output.

        Returns:
            Dictionary representation of metadata
        """
        data = asdict(self)

        # Remove None values for cleaner output
        keys_to_remove = [k for k, v in data.items() if v is None]
        for key in keys_to_remove:
            del data[key]

        # Remove empty tool_versions
        if not data.get("tool_versions"):
            data.pop("tool_versions", None)

        return data

    def to_json(self, indent: int | None = None) -> str:
        """Convert metadata to JSON string.

        Args:
            indent: JSON indentation level (None for compact)

        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EnvironmentMetadata:
        """Create EnvironmentMetadata from dictionary.

        Args:
            data: Dictionary with metadata fields

        Returns:
            EnvironmentMetadata instance
        """
        # Extract known fields, ignoring unknown ones
        known_fields = {
            "hostname",
            "username",
            "platform",
            "python_version",
            "timestamp",
            "project_name",
            "tool_versions",
            "env",
            "git_commit",
            "git_branch",
            "git_status",
            "git_remote",
            "ci_provider",
            "ci_build_id",
            "ci_build_url",
        }
        filtered = {k: v for k, v in data.items() if k in known_fields}

        # Ensure tool_versions is a dict
        if "tool_versions" not in filtered:
            filtered["tool_versions"] = {}

        return cls(**filtered)

    @classmethod
    def from_json(cls, json_str: str) -> EnvironmentMetadata:
        """Create EnvironmentMetadata from JSON string.

        Args:
            json_str: JSON string with metadata fields

        Returns:
            EnvironmentMetadata instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    def __repr__(self) -> str:
        """Get string representation.

        Returns:
            Concise string representation of metadata
        """
        return (
            f"EnvironmentMetadata("
            f"hostname={self.hostname!r}, "
            f"username={self.username!r}, "
            f"project={self.project_name!r}, "
            f"timestamp={self.timestamp!r})"
        )
