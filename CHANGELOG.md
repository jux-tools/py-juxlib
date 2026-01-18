# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial project structure with Diátaxis documentation framework
- Foundation ADRs (0001, 0002, 0003, 0004)
- Sprint planning (Sprint 1, 2, 3)

#### Sprint 1: Core Modules (v0.1.0)

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

[Unreleased]: https://github.com/jrjsmrtn/py-juxlib/compare/v0.1.0...HEAD
