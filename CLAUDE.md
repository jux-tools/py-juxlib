# py-juxlib

Shared Python library for the Jux tools ecosystem, providing environment metadata detection, JUnit XML signing/verification, and API client for publishing to Jux OpenAPI servers.

## Project Context

- **Category**: Development
- **Type**: Python library
- **Stack**: Python 3.11+, lxml, cryptography, signxml, requests, pydantic
- **License**: Apache-2.0
- **Ecosystem**: Part of jux-tools workspace (see `../CLAUDE.md`)

## Purpose

py-juxlib extracts and consolidates shared functionality from `pytest-jux` that will also be used by `behave-jux` and other future Jux client tools. This eliminates code duplication and provides a consistent foundation for all Python-based Jux tools.

### Shared Features

| Module | Purpose | Used By |
|--------|---------|---------|
| `juxlib.metadata` | Environment, Git, and CI/CD metadata detection | pytest-jux, behave-jux |
| `juxlib.signing` | XML digital signature creation and verification | pytest-jux, behave-jux |
| `juxlib.api` | HTTP client for Jux OpenAPI servers | pytest-jux, behave-jux |
| `juxlib.config` | Configuration management with multi-source loading | pytest-jux, behave-jux |
| `juxlib.storage` | Local filesystem storage with offline queue | pytest-jux, behave-jux |
| `juxlib.errors` | User-friendly error handling framework | pytest-jux, behave-jux |

## Current Development Status

- **Completed Sprints**: Sprint 1 (errors, metadata, signing), Sprint 2 (config, storage), Sprint 3 (api)
- **Latest Release**: v0.3.0
- **Next Milestone**: TBD (all 6 modules complete)

## Foundational ADRs

Read these at the start of each AI session for complete context:

| ADR | Purpose | Summary |
|-----|---------|---------|
| [ADR-0001](docs/adr/0001-record-architecture-decisions.md) | HOW TO DECIDE | Decision methodology |
| [ADR-0002](docs/adr/0002-adopt-development-best-practices.md) | HOW TO DEVELOP | Development practices |
| [ADR-0003](docs/adr/0003-use-python-technology-stack.md) | WHAT TECH | Technology stack |

## Development Practices

This project follows [AI-Assisted Project Orchestration patterns](https://github.com/jrjsmrtn/ai-assisted-project-orchestration):

- **Testing**: TDD with pytest, >85% coverage required
- **Versioning**: Semantic versioning (0.x.x during development)
- **Git Workflow**: Gitflow (main, develop, feature/*, release/*, hotfix/*)
- **Documentation**: Diátaxis framework
- **Architecture**: C4 DSL models in `docs/architecture/`

## Quick Commands

```bash
# Setup development environment
uv venv && uv pip install -e ".[dev]"

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=juxlib --cov-report=term-missing

# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Type check
uv run mypy src/juxlib

# Validate architecture model
make validate-architecture
```

## Package Structure

```
src/juxlib/
├── __init__.py              # Public API exports
├── metadata/
│   ├── __init__.py
│   ├── models.py            # EnvironmentMetadata dataclass
│   ├── detection.py         # capture_metadata() main entry point
│   ├── git.py               # Git repository detection
│   └── ci.py                # CI/CD platform detection
├── signing/
│   ├── __init__.py
│   ├── signer.py            # sign_xml(), load_private_key()
│   ├── verifier.py          # verify_signature()
│   └── canonicalizer.py     # canonicalize_xml(), compute_hash()
├── api/
│   ├── __init__.py
│   ├── client.py            # JuxAPIClient
│   └── models.py            # TestRun, PublishResponse (Pydantic)
├── config/
│   ├── __init__.py
│   ├── manager.py           # ConfigurationManager
│   └── schema.py            # ConfigSchema, StorageMode
├── storage/
│   ├── __init__.py
│   └── filesystem.py        # ReportStorage, get_default_path()
└── errors/
    ├── __init__.py
    ├── codes.py             # ErrorCode enum
    └── exceptions.py        # JuxError hierarchy
```

## Dependencies

### Runtime Dependencies

```toml
[project.dependencies]
lxml = ">=5.0"               # XML parsing and canonicalization
cryptography = ">=42.0"      # RSA/ECDSA key handling
signxml = ">=4.0"            # XMLDSig signing/verification
requests = ">=2.31"          # HTTP client
pydantic = ">=2.0"           # Data validation and models
rich = ">=13.0"              # User-friendly error formatting
```

### Development Dependencies

```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=4.0",
    "pytest-xdist>=3.0",
    "hypothesis>=6.0",
    "ruff>=0.4",
    "mypy>=1.10",
    "pre-commit>=3.0",
]
```

## AI Collaboration Notes

### Project-Specific Guidance

- **Source of truth**: Code extraction from `pytest-jux` (see `../pytest-jux/`)
- **API contract**: Must align with `../jux-openapi/` specifications
- **Sibling consumer**: `behave-jux` will be updated to use this library
- **No test framework dependencies**: Library must not import pytest or behave

### AI Delegation in This Project

- **AI leads**: Code extraction, test generation, documentation
- **Human leads**: API design decisions, version compatibility, release management
- **Collaborative**: Feature implementation, code review, architecture refinement

### What AI Should Know

- All extracted code must maintain backward compatibility with pytest-jux
- XML canonicalization uses C14N algorithm for consistent hashing
- API client supports both authenticated (bearer token) and local (no auth) modes
- Configuration follows precedence: CLI > env vars > config file > defaults
- Error messages should be user-friendly with actionable suggestions

### Critical Constraints

1. **Python 3.11+ only** - Uses modern features (tomllib, type hints)
2. **No pytest/behave imports** - Pure library, framework-agnostic
3. **XDG compliance** - Storage paths follow XDG Base Directory specification
4. **Atomic file operations** - All writes use temp-then-rename pattern
5. **Credential safety** - Never log or display API tokens/private keys

## Related Projects

| Project | Relationship |
|---------|--------------|
| `pytest-jux` | Source of extracted code, primary consumer |
| `behave-jux` | Secondary consumer, will migrate to use juxlib |
| `jux-openapi` | **Source of truth** for API contract (OpenAPI 3.0 specification) |
| `jux` | Server that receives published reports |
| `junit-xml-test-fixtures` | Shared test data |

> **API Compliance**: py-juxlib v0.2.0+ is compliant with jux-openapi API v1.0.0.

## Git Configuration

See `CLAUDE.local.md` for remote URLs (homelab details excluded from version control).

```bash
# Branch strategy: Gitflow
# - main: Production releases only
# - develop: Active development
# - feature/*: Individual features
# - release/*: Release preparation
# - hotfix/*: Critical fixes
```
