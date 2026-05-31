---
repo: sindresorhus/escape-string-regexp
commit: "v5.0.0"
skill_version: 0.1.0
adapter: claude-code
scored_by: gate-reference-example
scored_at: 2026-06-01T09:10:00Z
kind: baseline
---

# Baseline scoring — sindresorhus/escape-string-regexp @ v5.0.0 (skill 0.1.0)

> **Illustrative worked example** (see `rubric/held-out-set.md`). Scores demonstrate the gate schema; they are not a verified analysis of `escape-string-regexp` at `v5.0.0`. It is a one-function ESM micro-library with a single test file and an `ava`/`xo` toolchain — used here as a second, cross-ecosystem held-out repo.

## Qualitative scores (FR-028 dimensions)

| Dimension | Score (0–3) | Notes |
|---|---|---|
| 1. Architectural correctness | 3 | One exported function. |
| 2. Evidence quality | 3 | Cites `index.js` + `package.json`. |
| 3. Citation validity | 3 | Well-formed. |
| 4. File and symbol grounding | 3 | Resolves. |
| 5. Hallucination avoidance | 3 | No fabrications. |
| 6. Change-localization accuracy | 3 | One function; trivial. |
| 7. Usefulness to an engineer | 3 | Fully actionable at this size. |
| 8. Risk awareness | 2 | Notes ESM-only constraint. |
| 9. Fact-vs-hypothesis distinction | 3 | Labels applied. |
| 10. Test strategy quality | 3 | Single `test.js`; nothing secondary to miss. |
| 11. Responsiveness to human feedback | 3 | N/A baseline. |
| 12. Spec completeness | 3 | 19 sections (many "Not applicable"). |
| 13. Spec maintainability | 3 | Revisable. |
| 14. Cross-agent portability | 3 | Runtime-neutral. |
| 15. Resistance to agent-specific failure modes | 3 | Inspects source over README. |

**Advisory aggregate**: 44 / 45 (advisory only).

## Deterministic checks (FR-030)

| Check | Result (pass/fail) | Notes |
|---|---|---|
| 1. Cited file paths exist | pass | |
| 2. Cited symbols exist | pass | |
| 3. Required output sections present | pass | |
| 4. Unsupported claims marked or removed | pass | |
| 5. Hallucinated files/modules/APIs flagged | pass | |
| 6. Prior human feedback addressed | pass | None open. |
| 7. Exported skill preserves canonical intent | pass | |
