# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""Tests for signing module using shared JUnit XML fixtures.

These tests verify that juxlib.signing can handle real-world JUnit XML
files from the shared junit-xml-test-fixtures repository.
"""

from pathlib import Path

import pytest

from juxlib.signing import (
    canonicalize_xml,
    compute_canonical_hash,
    has_signature,
    load_private_key,
    load_xml,
    sign_xml,
    verify_signature,
)

from ..conftest import (
    FIXTURES_DIR,
    get_dump2polarion_xml_files,
    get_testmoapp_xml_files,
)

# Get fixture file lists for parametrization
TESTMOAPP_FILES = get_testmoapp_xml_files()
DUMP2POLARION_FILES = get_dump2polarion_xml_files()

# Test key paths
RSA_KEY_PATH = FIXTURES_DIR / "test-private.pem"
RSA_CERT_PATH = FIXTURES_DIR / "test-cert.pem"


@pytest.fixture
def rsa_key():
    """Load RSA private key for signing tests."""
    if not RSA_KEY_PATH.exists():
        pytest.skip("Test RSA key not available")
    return load_private_key(RSA_KEY_PATH)


@pytest.fixture
def rsa_cert_text():
    """Load RSA certificate as text for signing tests."""
    if not RSA_CERT_PATH.exists():
        pytest.skip("Test RSA certificate not available")
    return RSA_CERT_PATH.read_text()


@pytest.mark.shared_fixtures
class TestLoadXMLWithSharedFixtures:
    """Test load_xml with shared JUnit XML fixtures."""

    @pytest.mark.parametrize(
        "xml_file",
        TESTMOAPP_FILES,
        ids=lambda p: p.name if p else "none",
    )
    def test_load_testmoapp_examples(self, xml_file: Path) -> None:
        """Verify we can load all testmoapp example files."""
        if not xml_file.exists():
            pytest.skip(f"Fixture not available: {xml_file}")

        tree = load_xml(xml_file)

        # All testmoapp examples have testsuites or testsuite as root
        assert tree.tag in ("testsuites", "testsuite")

    @pytest.mark.parametrize(
        "xml_file",
        DUMP2POLARION_FILES[:10],  # Limit to first 10 for speed
        ids=lambda p: p.name if p else "none",
    )
    def test_load_dump2polarion_examples(self, xml_file: Path) -> None:
        """Verify we can load dump2polarion example files."""
        if not xml_file.exists():
            pytest.skip(f"Fixture not available: {xml_file}")

        tree = load_xml(xml_file)

        # dump2polarion files have testsuites as root
        assert tree.tag in ("testsuites", "testsuite")


@pytest.mark.shared_fixtures
class TestCanonicalizeWithSharedFixtures:
    """Test XML canonicalization with shared fixtures."""

    def test_canonicalize_junit_complete(self, junit_complete_xml: str) -> None:
        """Canonicalize complete JUnit XML produces consistent output."""
        tree = load_xml(junit_complete_xml)

        c14n_bytes = canonicalize_xml(tree)

        # C14N output should be bytes
        assert isinstance(c14n_bytes, bytes)
        # Should contain the XML content
        assert b"<testsuites" in c14n_bytes
        assert b"Tests.Registration" in c14n_bytes

    def test_canonicalize_produces_consistent_hash(
        self, junit_complete_xml: str
    ) -> None:
        """Same XML content produces same canonical hash."""
        tree1 = load_xml(junit_complete_xml)
        tree2 = load_xml(junit_complete_xml)

        hash1 = compute_canonical_hash(tree1)
        hash2 = compute_canonical_hash(tree2)

        assert hash1 == hash2

    @pytest.mark.parametrize(
        "xml_file",
        TESTMOAPP_FILES,
        ids=lambda p: p.name if p else "none",
    )
    def test_canonicalize_all_testmoapp_files(self, xml_file: Path) -> None:
        """All testmoapp files can be canonicalized."""
        if not xml_file.exists():
            pytest.skip(f"Fixture not available: {xml_file}")

        tree = load_xml(xml_file)
        c14n_bytes = canonicalize_xml(tree)

        assert isinstance(c14n_bytes, bytes)
        assert len(c14n_bytes) > 0


@pytest.mark.shared_fixtures
class TestSigningWithSharedFixtures:
    """Test XML signing with shared JUnit XML fixtures."""

    def test_sign_junit_complete(
        self, junit_complete_xml: str, rsa_key, rsa_cert_text
    ) -> None:
        """Sign complete JUnit XML file."""
        tree = load_xml(junit_complete_xml)

        signed_tree = sign_xml(tree, rsa_key, rsa_cert_text)

        assert has_signature(signed_tree)

    def test_sign_and_verify_junit_complete(
        self, junit_complete_xml: str, rsa_key, rsa_cert_text
    ) -> None:
        """Sign and verify complete JUnit XML file."""
        tree = load_xml(junit_complete_xml)
        signed_tree = sign_xml(tree, rsa_key, rsa_cert_text)

        # Verification should succeed (requires certificate for self-signed)
        is_valid = verify_signature(signed_tree, cert=rsa_cert_text)
        assert is_valid is True

    def test_sign_junit_basic(
        self, junit_basic_xml: str, rsa_key, rsa_cert_text
    ) -> None:
        """Sign basic JUnit XML file."""
        tree = load_xml(junit_basic_xml)

        signed_tree = sign_xml(tree, rsa_key, rsa_cert_text)

        assert has_signature(signed_tree)

    @pytest.mark.parametrize(
        "xml_file",
        TESTMOAPP_FILES,
        ids=lambda p: p.name if p else "none",
    )
    def test_sign_all_testmoapp_files(
        self, xml_file: Path, rsa_key, rsa_cert_text
    ) -> None:
        """All testmoapp files can be signed."""
        if not xml_file.exists():
            pytest.skip(f"Fixture not available: {xml_file}")

        tree = load_xml(xml_file)

        signed_tree = sign_xml(tree, rsa_key, rsa_cert_text)

        assert has_signature(signed_tree)

    @pytest.mark.parametrize(
        "xml_file",
        TESTMOAPP_FILES,
        ids=lambda p: p.name if p else "none",
    )
    def test_sign_and_verify_all_testmoapp_files(
        self, xml_file: Path, rsa_key, rsa_cert_text
    ) -> None:
        """All testmoapp files can be signed and verified."""
        if not xml_file.exists():
            pytest.skip(f"Fixture not available: {xml_file}")

        tree = load_xml(xml_file)
        signed_tree = sign_xml(tree, rsa_key, rsa_cert_text)

        # Verification requires certificate for self-signed certs
        is_valid = verify_signature(signed_tree, cert=rsa_cert_text)

        assert is_valid is True


@pytest.mark.shared_fixtures
class TestHashConsistencyWithSharedFixtures:
    """Test hash computation consistency with shared fixtures."""

    @pytest.mark.parametrize(
        "xml_file",
        TESTMOAPP_FILES,
        ids=lambda p: p.name if p else "none",
    )
    def test_hash_is_deterministic(self, xml_file: Path) -> None:
        """Same file produces same hash on multiple loads."""
        if not xml_file.exists():
            pytest.skip(f"Fixture not available: {xml_file}")

        tree1 = load_xml(xml_file)
        tree2 = load_xml(xml_file)

        hash1 = compute_canonical_hash(tree1)
        hash2 = compute_canonical_hash(tree2)

        assert hash1 == hash2

    def test_different_files_produce_different_hashes(
        self,
        junit_basic_xml: str,
        junit_complete_xml: str,
    ) -> None:
        """Different XML files produce different hashes."""
        tree1 = load_xml(junit_basic_xml)
        tree2 = load_xml(junit_complete_xml)

        hash1 = compute_canonical_hash(tree1)
        hash2 = compute_canonical_hash(tree2)

        assert hash1 != hash2


@pytest.mark.shared_fixtures
class TestXMLStructureWithSharedFixtures:
    """Test XML structure parsing with shared fixtures."""

    def test_junit_complete_has_properties(self, junit_complete_xml: str) -> None:
        """Complete JUnit XML has properties element."""
        tree = load_xml(junit_complete_xml)

        properties = tree.find(".//properties")

        assert properties is not None
        # Should have multiple property elements
        property_elements = properties.findall("property")
        assert len(property_elements) > 0

    def test_junit_complete_has_testcases(self, junit_complete_xml: str) -> None:
        """Complete JUnit XML has testcase elements."""
        tree = load_xml(junit_complete_xml)

        testcases = tree.findall(".//testcase")

        assert len(testcases) > 0
        # Each testcase should have name attribute
        for tc in testcases:
            assert tc.get("name") is not None

    def test_junit_complete_has_results(self, junit_complete_xml: str) -> None:
        """Complete JUnit XML has failure/error/skipped elements."""
        tree = load_xml(junit_complete_xml)

        failures = tree.findall(".//failure")
        errors = tree.findall(".//error")
        skipped = tree.findall(".//skipped")

        # junit-complete.xml should have at least one of each
        assert len(failures) >= 1
        assert len(errors) >= 1
        assert len(skipped) >= 1

    def test_extract_testsuite_attributes(self, junit_complete_xml: str) -> None:
        """Can extract testsuite attributes from complete JUnit XML."""
        tree = load_xml(junit_complete_xml)

        testsuite = tree.find(".//testsuite")

        assert testsuite is not None
        assert testsuite.get("name") == "Tests.Registration"
        assert testsuite.get("tests") == "8"
        assert testsuite.get("failures") == "1"
        assert testsuite.get("errors") == "1"
