# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""CI/CD provider detection.

This module provides functions for detecting CI/CD providers and capturing
their standard environment variables. Supported providers:
- GitHub Actions
- GitLab CI
- Jenkins
- Travis CI
- CircleCI
- Azure Pipelines
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class CIInfo:
    """CI/CD provider information.

    Attributes:
        provider: Provider name (github, gitlab, jenkins, travis, circleci, azure)
        build_id: Unique build identifier
        build_url: URL to the build details
        env_vars: Standard environment variables for the provider
    """

    provider: str | None = None
    build_id: str | None = None
    build_url: str | None = None
    env_vars: dict[str, str] = field(default_factory=dict)


def _detect_github_actions() -> CIInfo | None:
    """Detect GitHub Actions and capture metadata."""
    if not os.getenv("GITHUB_ACTIONS"):
        return None

    build_id = os.getenv("GITHUB_RUN_ID")
    repo = os.getenv("GITHUB_REPOSITORY", "")
    server = os.getenv("GITHUB_SERVER_URL", "https://github.com")
    build_url = (
        f"{server}/{repo}/actions/runs/{build_id}" if build_id and repo else None
    )

    env_vars: dict[str, str] = {}
    for var in [
        "GITHUB_SHA",
        "GITHUB_REF",
        "GITHUB_ACTOR",
        "GITHUB_WORKFLOW",
        "GITHUB_RUN_NUMBER",
        "GITHUB_EVENT_NAME",
    ]:
        value = os.getenv(var)
        if value:
            env_vars[var] = value

    return CIInfo(
        provider="github",
        build_id=build_id,
        build_url=build_url,
        env_vars=env_vars,
    )


def _detect_gitlab_ci() -> CIInfo | None:
    """Detect GitLab CI and capture metadata."""
    if not os.getenv("GITLAB_CI"):
        return None

    env_vars: dict[str, str] = {}
    for var in [
        "CI_COMMIT_SHA",
        "CI_COMMIT_BRANCH",
        "CI_COMMIT_TAG",
        "CI_JOB_ID",
        "CI_JOB_NAME",
        "CI_PROJECT_PATH",
        "CI_PIPELINE_SOURCE",
    ]:
        value = os.getenv(var)
        if value:
            env_vars[var] = value

    return CIInfo(
        provider="gitlab",
        build_id=os.getenv("CI_PIPELINE_ID"),
        build_url=os.getenv("CI_PIPELINE_URL"),
        env_vars=env_vars,
    )


def _detect_jenkins() -> CIInfo | None:
    """Detect Jenkins and capture metadata."""
    if not os.getenv("JENKINS_URL"):
        return None

    env_vars: dict[str, str] = {}
    for var in [
        "GIT_COMMIT",
        "GIT_BRANCH",
        "JOB_NAME",
        "BUILD_NUMBER",
        "NODE_NAME",
    ]:
        value = os.getenv(var)
        if value:
            env_vars[var] = value

    return CIInfo(
        provider="jenkins",
        build_id=os.getenv("BUILD_ID"),
        build_url=os.getenv("BUILD_URL"),
        env_vars=env_vars,
    )


def _detect_travis_ci() -> CIInfo | None:
    """Detect Travis CI and capture metadata."""
    if not os.getenv("TRAVIS"):
        return None

    env_vars: dict[str, str] = {}
    for var in [
        "TRAVIS_COMMIT",
        "TRAVIS_BRANCH",
        "TRAVIS_JOB_ID",
        "TRAVIS_BUILD_NUMBER",
        "TRAVIS_REPO_SLUG",
    ]:
        value = os.getenv(var)
        if value:
            env_vars[var] = value

    return CIInfo(
        provider="travis",
        build_id=os.getenv("TRAVIS_BUILD_ID"),
        build_url=os.getenv("TRAVIS_BUILD_WEB_URL"),
        env_vars=env_vars,
    )


def _detect_circleci() -> CIInfo | None:
    """Detect CircleCI and capture metadata."""
    if not os.getenv("CIRCLECI"):
        return None

    env_vars: dict[str, str] = {}
    for var in [
        "CIRCLE_SHA1",
        "CIRCLE_BRANCH",
        "CIRCLE_JOB",
        "CIRCLE_WORKFLOW_ID",
        "CIRCLE_PROJECT_REPONAME",
    ]:
        value = os.getenv(var)
        if value:
            env_vars[var] = value

    return CIInfo(
        provider="circleci",
        build_id=os.getenv("CIRCLE_BUILD_NUM"),
        build_url=os.getenv("CIRCLE_BUILD_URL"),
        env_vars=env_vars,
    )


def _detect_azure_pipelines() -> CIInfo | None:
    """Detect Azure Pipelines and capture metadata."""
    if not os.getenv("TF_BUILD"):
        return None

    build_id = os.getenv("BUILD_BUILDID")
    org_uri = os.getenv("SYSTEM_COLLECTIONURI", "")
    project = os.getenv("SYSTEM_TEAMPROJECT", "")
    build_url = (
        f"{org_uri}{project}/_build/results?buildId={build_id}" if build_id else None
    )

    env_vars: dict[str, str] = {}
    for var in [
        "BUILD_SOURCEVERSION",
        "BUILD_SOURCEBRANCH",
        "BUILD_BUILDNUMBER",
        "AGENT_NAME",
        "BUILD_REASON",
    ]:
        value = os.getenv(var)
        if value:
            env_vars[var] = value

    return CIInfo(
        provider="azure",
        build_id=build_id,
        build_url=build_url,
        env_vars=env_vars,
    )


# List of all CI detection functions in priority order
_CI_DETECTORS = [
    _detect_github_actions,
    _detect_gitlab_ci,
    _detect_jenkins,
    _detect_travis_ci,
    _detect_circleci,
    _detect_azure_pipelines,
]


def detect_ci_provider() -> CIInfo:
    """Detect the current CI/CD provider and capture metadata.

    Tries each supported provider in order and returns the first match.

    Returns:
        CIInfo instance with provider details, or empty CIInfo if not in CI
    """
    for detector in _CI_DETECTORS:
        result = detector()
        if result is not None:
            return result

    return CIInfo()


def is_ci_environment() -> bool:
    """Check if running in a CI/CD environment.

    Returns:
        True if a CI provider is detected, False otherwise
    """
    return detect_ci_provider().provider is not None
