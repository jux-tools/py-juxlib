# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial project structure with Diátaxis documentation framework
- Foundation ADRs (0001, 0002, 0003, 0004)
- Package skeleton for juxlib modules:
  - `juxlib.metadata` - Environment and Git/CI metadata detection
  - `juxlib.signing` - XML digital signature creation and verification
  - `juxlib.api` - HTTP client for Jux OpenAPI servers
  - `juxlib.config` - Configuration management with multi-source loading
  - `juxlib.storage` - Local filesystem storage with offline queue
  - `juxlib.errors` - User-friendly error handling framework

[Unreleased]: https://github.com/jrjsmrtn/py-juxlib/compare/v0.1.0...HEAD
