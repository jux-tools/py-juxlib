# Sprint 1 Plan

**Target Version**: v0.1.0
**Duration**: 2026-01-18 - 2026-02-01 (2 weeks)
**Status**: 🔄 In Progress

## Sprint Goal

Extract foundational modules from pytest-jux to establish py-juxlib as a working shared library with error handling, metadata detection, and XML signing capabilities.

## Story Points Summary

| Category | Points |
|----------|--------|
| Total Planned | 21 |
| Completed | 13 |
| In Progress | 0 |
| Remaining | 8 |

## User Stories

### Story 1.1: Error Handling Framework

**Points**: 5 | **Priority**: High | **Status**: ✅ Complete

**User Story**:
> As a library consumer, I want consistent, user-friendly error handling so that I can provide helpful feedback to my users when things go wrong.

**Acceptance Criteria**:
- [x] ErrorCode enum with categorized error codes (1xx-6xx)
- [x] JuxError base exception with message, code, suggestions, details
- [x] Specialized exceptions: FileError, KeyError, XMLError, ConfigError, APIError
- [x] Rich terminal formatting for error display
- [x] format_error() and print_error() methods
- [x] 88% test coverage for error module (38 tests)

**Technical Notes**:
- Extract from `pytest-jux/pytest_jux/errors.py` (490 lines)
- Adapt for library use (remove CLI-specific code)
- Ensure Rich is optional dependency for formatting

**Files to Create**:
- `src/juxlib/errors/codes.py`
- `src/juxlib/errors/exceptions.py`
- `src/juxlib/errors/__init__.py` (update exports)
- `tests/unit/test_errors.py`

**Source Reference**:
- `/Users/gm/Projects/jux-tools/pytest-jux/pytest_jux/errors.py`

---

### Story 1.2: Environment Metadata Detection

**Points**: 8 | **Priority**: High | **Status**: ✅ Complete

**User Story**:
> As a test framework integrator, I want to capture comprehensive environment metadata so that test reports include Git, CI/CD, and runtime context.

**Acceptance Criteria**:
- [x] EnvironmentMetadata dataclass with all fields
- [x] Git detection: commit, branch, status (clean/dirty), remote URL
- [x] CI detection: GitHub Actions, GitLab CI, Jenkins, CircleCI, Travis, Azure
- [x] Runtime: hostname, platform, Python version, project name
- [x] Project name detection: git remote > pyproject.toml > env var > directory
- [x] Credential sanitization for git URLs
- [x] Safe subprocess handling with timeouts
- [x] 86% test coverage (37 tests)

**Technical Notes**:
- Extract from `pytest-jux/pytest_jux/metadata.py` (401 lines)
- Remove pytest-specific version detection
- Add generic "library_version" parameter for consumers
- Test with mocked subprocess and environment

**Files to Create**:
- `src/juxlib/metadata/models.py`
- `src/juxlib/metadata/git.py`
- `src/juxlib/metadata/ci.py`
- `src/juxlib/metadata/detection.py`
- `src/juxlib/metadata/__init__.py` (update exports)
- `tests/unit/test_metadata.py`

**Source Reference**:
- `/Users/gm/Projects/jux-tools/pytest-jux/pytest_jux/metadata.py`

---

### Story 1.3: XML Signing and Canonicalization

**Points**: 8 | **Priority**: High | **Status**: 📋 Planned

**User Story**:
> As a test framework integrator, I want to sign JUnit XML reports with XMLDSig so that report authenticity can be verified by the Jux server.

**Acceptance Criteria**:
- [ ] load_xml() from file, string, or bytes
- [ ] canonicalize_xml() using C14N algorithm
- [ ] compute_canonical_hash() with configurable algorithm
- [ ] load_private_key() from file, PEM string, or bytes
- [ ] sign_xml() with automatic RSA/ECDSA detection
- [ ] verify_signature() with embedded or external certificate
- [ ] Support for RSA-SHA256 and ECDSA-SHA256
- [ ] >85% test coverage with fixture XML files

