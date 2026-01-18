# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""
HTTP client for Jux OpenAPI servers.

This module provides a resilient HTTP client for publishing signed JUnit XML
reports to Jux servers, with automatic retry logic and authentication handling.

Features:
- Bearer token authentication for remote servers
- Localhost bypass (no auth required for local development)
- Exponential backoff retry on server errors
- Pydantic models for type-safe response handling

Example usage:

    >>> from juxlib.api import JuxAPIClient
    >>>
    >>> client = JuxAPIClient(
    ...     api_url="https://jux.example.com",
    ...     bearer_token="your-token"
    ... )
    >>>
    >>> with open("junit-report-signed.xml") as f:
    ...     response = client.publish_report(f.read())
    >>>
    >>> print(f"Test run ID: {response.test_run.id}")
    >>> print(f"Success rate: {response.test_run.success_rate}%")
"""

# Public API will be exported here once implemented
# from .client import JuxAPIClient
# from .models import TestRun, PublishResponse

__all__: list[str] = []
