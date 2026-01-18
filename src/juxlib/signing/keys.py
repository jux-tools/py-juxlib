# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""Cryptographic key and certificate loading.

This module provides functionality for loading private keys and certificates
from various sources for use in XML signing and verification.

Supported key types:
- RSA keys (RSA-SHA256 signature algorithm)
- ECDSA keys (ECDSA-SHA256 signature algorithm)

Example usage:

    >>> from juxlib.signing import load_private_key, load_certificate
    >>>
    >>> # Load from file
    >>> key = load_private_key(Path("private.pem"))
    >>>
    >>> # Load from PEM string
    >>> key = load_private_key(pem_string)
    >>>
    >>> # Load certificate
    >>> cert = load_certificate(Path("cert.pem"))
"""

from __future__ import annotations

from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.x509 import Certificate, load_pem_x509_certificate

# Type aliases for key types
PrivateKey = rsa.RSAPrivateKey | ec.EllipticCurvePrivateKey
PublicKey = rsa.RSAPublicKey | ec.EllipticCurvePublicKey


def load_private_key(
    source: str | bytes | Path,
    password: bytes | None = None,
) -> PrivateKey:
    """Load private key from various sources.

    Supports RSA and ECDSA keys in PEM format.

    Args:
        source: Key source - can be:
            - Path object pointing to PEM file
            - PEM content as string
            - PEM content as bytes
        password: Optional password for encrypted keys (default: None)

    Returns:
        Private key object (RSA or ECDSA)

    Raises:
        FileNotFoundError: If file path doesn't exist
        ValueError: If key data is invalid, unsupported format,
                   or wrong password for encrypted key

    Note:
        Only RSA and ECDSA keys are supported for XMLDSig operations.
        Other key types (DSA, Ed25519, etc.) will raise ValueError.
    """
    # Load key data from source
    if isinstance(source, Path):
        if not source.exists():
            raise FileNotFoundError(f"Key file not found: {source}")
        key_data = source.read_bytes()
    elif isinstance(source, str):
        # Check if it's a file path
        if source.startswith(("/", "./", "../")) or (
            len(source) < 260 and not source.strip().startswith("-----BEGIN")
        ):
            path = Path(source)
            key_data = path.read_bytes() if path.exists() else source.encode("utf-8")
        else:
            # PEM content as string
            key_data = source.encode("utf-8")
    else:
        key_data = source

    # Parse private key
    try:
        private_key = serialization.load_pem_private_key(
            key_data,
            password=password,
        )
    except Exception as e:
        raise ValueError(f"Failed to load private key: {e}") from e

    # Verify it's a supported key type
    if not isinstance(private_key, rsa.RSAPrivateKey | ec.EllipticCurvePrivateKey):
        raise ValueError(
            f"Unsupported key type: {type(private_key).__name__}. "
            "Only RSA and ECDSA keys are supported for XMLDSig."
        )

    return private_key


def load_certificate(source: str | bytes | Path) -> Certificate:
    """Load X.509 certificate from various sources.

    Args:
        source: Certificate source - can be:
            - Path object pointing to PEM file
            - PEM content as string
            - PEM content as bytes

    Returns:
        X.509 certificate object

    Raises:
        FileNotFoundError: If file path doesn't exist
        ValueError: If certificate data is invalid
    """
    # Load certificate data from source
    if isinstance(source, Path):
        if not source.exists():
            raise FileNotFoundError(f"Certificate file not found: {source}")
        cert_data = source.read_bytes()
    elif isinstance(source, str):
        # Check if it's a file path
        if source.startswith(("/", "./", "../")) or (
            len(source) < 260 and not source.strip().startswith("-----BEGIN")
        ):
            path = Path(source)
            cert_data = path.read_bytes() if path.exists() else source.encode("utf-8")
        else:
            # PEM content as string
            cert_data = source.encode("utf-8")
    else:
        cert_data = source

    # Parse certificate
    try:
        return load_pem_x509_certificate(cert_data)
    except Exception as e:
        raise ValueError(f"Failed to load certificate: {e}") from e


def get_public_key_from_certificate(cert: Certificate) -> PublicKey:
    """Extract public key from X.509 certificate.

    Args:
        cert: X.509 certificate

    Returns:
        Public key object (RSA or ECDSA)

    Raises:
        ValueError: If certificate contains unsupported key type
    """
    public_key = cert.public_key()

    if not isinstance(public_key, rsa.RSAPublicKey | ec.EllipticCurvePublicKey):
        raise ValueError(
            f"Unsupported key type in certificate: {type(public_key).__name__}. "
            "Only RSA and ECDSA keys are supported."
        )

    return public_key
