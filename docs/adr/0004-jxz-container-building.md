<!-- SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com> -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# ADR-0004: Depend on py-jxz for Container Operations

## Status

Draft

## Context

The `.jxz` signed container format ([jux-container-format spec](../../../jux-container-format/specs/v1/jxz-format.md)) defines a ZIP-based package for transmitting signed JUnit XML reports with attachments. py-juxlib currently signs individual XML documents using enveloped XMLDSig (`juxlib.signing`), but the `.jxz` format uses a different approach: a detached signature over a manifest that lists SHA-256 digests of all container entries.

py-juxlib needs to produce `.jxz` containers so that pytest-jux, behave-jux, and future clients can package reports with attachments for submission to jux-openapi compliant servers.

### Why Not Build It In-House

The `.jxz` format is consumed by both client libraries (py-juxlib) and servers (spooky). If container handling lived inside py-juxlib, spooky would need to depend on a client library — pulling in `requests`, `pydantic`, metadata detection, and other things a server does not want. A standalone `py-jxz` package provides a clean dependency boundary.

### Current Signing vs .jxz Signing

| Aspect | Current (enveloped) | .jxz (detached) |
|--------|---------------------|------------------|
| Signature location | Inside the XML document | `META-INF/SIGNATURE.XML` |
| What is signed | XML content directly | `META-INF/MANIFEST.MF` (digest chain) |
| Attachments | Not supported | Included in ZIP, digests in manifest |
| Transport | Raw XML POST | ZIP POST with `application/vnd.jux.report+zip` |

## Decision

### Add py-jxz as a Dependency

Add `py-jxz` to py-juxlib's runtime dependencies:

```toml
dependencies = [
    "py-jxz>=0.1.0",
    # ... existing deps
]
```

### Usage in py-juxlib

py-juxlib uses `py-jxz`'s `ContainerBuilder` and `ContainerReader` to build and read `.jxz` containers:

```python
from jxz import ContainerBuilder

builder = ContainerBuilder()
builder.set_report(junit_xml_bytes)
builder.add_attachment("screenshots/login.png", png_bytes, for_testcase="test_login")

# Signed container
jxz_bytes = builder.build(private_key=key, certificate=cert)
```

### Integration with Existing Modules

- **`juxlib.signing`**: Existing `load_private_key()` reused for loading keys passed to `ContainerBuilder.build()`; enveloped signing preserved for backward compatibility
- **`juxlib.metadata`**: `capture_metadata()` output populates manifest main section fields via `ContainerBuilder`
- **`juxlib.api`**: New submission method uses built container (see ADR-0005)

### Re-export for Consumer Convenience

py-juxlib may re-export key py-jxz types for consumer convenience:

```python
# juxlib/__init__.py
from jxz import ContainerBuilder, ContainerReader
```

This allows pytest-jux to import from `juxlib` without knowing about `py-jxz` directly.

## Consequences

### Positive

- Clean dependency boundary — spooky depends on py-jxz directly, not py-juxlib
- Container format logic maintained in one place (py-jxz)
- py-juxlib stays focused on client concerns (metadata, API, config)
- Enveloped signing in `juxlib.signing` preserved — not a breaking change

### Negative

- One additional dependency to manage and version
- Consumers may need to understand the py-juxlib / py-jxz boundary
- Version coordination between py-juxlib and py-jxz during development

### Future

- Deprecation path for enveloped signing once `.jxz` adoption is sufficient

## Related

- [jux-container-format spec](../../../jux-container-format/specs/v1/jxz-format.md) — Format specification
- [py-jxz](../../../py-jxz/) — The container format library this depends on
- [ADR-0005](0005-package-submission-endpoint.md) — API submission of built containers
- [ADR-0003](0003-use-python-technology-stack.md) — Technology stack
