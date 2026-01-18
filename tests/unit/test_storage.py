# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""Tests for juxlib.storage module."""

from __future__ import annotations

import os
import platform
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from juxlib.errors import (
    QueuedReportNotFoundError,
    ReportNotFoundError,
    StorageWriteError,
)
from juxlib.storage import ReportStorage, get_default_storage_path

# =============================================================================
# get_default_storage_path tests
# =============================================================================


class TestGetDefaultStoragePath:
    """Tests for get_default_storage_path function."""

    def test_returns_path_object(self) -> None:
        """Should return a Path object."""
        result = get_default_storage_path()
        assert isinstance(result, Path)

    def test_path_ends_with_jux(self) -> None:
        """Should return path ending with 'jux'."""
        result = get_default_storage_path()
        assert result.name == "jux"

    @patch("platform.system")
    def test_macos_path(self, mock_system: patch) -> None:
        """Should use ~/Library/Application Support on macOS."""
        mock_system.return_value = "Darwin"
        result = get_default_storage_path()
        assert "Library" in str(result)
        assert "Application Support" in str(result)
        assert result.name == "jux"

    @patch("platform.system")
    def test_linux_path_default(self, mock_system: patch) -> None:
        """Should use ~/.local/share on Linux by default."""
        mock_system.return_value = "Linux"
        with patch.dict(os.environ, {}, clear=True):
            # Remove XDG_DATA_HOME if set
            os.environ.pop("XDG_DATA_HOME", None)
            result = get_default_storage_path()
            assert ".local" in str(result)
            assert "share" in str(result)
            assert result.name == "jux"

    @patch("platform.system")
    def test_linux_path_xdg(self, mock_system: patch) -> None:
        """Should use XDG_DATA_HOME on Linux if set."""
        mock_system.return_value = "Linux"
        with patch.dict(os.environ, {"XDG_DATA_HOME": "/custom/data"}):
            result = get_default_storage_path()
            assert result == Path("/custom/data/jux")

    @patch("platform.system")
    def test_windows_path_localappdata(self, mock_system: patch) -> None:
        """Should use LOCALAPPDATA on Windows if set."""
        mock_system.return_value = "Windows"
        with patch.dict(
            os.environ, {"LOCALAPPDATA": "C:\\Users\\Test\\AppData\\Local"}
        ):
            result = get_default_storage_path()
            assert "AppData" in str(result) or "Local" in str(result)
            assert result.name == "jux"

    @patch("platform.system")
    def test_windows_path_fallback(self, mock_system: patch) -> None:
        """Should use AppData/Local on Windows as fallback."""
        mock_system.return_value = "Windows"
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("LOCALAPPDATA", None)
            result = get_default_storage_path()
            assert result.name == "jux"


# =============================================================================
# ReportStorage initialization tests
# =============================================================================


class TestReportStorageInit:
    """Tests for ReportStorage initialization."""

    def test_creates_storage_directory(self, tmp_path: Path) -> None:
        """Should create storage directory on init."""
        storage_path = tmp_path / "storage"
        assert not storage_path.exists()

        ReportStorage(storage_path)

        assert storage_path.exists()
        assert storage_path.is_dir()

    def test_creates_reports_subdirectory(self, tmp_path: Path) -> None:
        """Should create reports subdirectory."""
        storage = ReportStorage(tmp_path)
        assert (storage.storage_path / "reports").exists()

    def test_creates_queue_subdirectory(self, tmp_path: Path) -> None:
        """Should create queue subdirectory."""
        storage = ReportStorage(tmp_path)
        assert (storage.storage_path / "queue").exists()

    def test_uses_default_path_when_none(self) -> None:
        """Should use default path when none provided."""
        storage = ReportStorage(None)
        assert storage.storage_path == get_default_storage_path()

    def test_uses_custom_path(self, tmp_path: Path) -> None:
        """Should use custom path when provided."""
        custom_path = tmp_path / "custom"
        storage = ReportStorage(custom_path)
        assert storage.storage_path == custom_path


