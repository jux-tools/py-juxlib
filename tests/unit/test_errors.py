# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""Tests for juxlib.errors module."""

from pathlib import Path

import pytest

from juxlib.errors import (
    APIAuthenticationError,
    APIConnectionError,
    APIServerError,
    CertInvalidFormatError,
    CertNotFoundError,
    ConfigInvalidSyntaxError,
    ConfigInvalidValueError,
    ConfigNotFoundError,
    ErrorCode,
    FileAlreadyExistsError,
    FileNotFoundError,
    FilePermissionError,
    InvalidArgumentError,
    JuxError,
    KeyInvalidFormatError,
    KeyNotFoundError,
    ReportNotFoundError,
    StorageNotFoundError,
    XMLParseError,
    XMLSignatureInvalidError,
    XMLSignatureMissingError,
)


class TestErrorCode:
    """Tests for ErrorCode enum."""

    def test_file_errors_in_1xx_range(self) -> None:
        """File errors should be in 100-199 range."""
        assert ErrorCode.FILE_NOT_FOUND.value == 101
        assert ErrorCode.FILE_PERMISSION_DENIED.value == 102
        assert ErrorCode.FILE_ALREADY_EXISTS.value == 103
        assert ErrorCode.DIRECTORY_NOT_FOUND.value == 104

    def test_key_cert_errors_in_2xx_range(self) -> None:
        """Key/certificate errors should be in 200-299 range."""
        assert ErrorCode.KEY_NOT_FOUND.value == 201
        assert ErrorCode.KEY_INVALID_FORMAT.value == 202
        assert ErrorCode.CERT_NOT_FOUND.value == 211
        assert ErrorCode.CERT_INVALID_FORMAT.value == 212

    def test_xml_errors_in_3xx_range(self) -> None:
        """XML errors should be in 300-399 range."""
        assert ErrorCode.XML_PARSE_ERROR.value == 301
        assert ErrorCode.XML_SIGNATURE_MISSING.value == 303
        assert ErrorCode.XML_SIGNATURE_INVALID.value == 304

    def test_config_errors_in_4xx_range(self) -> None:
        """Configuration errors should be in 400-499 range."""
        assert ErrorCode.CONFIG_NOT_FOUND.value == 401
        assert ErrorCode.CONFIG_INVALID_SYNTAX.value == 402
        assert ErrorCode.CONFIG_INVALID_VALUE.value == 403

    def test_storage_errors_in_5xx_range(self) -> None:
        """Storage errors should be in 500-599 range."""
        assert ErrorCode.STORAGE_NOT_FOUND.value == 501
        assert ErrorCode.REPORT_NOT_FOUND.value == 511

    def test_api_errors_in_6xx_range(self) -> None:
        """API errors should be in 600-699 range."""
        assert ErrorCode.API_CONNECTION_ERROR.value == 601
        assert ErrorCode.API_AUTHENTICATION_ERROR.value == 602
        assert ErrorCode.API_SERVER_ERROR.value == 603

    def test_generic_errors_in_9xx_range(self) -> None:
        """Generic errors should be in 900-999 range."""
        assert ErrorCode.INVALID_ARGUMENT.value == 901
        assert ErrorCode.UNEXPECTED_ERROR.value == 999


class TestJuxError:
    """Tests for JuxError base class."""

    def test_init_with_required_args(self) -> None:
        """JuxError should initialize with required arguments."""
        error = JuxError("Test message", ErrorCode.UNEXPECTED_ERROR)

        assert error.message == "Test message"
        assert error.error_code == ErrorCode.UNEXPECTED_ERROR
        assert error.suggestions == []
        assert error.details is None
        assert str(error) == "Test message"

    def test_init_with_all_args(self) -> None:
        """JuxError should initialize with all arguments."""
        error = JuxError(
            message="Test message",
            error_code=ErrorCode.FILE_NOT_FOUND,
            suggestions=["Try this", "Or that"],
            details="Additional info",
        )

        assert error.message == "Test message"
        assert error.error_code == ErrorCode.FILE_NOT_FOUND
        assert error.suggestions == ["Try this", "Or that"]
        assert error.details == "Additional info"

    def test_format_error_with_rich(self) -> None:
        """format_error should include Rich markup by default."""
        error = JuxError(
            message="Something failed",
            error_code=ErrorCode.OPERATION_FAILED,
            suggestions=["Fix it"],
            details="Details here",
        )

        formatted = error.format_error(use_rich=True)

        assert "[red]Error:[/red]" in formatted
        assert "Something failed" in formatted
        assert "[yellow]Possible solutions:[/yellow]" in formatted
        assert "1. Fix it" in formatted
        assert "Details here" in formatted
        assert "[dim]Error code: OPERATION_FAILED[/dim]" in formatted

    def test_format_error_without_rich(self) -> None:
        """format_error should work without Rich markup."""
        error = JuxError(
            message="Something failed",
            error_code=ErrorCode.OPERATION_FAILED,
            suggestions=["Fix it"],
        )

        formatted = error.format_error(use_rich=False)

        assert "[red]" not in formatted
        assert "Error: Something failed" in formatted
        assert "Possible solutions:" in formatted
        assert "Error code: OPERATION_FAILED" in formatted

    def test_format_error_minimal(self) -> None:
        """format_error should work with minimal error."""
        error = JuxError("Simple error", ErrorCode.UNEXPECTED_ERROR)

        formatted = error.format_error(use_rich=False)

        assert "Error: Simple error" in formatted
        assert "Possible solutions:" not in formatted
        assert "Error code: UNEXPECTED_ERROR" in formatted

    def test_is_exception(self) -> None:
        """JuxError should be an Exception."""
        error = JuxError("Test", ErrorCode.UNEXPECTED_ERROR)

        assert isinstance(error, Exception)

        with pytest.raises(JuxError) as exc_info:
            raise error

        assert exc_info.value.message == "Test"


