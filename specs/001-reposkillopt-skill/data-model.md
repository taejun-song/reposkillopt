# Phase 1 Data Model — RepoSkillOpt Artifact Schemas

**Feature**: 001-reposkillopt-skill
**Date**: 2026-05-31

This project ships no application data. Its "data model" is a set of **artifact schemas** — the structures of the Markdown files the project produces or expects. Each schema below lists required front matter (or metadata block), required sections, field-level rules, identifier conventions, and lifecycle states.

## Conventions

- All artifacts are CommonMark Markdown.
- All artifacts that support YAML front matter use the standard `---` delimiter.
- Artifacts in environments that forbid YAML front matter use the HTML-comment metadata block from Phase 0 R3:
  ```
  <!-- repo-skillopt-meta
  key: value
  -->
  ```
- All filenames are kebab-case unless an external tool requires otherwise.
- All timestamps are ISO-8601 (`YYYY-MM-DD` for date-only, `YYYY-MM-DDTHH:MM:SSZ` for full).
- Identifier slugs use kebab-case and are stable for the lifetime of the artifact.
- Claim labels follow R10: `**[fact]**`, `**[inference]**`, `**[unknown]**`, `**[human]**`.
- Citations use the form `path/to/file.ext:line` or `path/to/file.ext:start-end`; symbol form is `path/to/file.ext:Symbol` or `path/to/file.ext:Symbol:line`.

---

## 1. Canonical Skill — `skills/repo-skillopt/SKILL.md`

**Front matter (required)**:
```yaml
---
name: repo-skillopt
description: <one-line description; must include the trigger conditions from FR-004>
version: <semver MAJOR.MINOR.PATCH>           # FR-027a
---
```
**Front matter (optional)**: `model`, `triggers`, `keywords`.

**Required sections** (in order, per FR-003):
1. `# RepoSkillOpt — Canonical Skill`
2. `## Purpose`
3. `## Trigger Conditions`
4. `## Operating Principles`
5. `## Repository Understanding Workflow` (must list FR-012 stages a–g in order)
6. `## Repository Specification Format` (must reference the template and list FR-005 sections)
7. `## Human Feedback Loop`
8. `## Skill Convergence Loop`
9. `## Output Discipline`

**Section-level rules**:
- *Trigger Conditions* must contain the FR-004 enumerated triggers verbatim or as a recognizable paraphrase.
- *Operating Principles* must contain a bullet for each FR-007 / FR-008 / FR-009 / FR-010 / FR-011 rule.
- *Repository Understanding Workflow* must list FR-012 stages (a)–(g).
- *Output Discipline* must require the four-way label categorization per FR-008 using the R10 notation.

**Versioning**: `version:` increments per semver semantics. Major bumps for changes that break the adapter-equivalence checklist; minor for additive instructions; patch for clarifications.

---

## 2. Canonical Skill Changelog — `skills/repo-skillopt/CHANGELOG.md`

**Format**: Keep a Changelog. Reverse chronological. Versions are headings:
```markdown
## [0.1.0] — 2026-05-31
### Added
- Initial canonical skill.
```
Entries reference the `version:` in `SKILL.md`. No front matter.

---

## 3. Adapter — `adapters/<target>/<adapter-file>`

**Targets and files**:
| Target | File | Metadata mechanism |
|---|---|---|
| `claude-code` | `SKILL.md` | YAML front matter |
| `codex` | `AGENTS.md` | HTML-comment metadata block |
| `opencode` | `AGENTS.md` | HTML-comment metadata block |
| `generic` | `skill.md` (+ `system-prompt-fragment.md`) | YAML front matter |

**Required metadata** (front matter or comment block):
- `canonical_version: <semver>` — must match an existing canonical `version`.
- `adapter: <target>` — one of `claude-code`, `codex`, `opencode`, `generic`.

**Required content equivalence** (FR-024, FR-025): every required section of the canonical skill (R1–9 above) must be present in the adapter, in the same order, preserving rule strength. Adapters may *add* per-environment notes after the canonical content but must not weaken or remove any canonical instruction. The Adapter Equivalence contract enforces this.

**Lifecycle**: adapter `canonical_version` is bumped lockstep with canonical version bumps. An adapter whose `canonical_version` does not resolve to an existing canonical version is invalid.

