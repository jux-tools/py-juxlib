# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""User-friendly error handling framework.

This module provides structured exceptions with error codes, user-friendly
messages, and actionable suggestions for fixing common issues.

Features:
- Categorized error codes for programmatic handling
- Rich terminal formatting with colored output
- Actionable suggestions for each error type
- Separation of user message and technical details

Error categories:
- 1xx: File errors (not found, permission denied, etc.)
- 2xx: Key/certificate errors (invalid format, not found, etc.)
- 3xx: XML errors (parse error, signature issues, etc.)
- 4xx: Configuration errors (invalid syntax, missing values, etc.)
- 5xx: Storage errors (not found, permission issues, etc.)
- 6xx: API errors (connection, authentication, etc.)
- 9xx: Generic errors (invalid argument, unexpected, etc.)

Example usage:

    >>> from juxlib.errors import KeyNotFoundError, ErrorCode
    >>>
    >>> try:
    ...     key = load_private_key(path)
    ... except OSError:
    ...     raise KeyNotFoundError(path)
    >>>
    >>> # Programmatic error handling
    >>> try:
    ...     do_something()
    ... except JuxError as e:
    ...     if e.error_code == ErrorCode.KEY_NOT_FOUND:
    ...         # Handle specifically
    ...         pass
    ...     e.print_error()  # Rich formatted output
"""

from .codes import ErrorCode
from .exceptions import (
    APIAuthenticationError,
    APIConnectionError,
    APIServerError,
    CertInvalidFormatError,
    CertNotFoundError,
    ConfigInvalidSyntaxError,
    ConfigInvalidValueError,
    ConfigNotFoundError,
    FileAlreadyExistsError,
    FileNotFoundError,
    FilePermissionError,
    InvalidArgumentError,
    JuxError,
    KeyInvalidFormatError,
    KeyNotFoundError,
    QueuedReportNotFoundError,
    ReportNotFoundError,
    StorageNotFoundError,
    StorageWriteError,
    XMLParseError,
    XMLSignatureInvalidError,
    XMLSignatureMissingError,
    handle_unexpected_error,
)

__all__ = [  # noqa: RUF022 - intentionally grouped by category
    # Base
    "ErrorCode",
    "JuxError",
    # File errors (1xx)
    "FileNotFoundError",
    "FilePermissionError",
    "FileAlreadyExistsError",
    # Key/Certificate errors (2xx)
    "KeyNotFoundError",
    "KeyInvalidFormatError",
    "CertNotFoundError",
    "CertInvalidFormatError",
    # XML errors (3xx)
    "XMLParseError",
    "XMLSignatureMissingError",
    "XMLSignatureInvalidError",
    # Configuration errors (4xx)
    "ConfigNotFoundError",
    "ConfigInvalidSyntaxError",
    "ConfigInvalidValueError",
    # Storage errors (5xx)
    "StorageNotFoundError",
    "StorageWriteError",
    "ReportNotFoundError",
    "QueuedReportNotFoundError",
    # API errors (6xx)
    "APIConnectionError",
    "APIAuthenticationError",
    "APIServerError",
    # Generic errors (9xx)
    "InvalidArgumentError",
    # Utilities
    "handle_unexpected_error",
]
