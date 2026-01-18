# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""Tests for juxlib.signing module."""

from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from lxml import etree

from juxlib.signing import (
    canonicalize_xml,
    compute_canonical_hash,
    get_public_key_from_certificate,
    has_signature,
    load_certificate,
    load_private_key,
    load_xml,
    sign_xml,
    verify_signature,
    verify_signature_strict,
    verify_with_certificate,
)

# Path to test fixtures
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
RSA_KEY_PATH = FIXTURES_DIR / "test-private.pem"
RSA_CERT_PATH = FIXTURES_DIR / "test-cert.pem"
EC_KEY_PATH = FIXTURES_DIR / "test-ec-private.pem"
EC_CERT_PATH = FIXTURES_DIR / "test-ec-cert.pem"
SAMPLE_XML_PATH = FIXTURES_DIR / "sample-report.xml"


class TestLoadXML:
    """Tests for load_xml function."""

    def test_load_from_file_path(self) -> None:
        """load_xml should load from Path object."""
        tree = load_xml(SAMPLE_XML_PATH)

        assert tree.tag == "testsuites"
        assert tree.get("name") == "pytest"

    def test_load_from_string_path(self) -> None:
        """load_xml should load from string path."""
        tree = load_xml(str(SAMPLE_XML_PATH))

        assert tree.tag == "testsuites"

    def test_load_from_xml_string(self) -> None:
        """load_xml should load from XML string."""
        xml_str = "<root><child>text</child></root>"

        tree = load_xml(xml_str)

        assert tree.tag == "root"
        assert tree.find("child").text == "text"

    def test_load_from_xml_bytes(self) -> None:
        """load_xml should load from XML bytes."""
        xml_bytes = b"<root><child>text</child></root>"

        tree = load_xml(xml_bytes)

        assert tree.tag == "root"

    def test_load_file_not_found(self) -> None:
        """load_xml should raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            load_xml(Path("/nonexistent/file.xml"))

    def test_load_invalid_xml(self) -> None:
        """load_xml should raise XMLSyntaxError for invalid XML."""
        with pytest.raises(etree.XMLSyntaxError):
            load_xml("<invalid><xml>")


class TestCanonicalizeXML:
    """Tests for canonicalize_xml function."""

    def test_canonicalize_basic(self) -> None:
        """canonicalize_xml should produce canonical output."""
        tree = load_xml("<root><child/></root>")

        canonical = canonicalize_xml(tree)

        assert isinstance(canonical, bytes)
        assert b"<root>" in canonical

    def test_canonicalize_normalizes_attributes(self) -> None:
        """canonicalize_xml should normalize attribute order."""
        # C14N sorts attributes lexicographically
        tree1 = load_xml('<root z="3" a="1" m="2"/>')
        tree2 = load_xml('<root a="1" m="2" z="3"/>')

        canon1 = canonicalize_xml(tree1)
        canon2 = canonicalize_xml(tree2)

        # Canonical form should be identical regardless of attribute order
        assert canon1 == canon2

    def test_canonicalize_without_comments(self) -> None:
        """canonicalize_xml should exclude comments by default."""
        tree = load_xml("<root><!-- comment --><child/></root>")

        canonical = canonicalize_xml(tree)

        assert b"comment" not in canonical

    def test_canonicalize_with_comments(self) -> None:
        """canonicalize_xml should include comments when requested."""
        tree = load_xml("<root><!-- comment --><child/></root>")

        canonical = canonicalize_xml(tree, with_comments=True)

        assert b"comment" in canonical

    def test_canonicalize_type_error(self) -> None:
        """canonicalize_xml should raise TypeError for invalid input."""
        with pytest.raises(TypeError):
            canonicalize_xml("not an element")  # type: ignore[arg-type]


class TestComputeCanonicalHash:
    """Tests for compute_canonical_hash function."""

    def test_compute_hash_default_sha256(self) -> None:
        """compute_canonical_hash should use SHA-256 by default."""
        tree = load_xml("<root><child/></root>")

        hash_value = compute_canonical_hash(tree)

        assert isinstance(hash_value, str)
        assert len(hash_value) == 64  # SHA-256 produces 64 hex chars

    def test_compute_hash_sha512(self) -> None:
        """compute_canonical_hash should support SHA-512."""
        tree = load_xml("<root><child/></root>")

        hash_value = compute_canonical_hash(tree, algorithm="sha512")

        assert len(hash_value) == 128  # SHA-512 produces 128 hex chars

    def test_compute_hash_invalid_algorithm(self) -> None:
        """compute_canonical_hash should raise ValueError for invalid algorithm."""
        tree = load_xml("<root><child/></root>")

        with pytest.raises(ValueError, match="Unsupported hash algorithm"):
            compute_canonical_hash(tree, algorithm="invalid")

    def test_compute_hash_deterministic(self) -> None:
        """compute_canonical_hash should produce consistent results."""
        tree1 = load_xml("<root><child/></root>")
        tree2 = load_xml("<root><child/></root>")

        hash1 = compute_canonical_hash(tree1)
        hash2 = compute_canonical_hash(tree2)

        assert hash1 == hash2


class TestLoadPrivateKey:
    """Tests for load_private_key function."""

    def test_load_rsa_key_from_path(self) -> None:
        """load_private_key should load RSA key from Path."""
        key = load_private_key(RSA_KEY_PATH)

        assert isinstance(key, rsa.RSAPrivateKey)

    def test_load_rsa_key_from_string_path(self) -> None:
        """load_private_key should load RSA key from string path."""
        key = load_private_key(str(RSA_KEY_PATH))

        assert isinstance(key, rsa.RSAPrivateKey)

    def test_load_rsa_key_from_pem_bytes(self) -> None:
        """load_private_key should load RSA key from PEM bytes."""
        pem_bytes = RSA_KEY_PATH.read_bytes()

        key = load_private_key(pem_bytes)

        assert isinstance(key, rsa.RSAPrivateKey)

    def test_load_rsa_key_from_pem_string(self) -> None:
        """load_private_key should load RSA key from PEM string."""
        pem_string = RSA_KEY_PATH.read_text()

        key = load_private_key(pem_string)

        assert isinstance(key, rsa.RSAPrivateKey)

    def test_load_ecdsa_key(self) -> None:
        """load_private_key should load ECDSA key."""
        key = load_private_key(EC_KEY_PATH)

        assert isinstance(key, ec.EllipticCurvePrivateKey)

    def test_load_key_file_not_found(self) -> None:
        """load_private_key should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_private_key(Path("/nonexistent/key.pem"))

    def test_load_key_invalid_data(self) -> None:
        """load_private_key should raise ValueError for invalid data."""
        with pytest.raises(ValueError, match="Failed to load private key"):
            load_private_key(b"not a valid key")