---

## 4. Repository Specification — `.reposkillopt/specs/repository-specification.md`

**Front matter**:
```yaml
---
spec_id: <slug>                       # e.g., "click-8.1.7"
target_repository: <name>
target_repository_url: <url>          # if applicable
target_repository_commit: <sha or tag>
skill_version: <semver of SKILL.md used>
adapter: <claude-code|codex|opencode|generic>
created: <ISO date>
revised: <ISO date>                   # updated on every revision
revision: <integer; starts at 1>
status: <draft|revised|superseded>
---
```

**Required sections** (FR-005, all 19, in order):
1. `## Repository overview`
2. `## Technology stack`
3. `## Build and runtime commands`
4. `## Major entrypoints`
5. `## Architectural layers`
6. `## Core modules`
7. `## Domain model`
8. `## Data model`
9. `## External integrations`
10. `## Control-flow traces`
11. `## Data-flow traces`
12. `## Dependency map`
13. `## Configuration map`
14. `## Testing strategy`
15. `## Deployment assumptions`
16. `## Change-impact map`
17. `## Known risks`
18. `## Unknowns and unresolved questions`
19. `## Evidence index`

**Optional appendix**: `## Change log` (per FR-006 / SC-007), bullet per revision noting which feedback items were applied.

**Rules**:
- Every major claim (FR-008) in any section MUST carry one of the R10 labels (`**[fact]**` / `**[inference]**` / `**[unknown]**` / `**[human]**`).
- `**[fact]**` claims MUST be followed by at least one citation in the form defined under Conventions.
- `**[unknown]**` claims appear (or are referenced) under the *Unknowns and unresolved questions* section.
- `**[human]**` claims cite the originating Feedback Item id.
- The *Evidence index* lists every citation appearing in the document; duplicates are de-duplicated.

**State transitions**:
```
draft  ──first save──▶  revised ──new revision──▶ revised  ──explicit replacement──▶ superseded
```

---

## 5. Human Feedback Item — `.reposkillopt/feedback/<id>.md`

**Filename / id convention**: `FB-YYYY-MM-DD-NNN-<slug>.md`. The id (`FB-YYYY-MM-DD-NNN`) is stable.

**Front matter** (per FR-013):
```yaml
---
id: FB-YYYY-MM-DD-NNN
timestamp: <ISO datetime>
author: <optional, free-form>
type: <correction|confirmation|missing-context|terminology|quality-rating|avoid-path|deeper-analysis|criticism-of-claim|format|detail-level|cross-agent-difference>
references:
  - spec_id: <spec slug>
    claim_ref: <section header or quoted snippet>
scope: <repository-scoped|candidate-for-generic>     # FR-016, FR-022
status: <open|applied|deferred|withdrawn>
---
```

**Required sections**:
1. `## Feedback`
2. `## Suggested action`

**Rules**:
- `scope: repository-scoped` items MUST NOT enter the canonical skill. They may still be referenced from a Repository Specification.
- `scope: candidate-for-generic` items are inputs to the Skill Convergence Loop; promotion still requires a Skill Edit Proposal (FR-016, FR-022).
- The agent must record a Feedback Item before applying the feedback (FR-014).

**State transitions**:
```
open ──applied to current spec──▶ applied
open ──no action this session──▶ deferred
open ──user retracts──▶ withdrawn
```

---

## 6. Rollout Log — `.reposkillopt/rollouts/<id>.md`

**Filename / id convention**: `RL-YYYY-MM-DDTHHMMSS-<adapter>.md`.

**Front matter** (per FR-017):
```yaml
---
id: RL-YYYY-MM-DDTHHMMSS-<adapter>
agent: <identifier — e.g., "Claude Code">
agent_version: <if known>
adapter: <claude-code|codex|opencode|generic>
skill_version: <semver>
canonical_version: <semver mirrored by adapter>
task: <one-line description of what the user asked>
started: <ISO datetime>
ended: <ISO datetime>
spec_id: <Repository Specification id this rollout produced or revised>
---
```

**Required sections**:
1. `## Files inspected` — bullet list of paths (with line ranges when applicable).
2. `## Claims produced` — bullet list, each prefixed with its R10 label and any citations.
3. `## Human feedback received this session` — bullet list of Feedback Item ids.
4. `## Revisions applied` — bullet list (Spec section → change).

