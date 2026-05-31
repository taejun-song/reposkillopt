# Contract — Majority Gate Report (`rubric/gates/VG-<id>.md`, `mode: majority`)

**Scope**: A Validation Gate Report produced in majority mode (FR-006, FR-009). Extends feature 003's `validation-gate-report.contract.md`.
**Consumers**: The skill maintainer; the gated Skill Edit Proposal; auditors.

## Required front matter (adds to the feature-003 report)

```yaml
---
id: VG-YYYY-MM-DD-NNN
proposal_id: SP-YYYY-MM-DD-NNN
candidate_version: <released>+<proposal-id>
released_baseline_version: <semver>
mode: majority
roster:
  - id: <scorer-1>
    kind: human|agent
  - id: <scorer-2>
    kind: human|agent
  - id: <scorer-3>
    kind: human|agent
independence_attestation: <statement that scores were submitted blind>
held_out_set:
  - repo: <owner/name>
    commit: <tag-or-sha>
regenerated_specs:
  - <path under <repo>/.reposkillopt/specs/>
verdict: <PASS|FAIL|HELD>
---
```

`roster` MUST have an **odd** count **≥3**.

## Required sections (per held-out repo)

1. `## Per-scorer scores — <repo>` — a table with one row per scorer × the 15 dimensions (0–3), plus a per-scorer deterministic-checks sub-table (7 checks).
2. `## Aggregated — <repo>` — 15 rows: `Dimension | Baseline | <scorer values…> | Aggregate | Method | Range | Low-agree | vs Baseline`. `Method` ∈ {majority, median}; `Low-agree` true iff `Range ≥ 2`.
3. `## Adjudications` (only if any contested at-or-below dimension exists) — one row per such dimension: `Dimension | Repo | Adjudicator | Resolved value | Outcome`.
4. `## Verdict` — `PASS`/`FAIL`/`HELD` with rationale (for FAIL: the regressed dimension/check + repo; for HELD: the unadjudicated contested dimension(s)).

## Verdict rule (deterministic — reproducible from the matrix)

```
FAIL  if any dimension Aggregate < Baseline on any repo,
      OR any deterministic check aggregates (majority) to fail.
HELD  if not FAIL, AND some dimension is Low-agree AND vs Baseline is equal/below AND not adjudicated to resolution.
PASS  otherwise (no regression; every contested at-or-below dimension adjudicated; expected effect realized or waived).
```

Aggregation per dimension: **majority** (modal) value; if no strict majority, the **median**, marked `Method: median` and `Low-agree: true`.

## Rules

- Cross-scorer aggregation is **within a single dimension**; the report MUST NOT compute a cross-dimension aggregate to decide the verdict (FR-013/FR-029).
- A scorer who was not independent has their row **excluded or redone**; the roster used for the verdict MUST be independent and odd ≥3 (FR-002/FR-014).
- A low-agreement dimension **above** baseline is recorded but does not block; **at or below** baseline it blocks (HELD) until adjudicated (FR-008).
- FAIL and HELD reports are **preserved** (carries over feature 003 FR-012).
- A PASS majority report is a valid precondition for proposal acceptance wherever majority mode is required (FR-006, scoring-modes contract).

## Acceptance checklist

- [ ] `mode: majority`; `roster` odd & ≥3 with `kind` per scorer; `independence_attestation` present.
- [ ] Per-scorer matrix present for every held-out member (15 dims + 7 checks per scorer).
- [ ] Aggregated table records Aggregate, Method, Range, Low-agree, vs Baseline for all 15 dims.
- [ ] Every `Low-agree` dimension that is equal/below baseline has an Adjudication row OR the verdict is HELD.
- [ ] `verdict` equals the deterministic rule applied to the aggregated table + adjudications.
- [ ] No cross-dimension aggregate is used to decide the verdict.
