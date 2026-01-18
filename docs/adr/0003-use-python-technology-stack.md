# ADR-0003: Use Python Technology Stack

Date: 2026-01-18

## Status

Accepted

## Context

py-juxlib needs to provide shared functionality for Jux client tools, specifically:

1. **Environment metadata detection** - Capture Git, CI/CD, and runtime context
2. **XML digital signatures** - Sign and verify JUnit XML reports (XMLDSig)
3. **API client** - Publish reports to Jux OpenAPI servers
4. **Configuration management** - Multi-source configuration with precedence
5. **Local storage** - Filesystem storage with offline queue support
6. **Error handling** - User-friendly errors with actionable suggestions

Key requirements:
- Must integrate with pytest (Python) and behave (Python)
- Must handle XML processing efficiently
- Must support cryptographic operations (RSA, ECDSA)
- Must be installable via pip/uv
- Must support Python 3.11+ (modern type hints, tomllib)

## Decision

We will use Python 3.11+ with the following technology stack:

### Core Language

**Python 3.11+** selected for:
- Native `tomllib` for TOML parsing (no external dependency)
- Improved type hints (`Self`, `TypeVarTuple`, union syntax `X | Y`)
- Better error messages for debugging
- Performance improvements (10-60% faster than 3.10)
- Long-term support (3.11 EOL: October 2027)

### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `lxml` | >=5.0 | XML parsing, canonicalization (C14N), XPath |
| `cryptography` | >=42.0 | RSA/ECDSA key loading, certificate handling |
| `signxml` | >=4.0 | XMLDSig signing and verification |
| `requests` | >=2.31 | HTTP client with session management |
| `pydantic` | >=2.0 | Data validation, API response models |
| `rich` | >=13.0 | User-friendly error formatting |

### Development Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `pytest` | >=8.0 | Test framework |
| `pytest-cov` | >=4.0 | Coverage measurement |
| `pytest-xdist` | >=3.0 | Parallel test execution |
| `hypothesis` | >=6.0 | Property-based testing |
| `ruff` | >=0.4 | Linting and formatting |
| `mypy` | >=1.10 | Static type checking |
| `pre-commit` | >=3.0 | Git hook management |

### Build System

**Hatchling** selected for:
- Modern PEP 517/518 compliant build backend
- Simple configuration in `pyproject.toml`
- Native support for src-layout
- Fast builds with minimal dependencies

### Alternatives Considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **lxml** | Fast C implementation, full XPath/XSLT, C14N support | Binary dependency | Selected |
| `xml.etree` | Stdlib, no external deps | No C14N, limited XPath | Rejected |
| `defusedxml` | Security-focused | Limited features | Used with lxml |

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **signxml** | Pure Python XMLDSig, well-maintained | Depends on lxml, cryptography | Selected |
| `xmlsec` | Feature-rich, libxmlsec binding | Complex binary dependency | Rejected |
| Custom impl | Full control | Security risk, maintenance burden | Rejected |

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **requests** | Simple API, widely used, battle-tested | Synchronous only | Selected |
| `httpx` | Async support, modern | Additional complexity | Deferred |
| `urllib3` | Lower level, more control | More verbose | Rejected |

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **pydantic** | Fast validation, great DX, JSON schema | Rust dependency | Selected |
| `dataclasses` | Stdlib, simple | No validation | Rejected |
| `attrs` | Flexible, fast | Less ecosystem support | Rejected |

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **hatchling** | Modern, simple, extensible | Newer | Selected |
| `setuptools` | Ubiquitous, well-known | Verbose config | Rejected |
| `poetry` | Good DX | Lock file complexity | Rejected |
| `flit` | Minimal | Limited features | Rejected |

## Consequences

**Positive**:
- Mature, well-tested libraries for all core functionality
- Strong type checking with mypy in strict mode
- Easy installation for pytest-jux and behave-jux consumers
- Active maintenance and security updates for all dependencies
- Familiar tooling for Python developers

**Negative**:
- Binary dependencies (lxml, cryptography) require compilation or wheels
- signxml brings transitive dependencies
- Python 3.11+ requirement excludes older Python versions

**Risks and Mitigations**:
- **Binary wheel availability**: lxml and cryptography have wheels for all major platforms; documented fallback to source builds
- **Dependency conflicts**: Use version ranges (>=) rather than pinned versions for flexibility
- **Security vulnerabilities**: Dependabot alerts enabled, regular dependency updates

## References

- [lxml Documentation](https://lxml.de/)
- [signxml Documentation](https://signxml.readthedocs.io/)
- [cryptography Documentation](https://cryptography.io/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Hatch Documentation](https://hatch.pypa.io/)
