# Implementation Plan: Validation-Gated Skill Convergence

**Branch**: `003-validation-gating` | **Date**: 2026-05-31 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-validation-gating/spec.md`

## Summary

Add a **human-run, rubric-based validation gate** to the existing Skill Convergence Loop: a `scope: generic` Skill Edit Proposal can only be accepted if, on a **commit-pinned held-out reference set** disjoint from the repositories that motivated it, the candidate skill version (proposed edit applied) **regenerates** Repository Specifications whose **per-dimension rubric scores do not regress** and whose **deterministic checks still pass**, with the proposal's expected effect realized on ≥1 dimension (or explicitly waived). Each run produces a **Validation Gate Report** signed by a named scorer-of-record; the verdict is a deterministic function of the recorded scores. The gate is methodology + Markdown artifacts reusing the existing rubric — no service, database, training loop, or model fine-tuning. Making the gate *binding* requires a small additive edit to the canonical skill (and its four adapters), bumping the canonical version `0.1.0 → 0.2.0`.

## Technical Context

**Language/Version**: Markdown (CommonMark) + YAML front matter for every artifact (gate report, held-out-set definition, baseline/candidate scoring sheets, the gate methodology doc). One **optional** POSIX-`sh` helper may compute the PASS/FAIL verdict from a report's recorded score tables; it is outside acceptance (the verdict rule is fully specified in prose).
**Primary Dependencies**: The existing rubric — `rubric/evaluation-rubric.md` (15 dimensions, 0–3) and `rubric/deterministic-checks.md` (7 checks) plus the scoring-sheet schema. No new runtime dependency.
**Storage**: Filesystem Markdown only. Gate reports and held-out scoring sheets live under `rubric/`; regenerated candidate specs for a held-out repo live under that repo's `.reposkillopt/specs/`.
**Testing**: Manual validation checkpoints against the new contracts (this is methodology, mirroring feature 001). If the optional verdict helper ships, it carries POSIX-`sh` tests like feature 002.
**Target Platform**: Repository-local methodology; no execution target beyond a text editor (and a shell, only if the optional helper is used).
**Project Type**: Documentation/methodology artifact set (skill-first), plus a small additive edit to the canonical skill and adapters.
**Performance Goals**: A gate run is bounded by regenerating + scoring the held-out set (small: ≥2 repos); SC-001 budget is "a single working session".
**Constraints**: Vendor-neutral; per-dimension-over-aggregate (FR-005); reproducible verdict from recorded scores (FR-011); held-out set disjoint from motivating repos (FR-008); the gate authorizes — never bypasses — the existing acceptance/version-bump flow (FR-013).
**Scale/Scope**: Small — one methodology doc, one held-out-set definition, a report schema + first report, baseline sheets for the held-out set, an additive Skill Convergence Loop edit mirrored across 4 adapters, and an optional verdict helper.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` is the unratified template (placeholders). Gating against the project's established **non-negotiables** (feature 001 / `CLAUDE.md`):

| Gate (project non-negotiable) | Verdict | Notes |
|---|---|---|
| **Vendor neutrality** of `skills/repo-skillopt/SKILL.md` (FR-002) | ✅ Pass | The gating step added to the Skill Convergence Loop is runtime-neutral; it names the rubric and the gate, not any harness. |
| **Adapter-equivalence** (FR-024/025, FR-027a) | ⚠️ Pass *with required work* | Editing `SKILL.md` means all four adapters MUST mirror the new content and bump `canonical_version` to `0.2.0`. This is in-scope implementation, not a violation — but it is the highest-risk task (4 adapters + equivalence re-check). |
| **Per-dimension over aggregate** (FR-029) | ✅ Pass | FR-005 forbids an aggregate gate; the report records per-dimension deltas. |
| **Skill-first scope** — helpers optional & outside acceptance (FR-033) | ✅ Pass | Core deliverable is Markdown methodology + artifacts; the verdict helper is optional. |
| **No SaaS / DB / frontend / fine-tune / training loop** | ✅ Pass | Human-run gate over existing rubric; no automation pipeline, no reward model. |
| **Scope discipline** (FR-016/022) | ✅ Pass | Only `scope: generic` proposals are gated; `repository-scoped` ones are rejected upstream and never reach the gate. |
| **Target `.reposkillopt/` layout** (FR-036a) | ✅ Pass | Regenerated candidate specs for a held-out repo live under that repo's `.reposkillopt/`; project-level gate artifacts live under `rubric/`, where the rubric and scoring sheets already live. |

