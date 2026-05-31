# Phase 1 Data Model — Validation-Gated Skill Convergence

Entities are Markdown artifacts (YAML front matter + tables) layered on the existing rubric. No database.

## Entity 1 — Held-out Reference Set (`rubric/held-out-set.md`)

The commit-pinned repositories reserved for gating.

| Field | Type | Description | Validation |
|---|---|---|---|
| `members[]` | list | Each: `repo`, `commit`, `ecosystem`, `baseline_sheet` path | ≥2 members; every `commit` is a specific tag/SHA. |
| `excludes[]` | list | Repos explicitly barred (motivating repos) | MUST include `pallets/click` (motivated the demo proposals). |
| `released_version` | semver | The released skill version these baselines describe | Matches `skills/repo-skillopt/SKILL.md` `version`. |

**Rules**: every member is commit-pinned (FR-007); the set is disjoint from any gated proposal's `supporting_feedback` repos (FR-008); recomputed/relabeled when `released_version` changes (FR-007 re-baseline).

## Entity 2 — Baseline Scores (`rubric/scoring/<repo>-<ver>-baseline.md`)

Per-held-out-repo rubric scores for the **current released** skill version — the comparison floor.

| Field | Type | Description | Validation |
|---|---|---|---|
| front matter | — | `repo`, `commit`, `skill_version`, `adapter`, `scored_by`, `scored_at` | `skill_version` = released version. |
| qualitative table | 15 rows | `Dimension | Score (0–3) | Notes` | All 15 FR-028 dimensions. |
| deterministic table | 7 rows | `Check | Result (pass/fail) | Notes` | All 7 FR-030 checks. |

Reuses the existing scoring-sheet schema (`rubric/deterministic-checks.md` → *Scoring-sheet format*).

## Entity 3 — Candidate Skill Version

The canonical skill with a proposed edit applied; unreleased. Not a stored file of its own — it is the *input state* under which held-out specs are regenerated. Identified in a report by `candidate_version` (e.g., `0.1.0+SP-2026-06-01-001`) and the proposal id.

| Field | Type | Description | Validation |
|---|---|---|---|
| `proposal_id` | id | The `SP-…` being gated | Must exist; `scope: generic`. |
| `candidate_version` | label | Released version + proposal tag | Distinct from any released version. |

## Entity 4 — Candidate Scores (`rubric/scoring/<repo>-<candidate>-candidate.md`)

Same schema as Baseline Scores, but scored against the **regenerated** spec produced by the candidate version (R2).

## Entity 5 — Validation Gate Report (`rubric/gates/VG-YYYY-MM-DD-NNN-<slug>.md`)

The decision artifact; referenced by the proposal.

| Field | Type | Description | Validation |
|---|---|---|---|
| `id` | id | `VG-YYYY-MM-DD-NNN` | Matches filename. |
| `proposal_id` | id | The gated `SP-…` | Exists; `scope: generic`. |
| `candidate_version` | label | Candidate version label | Distinct from released. |
| `held_out_set` | ref | Snapshot of members + commit pins used | ≥2; excludes the proposal's motivating repos. |
| `scorer_of_record` | string | Named human scorer | Required. |
| `regenerated_specs[]` | paths | The candidate specs scored (under each repo's `.reposkillopt/`) | One per held-out member. |
| `per_dimension[]` | table | Per repo × 15 dims: baseline, candidate, delta | No `candidate < baseline` for PASS. |
| `deterministic[]` | table | Per repo × 7 checks: baseline, candidate | No pass→fail flip for PASS. |
| `effect_realized` | enum | `yes` (dim named) \| `waived` (clarifying) | If `no`, verdict FAIL. |
| `verdict` | enum | `PASS` \| `FAIL` \| `HELD` | Deterministic function of the tables + effect clause. |
| `rationale` | text | Why; for FAIL, the regressed dim(s)/check(s) + repo | Required. |

**State**: `HELD` is used when the gate is invalid (e.g., overfitting conflict — a motivating repo appears in the held-out set).

## Entity 6 — Skill Edit Proposal (existing, extended)

`templates/skill-edit-proposal.md` gains one optional field:

| Field | Type | Description | Validation |
|---|---|---|---|
| `validation_gate_report` | id (optional) | The `VG-…` that gated this proposal | **Required to be a PASS** before `status: accepted` (FR-006). |

## Relationships

```text
Held-out Reference Set --(baseline per member)--> Baseline Scores  (1 : N)
Skill Edit Proposal --(gated by)--> Validation Gate Report  (1 : 0..1)
Validation Gate Report --(compares)--> Baseline Scores vs Candidate Scores  (per held-out member)
Validation Gate Report --(references)--> Regenerated candidate specs in each held-out repo's .reposkillopt/
Skill Edit Proposal.status = accepted  REQUIRES  validation_gate_report.verdict = PASS
```

## State transitions (a gated proposal)

```text
proposed ──run gate──▶ VG report produced
   │                        │ PASS  → eligible → accepted (existing version-bump flow)
   │                        │ FAIL  → rejected (report preserved)  ── revise edit ──▶ proposed (new VG)
   │                        │ HELD  → blocked (fix held-out set / proposal disjointness) ─▶ proposed
   └───(repository-scoped)──▶ never gated; rejected upstream by scope discipline
```

## Validation rules summary (traceable to FRs)

- Gate uses the existing 15-dim + 7-check rubric only (FR-002); per-dimension, never aggregate (FR-005).
- Candidate scores come from **regenerated** specs (FR-003).
- Held-out set commit-pinned (FR-007) and disjoint from motivating repos (FR-008).
- Report records scorer-of-record; verdict is a function of recorded scores (FR-011, FR-015).
- `status: accepted` requires a referenced PASS report (FR-006); acceptance still runs the normal version-bump flow (FR-013).
- FAIL/HELD reports preserved (FR-012).
