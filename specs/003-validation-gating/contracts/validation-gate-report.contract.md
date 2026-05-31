# Contract — Validation Gate Report (`rubric/gates/VG-<id>.md`)

**Scope**: The artifact recording one gate run and its verdict (FR-009, FR-010, FR-015).
**Consumers**: The skill maintainer; the gated Skill Edit Proposal; future auditors.

## Filename / id convention

`VG-YYYY-MM-DD-NNN-<slug>.md` with `id: VG-YYYY-MM-DD-NNN`.

## Required front matter

```yaml
---
id: VG-YYYY-MM-DD-NNN
proposal_id: SP-YYYY-MM-DD-NNN
candidate_version: <released-version>+<proposal-id-or-tag>
released_baseline_version: <semver of the released version the baselines describe>
held_out_set:
  - repo: <owner/name>
    commit: <tag-or-sha>
  - repo: <owner/name>
    commit: <tag-or-sha>
scorer_of_record: <name/identifier>
scored_at: <ISO-8601>
regenerated_specs:
  - <path under <repo>/.reposkillopt/specs/>
verdict: <PASS|FAIL|HELD>
---
```

## Required sections

1. `## Per-dimension scores` — one sub-table per held-out repo, 15 rows: `Dimension | Baseline | Candidate | Δ | Notes`.
2. `## Deterministic checks` — one sub-table per held-out repo, 7 rows: `Check | Baseline | Candidate | Notes`.
3. `## Expected effect` — states the proposal's `expected_effect`, and either the dimension(s) where it was realized (`effect_realized: yes`) or an explicit waiver for a clarifying edit (`effect_realized: waived`).
4. `## Verdict` — `PASS`/`FAIL`/`HELD` with rationale; for FAIL, names the regressed dimension(s)/check(s) and repo(s); for HELD, names the invalidity (e.g., overfitting conflict).

## Verdict rule (deterministic — FR-004, FR-011)

`FAIL` if, on **any** held-out repo, **any** dimension has `Candidate < Baseline`, OR any deterministic check flips `pass → fail`, OR `effect_realized` is `no`.
`HELD` if the held-out set is invalid for this proposal (a member repo appears in the proposal's `supporting_feedback`).
Otherwise `PASS`.

The verdict MUST be reproducible from the recorded tables alone (no external state). The optional `rubric/scripts/gate-verdict.sh` MUST implement exactly this rule.

## Rules

- Per-dimension comparison only; an aggregate MUST NOT determine the verdict (FR-005).
- `held_out_set` MUST have ≥2 members and MUST NOT intersect the proposal's `supporting_feedback` repos (FR-008) — otherwise `verdict: HELD`.
- Candidate scores MUST come from regenerated specs listed in `regenerated_specs` (FR-003).
- FAIL and HELD reports are **preserved** (FR-012).
- A PASS report is the precondition for the proposal's `status: accepted` (FR-006); it authorizes but does not perform the version bump (FR-013).

## Acceptance checklist

- [ ] Filename matches `id`.
- [ ] Front matter complete; `held_out_set` ≥2, commit-pinned, disjoint from the proposal's motivating repos.
- [ ] `scorer_of_record` present; `regenerated_specs` lists one spec per held-out member.
- [ ] Per-dimension table has all 15 dimensions per repo; deterministic table all 7 checks per repo.
- [ ] `verdict` equals the deterministic rule applied to the tables + effect clause.
- [ ] FAIL names the regressed dimension(s)/check(s) and repo(s); HELD names the invalidity.
- [ ] PASS only if no per-dimension regression, no check flip, and effect realized or waived.
