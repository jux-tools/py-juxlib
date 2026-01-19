# Sprint 3 Plan

**Target Version**: v0.3.0
**Duration**: 2026-02-15 - 2026-03-01 (2 weeks)
**Status**: 📋 Planned

## Sprint Goal

Complete the API client module and validate full integration with pytest-jux and behave-jux consumers.

## Story Points Summary

| Category | Points |
|----------|--------|
| Total Planned | 8 |
| Completed | 8 |
| Moved | 10 |
| In Progress | 0 |
| Remaining | 0 |

**Note**:
- Story 3.2 (5 pts) moved to pytest-jux Sprint 9
- Story 3.3 (5 pts) moved to behave-jux Sprint 5

## User Stories

### Story 3.1: Jux API Client

**Points**: 8 | **Priority**: High | **Status**: ✅ Completed

**User Story**:
> As a library consumer, I want an HTTP client for Jux servers so that signed reports can be published with proper authentication and retry handling.

**Acceptance Criteria**:
- [x] JuxAPIClient class with configurable base URL and timeout
- [x] Bearer token authentication for remote servers
- [x] Localhost bypass (no auth for 127.0.0.1, ::1, localhost)
- [x] publish_report() method accepting signed XML string
- [x] Exponential backoff retry (1s, 2s, 4s) on server errors
- [x] Automatic retry on 500, 502, 503, 504 errors
- [x] Configurable max_retries (default 3)
- [x] Pydantic models: TestRun, PublishResponse
- [x] Connection pooling with session management
- [x] Enhanced error messages with server response details
- [x] >85% test coverage with mocked responses (98% achieved)

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

**Points**: 5 | **Priority**: High | **Status**: ➡️ Moved

> **NOTE**: This story has been moved to pytest-jux Sprint 9 (`pytest-jux/docs/sprints/sprint-09-juxlib-migration.md`).
> The migration is better managed as a pytest-jux sprint since it primarily involves changes to that project.

---

### Story 3.3: behave-jux Integration

**Points**: 5 | **Priority**: High | **Status**: ➡️ Moved

> **NOTE**: This story has been moved to behave-jux Sprint 5 (`behave-jux/docs/sprints/sprint-5-juxlib-integration.md`).
> The integration is better managed as a behave-jux sprint since it primarily involves changes to that project.

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
