<!-- SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com> -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# ADR-0005: Package Submission Endpoint

## Status

Draft

## Context

The Jux API specification defines a package submission endpoint ([jux-openapi ADR-0003](../../../jux-openapi/docs/adr/0003-signed-container-package-support.md)) for receiving `.jxz` signed containers:

```
POST /api/v1/reports/package
Content-Type: application/vnd.jux.report+zip
```

py-juxlib's API client (`juxlib.api.client.JuxAPIClient`) currently only supports submitting raw XML to `POST /api/v1/junit/submit`. It needs a second submission method for `.jxz` containers built by `py-jxz` (see [ADR-0004](0004-jxz-container-building.md)).

### Two Submission Paths

| Path | Endpoint | Content-Type | Use Case |
|------|----------|-------------|----------|
| Raw XML | `POST /api/v1/junit/submit` | `application/xml` | Simple, no attachments |
| Package | `POST /api/v1/reports/package` | `application/vnd.jux.report+zip` | Signed, with attachments |

Both paths coexist — clients choose based on whether they have attachments or need container-level signing.

## Decision

### Extend JuxAPIClient

Add a `submit_package()` method alongside the existing `submit()`:

```python
class JuxAPIClient:
    def submit(self, xml_content: bytes) -> PublishResponse:
        """Submit raw JUnit XML to /api/v1/junit/submit."""
        ...  # existing

    def submit_package(self, jxz_content: bytes) -> PublishResponse:
        """Submit .jxz container to /api/v1/reports/package."""
        response = self._session.post(
            f"{self._base_url}/api/v1/reports/package",
            data=jxz_content,
            headers={"Content-Type": "application/vnd.jux.report+zip"},
        )
        response.raise_for_status()
        return PublishResponse.model_validate(response.json())
```

### Size Validation

Validate container size before sending:

```python
def submit_package(self, jxz_content: bytes, max_size: int = 50_000_000) -> PublishResponse:
    if len(jxz_content) > max_size:
        raise PackageTooLargeError(len(jxz_content), max_size)
    ...
```

The default 50 MB limit matches the server-side default from the [Server Implementer's Guide](../../../jux-openapi/docs/guides/server-implementers-guide.md).

### Error Handling

Map server error responses to specific exceptions:

| HTTP Status | Server Meaning | Client Exception |
|-------------|----------------|------------------|
| 400 | Not a ZIP / path traversal | `InvalidPackageError` |
| 413 | Package too large | `PackageTooLargeError` |
| 422 | Verification failed (signature, digest, missing files) | `PackageVerificationError` |
| 401/403 | Authentication failure | Existing `AuthenticationError` |

```python
class PackageError(JuxError):
    """Base for package submission errors."""

class InvalidPackageError(PackageError): ...
class PackageTooLargeError(PackageError): ...
class PackageVerificationError(PackageError): ...
```

### Retry Behavior

Reuse the existing retry configuration from `JuxAPIClient`:
- Retry on 429 (rate limited) and 5xx
- Do **not** retry on 400, 413, 422 (client/validation errors)
- Honor `Retry-After` header from 413 responses

### Convenience: Build and Submit

Provide a high-level method that combines container building and submission:

```python
class JuxAPIClient:
    def publish_package(
        self,
        junit_xml: bytes,
        attachments: dict[str, bytes] | None = None,
        private_key: PrivateKey | None = None,
        certificate: Certificate | None = None,
    ) -> PublishResponse:
        """Build a .jxz container and submit it.

        Convenience method combining py-jxz ContainerBuilder.build() and submit_package().
        """
        from jxz import ContainerBuilder

        builder = ContainerBuilder()
        builder.set_report(junit_xml)
        if attachments:
            for name, content in attachments.items():
                builder.add_attachment(name, content)

        jxz = builder.build(private_key=private_key, certificate=certificate)
        return self.submit_package(jxz)
```

### Authentication

Same authentication model as raw XML submission:
- **Localhost**: No authentication required
- **Remote**: Bearer token in `Authorization` header

No changes to authentication — the existing token handling in `JuxAPIClient.__init__` applies to both endpoints.

## Consequences

### Positive

- Additive change — `submit()` preserved, no breaking changes
- Reuses existing session, retry, and auth configuration
- Specific exception hierarchy provides actionable error messages
- `publish_package()` convenience method simplifies client plugin code
- Size validation catches oversized packages before network transfer

### Negative

- Two submission methods increase API surface
- Client must choose between `submit()` and `submit_package()` — callers need guidance on when to use which
- In-memory `jxz_content: bytes` limits practical package size to available RAM

### Migration Path for Client Plugins

pytest-jux and behave-jux can adopt package submission incrementally:

1. **Phase 1**: Continue using `submit()` for XML-only reports (current behavior)
2. **Phase 2**: Use `publish_package()` when attachments are present (e.g., `--jux-attach screenshots/`)
3. **Phase 3**: Default to `publish_package()` for all submissions (optional)

## Related

- [jux-openapi ADR-0003](../../../jux-openapi/docs/adr/0003-signed-container-package-support.md) — API contract this implements
- [jux-openapi Server Implementer's Guide](../../../jux-openapi/docs/guides/server-implementers-guide.md) — Server-side handling recommendations
- [ADR-0004](0004-jxz-container-building.md) — py-jxz dependency for container building
- [ADR-0003](0003-use-python-technology-stack.md) — Technology stack (requests, signxml)
