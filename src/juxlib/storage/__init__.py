# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""
Local filesystem storage with offline queue support.

This module provides XDG-compliant local storage for signed test reports,
with support for offline queuing when the API server is unavailable.

Features:
- Platform-appropriate default paths (XDG on Linux, ~/Library on macOS)
- Atomic file writes (temp-then-rename pattern)
- Deduplication via canonical hash identifiers
- Offline queue for unreachable servers
- Storage statistics and management

Directory structure:
    ~/.local/share/jux/
    ├── reports/       # Published reports
    │   ├── hash1.xml
    │   └── hash2.xml
    └── queue/         # Queued (unpublished) reports
        ├── hash3.xml
        └── hash4.xml

Example usage:

    >>> from juxlib.storage import ReportStorage, get_default_storage_path
    >>>
    >>> storage = ReportStorage(get_default_storage_path())
    >>> storage.store_report(xml_bytes, canonical_hash)
    >>>
    >>> # Check for queued reports
    >>> queued = storage.list_queued_reports()
    >>> for hash in queued:
    ...     xml = storage.get_report(hash)
    ...     # Try to publish...
    ...     storage.dequeue_report(hash)
"""

# Public API will be exported here once implemented
# from .filesystem import ReportStorage, get_default_storage_path

__all__: list[str] = []
