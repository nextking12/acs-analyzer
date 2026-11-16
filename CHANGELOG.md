# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- CI workflow running lint, format check, and tests on pushes to `main` and
  pull requests.
- Package metadata: description, keywords, classifiers, and project URLs.
- `__version__` export in `access_control_analyzer`.
- This changelog.

### Changed

- README: added CI and license badges and a link to this changelog.

## [0.1.0] - 2026-08-19

### Added

- Streamlit interface for uploading cardholder CSV exports or running a
  built-in synthetic sample-data demo.
- Audit rules: expired active credential, missing or invalid expiration date
  on an active credential, duplicate nonblank badge number, and active
  credential missing a department.
- Severity summaries, rule and severity filters, findings CSV export, and a
  printable executive HTML report.
- Test suite covering the analyzer, loader, normalizer, presentation,
  reporting, and rules modules.
