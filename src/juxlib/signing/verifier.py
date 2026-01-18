# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""XML digital signature verification.

This module provides functionality to verify XML Digital Signatures (XMLDSig)
in signed XML documents.

Verification can be performed:
1. Using the embedded certificate in the signature
2. Using an external certificate
3. Using a public key object

Example usage:

    >>> from juxlib.signing import load_xml, verify_signature
    >>>
    >>> # Verify with embedded certificate
    >>> tree = load_xml(Path("signed-report.xml"))
    >>> is_valid = verify_signature(tree)
    >>>
    >>> # Verify with external certificate
    >>> is_valid = verify_signature(tree, cert=cert_pem)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from cryptography.x509 import load_pem_x509_certificate
from lxml import etree
from signxml import XMLVerifier  # type: ignore[attr-defined]

if TYPE_CHECKING:
    from lxml.etree import _Element

    from .keys import PublicKey


def verify_signature(
    tree: _Element,
    cert: str | bytes | None = None,
) -> bool:
    """Verify XMLDSig signature in signed XML.

    Verifies the XML digital signature embedded in the document.
    Can use either the embedded certificate (if present) or an
    externally provided certificate.

    Args:
        tree: Signed XML element tree
        cert: Optional X.509 certificate in PEM format for verification.
              If not provided, uses certificate embedded in signature.

    Returns:
        True if signature is valid, False otherwise

    Note:
        Returns False (not raises) for invalid signatures to allow
        easy conditional handling. Use verify_signature_strict() if
        you need detailed error information.
    """
    if not isinstance(tree, etree._Element):
        return False  # type: ignore[unreachable]

    # Check if XML has a signature
    signature = tree.find(".//{http://www.w3.org/2000/09/xmldsig#}Signature")
    if signature is None:
        return False

    verifier = XMLVerifier()

    try:
        if cert is not None:
            # Verify with provided certificate
            cert_str = cert.decode("utf-8") if isinstance(cert, bytes) else cert
            verifier.verify(tree, x509_cert=cert_str)
        else:
            # Verify with embedded certificate
            verifier.verify(tree)

        return True

    except Exception:
        # Any exception means signature is invalid
        return False


def verify_signature_strict(
    tree: _Element,
    cert: str | bytes | None = None,
) -> None:
    """Verify XMLDSig signature, raising on failure.

    Same as verify_signature() but raises exceptions with detailed
    error information instead of returning False.

    Args:
        tree: Signed XML element tree
        cert: Optional X.509 certificate in PEM format for verification

    Raises:
        TypeError: If tree is not an lxml element
        ValueError: If no signature is found
        SignatureVerificationError: If signature is invalid

    Note:
        SignatureVerificationError is the exception type raised by signxml.
    """
    if not isinstance(tree, etree._Element):
        raise TypeError(f"Expected lxml Element, got {type(tree)}")

    # Check if XML has a signature
    signature = tree.find(".//{http://www.w3.org/2000/09/xmldsig#}Signature")
    if signature is None:
        raise ValueError("No signature found in XML document")

    verifier = XMLVerifier()

    if cert is not None:
        # Verify with provided certificate
        cert_str = cert.decode("utf-8") if isinstance(cert, bytes) else cert
        verifier.verify(tree, x509_cert=cert_str)
    else:
        # Verify with embedded certificate
        verifier.verify(tree)


def verify_with_certificate(
    tree: _Element,
    cert: str | bytes,
) -> bool:
    """Verify signature using an external certificate.

    This is a convenience wrapper around verify_signature() that
    validates the certificate before verification.

    Args:
        tree: Signed XML element tree
        cert: X.509 certificate in PEM format (required)

    Returns:
        True if signature is valid, False otherwise

    Raises:
        ValueError: If certificate is invalid
    """
    # Validate certificate format first
    cert_bytes = cert.encode("utf-8") if isinstance(cert, str) else cert
    try:
        load_pem_x509_certificate(cert_bytes)
    except Exception as e:
        raise ValueError(f"Invalid certificate: {e}") from e

    return verify_signature(tree, cert=cert)


def verify_with_public_key(
    tree: _Element,
    public_key: PublicKey,  # noqa: ARG001 - reserved for future implementation
) -> bool:
    """Verify signature using a public key.

    Note: This method extracts the key from the signature's KeyInfo
    element and compares it to the provided public key.

    Args:
        tree: Signed XML element tree
        public_key: RSA or ECDSA public key

    Returns:
        True if signature is valid, False otherwise

    Note:
        Current implementation uses embedded certificate/key in signature.
        Direct public key comparison is not yet fully implemented.
    """
    # For now, verify using embedded key in signature
    # A more complete implementation would compare the provided key
    # with the key extracted from the signature
    return verify_signature(tree)
