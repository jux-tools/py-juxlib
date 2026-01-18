# ADR-0002: Adopt Development Best Practices

Date: 2026-01-18

## Status

Accepted

## Context

py-juxlib is a shared Python library that will be consumed by multiple projects (pytest-jux, behave-jux) within the Jux ecosystem. This requires:

- High reliability and quality standards
- Consistent APIs across consumers
- Clear documentation for library users
- Maintainability for long-term evolution

We need to establish development practices that ensure professional-quality output suitable for both internal use and potential public release.

## Decision

We adopt the following development best practices for py-juxlib:

### 1. Test-Driven Development (TDD)

**Approach**: Red-Green-Refactor cycle for all new functionality

**Tools**:
- `pytest` for unit and integration testing
- `pytest-cov` for coverage measurement (>85% required)
- `hypothesis` for property-based testing of edge cases

**Test Organization**:
```
tests/
├── unit/           # Fast, isolated tests
│   ├── test_metadata.py
│   ├── test_signing.py
│   └── ...
├── integration/    # Tests with external dependencies
│   └── ...
└── conftest.py     # Shared fixtures
```

### 2. Semantic Versioning

**Format**: MAJOR.MINOR.PATCH following [SemVer 2.0.0](https://semver.org/)

**Development Phase**: 0.x.x versioning during initial development
- 0.1.x: Core feature implementation
- Breaking changes allowed before 1.0.0
- Clear CHANGELOG entries for all changes

**Post-1.0.0**: Strict semantic versioning
- MAJOR: Incompatible API changes
- MINOR: Backward-compatible functionality
- PATCH: Backward-compatible bug fixes

### 3. Git Workflow (Gitflow-Based)

**Branches**:
- `main`: Production releases only (protected)
- `develop`: Integration branch for ongoing development
- `feature/*`: Individual feature development
- `release/*`: Release preparation and stabilization
- `hotfix/*`: Critical fixes for production

**Commit Convention**: [Conventional Commits v1.0.0](https://www.conventionalcommits.org/)
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types**: feat, fix, docs, style, refactor, perf, test, build, ci, chore

### 4. Keep a Changelog

**Format**: [Keep a Changelog 1.1.0](https://keepachangelog.com/)

**Categories**:
- Added: New features
- Changed: Changes to existing functionality
- Deprecated: Soon-to-be removed features
- Removed: Removed features
- Fixed: Bug fixes
- Security: Vulnerability fixes

**Location**: `CHANGELOG.md` at project root

### 5. Architecture as Code (C4 DSL)

**Tool**: Structurizr DSL
**Location**: `docs/architecture/`

**Models**:
- System Context: py-juxlib in the Jux ecosystem
- Container: Module structure and boundaries
- Component: Key classes and their relationships

**Validation**: `structurizr/cli validate` before commits

### 6. Documentation Framework (Diátaxis)

**Structure**:
```
docs/
├── tutorials/      # Learning-oriented
├── howto/          # Problem-oriented
├── reference/      # Information-oriented
└── explanation/    # Understanding-oriented
```

**For a library**:
- **Tutorials**: Getting started, integration guides
- **How-to**: Common use cases, migration guides
- **Reference**: API documentation, type signatures
- **Explanation**: Architecture, design decisions

### 7. Sprint-Based Development

**Cycle**: 2-week sprints
**Artifacts**:
- Sprint plan (`docs/sprints/sprint-NN-plan.md`)
- Sprint retrospective (`docs/sprints/sprint-NN-retro.md`)

**Process**:
1. Sprint planning with story point estimation
2. Daily progress tracking
3. Sprint review with deliverable validation
4. Retrospective with lessons learned

### 8. Code Quality Automation

**Pre-commit Hooks**:
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    hooks:
      - id: mypy
  - repo: https://github.com/gitleaks/gitleaks
    hooks:
      - id: gitleaks
```

**Tool Configuration** (in `pyproject.toml`):
- `ruff`: Linting and formatting (replaces black, isort, flake8)
- `mypy`: Static type checking (strict mode)
- `gitleaks`: Secret detection

**CI/CD**:
- GitHub Actions for automated testing
- Test matrix: Python 3.11, 3.12, 3.13
- Coverage reporting with fail threshold

### 9. Type Hints

**Standard**: Full type hints for all public APIs

**Tools**:
- `mypy` in strict mode
- `py.typed` marker for PEP 561 compliance

**Conventions**:
- Use `from __future__ import annotations` for forward references
- Prefer `collections.abc` types over `typing` equivalents
- Document complex types with docstrings

## Consequences

**Positive**:
- High code quality maintained through automation
- Clear documentation for library consumers
- Consistent development experience across team
- AI assistants have clear context from ADRs and documentation
- Type safety reduces runtime errors

**Negative**:
- Initial setup overhead for tooling
- Learning curve for strict typing practices
- Pre-commit hooks add time to commit cycle

**Trade-offs Accepted**:
- Strictness over speed: Quality automation adds overhead but prevents bugs
- Documentation overhead: Comprehensive docs require maintenance but reduce support burden

## References

- [Semantic Versioning 2.0.0](https://semver.org/)
- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/)
- [Keep a Changelog 1.1.0](https://keepachangelog.com/)
- [Diátaxis Documentation Framework](https://diataxis.fr/)
- [C4 Model](https://c4model.com/)
- [PEP 561 - Distributing Type Information](https://peps.python.org/pep-0561/)
