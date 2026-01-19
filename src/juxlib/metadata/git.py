# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""Git repository information detection.

This module provides functions for detecting git repository state including
commit hash, branch name, working tree status, and remote URL.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass


@dataclass
class GitInfo:
    """Git repository information.

    Attributes:
        commit: Full commit hash (40 characters)
        branch: Current branch name
        author: Commit author in "Name <email>" format
        status: "clean" or "dirty" indicating working tree state
        remote: Remote URL (sanitized to remove credentials)
    """

    commit: str | None = None
    branch: str | None = None
    author: str | None = None
    status: str | None = None
    remote: str | None = None


def run_git_command(args: list[str], timeout: float = 2.0) -> str | None:
    """Run a git command and return output.

    Args:
        args: Git command arguments (e.g., ["rev-parse", "HEAD"])
        timeout: Command timeout in seconds

    Returns:
        Command output stripped of whitespace, or None on failure
    """
    try:
        result = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None


def is_git_repository() -> bool:
    """Check if current directory is inside a git repository.

    Returns:
        True if in a git repository, False otherwise
    """
    return run_git_command(["rev-parse", "--git-dir"]) is not None


def get_commit_hash() -> str | None:
    """Get the current commit hash.

    Returns:
        Full commit hash (40 characters) or None if not in a repository
    """
    return run_git_command(["rev-parse", "HEAD"])


def get_branch_name() -> str | None:
    """Get the current branch name.

    Returns:
        Branch name or None if not in a repository or detached HEAD
    """
    return run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])


def get_commit_author() -> str | None:
    """Get the author of the HEAD commit.

    Returns:
        Author in "Name <email>" format, or None if not in a repository
    """
    return run_git_command(["log", "-1", "--format=%an <%ae>"])


def get_working_tree_status() -> str | None:
    """Get the working tree status (clean/dirty).

    Returns:
        "clean" if no uncommitted changes, "dirty" if changes exist,
        None if not in a repository
    """
    if not is_git_repository():
        return None

    status_output = run_git_command(["status", "--porcelain"])

    if status_output is None:
        return None
    elif status_output == "":
        return "clean"
    else:
        return "dirty"


def get_remote_url(remote_names: list[str] | None = None) -> str | None:
    """Get the remote URL, sanitized to remove credentials.

    Tries multiple remote names in order until one is found.

    Args:
        remote_names: List of remote names to try (default: origin, upstream, etc.)

    Returns:
        Sanitized remote URL or None if no remote found
    """
    if remote_names is None:
        remote_names = ["origin", "home", "upstream", "github", "gitlab"]

    remote_url = None
    for remote_name in remote_names:
        remote_url = run_git_command(["config", "--get", f"remote.{remote_name}.url"])
        if remote_url:
            break

    if remote_url:
        # Sanitize URL to remove credentials
        # Convert https://user:pass@host/repo to https://host/repo
        remote_url = re.sub(r"https://[^@]+@", "https://", remote_url)

    return remote_url


def capture_git_info(remote_names: list[str] | None = None) -> GitInfo:
    """Capture all git repository information.

    Args:
        remote_names: List of remote names to try for URL detection

    Returns:
        GitInfo instance with all available repository information
    """
    if not is_git_repository():
        return GitInfo()

    return GitInfo(
        commit=get_commit_hash(),
        branch=get_branch_name(),
        author=get_commit_author(),
        status=get_working_tree_status(),
        remote=get_remote_url(remote_names),
    )
