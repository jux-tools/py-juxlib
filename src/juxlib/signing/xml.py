# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""XML loading and canonicalization.

This module provides functionality for loading XML from various sources
and canonicalizing it using the C14N algorithm for cryptographic operations.

Example usage:

    >>> from juxlib.signing import load_xml, canonicalize_xml, compute_canonical_hash
    >>>
    >>> # Load from file
    >>> tree = load_xml(Path("report.xml"))
    >>>
    >>> # Load from string
    >>> tree = load_xml("<report><test/></report>")
    >>>
    >>> # Canonicalize
    >>> canonical = canonicalize_xml(tree)
    >>>
    >>> # Compute hash
    >>> hash_value = compute_canonical_hash(tree)
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import TYPE_CHECKING

from lxml import etree

if TYPE_CHECKING:
    from lxml.etree import _Element


def load_xml(source: str | bytes | Path) -> _Element:
    """Load XML from various sources.

    Parses XML content from a file path, string, or bytes.

    Args:
        source: XML source - can be:
            - Path object pointing to XML file
            - String path to XML file (converted to Path)
            - XML content as string
            - XML content as bytes

    Returns:
        Parsed XML element tree root

    Raises:
        FileNotFoundError: If file path doesn't exist
        XMLSyntaxError: If XML is malformed
    """
    # Handle file paths
    if isinstance(source, Path):
        if not source.exists():
            raise FileNotFoundError(f"XML file not found: {source}")
        with source.open("rb") as f:
            return etree.parse(f).getroot()

    # Handle string - could be path or XML content
    if isinstance(source, str):
        # Check if it looks like a file path (starts with / or ./ or contains typical path patterns)
        if source.startswith(("/", "./", "../")) or (
            len(source) < 260 and not source.lstrip().startswith("<")
        ):
            path = Path(source)
            if path.exists():
                with path.open("rb") as f:
                    return etree.parse(f).getroot()
        # Treat as XML content
        source = source.encode("utf-8")

    # Parse bytes as XML content
    return etree.fromstring(source)


def canonicalize_xml(
    tree: _Element,
    exclusive: bool = False,
    with_comments: bool = False,
) -> bytes:
    """Canonicalize XML using C14N algorithm.

    Converts XML to canonical form (C14N) which normalizes:
    - Whitespace normalization
    - Attribute order (lexicographic)
    - Namespace declarations
    - Comments (excluded by default)

    This ensures that semantically equivalent XML produces identical
    canonical output, enabling reliable duplicate detection via hashing
    and consistent signing.

    Args:
        tree: XML element tree to canonicalize
        exclusive: Use exclusive canonicalization (default: False)
                  Exclusive C14N only includes namespace declarations
                  that are visibly used in the output.
        with_comments: Include comments in canonical form (default: False)

    Returns:
        Canonical XML as bytes

    Raises:
        TypeError: If tree is not an lxml element
    """
    if not isinstance(tree, etree._Element):
        raise TypeError(f"Expected lxml Element, got {type(tree)}")

    # etree.tostring with method="c14n" always returns bytes
    return etree.tostring(
        tree,
        method="c14n",
        exclusive=exclusive,
        with_comments=with_comments,
    )


def compute_canonical_hash(
    tree: _Element,
    algorithm: str = "sha256",
) -> str:
    """Compute cryptographic hash of canonical XML.

    Canonicalizes the XML and computes a cryptographic hash of the
    canonical form. This hash can be used for:
    - Duplicate detection
    - Content verification
    - Change detection

    Args:
        tree: XML element tree to hash
        algorithm: Hash algorithm to use. Supported algorithms include:
                  sha256 (default), sha384, sha512, sha3_256, etc.

    Returns:
        Hexadecimal hash digest string

    Raises:
        ValueError: If hash algorithm is not supported
        TypeError: If tree is not an lxml element
    """
    if algorithm not in hashlib.algorithms_available:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")

    canonical = canonicalize_xml(tree)
    hasher = hashlib.new(algorithm)
    hasher.update(canonical)

    return hasher.hexdigest()
