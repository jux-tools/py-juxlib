# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>

"""End-to-end integration tests for sign → store → publish workflow.

These tests verify that the signing, storage, and API client modules
work together correctly in a realistic pipeline scenario.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import responses
from lxml import etree

from juxlib.api import JuxAPIClient, PublishResponse
from juxlib.signing import (
    compute_canonical_hash,
    has_signature,
    load_private_key,
    load_xml,
    sign_xml,
    verify_signature,
)
from juxlib.storage import ReportStorage

if TYPE_CHECKING:
    from pathlib import Path


class TestSignStorePublish:
    """End-to-end: sign XML → store locally → publish to API."""

    @responses.activate
    def test_rsa_sign_store_publish(
        self,
        tmp_path: Path,
        sample_xml_path: Path,
        rsa_private_key_path: Path,
        rsa_certificate_path: Path,
    ) -> None:
        """Full pipeline with RSA signing."""
        # 1. Load and sign
        tree = load_xml(sample_xml_path)
        key = load_private_key(rsa_private_key_path)
        cert_pem = rsa_certificate_path.read_text()
        signed_tree = sign_xml(tree, key, cert=cert_pem)

        assert has_signature(signed_tree)

        # 2. Serialize and compute hash
        signed_xml_bytes = etree.tostring(
            signed_tree, xml_declaration=True, encoding="UTF-8"
        )
        canonical_hash = compute_canonical_hash(signed_tree)

        # 3. Store locally
        storage = ReportStorage(tmp_path)
        storage.store_report(signed_xml_bytes, canonical_hash)

        assert storage.report_exists(canonical_hash)

        # 4. Publish to API
        responses.post(
            "http://localhost:4000/api/v1/junit/submit",
            json={
                "test_run_id": "550e8400-e29b-41d4-a716-446655440000",
                "message": "Test report submitted successfully",
                "test_count": 3,
                "failure_count": 0,
                "error_count": 0,
                "skipped_count": 0,
                "success_rate": 100.0,
            },
            status=201,
        )

        with JuxAPIClient(api_url="http://localhost:4000/api/v1") as client:
            response = client.publish_report(signed_xml_bytes.decode("utf-8"))

        assert isinstance(response, PublishResponse)
        assert response.test_run_id == "550e8400-e29b-41d4-a716-446655440000"
        assert response.test_count == 3

        # 5. Verify stored content matches what was published
        stored_content = storage.get_report(canonical_hash)
        assert stored_content == signed_xml_bytes

    @responses.activate
    def test_ecdsa_sign_store_publish(
        self,
        tmp_path: Path,
        sample_xml_path: Path,
        ec_private_key_path: Path,
        ec_certificate_path: Path,
    ) -> None:
        """Full pipeline with ECDSA signing."""
        tree = load_xml(sample_xml_path)
        key = load_private_key(ec_private_key_path)
        cert_pem = ec_certificate_path.read_text()
        signed_tree = sign_xml(tree, key, cert=cert_pem)

        assert has_signature(signed_tree)

        signed_xml_bytes = etree.tostring(
            signed_tree, xml_declaration=True, encoding="UTF-8"
        )
        canonical_hash = compute_canonical_hash(signed_tree)

        storage = ReportStorage(tmp_path)
        storage.store_report(signed_xml_bytes, canonical_hash)

        responses.post(
            "http://localhost:4000/api/v1/junit/submit",
            json={
                "test_run_id": "660e8400-e29b-41d4-a716-446655440001",
                "message": "Test report submitted successfully",
                "test_count": 3,
                "failure_count": 0,
                "error_count": 0,
                "skipped_count": 0,
                "success_rate": 100.0,
            },
            status=201,
        )

        with JuxAPIClient(api_url="http://localhost:4000/api/v1") as client:
            response = client.publish_report(signed_xml_bytes.decode("utf-8"))

        assert response.test_run_id == "660e8400-e29b-41d4-a716-446655440001"
        assert storage.report_exists(canonical_hash)


class TestQueueThenPublish:
    """End-to-end: sign → queue (offline) → dequeue and publish."""

    @responses.activate
    def test_offline_queue_then_publish(
        self,
        tmp_path: Path,
        sample_xml_path: Path,
        rsa_private_key_path: Path,
    ) -> None:
        """Simulate offline scenario: queue report, then publish later."""
        # 1. Sign report
        tree = load_xml(sample_xml_path)
        key = load_private_key(rsa_private_key_path)
        signed_tree = sign_xml(tree, key)
        signed_xml_bytes = etree.tostring(
            signed_tree, xml_declaration=True, encoding="UTF-8"
        )
        canonical_hash = compute_canonical_hash(signed_tree)

        # 2. Queue (offline)
        storage = ReportStorage(tmp_path)
        storage.queue_report(signed_xml_bytes, canonical_hash)

        assert storage.queued_report_exists(canonical_hash)
        assert not storage.report_exists(canonical_hash)

        # 3. Later: retrieve queued report and publish
        queued = storage.list_queued_reports()
        assert len(queued) == 1

        queued_content = storage.get_queued_report(canonical_hash)

        responses.post(
            "http://localhost:4000/api/v1/junit/submit",
            json={
                "test_run_id": "770e8400-e29b-41d4-a716-446655440002",
                "message": "Test report submitted successfully",
                "test_count": 3,
                "failure_count": 0,
                "error_count": 0,
                "skipped_count": 0,
                "success_rate": 100.0,
            },
            status=201,
        )

        with JuxAPIClient(api_url="http://localhost:4000/api/v1") as client:
            response = client.publish_report(queued_content.decode("utf-8"))

        assert response.test_run_id == "770e8400-e29b-41d4-a716-446655440002"

        # 4. Dequeue after successful publish
        storage.dequeue_report(canonical_hash)

        assert storage.report_exists(canonical_hash)
        assert not storage.queued_report_exists(canonical_hash)


class TestSignatureVerificationRoundTrip:
    """End-to-end: sign → store → retrieve → verify signature."""

    def test_stored_report_signature_is_valid(
        self,
        tmp_path: Path,
        sample_xml_path: Path,
        rsa_private_key_path: Path,
        rsa_certificate_path: Path,
    ) -> None:
        """Signature should remain valid after storage round-trip."""
        # Sign
        tree = load_xml(sample_xml_path)
        key = load_private_key(rsa_private_key_path)
        cert_pem = rsa_certificate_path.read_text()
        signed_tree = sign_xml(tree, key, cert=cert_pem)
        signed_xml_bytes = etree.tostring(
            signed_tree, xml_declaration=True, encoding="UTF-8"
        )
        canonical_hash = compute_canonical_hash(signed_tree)

        # Store and retrieve
        storage = ReportStorage(tmp_path)
        storage.store_report(signed_xml_bytes, canonical_hash)
        retrieved = storage.get_report(canonical_hash)

        # Verify signature on retrieved content
        retrieved_tree = load_xml(retrieved)
        assert has_signature(retrieved_tree)
        verify_signature(retrieved_tree)

    def test_hash_deduplication_across_signs(
        self,
        tmp_path: Path,
        sample_xml_path: Path,
        rsa_private_key_path: Path,
    ) -> None:
        """Same XML signed twice should produce same canonical hash."""
        tree1 = load_xml(sample_xml_path)
        tree2 = load_xml(sample_xml_path)
        key = load_private_key(rsa_private_key_path)

        # Compute hash before signing (canonical hash is content-based)
        hash1 = compute_canonical_hash(tree1)
        hash2 = compute_canonical_hash(tree2)

        assert hash1 == hash2

        # Store both — should deduplicate
        storage = ReportStorage(tmp_path)
        signed1 = sign_xml(tree1, key)
        signed1_bytes = etree.tostring(signed1, xml_declaration=True, encoding="UTF-8")
        storage.store_report(signed1_bytes, hash1)
        storage.store_report(signed1_bytes, hash1)  # Same hash overwrites

        reports = storage.list_reports()
        assert len(reports) == 1


class TestStorageStatisticsAfterPipeline:
    """End-to-end: verify storage statistics after pipeline operations."""

    def test_stats_reflect_pipeline(
        self,
        tmp_path: Path,
        sample_xml_path: Path,
        rsa_private_key_path: Path,
    ) -> None:
        """Storage stats should accurately reflect pipeline operations."""
        tree = load_xml(sample_xml_path)
        key = load_private_key(rsa_private_key_path)
        signed_tree = sign_xml(tree, key)
        signed_xml_bytes = etree.tostring(
            signed_tree, xml_declaration=True, encoding="UTF-8"
        )
        canonical_hash = compute_canonical_hash(signed_tree)

        storage = ReportStorage(tmp_path)

        # Initially empty
        stats = storage.get_stats()
        assert stats["total_reports"] == 0
        assert stats["queued_reports"] == 0

        # Queue a report
        storage.queue_report(signed_xml_bytes, canonical_hash)
        stats = storage.get_stats()
        assert stats["queued_reports"] == 1
        assert stats["total_reports"] == 0

        # Dequeue (simulating successful publish)
        storage.dequeue_report(canonical_hash)
        stats = storage.get_stats()
        assert stats["total_reports"] == 1
        assert stats["queued_reports"] == 0
        assert stats["total_size"] > 0
