---
id: VG-2026-06-02-002
proposal_id: SP-2026-06-02-009-demo-contested
candidate_version: 0.1.0+contested-demo
released_baseline_version: 0.1.0
mode: majority
roster:
  - id: scorer-A
    kind: agent
  - id: scorer-B
    kind: agent
  - id: scorer-C
    kind: human
independence_attestation: All three scorers scored blind in separate sessions before comparison.
held_out_set:
  - repo: benjaminp/six
    commit: "1.16.0"
  - repo: sindresorhus/escape-string-regexp
    commit: "v5.0.0"
regenerated_specs:
  - examples/reference-output/held-out/six/.reposkillopt/specs/repository-specification.md
  - examples/reference-output/held-out/escape-string-regexp/.reposkillopt/specs/repository-specification.md
verdict: HELD
---

# Majority Gate Report VG-2026-06-02-002 — contested-dimension demonstration (mode: majority)

> **Illustrative HELD demonstration.** A *hypothetical* candidate where scorers split on a dimension that is **at baseline** — a possible masked regression. Left unadjudicated, the verdict is **HELD** (not PASS, not FAIL). Scores illustrative.

## Aggregated — benjaminp/six

| Dimension | Baseline | S-A | S-B | S-C | Aggregate | Method | Range | Low-agree | vs Baseline |
|---|---|---|---|---|---|---|---|---|---|
| 1. Architectural correctness | 3 | 3 | 3 | 3 | 3 | majority | 0 | no | equal |
| 2. Evidence quality | 3 | 3 | 3 | 3 | 3 | majority | 0 | no | equal |
| 3. Citation validity | 3 | 3 | 3 | 3 | 3 | majority | 0 | no | equal |
| 4. File and symbol grounding | 3 | 3 | 3 | 3 | 3 | majority | 0 | no | equal |
| 5. Hallucination avoidance | 3 | 3 | 3 | 3 | 3 | majority | 0 | no | equal |
| 6. Change-localization accuracy | 3 | 3 | 3 | 3 | 3 | majority | 0 | no | equal |
| 7. Usefulness to an engineer | 2 | 2 | 2 | 2 | 2 | majority | 0 | no | equal |
| 8. Risk awareness | 2 | 2 | 1 | 3 | 2 | median | 2 | yes | equal |
| 9. Fact-vs-hypothesis distinction | 3 | 3 | 3 | 3 | 3 | majority | 0 | no | equal |
| 10. Test strategy quality | 2 | 2 | 2 | 2 | 2 | majority | 0 | no | equal |
| 11. Responsiveness to human feedback | 3 | 3 | 3 | 3 | 3 | majority | 0 | no | equal |
| 12. Spec completeness | 3 | 3 | 3 | 3 | 3 | majority | 0 | no | equal |
| 13. Spec maintainability | 3 | 3 | 3 | 3 | 3 | majority | 0 | no | equal |
| 14. Cross-agent portability | 3 | 3 | 3 | 3 | 3 | majority | 0 | no | equal |
| 15. Resistance to agent-specific failure modes | 3 | 3 | 3 | 3 | 3 | majority | 0 | no | equal |

Dimension 8 is **low-agreement** (scorers 2/1/3, no majority → median 2, range 2) and its aggregate equals baseline — a contested potential regression.

## Deterministic — benjaminp/six

All 7 checks aggregate (majority) to **pass**.

## Aggregated — sindresorhus/escape-string-regexp

No-op control: all 15 dimensions Baseline == Aggregate, Range 0, Low-agree no, vs Baseline equal; all checks pass.

## Adjudications

**None yet** — dimension 8 (Risk awareness) on `six` is low-agreement and at baseline; it MUST be adjudicated (re-scored to resolution) before this gate could PASS.

## Verdict

**HELD.** No dimension aggregate is below baseline (so not FAIL), but dimension 8 on `six` is low-agreement and at baseline and has not been adjudicated. Per the majority rule, a contested at-or-below dimension yields HELD until resolved. The report is preserved; the maintainer adjudicates dimension 8 and re-runs.
