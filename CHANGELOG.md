# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.1] - 2026-01-19

### Changed

- **BREAKING**: Remove backward compatibility `test_run` property from `PublishResponse`
  - Removed `TestRunRef` class
  - All client code should use `response.test_run_id` directly instead of `response.test_run.id`
  - This is acceptable during 0.x alpha phase

## [0.2.0] - 2026-01-18

### Added

- **juxlib.config** - Configuration management with multi-source loading
  - `ConfigSchema` with type definitions, defaults, and validation rules
  - `StorageMode` enum (LOCAL, API, BOTH, CACHE)
  - `ConfigurationManager` with get/set/validate methods
  - Multi-source precedence: explicit > CLI > env vars > file > defaults
  - Environment variable support (JUX_* prefix)
  - INI file parsing with XDG-compliant locations
  - TOML support via pyproject.toml [tool.jux] section
  - Type coercion (bool, int, enum, path expansion)
  - Source tracking for debugging
  - Dependency validation between settings
  - 51 tests, 90% coverage

- **juxlib.storage** - Local filesystem storage with offline queue support
  - `ReportStorage` class with full CRUD operations
  - Platform-appropriate paths (macOS ~/Library, Linux XDG)
  - Atomic writes using temp-then-rename pattern
  - Offline queue: `queue_report()`, `list_queued_reports()`, `dequeue_report()`
  - Storage statistics: count, size, oldest report
  - Deduplication via canonical hash identifiers
  - 55 tests, 86% coverage

- **Integration tests** for config + storage modules (16 tests)

- **New error types** in juxlib.errors:
  - `StorageWriteError` for storage write failures
  - `QueuedReportNotFoundError` for missing queued reports

### Technical Details

- **Sprint**: 2
- **Story Points**: 19
- **Unit Tests**: 122 new (247 total)
- **Integration Tests**: 16 new
- **Test Coverage**: 86-90%

## [0.1.0] - 2026-01-18

### Added

- Initial project structure with Diátaxis documentation framework
- Foundation ADRs (0001, 0002, 0003, 0004)
- Sprint planning (Sprint 1, 2, 3)

- **juxlib.errors** - User-friendly error handling framework
  - `ErrorCode` enum with categorized error codes (1xx-6xx)
  - `JuxError` base exception with message, code, suggestions, details
  - Specialized exceptions: `FileError`, `KeyError`, `XMLError`, `ConfigError`, `APIError`
  - Rich terminal formatting with `format_error()` and `print_error()`
  - 38 tests, 88% coverage

- **juxlib.metadata** - Environment and Git/CI metadata detection
  - `EnvironmentMetadata` dataclass with serialization (to_dict, to_json, from_dict, from_json)
  - Git detection: commit, branch, status (clean/dirty), remote URL with credential sanitization
  - CI provider detection: GitHub Actions, GitLab CI, Jenkins, CircleCI, Travis, Azure Pipelines
  - Project name detection: git remote > pyproject.toml > env var > directory fallback
  - Generic `tool_versions` dict for consumer-specific version tracking
  - 37 tests, 86% coverage

- **juxlib.signing** - XML digital signature creation and verification
  - `load_xml()` from file path, string, or bytes
  - `canonicalize_xml()` using C14N algorithm (exclusive and with-comments options)
  - `compute_canonical_hash()` with configurable algorithm (sha256, sha512, etc.)
  - `load_private_key()` and `load_certificate()` from various sources
  - `sign_xml()` with automatic RSA/ECDSA algorithm detection
  - `verify_signature()`, `verify_signature_strict()`, `verify_with_certificate()`
  - Support for RSA-SHA256 and ECDSA-SHA256 algorithms
  - Test fixtures with certificate generation script
  - 47 tests, 87% coverage

### Technical Details

- **Sprint**: 1
- **Story Points**: 21
- **Unit Tests**: 122 total
- **Test Coverage**: 87%

[Unreleased]: https://github.com/jrjsmrtn/py-juxlib/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/jrjsmrtn/py-juxlib/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/jrjsmrtn/py-juxlib/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/jrjsmrtn/py-juxlib/releases/tag/v0.1.0
