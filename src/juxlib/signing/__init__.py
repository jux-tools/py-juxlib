# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""
XML digital signature creation and verification.

This module provides XMLDSig enveloped signatures for JUnit XML reports,
supporting both RSA and ECDSA key types with automatic algorithm detection.

Features:
- Sign XML documents with RSA-SHA256 or ECDSA-SHA256
- Verify signatures with embedded or external certificates
- XML canonicalization (C14N) for stable hashing
- Key loading from files, PEM strings, or bytes

Example usage:

    >>> from juxlib.signing import sign_xml, load_private_key, verify_signature
    >>> from lxml import etree
    >>>
    >>> # Sign a document
    >>> key = load_private_key("~/.ssh/jux/dev-key.pem")
    >>> tree = etree.parse("junit-report.xml")
    >>> signed_tree = sign_xml(tree.getroot(), key)
    >>>
    >>> # Verify a signature
    >>> is_valid = verify_signature(signed_tree)
"""

# Public API will be exported here once implemented
# from .signer import sign_xml, load_private_key
# from .verifier import verify_signature
# from .canonicalizer import canonicalize_xml, compute_canonical_hash, load_xml

__all__: list[str] = []
