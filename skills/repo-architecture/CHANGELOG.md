# Canonical Skill Changelog — repo-architecture

[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) + [SemVer](https://semver.org/). Each
entry's `version:` matches `SKILL.md`; adapters' `canonical_version:` point at a version below.

## [0.1.0] — 2026-06-21

### Added

- Initial release of the **repo-architecture** skill (feature 019), part of the as-is → to-be → orchestrate
  extension. Vendor-neutral; reuses the existing Feedback Item / Skill Edit Proposal / validation-gate
  machinery; ships rubric dimensions (`rubric/architecture*-rubric.md`) and deterministic checks
  (`reposkillopt_engine/artifact_checks.py`). Mirrored into all four adapters (`canonical_version: 0.1.0`).
