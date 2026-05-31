---
repo: sindresorhus/escape-string-regexp
commit: "v5.0.0"
skill_version: 0.1.0
adapter: claude-code
mode: majority
roster: [scorer-A (agent), scorer-B (agent), scorer-C (human)]
scored_at: 2026-06-02T09:10:00Z
kind: majority-baseline
---

# N-scorer baseline — sindresorhus/escape-string-regexp @ v5.0.0 (skill 0.1.0)

> **Illustrative worked example** (see `rubric/held-out-set.md`). N = 3; aggregate = majority, else median.

## Aggregated baseline (per-scorer → aggregate)

| Dimension | S-A | S-B | S-C | Aggregate | Method |
|---|---|---|---|---|---|
| 1. Architectural correctness | 3 | 3 | 3 | 3 | majority |
| 2. Evidence quality | 3 | 3 | 3 | 3 | majority |
| 3. Citation validity | 3 | 3 | 3 | 3 | majority |
| 4. File and symbol grounding | 3 | 3 | 3 | 3 | majority |
| 5. Hallucination avoidance | 3 | 3 | 3 | 3 | majority |
| 6. Change-localization accuracy | 3 | 3 | 3 | 3 | majority |
| 7. Usefulness to an engineer | 3 | 3 | 3 | 3 | majority |
| 8. Risk awareness | 2 | 2 | 2 | 2 | majority |
| 9. Fact-vs-hypothesis distinction | 3 | 3 | 3 | 3 | majority |
| 10. Test strategy quality | 3 | 3 | 3 | 3 | majority |
| 11. Responsiveness to human feedback | 3 | 3 | 3 | 3 | majority |
| 12. Spec completeness | 3 | 3 | 3 | 3 | majority |
| 13. Spec maintainability | 3 | 3 | 3 | 3 | majority |
| 14. Cross-agent portability | 3 | 3 | 3 | 3 | majority |
| 15. Resistance to agent-specific failure modes | 3 | 3 | 3 | 3 | majority |

## Deterministic checks (majority pass/fail)

All 7 checks: unanimous **pass**.
