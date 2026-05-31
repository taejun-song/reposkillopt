---
id: VG-2026-06-01-002
proposal_id: SP-2026-06-01-009-demo-harmful
candidate_version: 0.1.0+harmful-demo
released_baseline_version: 0.1.0
held_out_set:
  - repo: benjaminp/six
    commit: "1.16.0"
  - repo: sindresorhus/escape-string-regexp
    commit: "v5.0.0"
scorer_of_record: gate-reference-example
scored_at: 2026-06-01T09:45:00Z
regenerated_specs:
  - examples/reference-output/held-out/six/.reposkillopt/specs/repository-specification.md
  - examples/reference-output/held-out/escape-string-regexp/.reposkillopt/specs/repository-specification.md
verdict: FAIL
---

# Validation Gate Report VG-2026-06-01-002 — harmful-edit demonstration

> **Illustrative FAIL demonstration.** The candidate is a deliberately harmful, *hypothetical* edit (`SP-2026-06-01-009-demo-harmful`) that **deletes the "Do not rely only on README files" Operating Principle** from the canonical skill. It exists only to show the gate rejecting a regression; it is not a real proposal on disk. Scores are illustrative.

## Per-dimension scores

### benjaminp/six @ 1.16.0

| Dimension | Baseline | Candidate | Δ | Notes |
|---|---|---|---|---|
| 2. Evidence quality | 3 | 2 | **−1** | candidate leans on README claims uncorroborated by code |
| 15. Resistance to agent-specific failure modes | 3 | 1 | **−2** | README-only trust reintroduced — the exact failure mode the deleted principle prevents |
| (all other dimensions) | = | = | 0 | unchanged |

### sindresorhus/escape-string-regexp @ v5.0.0

| Dimension | Baseline | Candidate | Δ | Notes |
|---|---|---|---|---|
| 15. Resistance to agent-specific failure modes | 3 | 2 | **−1** | README description trusted over `index.js` |
| (all other dimensions) | = | = | 0 | unchanged |

## Deterministic checks

All 7 checks remain `pass` on both members — the harm is qualitative (the regression is in scored dimensions, not a mechanical check), which is precisely why the per-dimension gate is needed alongside the deterministic checks.

## Expected effect

Not applicable — the candidate claims no legitimate expected effect; it is a regression demonstration.

## Verdict

**FAIL.** Dimension **15 (Resistance to agent-specific failure modes)** regresses on **both** held-out members (six 3 → 1; escape-string-regexp 3 → 2), and **dimension 2 (Evidence quality)** regresses on **six** (3 → 2). Any per-dimension regression on any member blocks acceptance.

→ The candidate is **rejected**; this report is **preserved** as part of the audit trail (FR-012). The deleted principle must stay in the canonical skill.
