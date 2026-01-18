# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""User-friendly exception classes for juxlib.

This module provides structured exceptions with:
- Clear, actionable error messages
- Error codes for programmatic handling
- Suggestions for fixing common problems
- Optional Rich terminal formatting
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING, NoReturn

from .codes import ErrorCode

if TYPE_CHECKING:
    from rich.console import Console


def _get_console() -> Console:
    """Get Rich console for error output (lazy import)."""
    from rich.console import Console

    return Console(stderr=True)


class JuxError(Exception):
    """Base exception for juxlib errors with user-friendly messaging.

    Attributes:
        message: Main error message (what went wrong)
        error_code: Error code for programmatic handling
        suggestions: List of actionable suggestions for fixing the error
        details: Additional technical details
    """

    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        suggestions: list[str] | None = None,
        details: str | None = None,
    ) -> None:
        """Initialize error with user-friendly information.

        Args:
            message: Main error message (what went wrong)
            error_code: Error code for programmatic handling
            suggestions: List of actionable suggestions for fixing the error
            details: Additional technical details (optional)
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.suggestions = suggestions or []
        self.details = details

    def format_error(self, *, use_rich: bool = True) -> str:
        """Format error message for display.

        Args:
            use_rich: If True, include Rich markup for colored output

        Returns:
            Formatted error message with suggestions
        """
        if use_rich:
            lines = [f"[red]Error:[/red] {self.message}"]
        else:
            lines = [f"Error: {self.message}"]

        if self.details:
            lines.append(f"\n{self.details}")

        if self.suggestions:
            if use_rich:
                lines.append("\n[yellow]Possible solutions:[/yellow]")
            else:
                lines.append("\nPossible solutions:")
            for i, suggestion in enumerate(self.suggestions, 1):
                lines.append(f"  {i}. {suggestion}")

        if use_rich:
            lines.append(f"\n[dim]Error code: {self.error_code.name}[/dim]")
        else:
            lines.append(f"\nError code: {self.error_code.name}")

        return "\n".join(lines)

    def print_error(self) -> None:
        """Print formatted error to stderr using Rich."""
        console = _get_console()
        console.print(self.format_error(use_rich=True))

    def print_and_exit(self, exit_code: int = 1) -> NoReturn:
        """Print formatted error and exit.

        Args:
            exit_code: Exit code (default: 1)
        """
        self.print_error()
        sys.exit(exit_code)


# =============================================================================
# File errors (1xx)
# =============================================================================


class FileNotFoundError(JuxError):
    """File not found error with suggestions."""

    def __init__(self, file_path: Path | str, file_type: str = "file") -> None:
        """Initialize file not found error.

        Args:
            file_path: Path to missing file
            file_type: Type of file (for better messaging)
        """
        self.file_path = Path(file_path)
        self.file_type = file_type

        suggestions = [
            f"Check that the {file_type} path is correct",
            f"Verify the {file_type} exists at the specified location",
        ]

        super().__init__(
            message=f"{file_type.capitalize()} not found",
            error_code=ErrorCode.FILE_NOT_FOUND,
            suggestions=suggestions,
            details=f"Path: {self.file_path}",
        )


class FilePermissionError(JuxError):
    """File permission denied error."""

    def __init__(self, file_path: Path | str, operation: str = "access") -> None:
        """Initialize permission error.

        Args:
            file_path: Path to file
            operation: Operation that failed (read, write, execute)
        """
        self.file_path = Path(file_path)
        self.operation = operation

        super().__init__(
            message=f"Permission denied: cannot {operation} file",
            error_code=ErrorCode.FILE_PERMISSION_DENIED,
            suggestions=[
                f"Check file permissions: ls -la {self.file_path}",
                f"Ensure you have {operation} access to the file",
                "Run with appropriate user permissions",
            ],
            details=f"Path: {self.file_path}",
        )


class FileAlreadyExistsError(JuxError):
    """File already exists error."""

    def __init__(self, file_path: Path | str, force_hint: str | None = None) -> None:
        """Initialize file exists error.

        Args:
            file_path: Path to existing file
            force_hint: Hint for forcing overwrite (e.g., "--force")
        """
        self.file_path = Path(file_path)

        suggestions = [
            "Choose a different output path",
            "Remove the existing file first",
        ]

        if force_hint:
            suggestions.append(f"Use {force_hint} to overwrite existing file")

        super().__init__(
            message="File already exists",
            error_code=ErrorCode.FILE_ALREADY_EXISTS,
            suggestions=suggestions,
            details=f"Path: {self.file_path}",
        )


# =============================================================================
# Key/Certificate errors (2xx)
# =============================================================================


class KeyNotFoundError(JuxError):
    """Private key not found error."""

    def __init__(self, key_path: Path | str) -> None:
        """Initialize key not found error.

        Args:
            key_path: Path to missing key
        """
        self.key_path = Path(key_path)

        super().__init__(
            message="Private key not found",
            error_code=ErrorCode.KEY_NOT_FOUND,
            suggestions=[
                "Check that the private key path is correct",
                "Verify the private key exists at the specified location",
                "Generate a new key pair if needed",
            ],
            details=f"Path: {self.key_path}",
        )


class KeyInvalidFormatError(JuxError):
    """Invalid key format error."""

    def __init__(self, key_path: Path | str, expected_format: str = "PEM") -> None:
        """Initialize invalid key format error.

        Args:
            key_path: Path to invalid key
            expected_format: Expected key format
        """
        self.key_path = Path(key_path)
        self.expected_format = expected_format

        super().__init__(
            message=f"Invalid key format (expected {expected_format})",
            error_code=ErrorCode.KEY_INVALID_FORMAT,
            suggestions=[
                f"Ensure key is in {expected_format} format",
                "Generate a new key pair if needed",
                "Convert key to PEM format using openssl",
            ],
            details=f"Path: {self.key_path}",
        )


class CertNotFoundError(JuxError):
    """Certificate not found error."""

    def __init__(self, cert_path: Path | str) -> None:
        """Initialize certificate not found error.

        Args:
            cert_path: Path to missing certificate
        """
        self.cert_path = Path(cert_path)

        super().__init__(
            message="Certificate not found",
            error_code=ErrorCode.CERT_NOT_FOUND,
            suggestions=[
                "Check that the certificate path is correct",
                "Verify the certificate exists at the specified location",
                "Generate a new certificate if needed",
            ],
            details=f"Path: {self.cert_path}",
        )


class CertInvalidFormatError(JuxError):
    """Invalid certificate format error."""

    def __init__(self, cert_path: Path | str) -> None:
        """Initialize invalid certificate format error.

        Args:
            cert_path: Path to invalid certificate
        """
        self.cert_path = Path(cert_path)

        super().__init__(
            message="Invalid certificate format (expected PEM)",
            error_code=ErrorCode.CERT_INVALID_FORMAT,
            suggestions=[
                "Ensure certificate is in PEM format",
                "Generate a new certificate if needed",
                "Convert certificate to PEM format using openssl",
            ],
            details=f"Path: {self.cert_path}",
        )


# =============================================================================
# XML errors (3xx)
# =============================================================================


class XMLParseError(JuxError):
    """XML parsing error."""

    def __init__(self, source: Path | str | None, parse_error: str) -> None:
        """Initialize XML parse error.

        Args:
            source: Path to XML file or description (None for stdin/bytes)
            parse_error: Parse error message
        """
        self.source = source
        self.parse_error = parse_error
        source_str = str(source) if source else "input"

        super().__init__(
            message="Failed to parse XML",
            error_code=ErrorCode.XML_PARSE_ERROR,
            suggestions=[
                "Verify the input contains valid XML",
                "Check for syntax errors in the XML",
                "Ensure the file is a valid JUnit XML report",
            ],
            details=f"Source: {source_str}\nError: {parse_error}",
        )


class XMLSignatureMissingError(JuxError):
    """XML signature missing error."""

    def __init__(self, source: Path | str | None = None) -> None:
        """Initialize signature missing error.

        Args:
            source: Path to XML file or description (None for stdin/bytes)
        """
        self.source = source
        source_str = str(source) if source else "input"

        super().__init__(
            message="XML document is not signed (no signature found)",
            error_code=ErrorCode.XML_SIGNATURE_MISSING,
            suggestions=[
                "Sign the document first using sign_xml()",
                "Verify you're using the correct (signed) document",
                "Check that signing completed successfully",
            ],
            details=f"Source: {source_str}",
        )


class XMLSignatureInvalidError(JuxError):
    """XML signature invalid error."""

    def __init__(self, reason: str) -> None:
        """Initialize signature invalid error.

        Args:
            reason: Reason why signature is invalid
        """
        self.reason = reason

        super().__init__(
            message="Signature verification failed",
            error_code=ErrorCode.XML_SIGNATURE_INVALID,
            suggestions=[
                "Ensure you're using the correct certificate/public key",
                "Check that the document hasn't been modified after signing",
                "Verify the signing key matches the verification certificate",
                "Re-sign the document if it has been tampered with",
            ],
            details=f"Reason: {reason}",
        )


# =============================================================================
# Configuration errors (4xx)
# =============================================================================


class ConfigNotFoundError(JuxError):
    """Configuration file not found error."""

    def __init__(self, config_path: Path | str) -> None:
        """Initialize config not found error.

        Args:
            config_path: Path to missing config
        """
        self.config_path = Path(config_path)

        super().__init__(
            message="Configuration file not found",
            error_code=ErrorCode.CONFIG_NOT_FOUND,
            suggestions=[
                "Create a configuration file at the specified path",
                "Use environment variables instead (JUX_* prefix)",
                "Specify options programmatically",
            ],
            details=f"Path: {self.config_path}",
        )


class ConfigInvalidSyntaxError(JuxError):
    """Configuration syntax error."""

    def __init__(self, config_path: Path | str, syntax_error: str) -> None:
        """Initialize config syntax error.

        Args:
            config_path: Path to config file
            syntax_error: Syntax error description
        """
        self.config_path = Path(config_path)
        self.syntax_error = syntax_error

        super().__init__(
            message="Configuration file has invalid syntax",
            error_code=ErrorCode.CONFIG_INVALID_SYNTAX,
            suggestions=[
                "Check the file syntax (TOML or INI format)",
                "Validate the configuration file",
                "See documentation for configuration format",
            ],
            details=f"Path: {self.config_path}\nError: {syntax_error}",
        )


class ConfigInvalidValueError(JuxError):
    """Configuration invalid value error."""

    def __init__(
        self,
        key: str,
        value: str,
        reason: str,
        valid_values: list[str] | None = None,
    ) -> None:
        """Initialize config invalid value error.

        Args:
            key: Configuration key
            value: Invalid value
            reason: Why the value is invalid
            valid_values: List of valid values (optional)
        """
        self.key = key
        self.value = value
        self.reason = reason
        self.valid_values = valid_values

        suggestions = [f"Check the value for '{key}'"]
        if valid_values:
            suggestions.append(f"Valid values: {', '.join(valid_values)}")

        details = f"Key: {key}\nValue: {value}\nReason: {reason}"
        if valid_values:
            details += f"\nValid values: {', '.join(valid_values)}"

        super().__init__(
            message=f"Invalid configuration value for '{key}'",
            error_code=ErrorCode.CONFIG_INVALID_VALUE,
            suggestions=suggestions,
            details=details,
        )


# =============================================================================
# Storage errors (5xx)
# =============================================================================


class StorageNotFoundError(JuxError):
    """Storage directory not found error."""

    def __init__(self, storage_path: Path | str) -> None:
        """Initialize storage not found error.

        Args:
            storage_path: Path to storage directory
        """
        self.storage_path = Path(storage_path)

        super().__init__(
            message="Storage directory not found",
            error_code=ErrorCode.STORAGE_NOT_FOUND,
            suggestions=[
                "Storage will be created automatically on first use",
                f"Create manually: mkdir -p {self.storage_path}",
                "Check storage path configuration",
            ],
            details=f"Path: {self.storage_path}",
        )


class ReportNotFoundError(JuxError):
    """Report not found in storage."""

    def __init__(self, report_hash: str) -> None:
        """Initialize report not found error.

        Args:
            report_hash: Canonical hash of missing report
        """
        self.report_hash = report_hash

        super().__init__(
            message="Report not found in storage",
            error_code=ErrorCode.REPORT_NOT_FOUND,
            suggestions=[
                "Check the report hash is correct",
                "List all stored reports to verify availability",
                "The report may have been deleted or cleaned up",
            ],
            details=f"Hash: {report_hash}",
        )


# =============================================================================
# API errors (6xx)
# =============================================================================


class APIConnectionError(JuxError):
    """API connection error."""

    def __init__(self, url: str, reason: str) -> None:
        """Initialize API connection error.

        Args:
            url: API URL that failed
            reason: Connection failure reason
        """
        self.url = url
        self.reason = reason

        super().__init__(
            message="Failed to connect to API server",
            error_code=ErrorCode.API_CONNECTION_ERROR,
            suggestions=[
                "Check that the API URL is correct",
                "Verify the server is running and accessible",
                "Check your network connection",
            ],
            details=f"URL: {url}\nReason: {reason}",
        )


class APIAuthenticationError(JuxError):
    """API authentication error."""

    def __init__(self, url: str, reason: str = "Invalid or missing token") -> None:
        """Initialize API authentication error.

        Args:
            url: API URL
            reason: Authentication failure reason
        """
        self.url = url
        self.reason = reason

        super().__init__(
            message="API authentication failed",
            error_code=ErrorCode.API_AUTHENTICATION_ERROR,
            suggestions=[
                "Check that your API token is valid",
                "Verify the token has not expired",
                "Ensure the token has the required permissions",
            ],
            details=f"URL: {url}\nReason: {reason}",
        )


class APIServerError(JuxError):
    """API server error (5xx responses)."""

    def __init__(self, url: str, status_code: int, response: str = "") -> None:
        """Initialize API server error.

        Args:
            url: API URL
            status_code: HTTP status code
            response: Server response (if any)
        """
        self.url = url
        self.status_code = status_code
        self.response = response

        super().__init__(
            message=f"API server error (HTTP {status_code})",
            error_code=ErrorCode.API_SERVER_ERROR,
            suggestions=[
                "The server may be temporarily unavailable",
                "Try again in a few moments",
                "Contact the server administrator if the problem persists",
            ],
            details=f"URL: {url}\nStatus: {status_code}\nResponse: {response}"
            if response
            else f"URL: {url}\nStatus: {status_code}",
        )


# =============================================================================
# Generic errors (9xx)
# =============================================================================


class InvalidArgumentError(JuxError):
    """Invalid argument error."""

    def __init__(
        self,
        argument: str,
        reason: str,
        valid_values: list[str] | None = None,
    ) -> None:
        """Initialize invalid argument error.

        Args:
            argument: Argument name
            reason: Why it's invalid
            valid_values: List of valid values (optional)
        """
        self.argument = argument
        self.reason = reason
        self.valid_values = valid_values

        suggestions = [f"Check the '{argument}' value is correct"]
        if valid_values:
            suggestions.append(f"Valid values: {', '.join(valid_values)}")

        details = f"Argument: {argument}\nReason: {reason}"
        if valid_values:
            details += f"\nValid values: {', '.join(valid_values)}"

        super().__init__(
            message=f"Invalid argument: {argument}",
            error_code=ErrorCode.INVALID_ARGUMENT,
            suggestions=suggestions,
            details=details,
        )


def handle_unexpected_error(
    error: Exception,
    *,
    debug: bool = False,
    project_name: str = "juxlib",
    issue_url: str | None = None,
) -> NoReturn:
    """Handle unexpected errors with user-friendly messaging.

    Args:
        error: The unexpected exception
        debug: If True, re-raise for full traceback
        project_name: Name of the project for error message
        issue_url: URL for reporting issues (optional)

    Raises:
        SystemExit: Always exits with code 1 (unless debug=True)
    """
    if debug:
        raise error

    console = _get_console()
    console.print("[red]Unexpected error:[/red]")
    console.print(f"  {type(error).__name__}: {error}")
    console.print(f"\n[yellow]This may be a bug in {project_name}[/yellow]")

    if issue_url:
        console.print("Please report this at:")
        console.print(f"  {issue_url}")

    console.print("\nInclude the error message above and the context.")
    console.print("\n[dim]Tip: Set debug=True for full traceback[/dim]")

    sys.exit(1)
