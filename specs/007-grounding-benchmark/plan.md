# Implementation Plan: Grounding Benchmark Harness

**Branch**: `007-grounding-benchmark` | **Date**: 2026-06-07 | **Spec**: [spec.md](./spec.md)

## Summary

A model-free benchmark that scores the skill's Repository Specifications by **citation-resolution rate** (and the 7 deterministic checks) across a **pinned** repo suite, then writes a reproducible report under `rubric/benchmarks/`. It reuses feature-005's `grounding.ground_spec` as the scoring engine; the only new machinery is a manifest parser, a per-entry runner (with pinned shallow-clone for `url@commit` entries), an aggregator, and a report writer — plus a `benchmark` CLI subcommand and a seed manifest.

## Technical Context

**Language/Version**: Python ≥ 3.10 (engine). No new language.
**Primary Dependencies**: none new — reuses `grounding`, `evidence`, `judge`, `rubric`; pinned clone uses `git` (already assumed by the engine's digest builder). Stdlib only otherwise (`statistics`, `pathlib`, `subprocess`).
**Storage**: filesystem; reports under `rubric/benchmarks/`; scratch clones in a temp dir, removed after.
**Testing**: `python -m unittest`; deterministic tests use tiny in-repo fixture repos + specs (no network, no LLM). A live run over the seed suite validates end to end.
**Target Platform**: local CLI (`reposkillopt-engine benchmark`).
**Project Type**: single (the `engine/` package + a `rubric/benchmarks/` output dir).
**Performance**: grounding reads only cited files → cost scales with citation count, not repo size; the suite runs in seconds once repos are present.
**Constraints**: default mode is **model-free and reproducible** (SC-002/SC-003); failed entries don't abort (FR-009); no canonical/rubric/005 change (FR-011).
**Scale/Scope**: small — one new module + CLI command + seed manifest + tests + report.

## Constitution Check

Unfilled constitution template — no ratified gates. Project non-negotiables:
- **Skill-first, helpers optional, no new deps** — benchmark is opt-in tooling in `engine/`, stdlib + `git` only. ✅
- **No canonical/rubric change** — reuses grounding read-only; reports are working artifacts (FR-011). ✅

No violations; Complexity Tracking empty.

## Project Structure

### Documentation (this feature)

```text
specs/007-grounding-benchmark/
├── spec.md ├── plan.md ├── research.md
├── data-model.md ├── contracts/benchmark.md ├── quickstart.md
└── checklists/requirements.md
```

### Source Code (repository root)

```text
engine/reposkillopt_engine/
├── benchmark.py        # NEW: manifest parse, ensure_repo (pinned clone), run_entry,
│                       #      aggregate, render_report, run_benchmark; reuses ground_spec
├── grounding.py        # unchanged (reused read-only)
├── evidence.py/judge.py# unchanged (reused only in generate mode)
└── cli.py              # CHANGED: `benchmark` subcommand (--manifest, --mode, --out)

engine/tests/
└── test_benchmark.py   # NEW: manifest parse; entry scoring vs known citations; aggregate
                        #      math; report shape; error entry doesn't abort; determinism

rubric/benchmarks/
├── seed-manifest.tsv   # NEW: pinned repos + shipped reference specs
└── README.md           # NEW: what the benchmark measures + how to run/reproduce
```

**Structure Decision**: one new engine module keeps the harness cohesive; `grounding` stays the single source of the metric so the benchmark and the optimizer agree by construction.

## Phase 0 / 1 outputs

- `research.md` — manifest format, pin/clone strategy, report layout, determinism decisions.
- `data-model.md` — manifest entry, entry result, aggregate, report.
- `contracts/benchmark.md` — function signatures + the manifest grammar + report contract.
- `quickstart.md` — run the seed suite + read the report + reproduce.

## Complexity Tracking

None — additive module reusing the existing deterministic metric; no new dependency, no canonical/rubric change.
