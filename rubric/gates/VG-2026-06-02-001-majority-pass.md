---
id: VG-2026-06-02-001
proposal_id: SP-2026-06-01-001
candidate_version: 0.1.0+SP-2026-06-01-001
released_baseline_version: 0.1.0
mode: majority
roster:
  - id: scorer-A
    kind: agent
  - id: scorer-B
    kind: agent
  - id: scorer-C
    kind: human
independence_attestation: All three scorers scored each regenerated spec blind, in separate sessions with no shared transcript, before any scores were compared.
held_out_set:
  - repo: benjaminp/six
    commit: "1.16.0"
  - repo: sindresorhus/escape-string-regexp
    commit: "v5.0.0"
regenerated_specs:
  - examples/reference-output/held-out/six/.reposkillopt/specs/repository-specification.md
  - examples/reference-output/held-out/escape-string-regexp/.reposkillopt/specs/repository-specification.md
verdict: PASS
---

# Majority Gate Report VG-2026-06-02-001 — `SP-2026-06-01-001` (mode: majority)

> **Illustrative worked example.** Majority-mode gate of the demo proposal `SP-2026-06-01-001` with a 3-scorer roster. Demonstrates majority aggregation and a contested-but-above-baseline dimension that is flagged yet non-blocking. Scores illustrative; schema/aggregation/verdict are real.

## Aggregated — benjaminp/six

| Dimension | Baseline | S-A | S-B | S-C | Aggregate | Method | Range | Low-agree | vs Baseline |
|---|---|---|---|---|---|---|---|---|---|
| 1. Architectural correctness | 3 | 3 | 3 | 3 | 3 | majority | 0 | no | equal |
| 2. Evidence quality | 3 | 3 | 3 | 3 | 3 | majority | 0 | no | equal |
| 3. Citation validity | 3 | 3 | 3 | 3 | 3 | majority | 0 | no | equal |
| 4. File and symbol grounding | 3 | 3 | 3 | 3 | 3 | majority | 0 | no | equal |
| 5. Hallucination avoidance | 3 | 3 | 3 | 3 | 3 | majority | 0 | no | equal |
| 6. Change-localization accuracy | 3 | 3 | 3 | 3 | 3 | majority | 0 | no | equal |
| 7. Usefulness to an engineer | 2 | 2 | 3 | 3 | 3 | majority | 1 | no | above |
| 8. Risk awareness | 2 | 2 | 2 | 2 | 2 | majority | 0 | no | equal |
| 9. Fact-vs-hypothesis distinction | 3 | 3 | 3 | 3 | 3 | majority | 0 | no | equal |
| 10. Test strategy quality | 2 | 3 | 3 | 1 | 3 | majority | 2 | yes | above |
| 11. Responsiveness to human feedback | 3 | 3 | 3 | 3 | 3 | majority | 0 | no | equal |
| 12. Spec completeness | 3 | 3 | 3 | 3 | 3 | majority | 0 | no | equal |
| 13. Spec maintainability | 3 | 3 | 3 | 3 | 3 | majority | 0 | no | equal |
| 14. Cross-agent portability | 3 | 3 | 3 | 3 | 3 | majority | 0 | no | equal |
| 15. Resistance to agent-specific failure modes | 3 | 3 | 3 | 3 | 3 | majority | 0 | no | equal |

Note: dimension 10 is **low-agreement** (scorer C said 1) but its aggregate (3) is **above** baseline (2) — flagged for the record, **non-blocking**. The lone `1` did not flip the majority `3` (SC-002).

## Deterministic — benjaminp/six

All 7 checks aggregate (majority) to **pass**.

## Aggregated — sindresorhus/escape-string-regexp

No-regression control: the candidate edit is a no-op here. All 15 dimensions: Baseline == Aggregate, Range 0, Low-agree no, vs Baseline equal. All 7 deterministic checks aggregate to **pass**.

## Adjudications

None required — no dimension is both low-agreement and at-or-below baseline.

## Expected effect

`SP-2026-06-01-001` expected effect (enumerate secondary structures) is **realized** on `six`: *Usefulness* (dim 7) 2→3 and *Test strategy quality* (dim 10) 2→3. `effect_realized: yes`.

## Verdict

**PASS.** No dimension aggregate is below baseline on any held-out repo; all deterministic checks pass; the one low-agreement dimension (six dim 10) is above baseline (non-blocking); the expected effect is realized. Per-dimension comparison only — no cross-dimension aggregate used.
