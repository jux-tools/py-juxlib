# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""XML digital signature generation.

This module provides functionality to sign XML documents using
XML Digital Signatures (XMLDSig) with RSA or ECDSA keys.

The signature uses the enveloped signature method, where the signature
is embedded within the signed document as a child element.

Example usage:

    >>> from juxlib.signing import load_xml, load_private_key, sign_xml
    >>>
    >>> tree = load_xml("<report><test/></report>")
    >>> key = load_private_key(Path("private.pem"))
    >>> signed = sign_xml(tree, key)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import signxml
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from lxml import etree
from signxml import XMLSigner  # type: ignore[attr-defined]

if TYPE_CHECKING:
    from lxml.etree import _Element

    from .keys import PrivateKey


def sign_xml(
    tree: _Element,
    private_key: PrivateKey,
    cert: str | bytes | None = None,
) -> _Element:
    """Sign XML with XMLDSig enveloped signature.

    Adds an enveloped XMLDSig signature to the XML document using
    the provided private key. The signature is placed as a child
    of the root element.

    The signature includes:
    - SignedInfo: Canonicalization and signature method information
    - SignatureValue: The actual cryptographic signature
    - KeyInfo: Key/certificate information (if cert provided)

    Args:
        tree: XML element tree to sign
        private_key: RSA or ECDSA private key for signing
        cert: Optional X.509 certificate in PEM format.
              If provided, the certificate is included in the signature
              for verification without needing external certificate.

    Returns:
        Signed XML element tree with Signature element added.
        Note: The original tree is modified in-place.

    Raises:
        TypeError: If tree is not an lxml element
        ValueError: If signing fails (e.g., invalid key or tree)

    Note:
        The signature algorithm is automatically selected based on key type:
        - RSA keys use RSA-SHA256
        - ECDSA keys use ECDSA-SHA256
    """
    if not isinstance(tree, etree._Element):
        raise TypeError(f"Expected lxml Element, got {type(tree)}")

    # Determine signature algorithm based on key type
    if isinstance(private_key, rsa.RSAPrivateKey):
        sig_algorithm = "rsa-sha256"
    elif isinstance(private_key, ec.EllipticCurvePrivateKey):
        sig_algorithm = "ecdsa-sha256"
    else:
        raise ValueError(
            f"Unsupported key type: {type(private_key).__name__}. "
            "Only RSA and ECDSA keys are supported."
        )

    # Create XML signer with enveloped signature method
    signer = XMLSigner(
        method=signxml.methods.enveloped,
        signature_algorithm=sig_algorithm,
        digest_algorithm="sha256",
    )

    try:
        # Sign the XML
        if cert is not None:
            # Convert bytes to string if needed (signxml expects str)
            cert_str = cert.decode("utf-8") if isinstance(cert, bytes) else cert
            signed_root = signer.sign(tree, key=private_key, cert=cert_str)
        else:
            signed_root = signer.sign(tree, key=private_key)

        return signed_root

    except Exception as e:
        raise ValueError(f"Failed to sign XML: {e}") from e


def has_signature(tree: _Element) -> bool:
    """Check if XML document contains an XMLDSig signature.

    Args:
        tree: XML element tree to check

    Returns:
        True if document contains a Signature element, False otherwise
    """
    if not isinstance(tree, etree._Element):
        return False  # type: ignore[unreachable]

    signature = tree.find(".//{http://www.w3.org/2000/09/xmldsig#}Signature")
    return signature is not None
