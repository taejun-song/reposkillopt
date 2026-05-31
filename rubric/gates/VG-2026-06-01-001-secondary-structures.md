---
id: VG-2026-06-01-001
proposal_id: SP-2026-06-01-001
candidate_version: 0.1.0+SP-2026-06-01-001
released_baseline_version: 0.1.0
held_out_set:
  - repo: benjaminp/six
    commit: "1.16.0"
  - repo: sindresorhus/escape-string-regexp
    commit: "v5.0.0"
scorer_of_record: gate-reference-example
scored_at: 2026-06-01T09:30:00Z
regenerated_specs:
  - examples/reference-output/held-out/six/.reposkillopt/specs/repository-specification.md
  - examples/reference-output/held-out/escape-string-regexp/.reposkillopt/specs/repository-specification.md
verdict: PASS
---

# Validation Gate Report VG-2026-06-01-001 — `SP-2026-06-01-001`

> **Illustrative worked example** demonstrating the gate on the pre-existing demo proposal `SP-2026-06-01-001` ("enumerate secondary structures — non-pytest test trees and internal modules — in workflow stages (c)/(d)"). Scores are illustrative (see `rubric/held-out-set.md`); the schema, comparison, and verdict are real.

## Per-dimension scores

### benjaminp/six @ 1.16.0

| Dimension | Baseline | Candidate | Δ | Notes |
|---|---|---|---|---|
| 1. Architectural correctness | 3 | 3 | 0 | |
| 2. Evidence quality | 3 | 3 | 0 | |
| 3. Citation validity | 3 | 3 | 0 | |
| 4. File and symbol grounding | 3 | 3 | 0 | |
| 5. Hallucination avoidance | 3 | 3 | 0 | |
| 6. Change-localization accuracy | 3 | 3 | 0 | |
| 7. Usefulness to an engineer | 2 | 3 | +1 | tox matrix now surfaced |
| 8. Risk awareness | 2 | 2 | 0 | |
| 9. Fact-vs-hypothesis distinction | 3 | 3 | 0 | |
| 10. Test strategy quality | 2 | 3 | **+1** | **secondary test surface (tox matrix) enumerated — the proposal's intended effect** |
| 11. Responsiveness to human feedback | 3 | 3 | 0 | |
| 12. Spec completeness | 3 | 3 | 0 | |
| 13. Spec maintainability | 3 | 3 | 0 | |
| 14. Cross-agent portability | 3 | 3 | 0 | |
| 15. Resistance to agent-specific failure modes | 3 | 3 | 0 | |

### sindresorhus/escape-string-regexp @ v5.0.0

| Dimension | Baseline | Candidate | Δ | Notes |
|---|---|---|---|---|
| 1–15 (all) | = | = | 0 | No-regression control: the edit is a no-op here (no secondary structures); every dimension equals its baseline. |

## Deterministic checks

| Check | six baseline | six candidate | esr baseline | esr candidate |
|---|---|---|---|---|
| 1. Cited paths exist | pass | pass | pass | pass |
| 2. Cited symbols exist | pass | pass | pass | pass |
| 3. 19 sections present | pass | pass | pass | pass |
| 4. Unsupported claims marked | pass | pass | pass | pass |
| 5. No hallucinated files/APIs | pass | pass | pass | pass |
| 6. Prior feedback addressed | pass | pass | pass | pass |
| 7. Adapter preserves intent | pass | pass | pass | pass |

No check flips `pass → fail` on either member.

## Expected effect

`SP-2026-06-01-001` `expected_effect`: make exhaustive enumeration of secondary structures a workflow instruction. **Realized** on `benjaminp/six` — *Test strategy quality* (dim 10) rose 2 → 3 and *Usefulness* (dim 7) rose 2 → 3. `effect_realized: yes`.

## Verdict

**PASS.** On every held-out member, no dimension's candidate score is below its baseline and no deterministic check flips. The proposal's expected effect is realized on ≥1 dimension (six dim 10). Per-dimension comparison only — no aggregate was used.

→ `SP-2026-06-01-001` is eligible for `status: accepted`. (In the MVP demo it remains illustrative and the canonical version is unchanged by *its* content; see that proposal's note.)
