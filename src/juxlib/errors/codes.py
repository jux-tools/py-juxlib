# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""Error codes for programmatic error handling.

Error code ranges:
- 1xx: File errors (not found, permission denied, etc.)
- 2xx: Key/certificate errors (invalid format, not found, etc.)
- 3xx: XML errors (parse error, signature issues, etc.)
- 4xx: Configuration errors (invalid syntax, missing values, etc.)
- 5xx: Storage errors (not found, permission issues, etc.)
- 6xx: API errors (connection, authentication, etc.)
- 9xx: Generic errors (invalid argument, unexpected, etc.)
"""

from enum import Enum


class ErrorCode(Enum):
    """Error codes for programmatic error handling.

    Each error code belongs to a category indicated by its first digit:
    - 1xx: File system errors
    - 2xx: Cryptographic key/certificate errors
    - 3xx: XML processing errors
    - 4xx: Configuration errors
    - 5xx: Storage errors
    - 6xx: API/network errors
    - 9xx: Generic/unexpected errors
    """

    # File errors (1xx)
    FILE_NOT_FOUND = 101
    FILE_PERMISSION_DENIED = 102
    FILE_ALREADY_EXISTS = 103
    DIRECTORY_NOT_FOUND = 104

    # Key/Certificate errors (2xx)
    KEY_NOT_FOUND = 201
    KEY_INVALID_FORMAT = 202
    KEY_PERMISSION_DENIED = 203
    CERT_NOT_FOUND = 211
    CERT_INVALID_FORMAT = 212
    CERT_EXPIRED = 213

    # XML errors (3xx)
    XML_PARSE_ERROR = 301
    XML_INVALID_STRUCTURE = 302
    XML_SIGNATURE_MISSING = 303
    XML_SIGNATURE_INVALID = 304

    # Configuration errors (4xx)
    CONFIG_NOT_FOUND = 401
    CONFIG_INVALID_SYNTAX = 402
    CONFIG_INVALID_VALUE = 403
    CONFIG_MISSING_REQUIRED = 404

    # Storage errors (5xx)
    STORAGE_NOT_FOUND = 501
    STORAGE_PERMISSION_DENIED = 502
    STORAGE_FULL = 503
    STORAGE_WRITE_ERROR = 504
    REPORT_NOT_FOUND = 511
    REPORT_QUEUED_NOT_FOUND = 512

    # API errors (6xx)
    API_CONNECTION_ERROR = 601
    API_AUTHENTICATION_ERROR = 602
    API_SERVER_ERROR = 603
    API_TIMEOUT = 604
    API_INVALID_RESPONSE = 605

    # Generic errors (9xx)
    INVALID_ARGUMENT = 901
    OPERATION_FAILED = 902
    UNEXPECTED_ERROR = 999