# =============================================================================
# Report storage operations tests
# =============================================================================


class TestReportStorageOperations:
    """Tests for ReportStorage CRUD operations."""

    @pytest.fixture
    def storage(self, tmp_path: Path) -> ReportStorage:
        """Create a ReportStorage instance for testing."""
        return ReportStorage(tmp_path)

    @pytest.fixture
    def sample_xml(self) -> bytes:
        """Sample XML content for testing."""
        return b'<?xml version="1.0"?><testsuites><testsuite name="test"/></testsuites>'

    # store_report tests

    def test_store_report_creates_file(
        self, storage: ReportStorage, sample_xml: bytes
    ) -> None:
        """Should create report file."""
        storage.store_report(sample_xml, "abc123")
        report_file = storage.storage_path / "reports" / "abc123.xml"
        assert report_file.exists()

    def test_store_report_content_matches(
        self, storage: ReportStorage, sample_xml: bytes
    ) -> None:
        """Should store correct content."""
        storage.store_report(sample_xml, "abc123")
        report_file = storage.storage_path / "reports" / "abc123.xml"
        assert report_file.read_bytes() == sample_xml

    def test_store_report_overwrites_existing(
        self, storage: ReportStorage, sample_xml: bytes
    ) -> None:
        """Should overwrite existing report."""
        storage.store_report(sample_xml, "abc123")
        new_content = b"<new>content</new>"
        storage.store_report(new_content, "abc123")

        report_file = storage.storage_path / "reports" / "abc123.xml"
        assert report_file.read_bytes() == new_content

    @pytest.mark.skipif(platform.system() == "Windows", reason="Unix permissions")
    def test_store_report_sets_permissions(
        self, storage: ReportStorage, sample_xml: bytes
    ) -> None:
        """Should set restrictive permissions (Unix only)."""
        storage.store_report(sample_xml, "abc123")
        report_file = storage.storage_path / "reports" / "abc123.xml"
        mode = report_file.stat().st_mode & 0o777
        assert mode == 0o600

    # get_report tests

    def test_get_report_returns_content(
        self, storage: ReportStorage, sample_xml: bytes
    ) -> None:
        """Should return stored content."""
        storage.store_report(sample_xml, "abc123")
        result = storage.get_report("abc123")
        assert result == sample_xml

    def test_get_report_not_found_raises(self, storage: ReportStorage) -> None:
        """Should raise ReportNotFoundError for missing report."""
        with pytest.raises(ReportNotFoundError) as exc_info:
            storage.get_report("nonexistent")
        assert exc_info.value.report_hash == "nonexistent"

    # report_exists tests

    def test_report_exists_true(
        self, storage: ReportStorage, sample_xml: bytes
    ) -> None:
        """Should return True for existing report."""
        storage.store_report(sample_xml, "abc123")
        assert storage.report_exists("abc123") is True

    def test_report_exists_false(self, storage: ReportStorage) -> None:
        """Should return False for missing report."""
        assert storage.report_exists("nonexistent") is False

    # delete_report tests

    def test_delete_report_removes_file(
        self, storage: ReportStorage, sample_xml: bytes
    ) -> None:
        """Should delete report file."""
        storage.store_report(sample_xml, "abc123")
        storage.delete_report("abc123")
        assert not storage.report_exists("abc123")

    def test_delete_report_nonexistent_no_error(self, storage: ReportStorage) -> None:
        """Should not raise error for nonexistent report."""
        # Should not raise
        storage.delete_report("nonexistent")

    # list_reports tests

    def test_list_reports_empty(self, storage: ReportStorage) -> None:
        """Should return empty list when no reports."""
        assert storage.list_reports() == []

    def test_list_reports_returns_hashes(
        self, storage: ReportStorage, sample_xml: bytes
    ) -> None:
        """Should return list of report hashes."""
        storage.store_report(sample_xml, "abc123")
        storage.store_report(sample_xml, "def456")
        storage.store_report(sample_xml, "ghi789")

        reports = storage.list_reports()
        assert len(reports) == 3
        assert "abc123" in reports
        assert "def456" in reports
        assert "ghi789" in reports


