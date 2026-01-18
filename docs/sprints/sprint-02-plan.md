# Sprint 2 Plan

**Target Version**: v0.2.0
**Duration**: 2026-02-01 - 2026-02-15 (2 weeks)
**Status**: 📋 Planned

## Sprint Goal

Complete the configuration and storage modules to enable offline-capable test report management with multi-source configuration.

## Story Points Summary

| Category | Points |
|----------|--------|
| Total Planned | 16 |
| Completed | 0 |
| In Progress | 0 |
| Remaining | 16 |

## User Stories

### Story 2.1: Configuration Management

**Points**: 8 | **Priority**: High | **Status**: 📋 Planned

**User Story**:
> As a library consumer, I want flexible configuration management so that settings can come from files, environment variables, or code with clear precedence.

**Acceptance Criteria**:
- [ ] StorageMode enum (local, api, both, cache)
- [ ] ConfigSchema with type definitions and defaults
- [ ] ConfigurationManager with get/set/validate methods
- [ ] Multi-source loading: explicit > CLI > env vars > file > defaults
- [ ] Environment variable support (JUX_* prefix)
- [ ] INI file parsing with XDG-compliant locations
- [ ] TOML support via pyproject.toml [tool.jux] section
- [ ] Type coercion (bool, int, enum, path expansion)
- [ ] Source tracking for debugging
- [ ] Dependency validation between settings
- [ ] >85% test coverage

**Technical Notes**:
- Extract from `pytest-jux/pytest_jux/config.py` (424 lines)
- Remove pytest-specific options
- Keep generic Jux configuration keys
- XDG paths: ~/.config/jux/config.ini, ~/.local/share/jux/

**Files to Create**:
- `src/juxlib/config/schema.py`
- `src/juxlib/config/manager.py`
- `src/juxlib/config/__init__.py` (update exports)
- `tests/unit/test_config.py`

**Source Reference**:
- `/Users/gm/Projects/jux-tools/pytest-jux/pytest_jux/config.py`

---

### Story 2.2: Local Filesystem Storage

**Points**: 8 | **Priority**: High | **Status**: 📋 Planned

**User Story**:
> As a library consumer, I want local storage for signed reports so that reports can be cached, deduplicated, and queued for later publishing.

**Acceptance Criteria**:
- [ ] get_default_storage_path() with XDG compliance
- [ ] Platform-appropriate paths (macOS ~/Library, Linux ~/.local/share)
- [ ] ReportStorage class with full CRUD operations
- [ ] store_report() with atomic writes (temp-then-rename)
- [ ] get_report() by canonical hash
- [ ] Deduplication via canonical hash identifiers
- [ ] Offline queue: queue_report(), list_queued_reports(), dequeue_report()
- [ ] Storage statistics: count, size, oldest report
- [ ] report_exists() for duplicate checking
- [ ] >85% test coverage

**Technical Notes**:
- Extract from `pytest-jux/pytest_jux/storage.py` (290 lines)
- Directory structure: reports/ (published), queue/ (pending)
- Atomic writes prevent corruption from interrupted operations
- Hash-based naming enables content-addressable storage

**Files to Create**:
- `src/juxlib/storage/filesystem.py`
- `src/juxlib/storage/__init__.py` (update exports)
- `tests/unit/test_storage.py`

**Source Reference**:
- `/Users/gm/Projects/jux-tools/pytest-jux/pytest_jux/storage.py`

---

## Technical Tasks

- [ ] **Task 1**: Add integration tests for config + storage together (2 pts)
- [ ] **Task 2**: Update CHANGELOG.md with Sprint 2 changes (1 pt)

## AI Collaboration Strategy

| Task Type | AI Role | Human Role |
|-----------|---------|------------|
| Code extraction | Lead | Review |
| Test generation | Lead | Validate |
| Path handling | Assist | Verify platform behavior |
| Documentation | Lead | Review |

**AI Delegation Guidelines for This Sprint**:
- **AI leads**: Code extraction, test generation, docstrings
- **Human leads**: XDG compliance verification, platform testing
- **Collaborative**: Edge case handling for file operations

## Dependencies

### External Dependencies
- [x] pytest-jux source code available
- [ ] Sprint 1 complete (errors module for exception handling)

### Internal Dependencies
- Story 2.2 (storage) may use Story 2.1 (config) for default paths
- Both stories can start in parallel

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Platform-specific path issues | Medium | Medium | Test on macOS and Linux |
| File permission errors in tests | Low | Low | Use tmp directories |
| Config file format compatibility | Low | Medium | Support both INI and TOML |

## Definition of Done

Sprint is complete when:
- [ ] All user stories meet acceptance criteria
- [ ] All tests passing (unit + integration)
- [ ] >85% test coverage
- [ ] Type hints complete (mypy strict passing)
- [ ] Module docstrings complete
- [ ] CHANGELOG.md updated
- [ ] No critical bugs outstanding

## Notes

**Sprint 2 Focus**:
- Configuration enables consistent settings across pytest-jux and behave-jux
- Storage enables offline operation and report deduplication
- Both modules have no network dependencies (API client in Sprint 3)
