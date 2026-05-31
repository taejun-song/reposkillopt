---
released_version: 0.1.0
revised: 2026-06-01
---

# Held-out Reference Set

The commit-pinned repositories reserved for **validation gating** (`rubric/validation-gate.md`). A candidate skill edit is scored against these repositories; because they are held **out** of the feedback that motivates proposals, the gate cannot be satisfied by overfitting to the very repository that prompted a change.

> **Illustrative worked example.** The scores in the referenced baseline/candidate sheets are an illustrative demonstration of the gate methodology and schema, not a verified analysis of these repositories at the pinned commits (regenerating and scoring real specs requires the repositories checked out). The *methodology, schema, and verdict rule* are the deliverable; a real gate run substitutes verified scores using the same shapes.

## Members

| repo | commit | ecosystem | baseline_sheet |
|---|---|---|---|
| `benjaminp/six` | `1.16.0` | python | `rubric/scoring/six-1.16.0-0.1.0-baseline.md` |
| `sindresorhus/escape-string-regexp` | `v5.0.0` | javascript | `rubric/scoring/escape-string-regexp-5.0.0-0.1.0-baseline.md` |

Both members are tiny, single-purpose libraries in **distinct ecosystems**, pinned to a tagged release, and deliberately **not** `pallets/click`.

## Exclusions

- **`pallets/click`** — the project's primary motivating repository. It motivated `FB-2026-05-31-002` and `FB-2026-06-01-004`, which in turn motivated `SP-2026-06-01-001`. A repository that motivates proposals MUST NOT validate them (FR-008), so `click` is excluded from the held-out set.

## Disjointness rule

For any proposal being gated, **no held-out member may appear in that proposal's `supporting_feedback` repositories**. If one does, the gate is invalid for that proposal and the report records `verdict: HELD` until the set or the proposal is adjusted.

## Disjointness audit

| proposal | supporting_feedback repos | held-out members | overlap | result |
|---|---|---|---|---|
| `SP-2026-06-01-001` | `pallets/click` (via `FB-2026-05-31-002`, `FB-2026-06-01-004`) | `benjaminp/six`, `sindresorhus/escape-string-regexp` | none | ✅ disjoint |

The audit confirms SC-004 (0 overlap) for the worked example.

## Re-baseline status

- Baselines on record describe `released_version: 0.1.0`.
- **Deferred**: feature `003-validation-gating` bumps the canonical skill to `0.2.0` via its bootstrapping edit (which is itself ungated — see `rubric/validation-gate.md` → *Bootstrapping note*). Re-baselining these members to `0.2.0` is **deferred to the next real gate run** and will update this file's `released_version` and the member baseline sheets at that time (FR-007). The `0.1.0` baselines remain valid for the worked example, which gates a `0.1.0`-era proposal.