# =============================================================================
# Queue operations tests
# =============================================================================


class TestQueueOperations:
    """Tests for ReportStorage queue operations."""

    @pytest.fixture
    def storage(self, tmp_path: Path) -> ReportStorage:
        """Create a ReportStorage instance for testing."""
        return ReportStorage(tmp_path)

    @pytest.fixture
    def sample_xml(self) -> bytes:
        """Sample XML content for testing."""
        return b'<?xml version="1.0"?><testsuites/>'

    # queue_report tests

    def test_queue_report_creates_file(
        self, storage: ReportStorage, sample_xml: bytes
    ) -> None:
        """Should create queued report file."""
        storage.queue_report(sample_xml, "abc123")
        queue_file = storage.storage_path / "queue" / "abc123.xml"
        assert queue_file.exists()

    def test_queue_report_content_matches(
        self, storage: ReportStorage, sample_xml: bytes
    ) -> None:
        """Should store correct content in queue."""
        storage.queue_report(sample_xml, "abc123")
        queue_file = storage.storage_path / "queue" / "abc123.xml"
        assert queue_file.read_bytes() == sample_xml

    # get_queued_report tests

    def test_get_queued_report_returns_content(
        self, storage: ReportStorage, sample_xml: bytes
    ) -> None:
        """Should return queued content."""
        storage.queue_report(sample_xml, "abc123")
        result = storage.get_queued_report("abc123")
        assert result == sample_xml

    def test_get_queued_report_not_found_raises(self, storage: ReportStorage) -> None:
        """Should raise QueuedReportNotFoundError for missing report."""
        with pytest.raises(QueuedReportNotFoundError) as exc_info:
            storage.get_queued_report("nonexistent")
        assert exc_info.value.report_hash == "nonexistent"

    # queued_report_exists tests

    def test_queued_report_exists_true(
        self, storage: ReportStorage, sample_xml: bytes
    ) -> None:
        """Should return True for existing queued report."""
        storage.queue_report(sample_xml, "abc123")
        assert storage.queued_report_exists("abc123") is True

    def test_queued_report_exists_false(self, storage: ReportStorage) -> None:
        """Should return False for missing queued report."""
        assert storage.queued_report_exists("nonexistent") is False

    # list_queued_reports tests

    def test_list_queued_reports_empty(self, storage: ReportStorage) -> None:
        """Should return empty list when no queued reports."""
        assert storage.list_queued_reports() == []

    def test_list_queued_reports_returns_hashes(
        self, storage: ReportStorage, sample_xml: bytes
    ) -> None:
        """Should return list of queued report hashes."""
        storage.queue_report(sample_xml, "abc123")
        storage.queue_report(sample_xml, "def456")

        queued = storage.list_queued_reports()
        assert len(queued) == 2
        assert "abc123" in queued
        assert "def456" in queued

    # dequeue_report tests

    def test_dequeue_report_moves_to_reports(
        self, storage: ReportStorage, sample_xml: bytes
    ) -> None:
        """Should move report from queue to reports."""
        storage.queue_report(sample_xml, "abc123")
        storage.dequeue_report("abc123")

        assert storage.report_exists("abc123")
        assert not storage.queued_report_exists("abc123")

    def test_dequeue_report_preserves_content(
        self, storage: ReportStorage, sample_xml: bytes
    ) -> None:
        """Should preserve content when dequeuing."""
        storage.queue_report(sample_xml, "abc123")
        storage.dequeue_report("abc123")

        assert storage.get_report("abc123") == sample_xml

    def test_dequeue_report_not_found_raises(self, storage: ReportStorage) -> None:
        """Should raise QueuedReportNotFoundError for missing report."""
        with pytest.raises(QueuedReportNotFoundError):
            storage.dequeue_report("nonexistent")

    # delete_queued_report tests

    def test_delete_queued_report_removes_file(
        self, storage: ReportStorage, sample_xml: bytes
    ) -> None:
        """Should delete queued report file."""
        storage.queue_report(sample_xml, "abc123")
        storage.delete_queued_report("abc123")
        assert not storage.queued_report_exists("abc123")

    def test_delete_queued_report_nonexistent_no_error(
        self, storage: ReportStorage
    ) -> None:
        """Should not raise error for nonexistent queued report."""
        # Should not raise
        storage.delete_queued_report("nonexistent")


