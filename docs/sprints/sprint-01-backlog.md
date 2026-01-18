# Sprint 1 Backlog

**Target Version**: v0.1.0
**Status**: ✅ Complete
**Dates**: 2026-01-18 - 2026-01-18 (1 day)

## Sprint Goal

Extract foundational modules from pytest-jux to establish py-juxlib as a working shared library with error handling, metadata detection, and XML signing capabilities.

## Story Points Summary

| Category | Points |
|----------|--------|
| Total Planned | 21 |
| Completed | 21 |
| Deferred | 0 |

## Backlog Items

### Story 1.1: Error Handling Framework

- **Points**: 5
- **Priority**: High
- **Status**: ✅ Complete

**User Story**: As a library consumer, I want consistent, user-friendly error handling so that I can provide helpful feedback to my users when things go wrong.

**Acceptance Criteria**:
- [x] ErrorCode enum with categorized error codes (1xx-6xx)
- [x] JuxError base exception with message, code, suggestions, details
- [x] Specialized exceptions: FileError, KeyError, XMLError, ConfigError, APIError
- [x] Rich terminal formatting for error display
- [x] format_error() and print_error() methods
- [x] 88% test coverage for error module (38 tests)

**Deliverables**:
- `src/juxlib/errors/codes.py` - Error code enumeration
- `src/juxlib/errors/exceptions.py` - Exception classes
- `src/juxlib/errors/__init__.py` - Module exports
- `tests/unit/test_errors.py` - 38 unit tests

---

### Story 1.2: Environment Metadata Detection

- **Points**: 8
- **Priority**: High
- **Status**: ✅ Complete

**User Story**: As a test framework integrator, I want to capture comprehensive environment metadata so that test reports include Git, CI/CD, and runtime context.

**Acceptance Criteria**:
- [x] EnvironmentMetadata dataclass with all fields
- [x] Git detection: commit, branch, status (clean/dirty), remote URL
- [x] CI detection: GitHub Actions, GitLab CI, Jenkins, CircleCI, Travis, Azure
- [x] Runtime: hostname, platform, Python version, project name
- [x] Project name detection: git remote > pyproject.toml > env var > directory
- [x] Credential sanitization for git URLs
- [x] Safe subprocess handling with timeouts
- [x] 86% test coverage (37 tests)

**Deliverables**:
- `src/juxlib/metadata/models.py` - EnvironmentMetadata dataclass
- `src/juxlib/metadata/git.py` - Git info detection
- `src/juxlib/metadata/ci.py` - CI provider detection
- `src/juxlib/metadata/project.py` - Project name detection
- `src/juxlib/metadata/detection.py` - Main capture function
- `src/juxlib/metadata/__init__.py` - Module exports
- `tests/unit/test_metadata.py` - 37 unit tests

---

### Story 1.3: XML Signing and Canonicalization

- **Points**: 8
- **Priority**: High
- **Status**: ✅ Complete

**User Story**: As a test framework integrator, I want to sign JUnit XML reports with XMLDSig so that report authenticity can be verified by the Jux server.

**Acceptance Criteria**:
- [x] load_xml() from file, string, or bytes
- [x] canonicalize_xml() using C14N algorithm
- [x] compute_canonical_hash() with configurable algorithm
- [x] load_private_key() from file, PEM string, or bytes
- [x] sign_xml() with automatic RSA/ECDSA detection
- [x] verify_signature() with embedded or external certificate
- [x] Support for RSA-SHA256 and ECDSA-SHA256
- [x] 87% test coverage with fixture XML files (47 tests)

**Deliverables**:
- `src/juxlib/signing/xml.py` - XML loading and canonicalization
- `src/juxlib/signing/keys.py` - Key and certificate loading
- `src/juxlib/signing/signer.py` - XML signing
- `src/juxlib/signing/verifier.py` - Signature verification
- `src/juxlib/signing/__init__.py` - Module exports
- `tests/unit/test_signing.py` - 47 unit tests
- `tests/fixtures/` - Test certificates and sample XML

---

## Technical Tasks

- [x] **Task 1**: Create test fixtures directory structure (1 pt)
- [x] **Task 2**: Add test key pair for signing tests (1 pt) - RSA and ECDSA keys/certs
- [x] **Task 3**: Update CHANGELOG.md with Sprint 1 changes (1 pt)

## Definition of Done

- [x] All acceptance criteria met
- [x] All tests passing (122 tests)
- [x] Code reviewed (pre-commit hooks passing)
- [x] >85% test coverage (87% achieved)
- [x] Type hints complete (mypy strict passing)
- [x] Module docstrings complete
- [x] CHANGELOG.md updated
- [x] No critical bugs outstanding
