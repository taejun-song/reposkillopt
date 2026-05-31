---
id: RL-YYYYMMDDTHHMMSS-<adapter>
agent: <identifier — e.g., "Claude Code">
agent_version: <if known, otherwise omit>
adapter: <claude-code|codex|opencode|generic>
skill_version: 0.1.0
canonical_version: 0.1.0
task: <one-line description of what the user asked>
started: <YYYY-MM-DDTHH:MM:SSZ>
ended: <YYYY-MM-DDTHH:MM:SSZ>
spec_id: <Repository Specification id this rollout produced or revised>
---

# Rollout Log <RL-YYYYMMDDTHHMMSS-adapter>

<!--
Filename convention: RL-YYYYMMDDTHHMMSS-<adapter>.md
Location:           .reposkillopt/rollouts/ inside the target repository

Produce ONE rollout log per session that creates or revises a Repository Specification.
canonical_version MUST match what the adapter mirrors (FR-027a).
-->

## Files inspected

<!-- Bullet list of paths examined this session. Include line ranges where applicable.
     Example:
     - src/click/core.py:1-300
     - pyproject.toml
     - tests/test_basic.py
-->

## Claims produced

<!-- Bullet list of major claims emitted (or revised) in this session, each prefixed with its R10 label and any citation(s).
     Example:
     - **[fact]** Click's primary entrypoint decorator is `click.command` (src/click/decorators.py:170-205).
     - **[inference]** The project predates type hints in some legacy modules; basis: presence of `# type: ignore` annotations.
-->

## Human feedback received this session

<!-- Bullet list of Feedback Item ids touched this session, each annotated with its disposition.
     Example:
     - FB-2026-05-31-001 (applied)
     - FB-2026-05-31-002 (applied)
     - FB-2026-05-31-003 (deferred — repository-scoped terminology; recorded in spec as **[human]** only)
-->

## Revisions applied

<!-- Bullet list of (Spec section → change). Use this list to drive the Repository Specification's own Change log appendix.
     Example:
     - Major entrypoints → replaced superseded claim; added new **[fact]** with citation.
     - Domain model → added **[human]** terminology note citing FB-2026-05-31-003.
-->

## Notes

<!-- Optional. Anything cross-cutting that may inform a future Skill Edit Proposal — adapter-specific surprises, recurring weaknesses, etc. -->