# =============================================================================
# Statistics tests
# =============================================================================


class TestStorageStats:
    """Tests for ReportStorage statistics."""

    @pytest.fixture
    def storage(self, tmp_path: Path) -> ReportStorage:
        """Create a ReportStorage instance for testing."""
        return ReportStorage(tmp_path)

    @pytest.fixture
    def sample_xml(self) -> bytes:
        """Sample XML content for testing."""
        return b'<?xml version="1.0"?><testsuites/>'

    def test_stats_empty_storage(self, storage: ReportStorage) -> None:
        """Should return correct stats for empty storage."""
        stats = storage.get_stats()
        assert stats["total_reports"] == 0
        assert stats["queued_reports"] == 0
        assert stats["total_size"] == 0
        assert stats["oldest_report"] is None

    def test_stats_total_reports(
        self, storage: ReportStorage, sample_xml: bytes
    ) -> None:
        """Should count total reports."""
        storage.store_report(sample_xml, "abc123")
        storage.store_report(sample_xml, "def456")

        stats = storage.get_stats()
        assert stats["total_reports"] == 2

    def test_stats_queued_reports(
        self, storage: ReportStorage, sample_xml: bytes
    ) -> None:
        """Should count queued reports."""
        storage.queue_report(sample_xml, "abc123")
        storage.queue_report(sample_xml, "def456")
        storage.queue_report(sample_xml, "ghi789")

        stats = storage.get_stats()
        assert stats["queued_reports"] == 3

    def test_stats_total_size(self, storage: ReportStorage) -> None:
        """Should calculate total size including queue."""
        content1 = b"a" * 100
        content2 = b"b" * 200
        content3 = b"c" * 50

        storage.store_report(content1, "abc123")
        storage.store_report(content2, "def456")
        storage.queue_report(content3, "ghi789")

        stats = storage.get_stats()
        assert stats["total_size"] == 350

    def test_stats_oldest_report(
        self, storage: ReportStorage, sample_xml: bytes
    ) -> None:
        """Should track oldest report timestamp."""
        storage.store_report(sample_xml, "first")
        time.sleep(0.1)  # Ensure different timestamps
        storage.store_report(sample_xml, "second")

        stats = storage.get_stats()
        assert stats["oldest_report"] is not None
        # Oldest report timestamp should be an ISO string
        assert "T" in stats["oldest_report"]


# =============================================================================
# Clear operations tests
# =============================================================================


