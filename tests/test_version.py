# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""Basic tests to verify package structure."""

import juxlib


def test_version_exists() -> None:
    """Verify package version is defined."""
    assert hasattr(juxlib, "__version__")
    assert isinstance(juxlib.__version__, str)
    assert juxlib.__version__ == "0.2.0"


def test_author_exists() -> None:
    """Verify package author is defined."""
    assert hasattr(juxlib, "__author__")
    assert juxlib.__author__ == "Georges Martin"


def test_email_exists() -> None:
    """Verify package email is defined."""
    assert hasattr(juxlib, "__email__")
    assert juxlib.__email__ == "jrjsmrtn@gmail.com"
