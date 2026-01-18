# Sprint 3 Plan

**Target Version**: v0.3.0
**Duration**: 2026-02-15 - 2026-03-01 (2 weeks)
**Status**: 📋 Planned

## Sprint Goal

Complete the API client module and validate full integration with pytest-jux and behave-jux consumers.

## Story Points Summary

| Category | Points |
|----------|--------|
| Total Planned | 18 |
| Completed | 0 |
| In Progress | 0 |
| Remaining | 18 |

## User Stories

### Story 3.1: Jux API Client

**Points**: 8 | **Priority**: High | **Status**: 📋 Planned

**User Story**:
> As a library consumer, I want an HTTP client for Jux servers so that signed reports can be published with proper authentication and retry handling.

**Acceptance Criteria**:
- [ ] JuxAPIClient class with configurable base URL and timeout
- [ ] Bearer token authentication for remote servers
- [ ] Localhost bypass (no auth for 127.0.0.1, ::1, localhost)
- [ ] publish_report() method accepting signed XML string
- [ ] Exponential backoff retry (1s, 2s, 4s) on server errors
- [ ] Automatic retry on 500, 502, 503, 504 errors
- [ ] Configurable max_retries (default 3)
- [ ] Pydantic models: TestRun, PublishResponse
- [ ] Connection pooling with session management
- [ ] Enhanced error messages with server response details
- [ ] >85% test coverage with mocked responses

**Technical Notes**:
- Extract from `pytest-jux/pytest_jux/api_client.py` (190 lines)
- API endpoint: POST /api/v1/junit/submit
- Content-Type: application/xml
- Response: JSON with test_run details

**Files to Create**:
- `src/juxlib/api/models.py`
- `src/juxlib/api/client.py`
- `src/juxlib/api/__init__.py` (update exports)
- `tests/unit/test_api_client.py`

**Source Reference**:
- `/Users/gm/Projects/jux-tools/pytest-jux/pytest_jux/api_client.py`

---

### Story 3.2: pytest-jux Integration

**Points**: 5 | **Priority**: High | **Status**: 📋 Planned

**User Story**:
> As a pytest-jux maintainer, I want to migrate pytest-jux to use py-juxlib so that code duplication is eliminated.

**Acceptance Criteria**:
- [ ] pytest-jux imports juxlib modules instead of local implementations
- [ ] All existing pytest-jux tests pass
- [ ] No regression in pytest-jux functionality
- [ ] pytest-jux version bumped with juxlib dependency
- [ ] Migration documented in pytest-jux CHANGELOG

**Technical Notes**:
- Update pytest-jux pyproject.toml to depend on py-juxlib
- Replace imports: `from pytest_jux.metadata import ...` → `from juxlib.metadata import ...`
- Verify CLI commands still work
- Run full pytest-jux test suite

**Files to Modify** (in pytest-jux):
- `pyproject.toml` (add juxlib dependency)
- `pytest_jux/plugin.py` (update imports)
- `pytest_jux/commands/*.py` (update imports)

---

### Story 3.3: behave-jux Integration

**Points**: 5 | **Priority**: High | **Status**: 📋 Planned

**User Story**:
> As a behave-jux maintainer, I want to integrate py-juxlib so that behave-jux gains signing and publishing capabilities.

**Acceptance Criteria**:
- [ ] behave-jux imports juxlib.metadata for Git/CI detection
- [ ] behave-jux can optionally sign reports using juxlib.signing
- [ ] behave-jux can optionally publish reports using juxlib.api
- [ ] Existing behave-jux tests pass
- [ ] New integration tests for signing/publishing
- [ ] behave-jux version bumped with juxlib dependency

**Technical Notes**:
- Replace local Git/CI detection with juxlib.metadata
- Add optional signing configuration
- Add optional publishing configuration
- Maintain backward compatibility (signing/publishing off by default)

**Files to Modify** (in behave-jux):
- `pyproject.toml` (add juxlib dependency)
- `src/behave_jux/reporter.py` (update imports, add signing/publishing)

---

## Technical Tasks

- [ ] **Task 1**: End-to-end integration test (sign → store → publish) (2 pts)
- [ ] **Task 2**: Update CHANGELOG.md with Sprint 3 changes (1 pt)
- [ ] **Task 3**: Prepare v0.3.0 release notes (1 pt)

## AI Collaboration Strategy

| Task Type | AI Role | Human Role |
|-----------|---------|------------|
| Code extraction | Lead | Review |
| Integration testing | Assist | Validate real-world scenarios |
| Cross-project changes | Assist | Coordinate and approve |
| Release preparation | Assist | Final approval |

**AI Delegation Guidelines for This Sprint**:
- **AI leads**: API client extraction, test mocking
- **Human leads**: Cross-project coordination, release decisions
- **Collaborative**: Integration testing, backward compatibility

## Dependencies

### External Dependencies
- [ ] Sprint 1 complete (errors, metadata, signing)
- [ ] Sprint 2 complete (config, storage)
- [ ] Access to pytest-jux repository
- [ ] Access to behave-jux repository

### Internal Dependencies
- Story 3.2 and 3.3 depend on Story 3.1 completion
- Stories 3.2 and 3.3 can run in parallel after 3.1

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| API compatibility issues | Medium | High | Maintain similar interfaces |
| Cross-project coordination | Medium | Medium | Clear communication, atomic changes |
| Network test flakiness | Medium | Low | Mock all HTTP calls |
| Breaking changes in consumers | Low | High | Comprehensive test coverage |

## Definition of Done

Sprint is complete when:
- [ ] All user stories meet acceptance criteria
- [ ] All tests passing (unit + integration)
- [ ] pytest-jux migrated and tests passing
- [ ] behave-jux integrated and tests passing
- [ ] >85% test coverage
- [ ] Type hints complete (mypy strict passing)
- [ ] CHANGELOG.md updated for all three projects
- [ ] v0.3.0 release ready

## Notes

**Sprint 3 Completes the Library**:
- All 6 modules implemented (errors, metadata, signing, config, storage, api)
- Real-world validation through pytest-jux migration
- behave-jux gains full Jux integration capabilities
- Library ready for PyPI publication consideration
