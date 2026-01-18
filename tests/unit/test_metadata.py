# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""Tests for juxlib.metadata module."""

import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

from juxlib.metadata import (
    CIInfo,
    EnvironmentMetadata,
    GitInfo,
    capture_git_info,
    capture_metadata,
    detect_ci_provider,
    detect_project_name,
    is_ci_environment,
    is_git_repository,
)


class TestEnvironmentMetadata:
    """Tests for EnvironmentMetadata dataclass."""

    def test_minimal_metadata(self) -> None:
        """EnvironmentMetadata should initialize with required fields."""
        metadata = EnvironmentMetadata(
            hostname="testhost",
            username="testuser",
            platform="Linux-5.15.0",
            python_version="3.12.0",
            timestamp="2026-01-18T10:00:00+00:00",
            project_name="test-project",
        )

        assert metadata.hostname == "testhost"
        assert metadata.username == "testuser"
        assert metadata.platform == "Linux-5.15.0"
        assert metadata.python_version == "3.12.0"
        assert metadata.timestamp == "2026-01-18T10:00:00+00:00"
        assert metadata.project_name == "test-project"
        assert metadata.tool_versions == {}
        assert metadata.env is None
        assert metadata.git_commit is None

    def test_full_metadata(self) -> None:
        """EnvironmentMetadata should handle all optional fields."""
        metadata = EnvironmentMetadata(
            hostname="testhost",
            username="testuser",
            platform="Linux-5.15.0",
            python_version="3.12.0",
            timestamp="2026-01-18T10:00:00+00:00",
            project_name="test-project",
            tool_versions={"pytest": "8.0.0"},
            env={"CI": "true"},
            git_commit="abc123",
            git_branch="main",
            git_status="clean",
            git_remote="https://github.com/owner/repo",
            ci_provider="github",
            ci_build_id="12345",
            ci_build_url="https://github.com/owner/repo/actions/runs/12345",
        )

        assert metadata.tool_versions == {"pytest": "8.0.0"}
        assert metadata.env == {"CI": "true"}
        assert metadata.git_commit == "abc123"
        assert metadata.ci_provider == "github"

    def test_to_dict_removes_none_values(self) -> None:
        """to_dict should remove None values."""
        metadata = EnvironmentMetadata(
            hostname="testhost",
            username="testuser",
            platform="Linux-5.15.0",
            python_version="3.12.0",
            timestamp="2026-01-18T10:00:00+00:00",
            project_name="test-project",
        )

        data = metadata.to_dict()

        assert "hostname" in data
        assert "git_commit" not in data
        assert "ci_provider" not in data
        assert "tool_versions" not in data  # Empty dict removed

    def test_to_dict_keeps_populated_values(self) -> None:
        """to_dict should keep populated optional values."""
        metadata = EnvironmentMetadata(
            hostname="testhost",
            username="testuser",
            platform="Linux-5.15.0",
            python_version="3.12.0",
            timestamp="2026-01-18T10:00:00+00:00",
            project_name="test-project",
            git_commit="abc123",
            tool_versions={"pytest": "8.0.0"},
        )

        data = metadata.to_dict()

        assert data["git_commit"] == "abc123"
        assert data["tool_versions"] == {"pytest": "8.0.0"}

    def test_to_json(self) -> None:
        """to_json should produce valid JSON."""
        metadata = EnvironmentMetadata(
            hostname="testhost",
            username="testuser",
            platform="Linux-5.15.0",
            python_version="3.12.0",
            timestamp="2026-01-18T10:00:00+00:00",
            project_name="test-project",
        )

        json_str = metadata.to_json()

        parsed = json.loads(json_str)
        assert parsed["hostname"] == "testhost"

    def test_to_json_with_indent(self) -> None:
        """to_json should support indentation."""
        metadata = EnvironmentMetadata(
            hostname="testhost",
            username="testuser",
            platform="Linux-5.15.0",
            python_version="3.12.0",
            timestamp="2026-01-18T10:00:00+00:00",
            project_name="test-project",
        )

        json_str = metadata.to_json(indent=2)

        assert "\n" in json_str
        assert "  " in json_str

    def test_from_dict(self) -> None:
        """from_dict should create instance from dictionary."""
        data = {
            "hostname": "testhost",
            "username": "testuser",
            "platform": "Linux-5.15.0",
            "python_version": "3.12.0",
            "timestamp": "2026-01-18T10:00:00+00:00",
            "project_name": "test-project",
            "git_commit": "abc123",
        }

        metadata = EnvironmentMetadata.from_dict(data)

        assert metadata.hostname == "testhost"
        assert metadata.git_commit == "abc123"

    def test_from_dict_ignores_unknown_fields(self) -> None:
        """from_dict should ignore unknown fields."""
        data = {
            "hostname": "testhost",
            "username": "testuser",
            "platform": "Linux-5.15.0",
            "python_version": "3.12.0",
            "timestamp": "2026-01-18T10:00:00+00:00",
            "project_name": "test-project",
            "unknown_field": "ignored",
        }

        metadata = EnvironmentMetadata.from_dict(data)

        assert metadata.hostname == "testhost"
        assert not hasattr(metadata, "unknown_field")

    def test_from_json(self) -> None:
        """from_json should create instance from JSON string."""
        json_str = json.dumps(
            {
                "hostname": "testhost",
                "username": "testuser",
                "platform": "Linux-5.15.0",
                "python_version": "3.12.0",
                "timestamp": "2026-01-18T10:00:00+00:00",
                "project_name": "test-project",
            }
        )

        metadata = EnvironmentMetadata.from_json(json_str)

        assert metadata.hostname == "testhost"

    def test_repr(self) -> None:
        """__repr__ should provide concise representation."""
        metadata = EnvironmentMetadata(
            hostname="testhost",
            username="testuser",
            platform="Linux-5.15.0",
            python_version="3.12.0",
            timestamp="2026-01-18T10:00:00+00:00",
            project_name="test-project",
        )

        repr_str = repr(metadata)

        assert "testhost" in repr_str
        assert "testuser" in repr_str
        assert "test-project" in repr_str


