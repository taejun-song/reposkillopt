---
spec_id: click-8.1.7
rollout_id: RL-20260531T140000-claude-code
skill_version: 0.1.0
adapter: claude-code
scored_by: rubric-reference-example
scored_at: 2026-06-01T11:00:00Z
---

# Scoring sheet — click-8.1.7 / RL-20260531T140000-claude-code

Scores the **revision-2** Claude Code reference Repository Specification
(`examples/reference-output/claude-code/.reposkillopt/specs/repository-specification.md`)
against `rubric/evaluation-rubric.md` and `rubric/deterministic-checks.md`. This is a
worked example demonstrating the schema; a researcher reproduces it against any other
`skill_version` to obtain per-dimension deltas (SC-012).

## Qualitative scores (FR-028 dimensions)

| Dimension | Score (0–3) | Notes |
|---|---|---|
| 1. Architectural correctness | 3 | Six layers attributed to files/symbols; dependency direction stated (*Architectural layers*, *Dependency map*). |
| 2. Evidence quality | 3 | Major claims cite concrete `path:line`/`path:Symbol` evidence throughout. |
| 3. Citation validity | 3 | Citations well-formed and resolve to the cited content at commit `8.1.7`. |
| 4. File and symbol grounding | 3 | Sampled citations (`core.py:1010-1100`, `decorators.py:241-249`, `setup.cfg:74`) all resolve. |
| 5. Hallucination avoidance | 3 | No fabricated files/APIs; uncertain items labeled `**[inference]**`/`**[unknown]**`. |
| 6. Change-localization accuracy | 3 | *Change-impact map* derives blast radius from the dependency map; distinguishes affected vs unaffected (Windows-only, completion-only). |
| 7. Usefulness to an engineer | 3 | Entrypoints, control/data traces, risks, and next steps are directly actionable. |
| 8. Risk awareness | 3 | Repository-specific risks (`filterwarnings = error`, strict `mypy`, Windows console) each tied to evidence. |
| 9. Fact-vs-hypothesis distinction | 3 | Every major claim labeled; every `**[fact]**` cited; `**[human]**` claims cite Feedback ids. |
| 10. Test strategy quality | 3 | pytest layout + fixtures correct; secondary `tests/typing/` surface enumerated (`**[human]**`, FB-002). |
| 11. Responsiveness to human feedback | 3 | All three rev-2 Feedback Items applied and traceable in the Change log with correct scope handling. |
| 12. Spec completeness | 3 | All 19 sections present; *Data model* explicitly "Not applicable". |
| 13. Spec maintainability | 3 | Revision metadata, accumulating Change log, de-duplicated Evidence index. |
| 14. Cross-agent portability | 3 | Content runtime-neutral; claude-code adapter passes Adapter Equivalence. |
| 15. Resistance to agent-specific failure modes | 3 | Corroborates beyond README; inspects this repo over pattern-matching; refuses to overclaim (CI workflow left `**[unknown]**`). |

**Advisory aggregate**: 45 / 45 (mean 3.0). *Advisory only — per FR-029 this MUST NOT replace the per-dimension vector above when comparing skill versions.*

## Deterministic checks (FR-030)

| Check | Result (pass/fail) | Notes |
|---|---|---|
| 1. Cited file paths exist | pass | Sampled paths resolve in `pallets/click@8.1.7`. |
| 2. Cited symbols exist | pass | `Command`, `BaseCommand.main`, `OptionParser`, `CliRunner` locatable in cited files. |
| 3. Required output sections present | pass | All 19 FR-005 sections present, in order. |
| 4. Unsupported claims marked or removed | pass | Every `**[fact]**` carries a citation; unverifiable items are `**[inference]**`/`**[unknown]**`. |
| 5. Hallucinated files / modules / APIs flagged | pass | No path or symbol references a non-existent artifact. |
| 6. Prior human feedback addressed | pass | FB-001/002/003 applied and recorded in the Change log; none left open and unaddressed. |
| 7. Exported skill preserves canonical intent | pass | `adapters/claude-code/SKILL.md` `canonical_version: 0.1.0` resolves; passes Adapter Equivalence. |

## How to use this sheet for version comparison

Re-score the same rollout (or its successor) under a hypothetical `skill_version: 0.2.0`
using this identical schema, then diff the per-dimension rows. For example, if a 0.2.0
workflow change improved *Test strategy quality* but regressed *Evidence quality*, the
advisory aggregate could stay at 45/45 while the per-dimension vector reveals the trade —
which is precisely why the aggregate must never stand in for the vector (FR-029, SC-012).