class TestClearOperations:
    """Tests for ReportStorage clear operations."""

    @pytest.fixture
    def storage(self, tmp_path: Path) -> ReportStorage:
        """Create a ReportStorage instance for testing."""
        return ReportStorage(tmp_path)

    @pytest.fixture
    def sample_xml(self) -> bytes:
        """Sample XML content for testing."""
        return b'<?xml version="1.0"?><testsuites/>'

    def test_clear_reports_removes_all(
        self, storage: ReportStorage, sample_xml: bytes
    ) -> None:
        """Should remove all reports."""
        storage.store_report(sample_xml, "abc123")
        storage.store_report(sample_xml, "def456")
        storage.store_report(sample_xml, "ghi789")

        count = storage.clear_reports()

        assert count == 3
        assert storage.list_reports() == []

    def test_clear_reports_returns_count(
        self, storage: ReportStorage, sample_xml: bytes
    ) -> None:
        """Should return count of deleted reports."""
        storage.store_report(sample_xml, "abc123")
        storage.store_report(sample_xml, "def456")

        count = storage.clear_reports()
        assert count == 2

    def test_clear_reports_empty_returns_zero(self, storage: ReportStorage) -> None:
        """Should return zero for empty storage."""
        count = storage.clear_reports()
        assert count == 0

    def test_clear_queue_removes_all(
        self, storage: ReportStorage, sample_xml: bytes
    ) -> None:
        """Should remove all queued reports."""
        storage.queue_report(sample_xml, "abc123")
        storage.queue_report(sample_xml, "def456")

        count = storage.clear_queue()

        assert count == 2
        assert storage.list_queued_reports() == []

    def test_clear_queue_returns_count(
        self, storage: ReportStorage, sample_xml: bytes
    ) -> None:
        """Should return count of deleted queued reports."""
        storage.queue_report(sample_xml, "abc123")
        storage.queue_report(sample_xml, "def456")
        storage.queue_report(sample_xml, "ghi789")

        count = storage.clear_queue()
        assert count == 3

    def test_clear_queue_empty_returns_zero(self, storage: ReportStorage) -> None:
        """Should return zero for empty queue."""
        count = storage.clear_queue()
        assert count == 0

    def test_clear_reports_preserves_queue(
        self, storage: ReportStorage, sample_xml: bytes
    ) -> None:
        """Should not affect queue when clearing reports."""
        storage.store_report(sample_xml, "report1")
        storage.queue_report(sample_xml, "queued1")

        storage.clear_reports()

        assert storage.list_reports() == []
        assert "queued1" in storage.list_queued_reports()

    def test_clear_queue_preserves_reports(
        self, storage: ReportStorage, sample_xml: bytes
    ) -> None:
        """Should not affect reports when clearing queue."""
        storage.store_report(sample_xml, "report1")
        storage.queue_report(sample_xml, "queued1")

        storage.clear_queue()

        assert "report1" in storage.list_reports()
        assert storage.list_queued_reports() == []


# =============================================================================
# Atomic write tests
# =============================================================================


class TestAtomicWrites:
    """Tests for atomic write behavior."""

    @pytest.fixture
    def storage(self, tmp_path: Path) -> ReportStorage:
        """Create a ReportStorage instance for testing."""
        return ReportStorage(tmp_path)

    def test_atomic_write_no_partial_file(
        self, storage: ReportStorage, tmp_path: Path
    ) -> None:
        """Atomic write should not leave partial files on error."""
        # Verify no temp files exist before
        temp_files_before = list(tmp_path.glob(".tmp_*"))
        assert len(temp_files_before) == 0

        # Write a file successfully
        storage.store_report(b"content", "test123")

        # Verify no temp files exist after
        temp_files_after = list(tmp_path.rglob(".tmp_*"))
        assert len(temp_files_after) == 0

    def test_write_error_raises_storage_write_error(self, tmp_path: Path) -> None:
        """Should raise StorageWriteError on write failure."""
        storage = ReportStorage(tmp_path)

        # Make reports directory read-only to trigger write error
        reports_dir = tmp_path / "reports"
        original_mode = reports_dir.stat().st_mode

        try:
            reports_dir.chmod(0o444)

            with pytest.raises(StorageWriteError):
                storage.store_report(b"content", "test123")
        finally:
            # Restore permissions
            reports_dir.chmod(original_mode)


# =============================================================================
# Module exports tests
# =============================================================================


class TestModuleExports:
    """Tests for module exports."""

    def test_reportstorage_exported(self) -> None:
        """ReportStorage should be exported from juxlib.storage."""
        from juxlib.storage import ReportStorage

        assert ReportStorage is not None

    def test_get_default_storage_path_exported(self) -> None:
        """get_default_storage_path should be exported from juxlib.storage."""
        from juxlib.storage import get_default_storage_path

        assert get_default_storage_path is not None

    def test_all_contains_expected_exports(self) -> None:
        """__all__ should contain expected exports."""
        import juxlib.storage

        assert "ReportStorage" in juxlib.storage.__all__
        assert "get_default_storage_path" in juxlib.storage.__all__
