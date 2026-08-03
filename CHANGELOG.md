# Changelog

All notable changes to IMIE Core will be documented in this file.

The project follows Semantic Versioning.

## Unreleased

### Added

### Changed

### Fixed

## 0.4.0 - 2026-08-03

### Added

- Institutional Market Phase Engine milestone.
- IMIE runtime console command: `imie-runtime`.
- Runtime and test dependency declarations.
- Package metadata validation tests.
- GitHub Actions testing on Python 3.12 and Python 3.14.
- Package build, distribution validation, and clean-install smoke testing.
- Automated GitHub Release workflow.
- Wheel and source-distribution release artifacts.

### Changed

- Package version synchronized across `pyproject.toml` and `src/imie/version.py`.
- Runtime provider imports deferred to avoid unnecessary Alpaca SDK loading.
- Runtime documentation and setup instructions expanded.
- Generated package metadata and build artifacts excluded from Git.
- Generated runtime-history files excluded from Git.

### Fixed

- Python 3.12 compatibility for frozen director dataclasses.
- Provider override tests isolated from the Alpaca SDK.
- Runtime dashboard temporary-file validation and replacement handling.
- Temporary file fingerprint typing.

[Unreleased]: https://github.com/tonnydulo/IMIE-Core/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/tonnydulo/IMIE-Core/releases/tag/v0.4.0