class TestGitInfo:
    """Tests for GitInfo dataclass."""

    def test_empty_git_info(self) -> None:
        """GitInfo should have sensible defaults."""
        info = GitInfo()

        assert info.commit is None
        assert info.branch is None
        assert info.status is None
        assert info.remote is None

    def test_populated_git_info(self) -> None:
        """GitInfo should store all values."""
        info = GitInfo(
            commit="abc123def456",
            branch="feature/test",
            status="dirty",
            remote="https://github.com/owner/repo",
        )

        assert info.commit == "abc123def456"
        assert info.branch == "feature/test"
        assert info.status == "dirty"
        assert info.remote == "https://github.com/owner/repo"


class TestCIInfo:
    """Tests for CIInfo dataclass."""

    def test_empty_ci_info(self) -> None:
        """CIInfo should have sensible defaults."""
        info = CIInfo()

        assert info.provider is None
        assert info.build_id is None
        assert info.build_url is None
        assert info.env_vars == {}

    def test_populated_ci_info(self) -> None:
        """CIInfo should store all values."""
        info = CIInfo(
            provider="github",
            build_id="12345",
            build_url="https://github.com/owner/repo/actions/runs/12345",
            env_vars={"GITHUB_SHA": "abc123"},
        )

        assert info.provider == "github"
        assert info.build_id == "12345"
        assert info.env_vars["GITHUB_SHA"] == "abc123"


class TestGitDetection:
    """Tests for git detection functions."""

    def test_is_git_repository_true(self) -> None:
        """is_git_repository should return True in git repo."""
        # The test is run from within a git repository
        assert is_git_repository() is True

    def test_capture_git_info_in_repo(self) -> None:
        """capture_git_info should return info in git repo."""
        info = capture_git_info()

        # We're in a git repo, so should have some info
        assert info.commit is not None or info.branch is not None

    @patch("juxlib.metadata.git.run_git_command")
    def test_capture_git_info_not_in_repo(self, mock_run: MagicMock) -> None:
        """capture_git_info should return empty GitInfo when not in repo."""
        mock_run.return_value = None

        info = capture_git_info()

        assert info.commit is None
        assert info.branch is None

    @patch("juxlib.metadata.git.run_git_command")
    def test_capture_git_info_clean_status(self, mock_run: MagicMock) -> None:
        """capture_git_info should detect clean status."""

        def mock_command(args: list[str], _timeout: float = 2.0) -> str | None:
            if args == ["rev-parse", "--git-dir"]:
                return ".git"
            elif args == ["rev-parse", "HEAD"]:
                return "abc123"
            elif args == ["rev-parse", "--abbrev-ref", "HEAD"]:
                return "main"
            elif args == ["status", "--porcelain"]:
                return ""  # Empty = clean
            elif args[0] == "config":
                return "https://github.com/owner/repo"
            return None

        mock_run.side_effect = mock_command

        info = capture_git_info()

        assert info.status == "clean"

    @patch("juxlib.metadata.git.run_git_command")
    def test_capture_git_info_dirty_status(self, mock_run: MagicMock) -> None:
        """capture_git_info should detect dirty status."""

        def mock_command(args: list[str], _timeout: float = 2.0) -> str | None:
            if args == ["rev-parse", "--git-dir"]:
                return ".git"
            elif args == ["status", "--porcelain"]:
                return "M file.txt"  # Modified file
            return None

        mock_run.side_effect = mock_command

        info = capture_git_info()

        assert info.status == "dirty"


