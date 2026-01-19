# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""Pydantic models for Jux API v1.0.0 responses.

This module provides type-safe data models for the Jux REST API,
enabling validation and IDE support for API response handling.
"""

from pydantic import BaseModel


class TestRun(BaseModel):
    """Test run details from Jux API v1.0.0.

    Represents the test run data returned by the /junit/submit endpoint.

    Attributes:
        id: UUID of the created test run
        status: Test run status (e.g., "completed")
        time: Test run duration in seconds (nullable)
        errors: Number of tests with errors
        branch: Git branch name (nullable)
        project: Project name
        failures: Number of failed tests
        skipped: Number of skipped tests
        success_rate: Success rate percentage (0-100)
        commit_sha: Git commit SHA (nullable)
        total_tests: Total number of tests in the run
        created_at: ISO 8601 timestamp of test run creation

    Example:
        >>> test_run = TestRun(
        ...     id="550e8400-e29b-41d4-a716-446655440000",
        ...     status="completed",
        ...     errors=0,
        ...     project="my-app",
        ...     failures=2,
        ...     skipped=1,
        ...     success_rate=90.0,
        ...     total_tests=30,
        ...     created_at="2026-01-08T12:00:00.000000Z"
        ... )
        >>> print(test_run.success_rate)
        90.0
    """

    id: str
    status: str
    time: float | None = None
    errors: int
    branch: str | None = None
    project: str
    failures: int
    skipped: int
    success_rate: float
    commit_sha: str | None = None
    total_tests: int
    created_at: str


class PublishResponse(BaseModel):
    """Response from Jux API v1.0.0 /junit/submit endpoint.

    Represents the complete response when publishing a JUnit XML report.

    Attributes:
        message: Human-readable success message
        status: Response status (e.g., "success")
        test_run: Nested test run details

    Example:
        >>> response = PublishResponse(
        ...     message="Test report submitted successfully",
        ...     status="success",
        ...     test_run=TestRun(...)
        ... )
        >>> print(response.test_run.id)
        550e8400-e29b-41d4-a716-446655440000
    """

    message: str
    status: str
    test_run: TestRun
