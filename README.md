# py-juxlib

Shared Python library for the Jux tools ecosystem.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Overview

py-juxlib provides common functionality for Jux client tools:

- **Environment metadata detection** - Capture Git, CI/CD, and runtime environment information
- **XML digital signatures** - Sign and verify JUnit XML reports using XMLDSig
- **API client** - Publish signed reports to Jux OpenAPI servers
- **Configuration management** - Multi-source configuration with precedence handling
- **Local storage** - Filesystem storage with offline queue support
- **Error handling** - User-friendly errors with actionable suggestions

## Installation

```bash
pip install py-juxlib
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv pip install py-juxlib
```

## Quick Start

### Capture Environment Metadata

```python
from juxlib.metadata import capture_metadata

metadata = capture_metadata()
print(f"Project: {metadata.project_name}")
print(f"Git commit: {metadata.git_commit}")
print(f"CI provider: {metadata.ci_provider}")
```

### Sign a JUnit XML Report

```python
from juxlib.signing import sign_xml, load_private_key
from lxml import etree

# Load your private key
key = load_private_key("~/.ssh/jux/dev-key.pem")

# Parse and sign XML
tree = etree.parse("junit-report.xml")
signed_tree = sign_xml(tree.getroot(), key)

# Write signed XML
with open("junit-report-signed.xml", "wb") as f:
    f.write(etree.tostring(signed_tree, xml_declaration=True, encoding="UTF-8"))
```

### Publish to Jux Server

```python
from juxlib.api import JuxAPIClient

client = JuxAPIClient(
    api_url="https://jux.example.com",
    bearer_token="your-token"
)

with open("junit-report-signed.xml") as f:
    response = client.publish_report(f.read())

print(f"Test run ID: {response.test_run_id}")
print(f"Success rate: {response.success_rate}%")
```

## Documentation

- [Tutorials](docs/tutorials/) - Getting started guides
- [How-To Guides](docs/howto/) - Task-specific solutions
- [Reference](docs/reference/) - API documentation
- [Explanation](docs/explanation/) - Architecture and design

## Development

```bash
# Clone the repository
git clone https://github.com/jrjsmrtn/py-juxlib.git
cd py-juxlib

# Setup development environment
uv venv && uv pip install -e ".[dev]"

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=juxlib --cov-report=term-missing

# Format and lint
uv run ruff format .
uv run ruff check .

# Type check
uv run mypy src/juxlib
```

## API Specification

> **Source of Truth**: The canonical API specifications live in **[jux-openapi](https://github.com/jrjsmrtn/jux-openapi)**.
> - OpenAPI specs: `jux-openapi/specs/v1/`
> - API changelog: `jux-openapi/docs/CHANGELOG.md`

py-juxlib v0.2.0+ is compliant with jux-openapi API v1.0.0.

## Related Projects

| Project | Description |
|---------|-------------|
| [pytest-jux](https://github.com/jrjsmrtn/pytest-jux) | pytest plugin for signing and publishing JUnit XML |
| [behave-jux](https://github.com/jrjsmrtn/behave-jux) | Enhanced JUnit reporter for behave BDD |
| [jux](https://github.com/jrjsmrtn/jux) | Server for receiving and analyzing test reports |
| [jux-openapi](https://github.com/jrjsmrtn/jux-openapi) | API contract specification (source of truth) |

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.