class TestCIDetection:
    """Tests for CI detection functions."""

    def test_detect_ci_provider_not_in_ci(self) -> None:
        """detect_ci_provider should return empty CIInfo when not in CI."""
        # Clear any CI env vars that might be set
        with patch.dict(os.environ, {}, clear=True):
            info = detect_ci_provider()

        assert info.provider is None

    def test_is_ci_environment_false(self) -> None:
        """is_ci_environment should return False when not in CI."""
        with patch.dict(os.environ, {}, clear=True):
            assert is_ci_environment() is False

    def test_detect_github_actions(self) -> None:
        """detect_ci_provider should detect GitHub Actions."""
        env = {
            "GITHUB_ACTIONS": "true",
            "GITHUB_RUN_ID": "12345",
            "GITHUB_REPOSITORY": "owner/repo",
            "GITHUB_SERVER_URL": "https://github.com",
            "GITHUB_SHA": "abc123",
        }

        with patch.dict(os.environ, env, clear=True):
            info = detect_ci_provider()

        assert info.provider == "github"
        assert info.build_id == "12345"
        assert "github.com" in info.build_url
        assert info.env_vars["GITHUB_SHA"] == "abc123"

    def test_detect_gitlab_ci(self) -> None:
        """detect_ci_provider should detect GitLab CI."""
        env = {
            "GITLAB_CI": "true",
            "CI_PIPELINE_ID": "12345",
            "CI_PIPELINE_URL": "https://gitlab.com/owner/repo/-/pipelines/12345",
            "CI_COMMIT_SHA": "abc123",
        }

        with patch.dict(os.environ, env, clear=True):
            info = detect_ci_provider()

        assert info.provider == "gitlab"
        assert info.build_id == "12345"
        assert info.env_vars["CI_COMMIT_SHA"] == "abc123"

    def test_detect_jenkins(self) -> None:
        """detect_ci_provider should detect Jenkins."""
        env = {
            "JENKINS_URL": "https://jenkins.example.com",
            "BUILD_ID": "42",
            "BUILD_URL": "https://jenkins.example.com/job/test/42",
            "GIT_COMMIT": "abc123",
        }

        with patch.dict(os.environ, env, clear=True):
            info = detect_ci_provider()

        assert info.provider == "jenkins"
        assert info.build_id == "42"

    def test_detect_travis_ci(self) -> None:
        """detect_ci_provider should detect Travis CI."""
        env = {
            "TRAVIS": "true",
            "TRAVIS_BUILD_ID": "12345",
            "TRAVIS_BUILD_WEB_URL": "https://travis-ci.com/owner/repo/builds/12345",
        }

        with patch.dict(os.environ, env, clear=True):
            info = detect_ci_provider()

        assert info.provider == "travis"
        assert info.build_id == "12345"

    def test_detect_circleci(self) -> None:
        """detect_ci_provider should detect CircleCI."""
        env = {
            "CIRCLECI": "true",
            "CIRCLE_BUILD_NUM": "42",
            "CIRCLE_BUILD_URL": "https://circleci.com/gh/owner/repo/42",
        }

        with patch.dict(os.environ, env, clear=True):
            info = detect_ci_provider()

        assert info.provider == "circleci"
        assert info.build_id == "42"

    def test_detect_azure_pipelines(self) -> None:
        """detect_ci_provider should detect Azure Pipelines."""
        env = {
            "TF_BUILD": "True",
            "BUILD_BUILDID": "12345",
            "SYSTEM_COLLECTIONURI": "https://dev.azure.com/org/",
            "SYSTEM_TEAMPROJECT": "project",
        }

        with patch.dict(os.environ, env, clear=True):
            info = detect_ci_provider()

        assert info.provider == "azure"
        assert info.build_id == "12345"


