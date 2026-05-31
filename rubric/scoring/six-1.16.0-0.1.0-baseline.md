---
repo: benjaminp/six
commit: "1.16.0"
skill_version: 0.1.0
adapter: claude-code
scored_by: gate-reference-example
scored_at: 2026-06-01T09:00:00Z
kind: baseline
---

# Baseline scoring — benjaminp/six @ 1.16.0 (skill 0.1.0)

> **Illustrative worked example** (see `rubric/held-out-set.md`). Scores demonstrate the gate schema; they are not a verified analysis of `six` at `1.16.0`. `six` is a single-module Python 2/3 compatibility library with a `tox`-driven test matrix and a typing-adjacent surface that a surface-only pass can miss — the property this held-out repo is chosen to exercise.

## Qualitative scores (FR-028 dimensions)

| Dimension | Score (0–3) | Notes |
|---|---|---|
| 1. Architectural correctness | 3 | Single module; structure trivially correct. |
| 2. Evidence quality | 3 | Claims cite the one module + setup. |
| 3. Citation validity | 3 | Citations well-formed. |
| 4. File and symbol grounding | 3 | Symbols resolve in the single file. |
| 5. Hallucination avoidance | 3 | No fabrications. |
| 6. Change-localization accuracy | 3 | Blast radius is the one module. |
| 7. Usefulness to an engineer | 2 | Useful but thin on the test matrix. |
| 8. Risk awareness | 2 | Notes py2/py3 risk; misses CI matrix nuance. |
| 9. Fact-vs-hypothesis distinction | 3 | Labels applied. |
| 10. Test strategy quality | **2** | Names the test file; **misses the tox matrix / non-default test surfaces**. |
| 11. Responsiveness to human feedback | 3 | N/A baseline; labels consistent. |
| 12. Spec completeness | 3 | All 19 sections present. |
| 13. Spec maintainability | 3 | Revisable; Change log present. |
| 14. Cross-agent portability | 3 | Runtime-neutral. |
| 15. Resistance to agent-specific failure modes | 3 | Corroborates beyond README. |

**Advisory aggregate**: 43 / 45 (advisory only — never substitutes for the per-dimension vector).

## Deterministic checks (FR-030)

| Check | Result (pass/fail) | Notes |
|---|---|---|
| 1. Cited file paths exist | pass | |
| 2. Cited symbols exist | pass | |
| 3. Required output sections present | pass | 19 sections. |
| 4. Unsupported claims marked or removed | pass | |
| 5. Hallucinated files/modules/APIs flagged | pass | |
| 6. Prior human feedback addressed | pass | None open. |
| 7. Exported skill preserves canonical intent | pass | adapter equivalence holds. |
