# ADR-0004: Operations Best Practices

Date: 2026-01-18

## Status

Accepted

## Context

py-juxlib is a Python library (not an application or service), so operational concerns are primarily focused on:

1. **Distribution**: How the library is packaged and published
2. **Versioning**: How releases are managed and communicated
3. **Security**: How vulnerabilities are handled
4. **Support**: How issues are triaged and resolved

This ADR documents lightweight operational practices appropriate for a library project.

## Decision

### Distribution

**Package Registry**: PyPI (Python Package Index)

**Package Format**:
- Source distribution (sdist): `.tar.gz`
- Binary wheels: Platform-specific for faster installation

**Publication Process**:
1. Version bump in `pyproject.toml` and `src/juxlib/__init__.py`
2. Update CHANGELOG.md with release notes
3. Create release commit on `develop`
4. Merge to `main` via release branch
5. Tag release: `git tag v0.1.0`
6. Build: `python -m build`
7. Publish: `twine upload dist/*`

**Automation**: GitHub Actions workflow for release publication

### Versioning and Releases

**Release Types**:
- **Major** (1.0.0): Breaking API changes
- **Minor** (0.1.0): New features, backward compatible
- **Patch** (0.1.1): Bug fixes, backward compatible

**Pre-release Tags**:
- Alpha: `0.1.0a1`
- Beta: `0.1.0b1`
- Release candidate: `0.1.0rc1`

**Changelog Requirements**:
- Every release must have CHANGELOG.md entry
- Entry must describe user-visible changes
- Entry must link to relevant issues/PRs

### Security

**Vulnerability Handling**:
1. Security issues reported via GitHub Security Advisories (private)
2. Assessment within 48 hours
3. Fix developed on private branch
4. Coordinated disclosure with patch release
5. CVE requested if applicable

**Dependency Security**:
- Dependabot enabled for dependency updates
- Security alerts monitored weekly
- Critical vulnerabilities patched within 7 days

**Code Security**:
- No credentials in source code (enforced by gitleaks)
- No hardcoded secrets in tests
- Secure defaults for cryptographic operations

### Support

**Issue Triage**:
- **Bug**: Unexpected behavior, reproduction steps required
- **Feature**: New functionality requests
- **Question**: Usage help, documentation clarification
- **Security**: Private reporting via Security Advisories

**Response Times** (best effort):
- Security issues: 48 hours
- Bugs blocking usage: 1 week
- Other bugs: 2 weeks
- Features: Evaluated during sprint planning

**Documentation**:
- README.md: Quick start and basic usage
- docs/: Comprehensive Diátaxis documentation
- CHANGELOG.md: Version history
- CONTRIBUTING.md: Contribution guidelines

### Monitoring

**Package Health**:
- PyPI download statistics (via pypistats)
- GitHub stars and issues as engagement proxy
- CI pass rate as quality indicator

**No Runtime Monitoring**: As a library, py-juxlib does not have its own runtime monitoring. Monitoring is the responsibility of consuming applications.

### Backward Compatibility

**API Stability Commitment**:
- Public API changes documented in CHANGELOG
- Deprecation warnings for 2 minor versions before removal
- Migration guides for breaking changes

**What Constitutes Public API**:
- All symbols exported in `__init__.py` files
- All documented classes, functions, and methods
- All type annotations in public signatures

**Not Public API**:
- Symbols prefixed with `_` (single underscore)
- Internal modules not exported in `__init__.py`
- Implementation details not in documentation

## Consequences

**Positive**:
- Clear process for releases and security handling
- Users can depend on documented API stability
- Security issues handled responsibly
- Low operational overhead appropriate for library

**Negative**:
- Response time commitments require ongoing attention
- Deprecation process extends migration timelines

## References

- [PyPI Publishing](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [Semantic Versioning](https://semver.org/)
- [GitHub Security Advisories](https://docs.github.com/en/code-security/security-advisories)
- [Keep a Changelog](https://keepachangelog.com/)
