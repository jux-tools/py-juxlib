# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""HTTP client for Jux REST API v1.0.0.

This module provides a resilient HTTP client for publishing signed JUnit XML
reports to Jux servers, with automatic retry logic and authentication handling.

API Specification: Jux API v1.0.0
Endpoint: POST /api/v1/junit/submit
Content-Type: application/xml
Authentication: Bearer token (remote) or localhost bypass
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from juxlib.api.models import PublishResponse


class JuxAPIClient:
    """HTTP client for Jux REST API v1.0.0.

    Simple client that POSTs signed JUnit XML to the Jux API Server.
    The server auto-extracts metadata from XML <properties> elements.

    Features:
        - Bearer token authentication for remote servers
        - Localhost bypass (no auth for 127.0.0.1, ::1, localhost)
        - Exponential backoff retry on server errors (500, 502, 503, 504)
        - Configurable timeout and max retries
        - Connection pooling with session management

    Example:
        >>> client = JuxAPIClient(
        ...     api_url="https://jux.example.com/api/v1",
        ...     bearer_token="your-api-token"
        ... )
        >>> response = client.publish_report(signed_xml)
        >>> print(response.test_run.id)
        550e8400-e29b-41d4-a716-446655440000

    Localhost Example (no auth):
        >>> client = JuxAPIClient(api_url="http://localhost:4000/api/v1")
        >>> response = client.publish_report(signed_xml)
    """

    def __init__(
        self,
        api_url: str,
        bearer_token: str | None = None,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """Initialize Jux API client.

        Args:
            api_url: Base API URL (e.g., https://jux.example.com/api/v1)
            bearer_token: Optional Bearer token for remote authentication.
                          Not required for localhost (127.0.0.1, ::1, localhost).
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum retry attempts for transient failures (default: 3)

        Example:
            >>> # Remote server with authentication
            >>> client = JuxAPIClient(
            ...     api_url="https://jux.example.com/api/v1",
            ...     bearer_token="your-token-here"
            ... )

            >>> # Localhost (no authentication)
            >>> client = JuxAPIClient(api_url="http://localhost:4000/api/v1")
        """
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout

        # Session with retry logic for transient failures
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,  # 1s, 2s, 4s exponential backoff
            status_forcelist=[500, 502, 503, 504],  # Retry on server errors
            allowed_methods=["POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set Content-Type for XML (required by Jux API v1.0.0)
        self.session.headers["Content-Type"] = "application/xml"

        # Optional Bearer token authentication
        if bearer_token:
            self.session.headers["Authorization"] = f"Bearer {bearer_token}"

    def publish_report(self, signed_xml: str) -> PublishResponse:
        """Publish signed JUnit XML to Jux API v1.0.0.

        The server auto-extracts metadata from XML <properties> elements,
        computes canonical hash, and detects signature algorithm from XMLDsig.

        Args:
            signed_xml: Complete signed JUnit XML document with:
                - XMLDsig signature (if signing enabled)
                - Metadata in <properties> elements (project, git:*, ci:*, jux:*)

        Returns:
            PublishResponse with nested test_run containing ID and statistics

        Raises:
            requests.exceptions.RequestException: Network errors, timeouts
            requests.exceptions.HTTPError: HTTP 4xx/5xx errors with details

        Example:
            >>> response = client.publish_report(signed_xml)
            >>> print(f"Test run created: {response.test_run.id}")
            >>> print(f"Success rate: {response.test_run.success_rate}%")
        """
        try:
            response = self.session.post(
                f"{self.api_url}/junit/submit",
                data=signed_xml.encode("utf-8"),
                timeout=self.timeout,
            )
            response.raise_for_status()

            # Parse JSON response
            data = response.json()
            return PublishResponse(**data)

        except requests.exceptions.Timeout as e:
            raise requests.exceptions.RequestException(
                f"Request timeout after {self.timeout}s"
            ) from e

        except requests.exceptions.HTTPError as e:
            # Enhanced error message with server details
            if e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get("error", str(e))
                    details = error_data.get("details", {})
                    raise requests.exceptions.HTTPError(
                        f"{e.response.status_code} {error_msg}: {details}"
                    ) from e
                except ValueError:
                    # Response not JSON, re-raise original
                    pass
            raise

    def close(self) -> None:
        """Close the HTTP session and release resources.

        Call this method when you're done using the client to free up
        connection pool resources.

        Example:
            >>> client = JuxAPIClient(api_url="http://localhost:4000/api/v1")
            >>> try:
            ...     response = client.publish_report(signed_xml)
            ... finally:
            ...     client.close()
        """
        self.session.close()

    def __enter__(self) -> "JuxAPIClient":
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Context manager exit - closes the session."""
        self.close()