class TestFileErrors:
    """Tests for file-related errors."""

    def test_file_not_found_error(self) -> None:
        """FileNotFoundError should have correct attributes."""
        error = FileNotFoundError(Path("/path/to/file.txt"))

        assert error.error_code == ErrorCode.FILE_NOT_FOUND
        assert error.file_path == Path("/path/to/file.txt")
        assert "File not found" in error.message
        assert "/path/to/file.txt" in error.details
        assert len(error.suggestions) >= 2

    def test_file_not_found_error_with_type(self) -> None:
        """FileNotFoundError should use file_type in message."""
        error = FileNotFoundError("/path/to/config", file_type="configuration")

        assert "Configuration not found" in error.message

    def test_file_not_found_error_accepts_string(self) -> None:
        """FileNotFoundError should accept string paths."""
        error = FileNotFoundError("/path/to/file")

        assert error.file_path == Path("/path/to/file")

    def test_file_permission_error(self) -> None:
        """FilePermissionError should have correct attributes."""
        error = FilePermissionError(Path("/path/to/file"), operation="write")

        assert error.error_code == ErrorCode.FILE_PERMISSION_DENIED
        assert "cannot write file" in error.message
        assert "/path/to/file" in error.details

    def test_file_already_exists_error(self) -> None:
        """FileAlreadyExistsError should have correct attributes."""
        error = FileAlreadyExistsError(Path("/path/to/file"))

        assert error.error_code == ErrorCode.FILE_ALREADY_EXISTS
        assert "already exists" in error.message

    def test_file_already_exists_error_with_hint(self) -> None:
        """FileAlreadyExistsError should include force hint."""
        error = FileAlreadyExistsError("/path/to/file", force_hint="--force")

        assert "--force" in str(error.suggestions)


class TestKeyErrors:
    """Tests for key-related errors."""

    def test_key_not_found_error(self) -> None:
        """KeyNotFoundError should have correct attributes."""
        error = KeyNotFoundError(Path("/path/to/key.pem"))

        assert error.error_code == ErrorCode.KEY_NOT_FOUND
        assert error.key_path == Path("/path/to/key.pem")
        assert "Private key not found" in error.message

    def test_key_invalid_format_error(self) -> None:
        """KeyInvalidFormatError should have correct attributes."""
        error = KeyInvalidFormatError(Path("/path/to/key"), expected_format="PEM")

        assert error.error_code == ErrorCode.KEY_INVALID_FORMAT
        assert "PEM" in error.message

    def test_cert_not_found_error(self) -> None:
        """CertNotFoundError should have correct attributes."""
        error = CertNotFoundError(Path("/path/to/cert.pem"))

        assert error.error_code == ErrorCode.CERT_NOT_FOUND
        assert "Certificate not found" in error.message

    def test_cert_invalid_format_error(self) -> None:
        """CertInvalidFormatError should have correct attributes."""
        error = CertInvalidFormatError(Path("/path/to/cert"))

        assert error.error_code == ErrorCode.CERT_INVALID_FORMAT
        assert "PEM" in error.message


class TestXMLErrors:
    """Tests for XML-related errors."""

    def test_xml_parse_error(self) -> None:
        """XMLParseError should have correct attributes."""
        error = XMLParseError(Path("/path/to/file.xml"), "Invalid syntax at line 5")

        assert error.error_code == ErrorCode.XML_PARSE_ERROR
        assert "Failed to parse XML" in error.message
        assert "Invalid syntax at line 5" in error.details

    def test_xml_parse_error_with_none_source(self) -> None:
        """XMLParseError should handle None source (stdin/bytes)."""
        error = XMLParseError(None, "Parse error")

        assert "input" in error.details

    def test_xml_signature_missing_error(self) -> None:
        """XMLSignatureMissingError should have correct attributes."""
        error = XMLSignatureMissingError(Path("/path/to/file.xml"))

        assert error.error_code == ErrorCode.XML_SIGNATURE_MISSING
        assert "not signed" in error.message

    def test_xml_signature_invalid_error(self) -> None:
        """XMLSignatureInvalidError should have correct attributes."""
        error = XMLSignatureInvalidError("Certificate mismatch")

        assert error.error_code == ErrorCode.XML_SIGNATURE_INVALID
        assert "verification failed" in error.message
        assert "Certificate mismatch" in error.details


