# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""Pydantic models for Jux API v1.0.0 responses.

This module provides type-safe data models for the Jux REST API,
enabling validation and IDE support for API response handling.
"""

from pydantic import BaseModel


class TestRun(BaseModel):
    """Test run summary from Jux API v1.0.0 query endpoints.

    Represents the test run data returned by /test_runs endpoints.

    Attributes:
        id: UUID of the test run
        project: Project name
        branch: Git branch name (nullable)
        commit_sha: Git commit SHA (nullable)
        total_tests: Total number of tests in the run
        failures: Number of failed tests
        errors: Number of tests with errors
        skipped: Number of skipped tests
        success_rate: Success rate percentage (0-100)
        inserted_at: ISO 8601 timestamp of test run creation

    Example:
        >>> test_run = TestRun(
        ...     id="550e8400-e29b-41d4-a716-446655440000",
        ...     project="my-app",
        ...     total_tests=30,
        ...     failures=2,
        ...     errors=0,
        ...     skipped=1,
        ...     success_rate=90.0,
        ...     inserted_at="2026-01-08T12:00:00.000000Z"
        ... )
        >>> print(test_run.success_rate)
        90.0
    """

    id: str
    project: str
    branch: str | None = None
    commit_sha: str | None = None
    total_tests: int
    failures: int
    errors: int
    skipped: int
    success_rate: float
    inserted_at: str
    tags: list[str] | None = None


class PublishResponse(BaseModel):
    """Response from Jux API v1.0.0 /junit/submit endpoint (jux-openapi SubmitResponse).

    Represents the complete response when publishing a JUnit XML report.

    Attributes:
        test_run_id: UUID of the created test run
        message: Human-readable success message
        test_count: Total number of tests in the run
        failure_count: Number of failed tests
        error_count: Number of tests with errors
        skipped_count: Number of skipped tests
        success_rate: Success rate percentage (0-100, optional)

    Example:
        >>> response = PublishResponse(
        ...     test_run_id="550e8400-e29b-41d4-a716-446655440000",
        ...     message="Test results submitted successfully",
        ...     test_count=30,
        ...     failure_count=2,
        ...     error_count=0,
        ...     skipped_count=1,
        ...     success_rate=90.0,
        ... )
        >>> print(response.test_run_id)
        550e8400-e29b-41d4-a716-446655440000
    """

    test_run_id: str
    message: str
    test_count: int
    failure_count: int
    error_count: int
    skipped_count: int
    success_rate: float | None = None
