# Implementation Plan: N-Scorers Majority Validation Gate

**Branch**: `004-majority-scoring` | **Date**: 2026-06-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-majority-scoring/spec.md`

## Summary

Add a **majority-scoring mode** to the existing validation gate (feature 003): instead of one scorer-of-record, **N independent scorers** (N odd, ≥3) each apply the rubric to every regenerated held-out specification, and each dimension is aggregated by **majority** (median when no strict majority, flagged low-agreement). The gate runs feature 003's no-regression criterion on the aggregated scores, with one new rule — a low-agreement dimension at or below baseline must be **adjudicated** before PASS, else the verdict is **`HELD`**. This is a methodology refinement of *how the gate is scored*; the canonical skill's gate rule already says "passes a validation gate," so **no canonical-skill or adapter change is required** (a sharp contrast with feature 003). Deliverables: an extended `rubric/validation-gate.md`, a Majority Gate Report schema + worked examples, a mode-selection rule, and an optional aggregation helper.

## Technical Context

**Language/Version**: Markdown (CommonMark) + YAML front matter for the methodology, the extended report, and the per-scorer matrices. One **optional** POSIX-`sh` helper aggregates a per-scorer matrix into a verdict; outside acceptance (the rules are normative in prose).
**Primary Dependencies**: Feature 003's gate (`rubric/validation-gate.md`, `rubric/held-out-set.md`, `rubric/gates/`) and the rubric (`rubric/evaluation-rubric.md`, `rubric/deterministic-checks.md`). No new runtime dependency.
**Storage**: Filesystem Markdown only. Majority reports and per-scorer matrices live under `rubric/gates/`; baselines under `rubric/scoring/`.
**Testing**: Manual validation checkpoints against the new contracts. If the aggregation helper ships, it carries a POSIX-`sh` test (like features 002/003).
**Target Platform**: Repository-local methodology; a shell only for the optional helper.
**Project Type**: Documentation/methodology extension (skill-first). **No executable change to the canonical skill or adapters.**
**Performance Goals**: A majority gate run costs ~N× the scoring effort of a single-scorer run; bounded by the held-out set size × N.
**Constraints**: Vendor-neutral; cross-scorer aggregation is *within one dimension* and must not be confused with the forbidden cross-dimension aggregate (FR-013/FR-029); verdict reproducible from the recorded matrix (FR-009); independence auditable (FR-014).
**Scale/Scope**: Small — extend one methodology doc, add a report schema + ≥1 worked example (incl. an adjudication/`HELD` demonstration), a mode-selection rule, and an optional aggregation helper.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` is the unratified template. Gating against the project's **non-negotiables**:

| Gate (project non-negotiable) | Verdict | Notes |
|---|---|---|
| **Vendor neutrality** of `skills/repo-skillopt/SKILL.md` | ✅ Pass | No canonical edit at all — majority mode is a scoring methodology under `rubric/`. |
| **Adapter-equivalence** (FR-024/025/027a) | ✅ Pass — **not triggered** | The canonical gate rule ("passes a validation gate") is unchanged; no adapter touch, no version bump. Contrast with feature 003. |
| **Per-dimension over aggregate** (FR-029) | ✅ Pass | Cross-scorer aggregation is *within a dimension* (FR-013); per-dimension comparison is preserved; no cross-dimension aggregate decides anything. |
| **Skill-first scope** — helpers optional (FR-033) | ✅ Pass | Methodology + report schema; the aggregation helper is optional. |
| **No SaaS / DB / fine-tune / training loop** | ✅ Pass | Human/agent scorers apply the existing rubric; no automation pipeline or consensus model. |
| **Reproducibility** | ✅ Pass | Verdict (incl. `HELD`) is a deterministic function of the recorded per-scorer matrix + rules. |
| **Builds on 003 without weakening it** | ✅ Pass | Single-scorer mode remains valid (`mode: single`); majority mode is additive (`mode: majority`). |

No violations; **Complexity Tracking empty** (notably, this feature avoids feature 003's 4-adapter/version-bump cost).

## Project Structure

### Documentation (this feature)

```text
specs/004-majority-scoring/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── majority-gate-report.contract.md
│   └── scoring-modes.contract.md
└── tasks.md             # Phase 2 output (/speckit.tasks — NOT created here)
```

### Source Code (repository root)

```text
rubric/
├── validation-gate.md            # EDIT — add "## Majority mode (N scorers)": roster, aggregation
│                                  #        (majority/median + low-agreement), adjudication + HELD,
│                                  #        mode field, and the mode-selection rule (when majority is required)
├── gates/                        # EXISTING dir — add worked majority reports:
│   ├── VG-2026-06-02-001-majority-pass.md   # NEW — mode: majority, 3 scorers, a contested dim adjudicated, PASS
│   └── VG-2026-06-02-002-majority-held.md   # NEW — unresolved contested potential-regression -> HELD
├── scoring/                      # EXISTING — N-scorer baseline matrices for the held-out set (illustrative)
│   └── <repo>-0.1.0-majority-baseline.md    # NEW — per-scorer baseline rows + aggregated baseline
└── scripts/
    ├── gate-verdict.sh           # EXISTING (feature 003) — unchanged; handles single-scorer reports
    ├── majority-aggregate.sh     # NEW (OPTIONAL) — per-scorer matrix -> per-dim majority/median + agreement
    └── test_majority_aggregate.sh# NEW (OPTIONAL) — its test

# NOT CHANGED: skills/repo-skillopt/SKILL.md, adapters/** (no canonical edit; stays version 0.2.0)
```

**Structure Decision**: Single project, methodology extension under `rubric/`. The held-out set and rubric from features 001/003 are reused unchanged. Because the canonical gate rule already delegates "how to score" to `rubric/validation-gate.md`, majority mode lands entirely in that doc + the report schema + the optional helper — **no `skills/` or `adapters/` changes**, so no adapter-equivalence pass and no version bump.

## Complexity Tracking

> No constitution violations. Section intentionally empty. (This feature deliberately scopes out any canonical/adapter change — the costliest part of feature 003 — by treating majority mode as scoring methodology under the existing generic gate rule.)

## Post-Design Constitution Re-Check

Re-evaluated after Phase 1:

- Contracts confirm all writes land under `rubric/` (methodology, reports, scoring sheets, optional scripts); zero writes to `skills/` or `adapters/` → vendor-neutrality and adapter-equivalence untouched.
- The report schema records per-scorer scores and an explicit `mode`, `agreement`, and adjudication fields; the verdict (`PASS`/`FAIL`/`HELD`) is computed per-dimension from the matrix — no cross-dimension aggregate involved (FR-013/FR-029 preserved).
- No new dependency/service. Reproducibility holds.

No new violations. Ready for `/speckit.tasks`.