class TestConfigErrors:
    """Tests for configuration-related errors."""

    def test_config_not_found_error(self) -> None:
        """ConfigNotFoundError should have correct attributes."""
        error = ConfigNotFoundError(Path("/path/to/config.toml"))

        assert error.error_code == ErrorCode.CONFIG_NOT_FOUND
        assert "Configuration file not found" in error.message

    def test_config_invalid_syntax_error(self) -> None:
        """ConfigInvalidSyntaxError should have correct attributes."""
        error = ConfigInvalidSyntaxError(
            Path("/path/to/config.toml"), "Invalid TOML at line 10"
        )

        assert error.error_code == ErrorCode.CONFIG_INVALID_SYNTAX
        assert "Invalid TOML" in error.details

    def test_config_invalid_value_error(self) -> None:
        """ConfigInvalidValueError should have correct attributes."""
        error = ConfigInvalidValueError(
            key="timeout",
            value="-1",
            reason="Must be positive",
            valid_values=["1", "5", "10"],
        )

        assert error.error_code == ErrorCode.CONFIG_INVALID_VALUE
        assert "timeout" in error.message
        assert "1, 5, 10" in error.details


class TestStorageErrors:
    """Tests for storage-related errors."""

    def test_storage_not_found_error(self) -> None:
        """StorageNotFoundError should have correct attributes."""
        error = StorageNotFoundError(Path("/path/to/storage"))

        assert error.error_code == ErrorCode.STORAGE_NOT_FOUND
        assert "Storage directory not found" in error.message

    def test_report_not_found_error(self) -> None:
        """ReportNotFoundError should have correct attributes."""
        error = ReportNotFoundError("abc123def456")

        assert error.error_code == ErrorCode.REPORT_NOT_FOUND
        assert "abc123def456" in error.details


class TestAPIErrors:
    """Tests for API-related errors."""

    def test_api_connection_error(self) -> None:
        """APIConnectionError should have correct attributes."""
        error = APIConnectionError(
            url="https://api.example.com", reason="Connection refused"
        )

        assert error.error_code == ErrorCode.API_CONNECTION_ERROR
        assert "api.example.com" in error.details
        assert "Connection refused" in error.details

    def test_api_authentication_error(self) -> None:
        """APIAuthenticationError should have correct attributes."""
        error = APIAuthenticationError(
            url="https://api.example.com", reason="Token expired"
        )

        assert error.error_code == ErrorCode.API_AUTHENTICATION_ERROR
        assert "authentication failed" in error.message

    def test_api_server_error(self) -> None:
        """APIServerError should have correct attributes."""
        error = APIServerError(
            url="https://api.example.com",
            status_code=503,
            response="Service unavailable",
        )

        assert error.error_code == ErrorCode.API_SERVER_ERROR
        assert "503" in error.message
        assert "Service unavailable" in error.details


class TestGenericErrors:
    """Tests for generic errors."""

    def test_invalid_argument_error(self) -> None:
        """InvalidArgumentError should have correct attributes."""
        error = InvalidArgumentError(
            argument="--format",
            reason="Unknown format",
            valid_values=["json", "xml", "csv"],
        )

        assert error.error_code == ErrorCode.INVALID_ARGUMENT
        assert "--format" in error.message
        assert "json, xml, csv" in error.details


class TestExportsAndImports:
    """Tests for module exports."""

    def test_all_error_classes_exported(self) -> None:
        """All error classes should be importable from juxlib.errors."""
        from juxlib import errors

        # Verify __all__ contains expected items
        expected = [
            "ErrorCode",
            "JuxError",
            "FileNotFoundError",
            "FilePermissionError",
            "FileAlreadyExistsError",
            "KeyNotFoundError",
            "KeyInvalidFormatError",
            "CertNotFoundError",
            "CertInvalidFormatError",
            "XMLParseError",
            "XMLSignatureMissingError",
            "XMLSignatureInvalidError",
            "ConfigNotFoundError",
            "ConfigInvalidSyntaxError",
            "ConfigInvalidValueError",
            "StorageNotFoundError",
            "ReportNotFoundError",
            "APIConnectionError",
            "APIAuthenticationError",
            "APIServerError",
            "InvalidArgumentError",
            "handle_unexpected_error",
        ]

        for name in expected:
            assert name in errors.__all__, f"{name} not in __all__"
            assert hasattr(errors, name), f"{name} not accessible"

    def test_error_inheritance(self) -> None:
        """All custom errors should inherit from JuxError."""
        error_classes = [
            FileNotFoundError,
            FilePermissionError,
            FileAlreadyExistsError,
            KeyNotFoundError,
            KeyInvalidFormatError,
            CertNotFoundError,
            CertInvalidFormatError,
            XMLParseError,
            XMLSignatureMissingError,
            XMLSignatureInvalidError,
            ConfigNotFoundError,
            ConfigInvalidSyntaxError,
            ConfigInvalidValueError,
            StorageNotFoundError,
            ReportNotFoundError,
            APIConnectionError,
            APIAuthenticationError,
            APIServerError,
            InvalidArgumentError,
        ]

        for cls in error_classes:
            assert issubclass(cls, JuxError), f"{cls.__name__} not subclass of JuxError"
