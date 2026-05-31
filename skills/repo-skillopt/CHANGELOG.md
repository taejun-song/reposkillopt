# Canonical Skill Changelog

All notable changes to `skills/repo-skillopt/SKILL.md` are recorded here in [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format. Versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Each entry's `version:` field matches the `version:` in `SKILL.md`. Adapters' `canonical_version:` fields MUST point at a version listed below.

## [0.2.0] — 2026-06-01

### Added

- **Validation gate for the Skill Convergence Loop** (step 6): a `scope: generic` Skill Edit Proposal may move to `status: accepted` only after passing a validation gate — regenerating specifications for a held-out reference set (disjoint from the repositories that motivated it) with no per-dimension rubric regression, no deterministic-check regression, and the expected effect realized (or waived). The run is recorded as a Validation Gate Report referenced by the proposal. Methodology in `rubric/validation-gate.md` + `rubric/held-out-set.md`; reports in `rubric/gates/`.

### Changed

- Renumbered the former Skill Convergence Loop step 7 ("Prefer edits that generalize") to step 8; the apply-accepted step is now step 7 and is gated by step 6. Additive/clarifying — no required canonical instruction was weakened or removed (minor bump).

## [0.1.0] — 2026-05-31

### Added

- Initial canonical skill (`SKILL.md`) — vendor-neutral, Markdown-first.
- Nine required sections: Purpose, Trigger Conditions, Operating Principles, Repository Understanding Workflow, Repository Specification Format, Human Feedback Loop, Skill Convergence Loop, Output Discipline.
- Four authoring templates (`templates/repository-specification.md`, `human-feedback.md`, `rollout-log.md`, `skill-edit-proposal.md`).
- `**[fact]**` / `**[inference]**` / `**[unknown]**` / `**[human]**` label notation (R10).
- Standard on-disk layout convention: `.reposkillopt/{specs,feedback,rollouts,proposals}/` at the target repository root.
- Skill Convergence Loop with six bounded edit kinds: ADD, REPLACE, DELETE, REORDER, SPECIALIZE, GENERALIZE.
