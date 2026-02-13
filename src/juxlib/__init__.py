# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""
py-juxlib: Shared Python library for Jux tools ecosystem.

This library provides common functionality for Jux client tools:

- Environment metadata detection (Git, CI/CD, runtime)
- XML digital signatures (XMLDSig signing and verification)
- API client for Jux OpenAPI servers
- Configuration management with multi-source loading
- Local filesystem storage with offline queue
- User-friendly error handling framework

Example usage:

    >>> from juxlib.metadata import capture_metadata
    >>> metadata = capture_metadata()
    >>> print(f"Project: {metadata.project_name}")

    >>> from juxlib.signing import sign_xml, load_private_key
    >>> key = load_private_key("~/.ssh/jux/dev-key.pem")
    >>> signed_tree = sign_xml(tree, key)

    >>> from juxlib.api import JuxAPIClient
    >>> client = JuxAPIClient(api_url="https://jux.example.com")
    >>> response = client.publish_report(signed_xml)
"""

from importlib.metadata import metadata

_meta = metadata("py-juxlib")
__version__ = _meta["Version"]
__author__ = _meta["Author-email"].split("<")[0].strip()
__email__ = _meta["Author-email"].split("<")[1].rstrip(">")

# Public API will be populated as modules are implemented
__all__ = [
    "__author__",
    "__email__",
    "__version__",
]
