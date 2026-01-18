# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""Integration tests for config and storage modules working together.

These tests verify that the configuration and storage modules integrate
correctly, particularly around path configuration and storage mode handling.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from juxlib.config import ConfigurationManager, StorageMode, get_xdg_data_home
from juxlib.storage import ReportStorage, get_default_storage_path

if TYPE_CHECKING:
    from pathlib import Path


class TestConfigStorageIntegration:
    """Integration tests for config + storage modules."""

    @pytest.fixture
    def config(self) -> ConfigurationManager:
        """Create a fresh ConfigurationManager instance."""
        return ConfigurationManager()

    @pytest.fixture
    def storage(self, tmp_path: Path) -> ReportStorage:
        """Create a ReportStorage with temporary directory."""
        return ReportStorage(tmp_path)

    @pytest.fixture
    def sample_xml(self) -> bytes:
        """Sample XML content for testing."""
        return b'<?xml version="1.0"?><testsuites><testsuite name="test"/></testsuites>'

    def test_storage_uses_config_path(self, tmp_path: Path) -> None:
        """Storage should use path from configuration."""
        config = ConfigurationManager()
        custom_path = tmp_path / "custom_storage"
        config.set("jux_storage_path", custom_path)

        # Create storage with configured path
        storage_path = config.get("jux_storage_path")
        storage = ReportStorage(storage_path)

        assert storage.storage_path == custom_path
        assert storage.storage_path.exists()

    def test_storage_mode_local_stores_report(
        self, tmp_path: Path, sample_xml: bytes
    ) -> None:
        """LOCAL storage mode should store reports locally."""
        config = ConfigurationManager()
        config.set("jux_storage_mode", StorageMode.LOCAL)

        storage = ReportStorage(tmp_path)
        storage.store_report(sample_xml, "test123")

        assert storage.report_exists("test123")
        assert config.get("jux_storage_mode") == StorageMode.LOCAL

    def test_storage_mode_cache_queues_report(
        self, tmp_path: Path, sample_xml: bytes
    ) -> None:
        """CACHE storage mode should queue reports for later publishing."""
        config = ConfigurationManager()
        config.set("jux_storage_mode", StorageMode.CACHE)

        storage = ReportStorage(tmp_path)
        # In CACHE mode, reports are queued first
        storage.queue_report(sample_xml, "test123")

        assert storage.queued_report_exists("test123")
        assert not storage.report_exists("test123")

    def test_cache_mode_dequeue_workflow(
        self, tmp_path: Path, sample_xml: bytes
    ) -> None:
        """CACHE mode workflow: queue -> dequeue -> stored."""
        config = ConfigurationManager()
        config.set("jux_storage_mode", StorageMode.CACHE)

        storage = ReportStorage(tmp_path)

        # 1. Queue report (offline)
        storage.queue_report(sample_xml, "test123")
        assert storage.queued_report_exists("test123")
        assert not storage.report_exists("test123")

        # 2. Dequeue (after publishing succeeds)
        storage.dequeue_report("test123")
        assert storage.report_exists("test123")
        assert not storage.queued_report_exists("test123")

    def test_both_mode_stores_locally_and_queues(
        self, tmp_path: Path, sample_xml: bytes
    ) -> None:
        """BOTH mode should store locally immediately."""
        config = ConfigurationManager()
        config.set("jux_storage_mode", StorageMode.BOTH)

        storage = ReportStorage(tmp_path)
        # In BOTH mode, store locally immediately
        storage.store_report(sample_xml, "test123")

        assert storage.report_exists("test123")

    def test_config_env_storage_path(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Configuration should load storage path from environment."""
        custom_path = tmp_path / "env_storage"
        monkeypatch.setenv("JUX_STORAGE_PATH", str(custom_path))

        config = ConfigurationManager()
        config.load_from_env()

        storage_path = config.get("jux_storage_path")
        assert storage_path == custom_path

    def test_config_env_storage_mode(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Configuration should load storage mode from environment."""
        monkeypatch.setenv("JUX_STORAGE_MODE", "cache")

        config = ConfigurationManager()
        config.load_from_env()

        assert config.get("jux_storage_mode") == StorageMode.CACHE

    def test_xdg_paths_consistent(self) -> None:
        """XDG paths should be consistent between config and storage."""
        # Config's XDG data home
        config_xdg_data = get_xdg_data_home()

        # Storage's default path
        storage_default = get_default_storage_path()

        # Storage default should be under XDG data home
        # (both should use "jux" subdirectory)
        assert storage_default.name == "jux"
        # On macOS, both should use ~/Library/Application Support
        # On Linux, both should use ~/.local/share or XDG_DATA_HOME
        assert str(config_xdg_data) in str(storage_default.parent)

    def test_storage_stats_after_operations(
        self, tmp_path: Path, sample_xml: bytes
    ) -> None:
        """Storage stats should reflect operations."""
        storage = ReportStorage(tmp_path)

        # Initial stats
        stats = storage.get_stats()
        assert stats["total_reports"] == 0
        assert stats["queued_reports"] == 0

        # Store reports
        storage.store_report(sample_xml, "report1")
        storage.store_report(sample_xml, "report2")
        storage.queue_report(sample_xml, "queued1")

        stats = storage.get_stats()
        assert stats["total_reports"] == 2
        assert stats["queued_reports"] == 1
        assert stats["total_size"] > 0

    def test_storage_deduplication(self, tmp_path: Path, sample_xml: bytes) -> None:
        """Reports with same hash should be deduplicated."""
        storage = ReportStorage(tmp_path)

        # Store same content with same hash twice
        storage.store_report(sample_xml, "same_hash")
        storage.store_report(sample_xml, "same_hash")

        # Should only have one report
        reports = storage.list_reports()
        assert reports.count("same_hash") == 1

    def test_config_toml_with_storage(self, tmp_path: Path) -> None:
        """Configuration from TOML should work with storage."""
        # Create a pyproject.toml with jux config
        pyproject = tmp_path / "pyproject.toml"
        storage_path = tmp_path / "toml_storage"
        pyproject.write_text(f"""
[tool.jux]
enabled = true
storage_mode = "local"
storage_path = "{storage_path}"
""")

        config = ConfigurationManager()
        config.load_from_toml(pyproject)

        assert config.get("jux_enabled") is True
        assert config.get("jux_storage_mode") == StorageMode.LOCAL
        assert config.get("jux_storage_path") == storage_path

    def test_config_ini_with_storage(self, tmp_path: Path) -> None:
        """Configuration from INI should work with storage."""
        # Create a config.ini with jux config
        config_file = tmp_path / "config.ini"
        storage_path = tmp_path / "ini_storage"
        config_file.write_text(f"""
[jux]
enabled = true
storage_mode = cache
storage_path = {storage_path}
""")

        config = ConfigurationManager()
        config.load_from_file(config_file)

        assert config.get("jux_enabled") is True
        assert config.get("jux_storage_mode") == StorageMode.CACHE
        assert config.get("jux_storage_path") == storage_path


class TestStorageModeWorkflows:
    """Tests for complete storage mode workflows."""

    @pytest.fixture
    def storage(self, tmp_path: Path) -> ReportStorage:
        """Create a ReportStorage with temporary directory."""
        return ReportStorage(tmp_path)

    @pytest.fixture
    def sample_xml(self) -> bytes:
        """Sample XML content for testing."""
        return b'<?xml version="1.0"?><testsuites/>'

    def test_local_mode_workflow(
        self, storage: ReportStorage, sample_xml: bytes
    ) -> None:
        """LOCAL mode: store locally only."""
        # Store report
        storage.store_report(sample_xml, "local_report")

        # Verify stored
        assert storage.report_exists("local_report")
        content = storage.get_report("local_report")
        assert content == sample_xml

    def test_cache_mode_complete_workflow(
        self, storage: ReportStorage, sample_xml: bytes
    ) -> None:
        """CACHE mode: queue -> check -> dequeue workflow."""
        # 1. Queue reports while offline
        storage.queue_report(sample_xml, "cached1")
        storage.queue_report(sample_xml, "cached2")

        # 2. List queued reports
        queued = storage.list_queued_reports()
        assert len(queued) == 2

        # 3. Get queued content for publishing
        content = storage.get_queued_report("cached1")
        assert content == sample_xml

        # 4. Dequeue after successful publish
        storage.dequeue_report("cached1")

        # 5. Verify state
        assert storage.report_exists("cached1")
        assert not storage.queued_report_exists("cached1")
        assert storage.queued_report_exists("cached2")

    def test_both_mode_workflow(
        self, storage: ReportStorage, sample_xml: bytes
    ) -> None:
        """BOTH mode: store locally AND prepare for API."""
        # Store locally
        storage.store_report(sample_xml, "both_report")

        # Verify both stored and retrievable
        assert storage.report_exists("both_report")
        content = storage.get_report("both_report")
        assert content == sample_xml

    def test_cleanup_workflow(self, storage: ReportStorage, sample_xml: bytes) -> None:
        """Cleanup workflow: clear old reports and queue."""
        # Add reports and queue
        storage.store_report(sample_xml, "old1")
        storage.store_report(sample_xml, "old2")
        storage.queue_report(sample_xml, "queued1")

        # Clear reports
        cleared = storage.clear_reports()
        assert cleared == 2
        assert storage.list_reports() == []
        assert storage.queued_report_exists("queued1")

        # Clear queue
        cleared = storage.clear_queue()
        assert cleared == 1
        assert storage.list_queued_reports() == []
