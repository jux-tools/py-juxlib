// SPDX-FileCopyrightText: 2026 Georges Martin <jrjsmrtn@gmail.com>
// SPDX-License-Identifier: Apache-2.0

/*
 * py-juxlib Architecture (C4 Model)
 *
 * Shared Python client library for JUnit XML test report enrichment,
 * signing, storage, and publishing. Used by pytest-jux and behave-jux.
 *
 * Version: 0.3.0
 */

workspace "py-juxlib" "Shared Python client library for JUnit XML test report operations" {

    model {
        # People
        developer = person "Developer" "Builds test report tooling using py-juxlib"

        # External Systems
        pytestJux = softwareSystem "pytest-jux" "pytest plugin that delegates to py-juxlib" "External System"
        behaveJux = softwareSystem "behave-jux" "behave plugin that delegates to py-juxlib" "External System"
        juxApiServer = softwareSystem "Jux API Server" "Server that receives and stores signed test reports" "External System"
        juxOpenapi = softwareSystem "jux-openapi" "REST API specification (source of truth)" "Specification"

        # py-juxlib System
        pyJuxlib = softwareSystem "py-juxlib" "Shared Python client library for JUnit XML test report operations" {

            metadataContainer = container "Metadata" "Environment metadata detection: system, Git, CI/CD" "Python package (metadata/)" {
                captureMetadata = component "capture_metadata()" "Main entry point: captures system, Git, CI metadata" "Python function (detection.py)"
                envMetadata = component "EnvironmentMetadata" "Dataclass with to_dict(), to_json(), from_dict(), from_json()" "Python dataclass (models.py)"
                gitDetector = component "Git Detector" "capture_git_info(), is_git_repository(): commit, branch, status, remote" "Python module (git.py)"
                ciDetector = component "CI Detector" "detect_ci_provider(), is_ci_environment(): GitHub Actions, GitLab CI, Jenkins, etc." "Python module (ci.py)"
                projectDetector = component "Project Detector" "detect_project_name(): infers from pyproject.toml, setup.cfg, or directory" "Python module (project.py)"

                captureMetadata -> envMetadata "Populates"
                captureMetadata -> gitDetector "Captures Git info"
                captureMetadata -> ciDetector "Detects CI provider"
                captureMetadata -> projectDetector "Detects project name"
            }

            signingContainer = container "Signing" "XML digital signature operations (XMLDSig)" "Python package (signing/)" {
                signerFn = component "sign_xml()" "Applies enveloped XMLDSig signature (RSA-SHA256 or ECDSA-SHA256)" "Python function (signer.py)"
                verifierFn = component "verify_signature()" "Verifies XMLDSig signature; strict and certificate modes" "Python function (verifier.py)"
                keyLoader = component "Key Loader" "load_private_key(), load_certificate(), get_public_key_from_certificate()" "Python module (keys.py)"
                xmlUtils = component "XML Utilities" "load_xml(), canonicalize_xml(), compute_canonical_hash(), has_signature()" "Python module (xml.py)"

                signerFn -> xmlUtils "Canonicalizes before signing"
                signerFn -> keyLoader "Loads private key"
                verifierFn -> xmlUtils "Canonicalizes for verification"
                verifierFn -> keyLoader "Loads certificate"
            }

            apiContainer = container "API Client" "HTTP client for Jux API v1.0.0" "Python package (api/)" {
                juxClient = component "JuxAPIClient" "publish_report(): POST /api/v1/junit/submit with retry and auth" "Python class (client.py)"
                apiModels = component "API Models" "PublishResponse, TestRun: Pydantic models for API payloads" "Python module (models.py)"

                juxClient -> apiModels "Uses response models"
            }

            configContainer = container "Configuration" "Multi-source configuration management" "Python package (config/)" {
                configManager = component "ConfigurationManager" "Loads from explicit, CLI, env, files, defaults with precedence" "Python class (manager.py)"
                configSchema = component "ConfigSchema" "Schema definition, field metadata, validation rules" "Python class (schema.py)"
                storageMode = component "StorageMode" "Enum: LOCAL, REMOTE, HYBRID" "Python enum (schema.py)"

                configManager -> configSchema "Validates against"
            }

            storageContainer = container "Storage" "Local filesystem storage for reports and offline queue" "Python package (storage/)" {
                reportStorage = component "ReportStorage" "store_report(), queue_report(), dequeue_report(): atomic writes, XDG paths" "Python class (filesystem.py)"

                reportStorage -> storageMode "Uses storage mode"
            }

            errorsContainer = container "Errors" "JuxError exception hierarchy with error codes and Rich formatting" "Python package (errors/)" "Supporting" {
                errorCodes = component "ErrorCode" "Enum: 1xx file, 2xx key, 3xx XML, 4xx config, 5xx storage, 6xx API, 9xx generic" "Python enum (codes.py)"
                errorClasses = component "Exception Classes" "JuxError base + 18 specific exceptions with suggestions" "Python module (exceptions.py)"
            }
        }

        # Relationships - External consumers
        pytestJux -> pyJuxlib "Re-exports signing, config, storage, API, metadata" "Python import"
        behaveJux -> pyJuxlib "Uses metadata, signing, API" "Python import"
        developer -> pyJuxlib "Builds tooling with" "Python API"
        pyJuxlib -> juxApiServer "Publishes reports to" "HTTPS/REST (POST /api/v1/junit/submit)"
        pyJuxlib -> juxOpenapi "Implements" "Specification"

        # Relationships - Container level
        developer -> metadataContainer "Captures environment info" "Python API"
        developer -> signingContainer "Signs and verifies reports" "Python API"
        developer -> apiContainer "Publishes reports" "Python API"
        developer -> configContainer "Manages configuration" "Python API"
        developer -> storageContainer "Stores reports locally" "Python API"

        # Relationships - Cross-container
        apiContainer -> juxApiServer "Publishes reports via" "HTTPS/REST"
        apiContainer -> configContainer "Reads API URL, auth, timeouts"
        storageContainer -> configContainer "Reads storage mode, path"
        storageContainer -> apiContainer "Retries queued reports via"
    }

    views {
        systemContext pyJuxlib "SystemContext" {
            include *
            autolayout lr
            description "py-juxlib: shared library consumed by pytest-jux and behave-jux plugins"
        }

        container pyJuxlib "Containers" {
            include *
            autolayout lr
            description "Six modules: metadata, signing, API, config, storage, errors"
        }

        component metadataContainer "MetadataComponents" {
            include *
            autolayout lr
            description "Environment metadata detection: system, Git, CI/CD"
        }

        component signingContainer "SigningComponents" {
            include *
            autolayout lr
            description "XMLDSig signing and verification with key management"
        }

        component apiContainer "APIComponents" {
            include *
            autolayout lr
            description "HTTP client for Jux API with Pydantic models"
        }

        component configContainer "ConfigComponents" {
            include *
            autolayout lr
            description "Multi-source configuration with schema validation"
        }

        dynamic pyJuxlib "PublishFlow" "Report publish workflow" {
            developer -> metadataContainer "1. capture_metadata()"
            developer -> signingContainer "2. sign_xml() (optional)"
            developer -> apiContainer "3. JuxAPIClient.publish_report()"
            apiContainer -> juxApiServer "4. POST /api/v1/junit/submit"
            autolayout lr
        }

        dynamic pyJuxlib "OfflineFlow" "Offline storage and retry workflow" {
            developer -> storageContainer "1. queue_report() (API unavailable)"
            developer -> storageContainer "2. list_queued_reports()"
            storageContainer -> apiContainer "3. Retry: publish_report()"
            apiContainer -> juxApiServer "4. POST /api/v1/junit/submit"
            autolayout lr
        }

        styles {
            element "Software System" {
                background #1168bd
                color #ffffff
                shape RoundedBox
            }
            element "External System" {
                background #999999
                color #ffffff
            }
            element "Specification" {
                background #6a1b9a
                color #ffffff
            }
            element "Person" {
                background #08427b
                color #ffffff
                shape Person
            }
            element "Container" {
                background #438dd5
                color #ffffff
                shape RoundedBox
            }
            element "Supporting" {
                background #85bbf0
                color #000000
            }
            element "Component" {
                background #85bbf0
                color #000000
                shape Component
            }
        }

        theme default
    }

    configuration {
        scope softwaresystem
    }
}
