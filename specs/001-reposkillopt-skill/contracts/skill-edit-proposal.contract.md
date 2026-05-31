# Contract — Skill Edit Proposal (`.reposkillopt/proposals/<id>.md`)

**Scope**: A bounded, reviewable proposed change to the canonical skill (FR-019).
**Consumers**: The skill maintainer; the canonical changelog; future readers of the audit trail.

## Filename / id convention

`SP-YYYY-MM-DD-NNN-<slug>.md`

## Required front matter (FR-019, FR-020, SC-009)

```yaml
---
id: SP-YYYY-MM-DD-NNN
proposed: <ISO date>
target_section: <one of the canonical required sections from FR-003>
edit_kind: <ADD|REPLACE|DELETE|REORDER|SPECIALIZE|GENERALIZE>
scope: <generic|repository-scoped>
supporting_feedback:
  - FB-YYYY-MM-DD-NNN
  - FB-YYYY-MM-DD-NNN
expected_effect: <short paragraph>
risk_notes: <short paragraph>
review_time_estimate_minutes: <integer 1–5>
status: <proposed|accepted|rejected>
decided: <ISO date; required when status is accepted or rejected>
decision_rationale: <required when status is accepted or rejected>
---
```

## Required sections

1. `## Proposed text` — the exact text to apply (for ADD / REPLACE) or the exact text to remove (for DELETE) or the reordering specification (for REORDER) or the specialization / generalization rewrite (for SPECIALIZE / GENERALIZE).
2. `## Diff against current canonical` — minimal diff representation, three-line context, showing exactly what changes in `SKILL.md`.
3. `## Justification` — short paragraph that names the recurring pattern in the supporting feedback ids and explains why an edit to the canonical skill is the right response (vs handling it only in a Repository Specification).

## Rules

- The proposal MUST be **bounded**: a single accept/reject unit (FR-020). `review_time_estimate_minutes` MUST be ≤ 5 (SC-009).
- `target_section` MUST be one of the canonical required sections (FR-003).
- `edit_kind` MUST be one of the six values; for SPECIALIZE the diff narrows the rule, for GENERALIZE it broadens.
- `scope: repository-scoped` proposals MUST NOT be accepted into the canonical SKILL.md (FR-016, FR-022). They are either rewritten to generalize, or rejected, or routed to a per-repository scope-decision artifact.
- `supporting_feedback` MUST contain at least one Feedback Item id, and every id MUST exist.
- Accepting a proposal triggers a canonical version bump per Keep-A-Changelog + semver (R8): major if the diff breaks the adapter-equivalence checklist, minor if additive, patch if clarifying.
- Rejected proposals are **preserved** (FR-021) — never deleted. The file remains with `status: rejected`, `decided`, and `decision_rationale` populated.

## Acceptance checklist

- [ ] Filename matches id convention.
- [ ] Front matter present, valid, all required keys populated.
- [ ] `target_section` is a canonical required section name.
- [ ] `edit_kind` is one of the six values.
- [ ] `review_time_estimate_minutes` ≤ 5.
- [ ] `supporting_feedback` non-empty; every id resolves to an existing Feedback Item.
- [ ] Body has `## Proposed text`, `## Diff against current canonical`, `## Justification`.
- [ ] Diff is small enough to be reviewed within the stated time estimate; if not, split the proposal.
- [ ] If `scope: repository-scoped` and `status: accepted`, the acceptance is into a per-repository artifact (not the canonical SKILL.md).
- [ ] If accepted into canonical SKILL.md, the version bump is reflected in `skills/repo-skillopt/CHANGELOG.md`.
- [ ] If rejected, the file is preserved with `decision_rationale`.