**Technical Notes**:
- Extract from `pytest-jux/pytest_jux/signer.py` (155 lines)
- Extract from `pytest-jux/pytest_jux/verifier.py` (87 lines)
- Extract from `pytest-jux/pytest_jux/canonicalizer.py` (119 lines)
- Use lxml and signxml libraries
- Create test fixtures from junit-xml-test-fixtures

**Files to Create**:
- `src/juxlib/signing/canonicalizer.py`
- `src/juxlib/signing/signer.py`
- `src/juxlib/signing/verifier.py`
- `src/juxlib/signing/__init__.py` (update exports)
- `tests/unit/test_signing.py`
- `tests/fixtures/` (sample XML and keys)

**Source References**:
- `/Users/gm/Projects/jux-tools/pytest-jux/pytest_jux/signer.py`
- `/Users/gm/Projects/jux-tools/pytest-jux/pytest_jux/verifier.py`
- `/Users/gm/Projects/jux-tools/pytest-jux/pytest_jux/canonicalizer.py`

---

## Technical Tasks

Tasks not tied to specific user stories:

- [ ] **Task 1**: Create test fixtures directory structure (1 pt)
- [ ] **Task 2**: Add test key pair for signing tests (1 pt)
- [ ] **Task 3**: Update CHANGELOG.md with Sprint 1 changes (1 pt)

## AI Collaboration Strategy

| Task Type | AI Role | Human Role |
|-----------|---------|------------|
| Code extraction | Lead | Review for correctness |
| Test generation | Lead | Validate coverage |
| API design | Assist | Final approval |
| Error messages | Lead | Review for clarity |
| Documentation | Lead | Review |

**AI Delegation Guidelines for This Sprint**:
- **AI leads**: Code extraction from pytest-jux, test generation, docstrings
- **Human leads**: API design decisions, public interface approval
- **Collaborative**: Edge case handling, error message wording

## Dependencies

### External Dependencies
- [x] pytest-jux source code available for reference
- [x] lxml, cryptography, signxml packages

### Internal Dependencies
- Story 1.2 and 1.3 can use Story 1.1 errors (but not required)
- All stories are independent and can be developed in parallel

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| API compatibility issues with pytest-jux | Medium | High | Maintain similar interfaces, test integration |
| Test key management for CI | Low | Medium | Generate ephemeral keys in test fixtures |
| signxml API changes | Low | Low | Pin version, test against specific version |

## Definition of Done

Sprint is complete when:
- [ ] All user stories meet acceptance criteria
- [ ] All tests passing (unit)
- [ ] Code reviewed (pre-commit hooks passing)
- [ ] >85% test coverage
- [ ] Type hints complete (mypy strict passing)
- [ ] Module docstrings complete
- [ ] CHANGELOG.md updated
- [ ] No critical bugs outstanding

## Daily Standup Template

### Day 1 (2026-01-18)
- **Completed**: Project bootstrap, ADRs, pre-commit hooks, Sprint 1 planning
- **In Progress**: Story 1.1, Story 1.2
- **Blockers**: None
- **AI Collaboration Notes**: AI led bootstrap, human approved structure

### Day 1 (continued)
- **Completed**: Story 1.1 (Error Handling Framework - 38 tests, 88% coverage)
- **Completed**: Story 1.2 (Environment Metadata Detection - 37 tests, 86% coverage)
- **In Progress**: Story 1.3 (XML Signing)
- **Blockers**: None
- **AI Collaboration Notes**: AI extracted and adapted code from pytest-jux, replaced pytest-specific fields with generic tool_versions dict

## Notes

**Sprint 1 Scope Decisions**:
- Configuration manager (juxlib.config) → Sprint 2
- Storage (juxlib.storage) → Sprint 2
- API client (juxlib.api) → Sprint 3
- Focus on foundational modules that enable pytest-jux/behave-jux integration

**Code Extraction Strategy**:
1. Copy source from pytest-jux
2. Remove pytest-specific code
3. Adapt for library use
4. Add comprehensive tests
5. Update type hints for strict mypy
