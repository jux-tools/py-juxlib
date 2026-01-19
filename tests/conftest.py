# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""Shared pytest fixtures for py-juxlib tests.

This module provides fixtures for accessing:
- Local test fixtures (keys, certificates, sample XML)
- Shared JUnit XML test fixtures from junit-xml-test-fixtures repository
"""

from collections.abc import Iterator
from pathlib import Path

import pytest

# =============================================================================
# Path Constants
# =============================================================================

# Local fixtures directory (keys, certs, sample XML)
FIXTURES_DIR = Path(__file__).parent / "fixtures"

# Shared JUnit XML test fixtures repository
# Located at: ../junit-xml-test-fixtures/ relative to py-juxlib
SHARED_FIXTURES_DIR = Path(__file__).parent.parent.parent / "junit-xml-test-fixtures"

# Key subdirectories in shared fixtures
TESTMOAPP_EXAMPLES = SHARED_FIXTURES_DIR / "testmoapp" / "examples"
DUMP2POLARION_DATA = SHARED_FIXTURES_DIR / "dump2polarion" / "tests" / "data"
WINDYROAD_SCHEMA = SHARED_FIXTURES_DIR / "windyroad-junit-schema"


# =============================================================================
# Local Fixtures
# =============================================================================


@pytest.fixture
def fixtures_dir() -> Path:
    """Path to local test fixtures directory."""
    return FIXTURES_DIR


@pytest.fixture
def rsa_private_key_path() -> Path:
    """Path to RSA private key for testing."""
    return FIXTURES_DIR / "test-private.pem"


@pytest.fixture
def rsa_certificate_path() -> Path:
    """Path to RSA certificate for testing."""
    return FIXTURES_DIR / "test-cert.pem"


@pytest.fixture
def ec_private_key_path() -> Path:
    """Path to EC private key for testing."""
    return FIXTURES_DIR / "test-ec-private.pem"


@pytest.fixture
def ec_certificate_path() -> Path:
    """Path to EC certificate for testing."""
    return FIXTURES_DIR / "test-ec-cert.pem"


@pytest.fixture
def sample_xml_path() -> Path:
    """Path to local sample JUnit XML report."""
    return FIXTURES_DIR / "sample-report.xml"


@pytest.fixture
def sample_xml_content(sample_xml_path: Path) -> str:
    """Content of local sample JUnit XML report."""
    return sample_xml_path.read_text()


# =============================================================================
# Shared JUnit XML Fixtures
# =============================================================================


@pytest.fixture
def shared_fixtures_available() -> bool:
    """Check if shared junit-xml-test-fixtures repository is available."""
    return SHARED_FIXTURES_DIR.exists() and TESTMOAPP_EXAMPLES.exists()


@pytest.fixture
def shared_fixtures_dir() -> Path:
    """Path to shared junit-xml-test-fixtures repository.

    Raises:
        pytest.skip: If shared fixtures are not available
    """
    if not SHARED_FIXTURES_DIR.exists():
        pytest.skip("Shared junit-xml-test-fixtures not available")
    return SHARED_FIXTURES_DIR


@pytest.fixture
def testmoapp_examples_dir(shared_fixtures_dir: Path) -> Path:
    """Path to testmoapp/examples directory with reference JUnit XML files."""
    examples_dir = shared_fixtures_dir / "testmoapp" / "examples"
    if not examples_dir.exists():
        pytest.skip("testmoapp/examples not available")
    return examples_dir


@pytest.fixture
def junit_basic_xml(testmoapp_examples_dir: Path) -> str:
    """Content of junit-basic.xml - basic JUnit XML structure."""
    return (testmoapp_examples_dir / "junit-basic.xml").read_text()


@pytest.fixture
def junit_complete_xml(testmoapp_examples_dir: Path) -> str:
    """Content of junit-complete.xml - complete JUnit XML with all features."""
    return (testmoapp_examples_dir / "junit-complete.xml").read_text()


@pytest.fixture
def junit_conventions_xml(testmoapp_examples_dir: Path) -> str:
    """Content of conventions.xml - advanced conventions and patterns."""
    return (testmoapp_examples_dir / "conventions.xml").read_text()


@pytest.fixture
def junit_testcase_properties_xml(testmoapp_examples_dir: Path) -> str:
    """Content of testcase-properties.xml - property patterns."""
    return (testmoapp_examples_dir / "testcase-properties.xml").read_text()


@pytest.fixture
def junit_testcase_output_xml(testmoapp_examples_dir: Path) -> str:
    """Content of testcase-output.xml - output capture patterns."""
    return (testmoapp_examples_dir / "testcase-output.xml").read_text()


# =============================================================================
# Parametrized Fixture Helpers
# =============================================================================


def get_testmoapp_xml_files() -> list[Path]:
    """Get all XML files from testmoapp/examples for parametrized tests."""
    if not TESTMOAPP_EXAMPLES.exists():
        return []
    return sorted(TESTMOAPP_EXAMPLES.glob("*.xml"))


def get_dump2polarion_xml_files() -> list[Path]:
    """Get all XML files from dump2polarion/tests/data for parametrized tests."""
    if not DUMP2POLARION_DATA.exists():
        return []
    return sorted(DUMP2POLARION_DATA.glob("*.xml"))


def get_all_shared_xml_files() -> list[Path]:
    """Get all shared XML fixture files for comprehensive testing."""
    files = []
    files.extend(get_testmoapp_xml_files())
    files.extend(get_dump2polarion_xml_files())
    return files


# =============================================================================
# Pytest Markers
# =============================================================================


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "shared_fixtures: tests that require shared junit-xml-test-fixtures",
    )


# =============================================================================
# Autouse Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def skip_shared_fixture_tests(request: pytest.FixtureRequest) -> Iterator[None]:
    """Skip tests marked with shared_fixtures if fixtures unavailable."""
    marker = request.node.get_closest_marker("shared_fixtures")
    if marker is not None and not SHARED_FIXTURES_DIR.exists():
        pytest.skip("Shared junit-xml-test-fixtures not available")
    yield