class TestProjectNameDetection:
    """Tests for project name detection."""

    def test_detect_project_name_from_env(self) -> None:
        """detect_project_name should use JUX_PROJECT_NAME env var."""
        with (
            patch.dict(os.environ, {"JUX_PROJECT_NAME": "my-project"}),
            patch("juxlib.metadata.project.get_remote_url", return_value=None),
            patch("juxlib.metadata.project._read_pyproject_name", return_value=None),
        ):
            name = detect_project_name()

        assert name == "my-project"

    def test_detect_project_name_fallback_to_directory(self) -> None:
        """detect_project_name should fall back to directory name."""
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("juxlib.metadata.project.get_remote_url", return_value=None),
            patch("juxlib.metadata.project._read_pyproject_name", return_value=None),
        ):
            name = detect_project_name()

        # Should return current directory name
        assert name == Path.cwd().name

    @patch("juxlib.metadata.project.get_remote_url")
    def test_detect_project_name_from_git_https(self, mock_remote: MagicMock) -> None:
        """detect_project_name should extract from HTTPS git URL."""
        mock_remote.return_value = "https://github.com/owner/my-repo.git"

        name = detect_project_name()

        assert name == "my-repo"

    @patch("juxlib.metadata.project.get_remote_url")
    def test_detect_project_name_from_git_ssh(self, mock_remote: MagicMock) -> None:
        """detect_project_name should extract from SSH git URL."""
        mock_remote.return_value = "git@github.com:owner/my-repo.git"

        name = detect_project_name()

        assert name == "my-repo"


class TestCaptureMetadata:
    """Tests for capture_metadata function."""

    def test_capture_metadata_basic(self) -> None:
        """capture_metadata should capture basic system info."""
        metadata = capture_metadata()

        assert metadata.hostname is not None
        assert metadata.username is not None
        assert metadata.platform is not None
        assert metadata.python_version is not None
        assert metadata.timestamp is not None
        assert metadata.project_name is not None

    def test_capture_metadata_with_tool_versions(self) -> None:
        """capture_metadata should include tool versions."""
        metadata = capture_metadata(
            tool_versions={"pytest": "8.0.0", "juxlib": "0.1.0"}
        )

        assert metadata.tool_versions["pytest"] == "8.0.0"
        assert metadata.tool_versions["juxlib"] == "0.1.0"

    def test_capture_metadata_with_env_vars(self) -> None:
        """capture_metadata should capture specified env vars."""
        with patch.dict(os.environ, {"MY_VAR": "my_value", "OTHER_VAR": "other"}):
            metadata = capture_metadata(include_env_vars=["MY_VAR", "OTHER_VAR"])

        assert metadata.env is not None
        assert metadata.env["MY_VAR"] == "my_value"
        assert metadata.env["OTHER_VAR"] == "other"

    def test_capture_metadata_with_project_name_override(self) -> None:
        """capture_metadata should use provided project name."""
        metadata = capture_metadata(project_name="custom-project")

        assert metadata.project_name == "custom-project"

    def test_capture_metadata_timestamp_is_iso8601(self) -> None:
        """capture_metadata should produce ISO 8601 timestamp."""
        metadata = capture_metadata()

        # Should be parseable as ISO 8601
        from datetime import datetime

        timestamp = datetime.fromisoformat(metadata.timestamp)
        assert timestamp is not None


class TestModuleExports:
    """Tests for module exports."""

    def test_all_exports_accessible(self) -> None:
        """All __all__ exports should be accessible."""
        from juxlib import metadata

        expected = [
            "capture_metadata",
            "EnvironmentMetadata",
            "GitInfo",
            "CIInfo",
            "detect_project_name",
            "capture_git_info",
            "is_git_repository",
            "detect_ci_provider",
            "is_ci_environment",
        ]

        for name in expected:
            assert hasattr(metadata, name), f"{name} not accessible"
