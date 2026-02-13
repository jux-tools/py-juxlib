# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""Basic tests to verify package structure."""

from importlib.metadata import version

import juxlib


def test_version_matches_metadata() -> None:
    """Package __version__ should match installed metadata (from pyproject.toml)."""
    assert hasattr(juxlib, "__version__")
    assert isinstance(juxlib.__version__, str)
    assert juxlib.__version__ == version("py-juxlib")


def test_author_exists() -> None:
    """Verify package author is defined."""
    assert hasattr(juxlib, "__author__")
    assert juxlib.__author__ == "Georges Martin"


def test_email_exists() -> None:
    """Verify package email is defined."""
    assert hasattr(juxlib, "__email__")
    assert juxlib.__email__ == "jrjsmrtn@gmail.com"
