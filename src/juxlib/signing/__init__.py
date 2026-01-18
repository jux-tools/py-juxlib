# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""XML digital signature creation and verification.

This module provides XMLDSig enveloped signatures for JUnit XML reports,
supporting both RSA and ECDSA key types with automatic algorithm detection.

Features:
- Sign XML documents with RSA-SHA256 or ECDSA-SHA256
- Verify signatures with embedded or external certificates
- XML canonicalization (C14N) for stable hashing
- Key loading from files, PEM strings, or bytes

Example usage:

    >>> from juxlib.signing import sign_xml, load_private_key, verify_signature
    >>> from pathlib import Path
    >>>
    >>> # Load and sign a document
    >>> tree = load_xml(Path("junit-report.xml"))
    >>> key = load_private_key(Path("private.pem"))
    >>> signed_tree = sign_xml(tree, key)
    >>>
    >>> # Verify a signature
    >>> is_valid = verify_signature(signed_tree)
    >>>
    >>> # Compute hash for duplicate detection
    >>> hash_value = compute_canonical_hash(tree)
"""

from .keys import (
    PrivateKey,
    PublicKey,
    get_public_key_from_certificate,
    load_certificate,
    load_private_key,
)
from .signer import has_signature, sign_xml
from .verifier import (
    verify_signature,
    verify_signature_strict,
    verify_with_certificate,
    verify_with_public_key,
)
from .xml import canonicalize_xml, compute_canonical_hash, load_xml

__all__ = [  # noqa: RUF022 - intentionally grouped by category
    # XML operations
    "load_xml",
    "canonicalize_xml",
    "compute_canonical_hash",
    # Key/certificate loading
    "load_private_key",
    "load_certificate",
    "get_public_key_from_certificate",
    # Type aliases
    "PrivateKey",
    "PublicKey",
    # Signing
    "sign_xml",
    "has_signature",
    # Verification
    "verify_signature",
    "verify_signature_strict",
    "verify_with_certificate",
    "verify_with_public_key",
]
