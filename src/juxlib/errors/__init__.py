# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""
User-friendly error handling framework.

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

Example usage:

    >>> from juxlib.errors import KeyNotFoundError, ErrorCode
    >>>
    >>> try:
    ...     key = load_private_key(path)
    ... except FileNotFoundError:
    ...     raise KeyNotFoundError(
    ...         path=path,
    ...         suggestions=[
    ...             "Check that the private key path is correct",
    ...             "Generate a new key: jux-keygen --output ~/.ssh/jux/dev-key.pem"
    ...         ]
    ...     )
"""

# Public API will be exported here once implemented
# from .codes import ErrorCode
# from .exceptions import (
#     JuxError,
#     FileNotFoundError,
#     KeyNotFoundError,
#     XMLParseError,
#     ConfigurationError,
#     APIError,
# )

__all__: list[str] = []