---

## 7. Skill Edit Proposal — `.reposkillopt/proposals/<id>.md`

**Filename / id convention**: `SP-YYYY-MM-DD-NNN-<slug>.md`.

**Front matter** (per FR-019, FR-020):
```yaml
---
id: SP-YYYY-MM-DD-NNN
proposed: <ISO date>
target_section: <canonical SKILL.md section name>
edit_kind: <ADD|REPLACE|DELETE|REORDER|SPECIALIZE|GENERALIZE>
scope: <generic|repository-scoped>       # repository-scoped requires explicit promotion rationale
supporting_feedback:
  - FB-YYYY-MM-DD-NNN
  - FB-YYYY-MM-DD-NNN
expected_effect: <one short paragraph>
risk_notes: <one short paragraph>
review_time_estimate_minutes: <integer ≤ 5>     # SC-009
status: <proposed|accepted|rejected>
decided: <ISO date when accepted/rejected>
decision_rationale: <required when status is accepted or rejected>
---
```

**Required sections**:
1. `## Proposed text` — the exact text to ADD / REPLACE / etc.
2. `## Diff against current canonical` — minimal diff representation.
3. `## Justification` — references to supporting feedback ids and to the recurring pattern they exhibit.

**Rules**:
- Each proposal is **bounded**: a single accept/reject unit (FR-020). If a proposal does not fit `review_time_estimate_minutes ≤ 5`, split it.
- `scope: repository-scoped` MUST NOT be accepted into the canonical SKILL.md (FR-016, FR-022); such proposals are routed to a per-repository scope-decision artifact instead, or rejected.
- Rejected proposals are **preserved** in place with `status: rejected` and `decision_rationale` (FR-021).
- Accepting a proposal triggers a canonical version bump per R8 semver rules.

**State transitions**:
```
proposed ──maintainer accepts──▶ accepted ──applied to SKILL.md──▶ (canonical version bump)
proposed ──maintainer rejects──▶ rejected (preserved)
```

---

## 8. Evaluation Rubric Scoring Sheet — `rubric/scoring/<spec_id>-<rollout_id>.md`

Produced per evaluation. Optional in v1 but follows a fixed schema so SC-012 (per-dimension deltas across skill versions) is mechanically possible.

**Front matter**:
```yaml
---
spec_id: <Repository Specification id>
rollout_id: <Rollout Log id>
skill_version: <semver>
adapter: <claude-code|codex|opencode|generic>
scored_by: <reviewer identifier>
scored_at: <ISO datetime>
---
```

**Required content**:
- A 15-row table with one row per FR-028 dimension, columns: `Dimension | Score (0–3) | Notes`.
- A table of FR-030 deterministic checks with `Check | Result (pass/fail) | Notes`.
- Aggregate per-dimension score (sum or mean) — recorded but never substituted for the per-dimension scores when comparing versions.

---

## Identifier index (cross-reference)

| Artifact | Id prefix | Example |
|---|---|---|
| Repository Specification | `SPEC-` or none (uses front-matter `spec_id`) | `spec_id: click-8.1.7` |
| Feedback Item | `FB-` | `FB-2026-05-31-001` |
| Rollout Log | `RL-` | `RL-2026-05-31T093000-claude-code` |
| Skill Edit Proposal | `SP-` | `SP-2026-05-31-001` |

Ids are stable for the artifact's lifetime; never reuse.

---

## Cross-artifact relationships

- A **Rollout Log** records the production of (or revision to) exactly one **Repository Specification**.
- A **Rollout Log** may reference zero or more **Feedback Items** received during the session.
- A **Skill Edit Proposal** references one or more **Feedback Items** as its supporting evidence.
- A **Skill Edit Proposal** that is accepted bumps the **Canonical Skill** version and a row is added to the **Changelog**.
- An **Adapter**'s `canonical_version` field must equal an existing **Canonical Skill** `version`.
- A **Repository Specification**'s `**[human]**` claim must cite a **Feedback Item** id.

No application database is required to maintain these relationships; they are all encoded in front-matter fields readable by `grep` or any YAML parser.
