# Implementation Plan: Deterministic Completeness Guarantee

**Branch**: `010-completeness-guarantee` | **Date**: 2026-06-10 | **Spec**: [spec.md](./spec.md)

## Summary

Add a deterministic, idempotent `ensure_symbol_completeness(spec, repo)` that appends/updates a "Symbols not yet analyzed" section listing every defined function/class not already accounted for — making `symbol_coverage` exactly 100%, model-free. Wire it into the engine spec-producing paths (optimize-repo output, benchmark generate-mode) and expose an `complete-spec` CLI helper for the agent path; the canonical skill's final stage instructs the agent to run it (mirrored to the 4 adapters, version → 0.4.0). Reuses feature-009 extraction; grounding/rubric/reward/metric definitions unchanged.

## Technical Context

**Language/Version**: Python ≥ 3.10 (engine) + Markdown (skill/adapters). No new language.
**Primary Dependencies**: none new — reuses `structure.extract_symbols` + the feature-009 accounting; stdlib `re`.
**Storage**: filesystem; no new artifacts.
**Testing**: `python -m unittest` fixtures (append → 100% coverage; idempotent; analyzed-fraction unchanged); a live generate-mode-through-the-step check on eco-standard-wiki.
**Target Platform**: local CLI + the Markdown skill.
**Project Type**: single (engine package) + Markdown skill/adapters.
**Performance**: one symbol extraction + string assembly; negligible.
**Constraints**: deterministic/idempotent/reproducible (SC-002/006); analyzed-fraction must not inflate (FR-005); grounding/rubric/reward/metric definitions unchanged (FR-010).
**Scale/Scope**: one new function + 2 wiring points + a CLI helper + skill/adapter edits + tests.

## Constitution Check

Unfilled constitution template — no ratified gates. Project non-negotiables:
- **Vendor neutrality / adapter-equivalence** — the skill edit is generic, mirrored to all 4 adapters, version bumped (FR-007/008). ✅
- **No new heavyweight dependency** — stdlib + feature-009 reuse. ✅
- **Helpers optional** — the completeness step ships as an optional helper consistent with project stance. ✅
- **Canonical change → validation gate** — referenced; live run as evidence.

No violations; Complexity Tracking empty.

## Project Structure

### Documentation (this feature)

```text
specs/010-completeness-guarantee/
├── spec.md ├── plan.md ├── research.md
├── data-model.md ├── contracts/completeness.md ├── quickstart.md
└── checklists/requirements.md
```

### Source Code (repository root)

```text
engine/reposkillopt_engine/
├── completeness.py     # NEW: ensure_symbol_completeness(spec_text, repo) -> str (idempotent)
├── structure.py        # unchanged (reused)
├── quality.py          # unchanged (accounting reused)
├── skillopt_native.py  # CHANGED: apply the step to the emitted best_spec (optimize-repo output)
├── benchmark.py        # CHANGED: generate-mode applies the step before scoring (engine path)
└── cli.py              # CHANGED: `complete-spec --repo --spec [--out]` helper subcommand

engine/tests/
└── test_completeness.py  # NEW: append→100% coverage; idempotent; analyzed-fraction unchanged; determinism

skills/repo-skillopt/SKILL.md        # CHANGED: final-stage instruction to run the completeness step (+ version 0.4.0, CHANGELOG)
adapters/{claude-code,codex,opencode,generic}/*  # CHANGED: mirror; canonical_version 0.4.0
```

**Structure Decision**: a dedicated `completeness.py` isolates the guarantee; the engine wires it at the two output/scoring points; the CLI helper + skill edit carry it to the agent path.

## Phase 0 / 1 outputs

- `research.md` — the append/update algorithm, idempotency, where it's wired, boundedness, the guaranteed-vs-analyzed split.
- `data-model.md` — the completeness transform + the listing shape.
- `contracts/completeness.md` — `ensure_symbol_completeness` signature + invariants + wiring + CLI.
- `quickstart.md` — run the helper + the engine-path demo + the live 100% check.

## Complexity Tracking

None — one additive deterministic function reusing feature-009; no new dependency; grounding/rubric/reward/metric definitions unchanged.