One item to justify in Complexity Tracking: the canonical-version bump + 4-adapter update is real surface area, accepted because FR-006 ("no acceptance without a passing gate") can only be made *binding* by stating it in the canonical skill.

## Project Structure

### Documentation (this feature)

```text
specs/003-validation-gating/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── validation-gate-report.contract.md
│   ├── held-out-set.contract.md
│   └── gate-procedure.contract.md
└── tasks.md             # Phase 2 output (/speckit.tasks — NOT created here)
```

### Source Code (repository root)

```text
rubric/
├── validation-gate.md            # NEW — gate procedure + acceptance criterion (FR-004), scorer-of-record rule, verdict definition
├── held-out-set.md               # NEW — held-out reference set: commit-pinned repos, disjointness rule (FR-007/008), pointers to baseline sheets
├── gates/                        # NEW — Validation Gate Reports: VG-YYYY-MM-DD-NNN-<slug>.md
│   └── VG-2026-06-01-001-...md   # NEW — first worked report (gates the existing demo proposal SP-2026-06-01-001)
├── scoring/                      # EXISTING — scoring sheets
│   ├── click-8.1.7-claude-code-rev2.md           # existing
│   └── <heldout>-<ver>-baseline.md / -candidate.md  # NEW — held-out baseline + candidate sheets
└── scripts/
    └── gate-verdict.sh           # NEW (OPTIONAL) — deterministic PASS/FAIL from a report's two tables

skills/repo-skillopt/SKILL.md     # EDIT — add the validation-gate step to "Skill Convergence Loop"; bump version 0.1.0 → 0.2.0
skills/repo-skillopt/CHANGELOG.md # EDIT — add the 0.2.0 entry
adapters/claude-code/SKILL.md     # EDIT — mirror new content; canonical_version 0.2.0
adapters/codex/AGENTS.md          # EDIT — mirror; canonical_version 0.2.0
adapters/opencode/AGENTS.md       # EDIT — mirror; canonical_version 0.2.0
adapters/generic/skill.md         # EDIT — mirror; canonical_version 0.2.0
templates/skill-edit-proposal.md  # EDIT — add optional `validation_gate_report:` front-matter field (the report reference, FR-006)
```

**Structure Decision**: Single project, methodology artifacts under `rubric/` (where the rubric + scoring sheets already live), plus an additive canonical-skill edit mirrored to the four adapters. The held-out set is intentionally **non-`click`** (click motivated the existing demo proposals, so it cannot also be their held-out validator — FR-008). No changes to `installer/`, `examples/` (historical, produced under 0.1.0), or `skills/`-beyond-the-additive-edit.

## Complexity Tracking

| Violation / cost | Why needed | Simpler alternative rejected because |
|---|---|---|
| Canonical version bump `0.1.0 → 0.2.0` + update all 4 adapters | FR-006 (no acceptance without a passing gate) is only *binding* if the canonical Skill Convergence Loop states it; adapters must mirror per FR-024/025/027a | Leaving the gate purely in `rubric/` docs would make it advisory, not enforceable — defeating the feature's purpose. The additive edit is the minimal way to make it normative. |

## Post-Design Constitution Re-Check

Re-evaluated after Phase 1 (data-model, contracts, quickstart):

- Contracts confirm gate artifacts are read-mostly over the rubric and write only to `rubric/gates/`, `rubric/scoring/`, and (for regenerated specs) the held-out repo's `.reposkillopt/`. The only canonical write is the single additive Convergence-Loop edit + version bump → adapter-equivalence task is explicit and bounded.
- No aggregate gate introduced (FR-005 honored in the report schema). No new dependency/service. Vendor-neutral.
- Disjointness (held-out ≠ motivating repo) is encoded in the held-out-set contract and is auditable.

No new violations. Ready for `/speckit.tasks`.
