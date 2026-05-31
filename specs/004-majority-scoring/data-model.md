# Phase 1 Data Model — N-Scorers Majority Validation Gate

Entities extend feature 003's gate artifacts. Markdown + YAML; no database.

## Entity 1 — Scorer Roster

The set of independent scorers for one gate run.

| Field | Type | Description | Validation |
|---|---|---|---|
| `scorers[]` | list | Each: `id`/role, `kind` (`human`\|`agent`) | Count **odd** and **≥3**. |
| `independence_attestation` | bool/text | States scores were submitted blind | Required; a breached scorer's row is excluded/redone. |
| `N` | int | Roster size | Odd, ≥3; default 3; may be 5/7 for high stakes. |

## Entity 2 — Per-scorer Score Matrix (per held-out repo)

| Field | Type | Description | Validation |
|---|---|---|---|
| rows | scorer × 15 dims | Each cell a 0–3 score | One row per roster scorer; all 15 dimensions. |
| checks | scorer × 7 checks | Each cell pass/fail | One row per scorer; all 7 checks. |

## Entity 3 — Aggregated Dimension Result (per dimension, per repo)

| Field | Type | Description | Validation |
|---|---|---|---|
| `aggregate` | 0–3 | Majority (modal); median if no strict majority | Recorded with `method`. |
| `method` | enum | `majority` \| `median` | `median` ⇒ low-agreement. |
| `range` | int | max − min across scorers | `range ≥ 2` ⇒ `low_agreement = true`. |
| `low_agreement` | bool | Scorers span ≥2 | Drives the adjudication rule. |
| `vs_baseline` | enum | `above` \| `equal` \| `below` | `equal`/`below` + `low_agreement` ⇒ adjudication required. |

## Entity 4 — Adjudication Record (only for contested at-or-below dimensions)

| Field | Type | Description | Validation |
|---|---|---|---|
| `dimension` | name | The adjudicated dimension | Must have been low-agreement & at/below baseline. |
| `adjudicator` | string | Who resolved it | Required. |
| `resolved_aggregate` | 0–3 | The resolved value | Replaces `aggregate` for the verdict. |
| `outcome` | enum | `resolved` \| `unresolved` | `unresolved` ⇒ verdict `HELD`. |

## Entity 5 — Majority Gate Report (extends feature 003's Validation Gate Report)

Adds to the 003 report front matter / sections:

| Field | Type | Description | Validation |
|---|---|---|---|
| `mode` | enum | `single` \| `majority` | This entity is the `majority` case. |
| `roster` | ref | Entity 1 | Odd, ≥3, attested. |
| per-scorer matrix | section | Entity 2 per repo | Present for every held-out member. |
| aggregated table | section | Entity 3 per dim per repo | Baseline, aggregate, method, range, low_agreement, vs_baseline. |
| adjudications | section | Entity 4 list | One per contested at-or-below dimension. |
| `verdict` | enum | `PASS` \| `FAIL` \| `HELD` | Per the R5 rule. |

## Entity 6 — Scoring Mode Selection rule

| Field | Type | Description | Validation |
|---|---|---|---|
| `majority_required_when` | list | At minimum: edits to *Operating Principles*; a proposal that previously failed a gate; low single-scorer confidence | Documented in `rubric/validation-gate.md`. |
| `single_eligible_when` | list | Low-risk clarifying edits | Documented. |

## Relationships

```text
Scorer Roster --(produces)--> Per-scorer Score Matrix (one per held-out repo)
Per-scorer Score Matrix --(aggregates to)--> Aggregated Dimension Result (per dim)
Aggregated Dimension Result [low_agreement & at/below baseline] --(requires)--> Adjudication Record
Majority Gate Report --(contains)--> roster + matrices + aggregated tables + adjudications + verdict
Skill Edit Proposal.status = accepted REQUIRES a referenced PASS Majority Gate Report (when majority mode applies)
```

## Verdict state machine (per gate run)

```text
aggregate all dims/checks
        │
        ├─ any dim aggregate < baseline, or any check -> fail  ──▶ FAIL (report preserved)
        │
        ├─ some dim low-agreement & at/below baseline & not adjudicated ──▶ HELD ──adjudicate──▶ re-evaluate
        │
        └─ otherwise (no regression; contested-at/below all adjudicated; effect realized/waived) ──▶ PASS
```

## Validation rules summary (traceable to FRs)

- N odd, ≥3 (FR-001/FR-007); independence attested + auditable (FR-002/FR-014).
- Per-dim aggregate = majority, else median + low-agreement flag (FR-003); checks majority pass/fail (FR-005).
- Verdict on aggregated scores vs aggregated baseline (FR-004); contested at/below ⇒ adjudicate-or-HELD (FR-008).
- Cross-scorer aggregation is within a dimension; not the forbidden cross-dimension aggregate (FR-013).
- Verdict reproducible from the matrix (FR-009); `mode` recorded (FR-010); majority baseline matches mode (FR-015).
