---
repo: benjaminp/six
commit: "1.16.0"
skill_version: 0.1.0
adapter: claude-code
mode: majority
roster: [scorer-A (agent), scorer-B (agent), scorer-C (human)]
scored_at: 2026-06-02T09:00:00Z
kind: majority-baseline
---

# N-scorer baseline — benjaminp/six @ 1.16.0 (skill 0.1.0)

> **Illustrative worked example** (see `rubric/held-out-set.md`). Demonstrates the N-scorer baseline schema; not a verified analysis of `six`. N = 3; aggregate = majority, else median (low-agreement).

## Aggregated baseline (per-scorer → aggregate)

| Dimension | S-A | S-B | S-C | Aggregate | Method |
|---|---|---|---|---|---|
| 1. Architectural correctness | 3 | 3 | 3 | 3 | majority |
| 2. Evidence quality | 3 | 3 | 3 | 3 | majority |
| 3. Citation validity | 3 | 3 | 3 | 3 | majority |
| 4. File and symbol grounding | 3 | 3 | 3 | 3 | majority |
| 5. Hallucination avoidance | 3 | 3 | 3 | 3 | majority |
| 6. Change-localization accuracy | 3 | 3 | 3 | 3 | majority |
| 7. Usefulness to an engineer | 2 | 2 | 3 | 2 | majority |
| 8. Risk awareness | 2 | 2 | 2 | 2 | majority |
| 9. Fact-vs-hypothesis distinction | 3 | 3 | 3 | 3 | majority |
| 10. Test strategy quality | 2 | 2 | 2 | 2 | majority |
| 11. Responsiveness to human feedback | 3 | 3 | 3 | 3 | majority |
| 12. Spec completeness | 3 | 3 | 3 | 3 | majority |
| 13. Spec maintainability | 3 | 3 | 3 | 3 | majority |
| 14. Cross-agent portability | 3 | 3 | 3 | 3 | majority |
| 15. Resistance to agent-specific failure modes | 3 | 3 | 3 | 3 | majority |

## Deterministic checks (majority pass/fail)

All 7 checks: S-A pass / S-B pass / S-C pass → **pass** (unanimous).