class TestLoadCertificate:
    """Tests for load_certificate function."""

    def test_load_certificate_from_path(self) -> None:
        """load_certificate should load from Path."""
        cert = load_certificate(RSA_CERT_PATH)

        assert cert.subject is not None

    def test_load_certificate_from_pem_bytes(self) -> None:
        """load_certificate should load from PEM bytes."""
        pem_bytes = RSA_CERT_PATH.read_bytes()

        cert = load_certificate(pem_bytes)

        assert cert.subject is not None

    def test_load_certificate_file_not_found(self) -> None:
        """load_certificate should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_certificate(Path("/nonexistent/cert.pem"))

    def test_load_certificate_invalid_data(self) -> None:
        """load_certificate should raise ValueError for invalid data."""
        with pytest.raises(ValueError, match="Failed to load certificate"):
            load_certificate(b"not a valid certificate")


class TestGetPublicKeyFromCertificate:
    """Tests for get_public_key_from_certificate function."""

    def test_get_rsa_public_key(self) -> None:
        """get_public_key_from_certificate should extract RSA key."""
        cert = load_certificate(RSA_CERT_PATH)

        public_key = get_public_key_from_certificate(cert)

        assert isinstance(public_key, rsa.RSAPublicKey)

    def test_get_ecdsa_public_key(self) -> None:
        """get_public_key_from_certificate should extract ECDSA key."""
        cert = load_certificate(EC_CERT_PATH)

        public_key = get_public_key_from_certificate(cert)

        assert isinstance(public_key, ec.EllipticCurvePublicKey)


class TestSignXML:
    """Tests for sign_xml function."""

    def test_sign_with_rsa_key(self) -> None:
        """sign_xml should sign with RSA key."""
        tree = load_xml(SAMPLE_XML_PATH)
        key = load_private_key(RSA_KEY_PATH)

        signed = sign_xml(tree, key)

        assert has_signature(signed)

    def test_sign_with_ecdsa_key(self) -> None:
        """sign_xml should sign with ECDSA key."""
        tree = load_xml(SAMPLE_XML_PATH)
        key = load_private_key(EC_KEY_PATH)

        signed = sign_xml(tree, key)

        assert has_signature(signed)

    def test_sign_with_certificate(self) -> None:
        """sign_xml should include certificate in signature."""
        tree = load_xml(SAMPLE_XML_PATH)
        key = load_private_key(RSA_KEY_PATH)
        cert = RSA_CERT_PATH.read_text()

        signed = sign_xml(tree, key, cert=cert)

        assert has_signature(signed)
        # Certificate should be embedded in the signature
        assert b"X509Certificate" in etree.tostring(signed)

    def test_sign_type_error(self) -> None:
        """sign_xml should raise TypeError for invalid tree."""
        key = load_private_key(RSA_KEY_PATH)

        with pytest.raises(TypeError):
            sign_xml("not an element", key)  # type: ignore[arg-type]


class TestHasSignature:
    """Tests for has_signature function."""

    def test_unsigned_document(self) -> None:
        """has_signature should return False for unsigned document."""
        tree = load_xml(SAMPLE_XML_PATH)

        assert has_signature(tree) is False

    def test_signed_document(self) -> None:
        """has_signature should return True for signed document."""
        tree = load_xml(SAMPLE_XML_PATH)
        key = load_private_key(RSA_KEY_PATH)
        signed = sign_xml(tree, key)

        assert has_signature(signed) is True

    def test_invalid_input(self) -> None:
        """has_signature should return False for invalid input."""
        assert has_signature("not an element") is False  # type: ignore[arg-type]


class TestVerifySignature:
    """Tests for verify_signature function."""

    def test_verify_valid_rsa_signature(self) -> None:
        """verify_signature should return True for valid RSA signature with explicit cert."""
        tree = load_xml(SAMPLE_XML_PATH)
        key = load_private_key(RSA_KEY_PATH)
        cert = RSA_CERT_PATH.read_text()
        signed = sign_xml(tree, key, cert=cert)

        # Verify with explicit certificate (bypasses strict X.509 chain validation)
        assert verify_signature(signed, cert=cert) is True

    def test_verify_valid_ecdsa_signature(self) -> None:
        """verify_signature should return True for valid ECDSA signature with explicit cert."""
        tree = load_xml(SAMPLE_XML_PATH)
        key = load_private_key(EC_KEY_PATH)
        cert = EC_CERT_PATH.read_text()
        signed = sign_xml(tree, key, cert=cert)

        # Verify with explicit certificate (bypasses strict X.509 chain validation)
        assert verify_signature(signed, cert=cert) is True

    def test_verify_with_external_certificate(self) -> None:
        """verify_signature should work with external certificate."""
        tree = load_xml(SAMPLE_XML_PATH)
        key = load_private_key(RSA_KEY_PATH)
        cert = RSA_CERT_PATH.read_text()
        signed = sign_xml(tree, key, cert=cert)

        assert verify_signature(signed, cert=cert) is True

    def test_verify_unsigned_document(self) -> None:
        """verify_signature should return False for unsigned document."""
        tree = load_xml(SAMPLE_XML_PATH)

        assert verify_signature(tree) is False

    def test_verify_tampered_document(self) -> None:
        """verify_signature should return False for tampered document."""
        tree = load_xml(SAMPLE_XML_PATH)
        key = load_private_key(RSA_KEY_PATH)
        cert = RSA_CERT_PATH.read_text()
        signed = sign_xml(tree, key, cert=cert)

        # Tamper with the document
        signed.set("tampered", "true")

        assert verify_signature(signed, cert=cert) is False

    def test_verify_invalid_input(self) -> None:
        """verify_signature should return False for invalid input."""
        assert verify_signature("not an element") is False  # type: ignore[arg-type]


class TestVerifySignatureStrict:
    """Tests for verify_signature_strict function."""

    def test_verify_valid_signature(self) -> None:
        """verify_signature_strict should not raise for valid signature with explicit cert."""
        tree = load_xml(SAMPLE_XML_PATH)
        key = load_private_key(RSA_KEY_PATH)
        cert = RSA_CERT_PATH.read_text()
        signed = sign_xml(tree, key, cert=cert)

        # Verify with explicit certificate (bypasses strict X.509 chain validation)
        verify_signature_strict(signed, cert=cert)

    def test_verify_unsigned_raises_value_error(self) -> None:
        """verify_signature_strict should raise ValueError for unsigned."""
        tree = load_xml(SAMPLE_XML_PATH)

        with pytest.raises(ValueError, match="No signature found"):
            verify_signature_strict(tree)

    def test_verify_invalid_input_raises_type_error(self) -> None:
        """verify_signature_strict should raise TypeError for invalid input."""
        with pytest.raises(TypeError):
            verify_signature_strict("not an element")  # type: ignore[arg-type]


class TestVerifyWithCertificate:
    """Tests for verify_with_certificate function."""

    def test_verify_with_valid_certificate(self) -> None:
        """verify_with_certificate should verify with valid cert."""
        tree = load_xml(SAMPLE_XML_PATH)
        key = load_private_key(RSA_KEY_PATH)
        cert = RSA_CERT_PATH.read_text()
        signed = sign_xml(tree, key, cert=cert)

        assert verify_with_certificate(signed, cert) is True

    def test_verify_with_invalid_certificate(self) -> None:
        """verify_with_certificate should raise for invalid cert."""
        tree = load_xml(SAMPLE_XML_PATH)
        key = load_private_key(RSA_KEY_PATH)
        signed = sign_xml(tree, key)

        with pytest.raises(ValueError, match="Invalid certificate"):
            verify_with_certificate(signed, "not a certificate")


class TestModuleExports:
    """Tests for module exports."""

    def test_all_exports_accessible(self) -> None:
        """All __all__ exports should be accessible."""
        from juxlib import signing

        expected = [
            "load_xml",
            "canonicalize_xml",
            "compute_canonical_hash",
            "load_private_key",
            "load_certificate",
            "get_public_key_from_certificate",
            "PrivateKey",
            "PublicKey",
            "sign_xml",
            "has_signature",
            "verify_signature",
            "verify_signature_strict",
            "verify_with_certificate",
            "verify_with_public_key",
        ]

        for name in expected:
            assert hasattr(signing, name), f"{name} not accessible"
