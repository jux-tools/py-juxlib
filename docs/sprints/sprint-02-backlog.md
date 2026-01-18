# Sprint 2 Backlog

**Target Version**: v0.2.0
**Status**: ✅ Complete
**Dates**: 2026-01-18 - 2026-01-18 (1 day)

## Sprint Goal

Complete the configuration and storage modules to enable offline-capable test report management with multi-source configuration.

## Story Points Summary

| Category | Points |
|----------|--------|
| Total Planned | 19 |
| Completed | 19 |
| Deferred | 0 |

## Backlog Items

### Epic: Offline-Capable Report Management

#### Story 2.1: Configuration Management
- **Points**: 8
- **Priority**: High
- **Status**: ✅ Complete

**User Story**: As a library consumer, I want flexible configuration management so that settings can come from files, environment variables, or code with clear precedence.

**Acceptance Criteria**:
- [x] StorageMode enum (local, api, both, cache)
- [x] ConfigSchema with type definitions and defaults
- [x] ConfigurationManager with get/set/validate methods
- [x] Multi-source loading: explicit > CLI > env vars > file > defaults
- [x] Environment variable support (JUX_* prefix)
- [x] INI file parsing with XDG-compliant locations
- [x] TOML support via pyproject.toml [tool.jux] section
- [x] Type coercion (bool, int, enum, path expansion)
- [x] Source tracking for debugging
- [x] Dependency validation between settings
- [x] >85% test coverage (achieved: 90%)

**Tests**: 51 unit tests - **ALL PASSING** ✅

---

#### Story 2.2: Local Filesystem Storage
- **Points**: 8
- **Priority**: High
- **Status**: ✅ Complete

**User Story**: As a library consumer, I want local storage for signed reports so that reports can be cached, deduplicated, and queued for later publishing.

**Acceptance Criteria**:
- [x] get_default_storage_path() with XDG compliance
- [x] Platform-appropriate paths (macOS ~/Library, Linux ~/.local/share)
- [x] ReportStorage class with full CRUD operations
- [x] store_report() with atomic writes (temp-then-rename)
- [x] get_report() by canonical hash
- [x] Deduplication via canonical hash identifiers
- [x] Offline queue: queue_report(), list_queued_reports(), dequeue_report()
- [x] Storage statistics: count, size, oldest report
- [x] report_exists() for duplicate checking
- [x] >85% test coverage (achieved: 86%)

**Tests**: 55 unit tests - **ALL PASSING** ✅

---

### Technical Tasks

#### Task 1: Integration Tests
- **Points**: 2
- **Status**: ✅ Complete

**Description**: Add integration tests for config + storage together

**Tests**: 16 integration tests - **ALL PASSING** ✅

---

#### Task 2: Update CHANGELOG
- **Points**: 1
- **Status**: ✅ Complete

**Description**: Update CHANGELOG.md with Sprint 2 changes

---

## Definition of Done

- [x] All acceptance criteria met
- [x] Code reviewed (AI-assisted)
- [x] Tests passing (unit + integration): 247 total
- [x] Test coverage >85%: config 90%, storage 86%
- [x] Type hints complete (mypy passing)
- [x] Documentation updated (CHANGELOG)
- [x] No critical bugs outstanding
