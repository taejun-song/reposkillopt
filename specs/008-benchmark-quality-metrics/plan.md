# Implementation Plan: Deterministic Quality Metrics for the Benchmark

**Branch**: `008-benchmark-quality-metrics` | **Date**: 2026-06-09 | **Spec**: [spec.md](./spec.md)

## Summary

Add a small, **model-free** quality-metrics layer to the benchmark so optimization lift shows even when citation-resolution is already maxed (the objectiv case). A new `quality.py` reuses feature-005's citation parsing/resolution and the 19-section/label constructs to compute citation density, labeled-claim rate, malformed-citation rate, section completeness, (optional) trace presence, and a documented composite score. `benchmark.py` attaches these to each entry and surfaces them — plus the 7 checks individually — in the report and TSV. Grounding behavior, the rubric, the canonical skill, and the optimizer reward are untouched.

## Technical Context

**Language/Version**: Python ≥ 3.10 (engine). No new language.
**Primary Dependencies**: none new — reuses `grounding` (parse_citations, GroundingResult, REQUIRED_SECTIONS), `benchmark`, stdlib (`re`, `statistics`).
**Storage**: filesystem; reports under `rubric/benchmarks/` (extended additively).
**Testing**: `python -m unittest`; deterministic fixtures with known `[fact]`/citation/section/malformed content asserting exact metric values; the optional LLM rubric is excluded from acceptance.
**Target Platform**: local CLI (`reposkillopt-engine benchmark`).
**Project Type**: single (the `engine/` package).
**Performance**: all metrics derive from the already-parsed citations + spec text; negligible cost, no extra repo I/O beyond what grounding already did.
**Constraints**: deterministic/reproducible (SC-002/SC-003); citation-resolution stays the headline (FR-006); no change to grounding/rubric/canonical/reward (FR-009).
**Scale/Scope**: small — one new module + benchmark surfacing + report fields + tests.

## Constitution Check

Unfilled constitution template — no ratified gates. Project non-negotiables:
- **No canonical/rubric/005 change** — satisfied: new module only *reads*; grounding/rubric/reward untouched (FR-009). ✅
- **Skill-first, helpers optional, no new deps** — engine-only, stdlib. ✅

No violations; Complexity Tracking empty.

## Project Structure

### Documentation (this feature)

```text
specs/008-benchmark-quality-metrics/
├── spec.md ├── plan.md ├── research.md
├── data-model.md ├── contracts/quality.md ├── quickstart.md
└── checklists/requirements.md
```

### Source Code (repository root)

```text
engine/reposkillopt_engine/
├── quality.py          # NEW: QualityMetrics + compute_quality(spec_text, ground, repo_path)
│                       #      — all deterministic; reuses grounding parsing/resolution
├── grounding.py        # unchanged (reused read-only)
├── benchmark.py        # CHANGED: EntryResult.quality + per-check; render_report surfaces them;
│                       #          TSV gains columns; optional --rubric (off by default)
├── judge.py            # unchanged (used only by the optional rubric signal)
└── cli.py              # CHANGED: benchmark gains --rubric flag (off by default)

engine/tests/
└── test_quality.py     # NEW: each metric on known fixtures; two-specs-same-grounding-differ;
                        #      determinism; composite math
engine/tests/test_benchmark.py  # CHANGED: assert new fields in result + report + TSV
```

**Structure Decision**: a dedicated `quality.py` keeps the new metrics isolated and leaves feature-005 `grounding.py` byte-untouched; the benchmark is the single surfacing point.

## Phase 0 / 1 outputs

- `research.md` — exact metric definitions (esp. malformed = comma-disjoint locators), composite weighting, non-empty-section rule, determinism.
- `data-model.md` — `QualityMetrics` fields + the extended `EntryResult`/report/TSV.
- `contracts/quality.md` — `compute_quality` signature + per-metric formula + report contract.
- `quickstart.md` — run + read the new columns + the optional `--rubric`.

## Complexity Tracking

None — additive read-only module reusing the deterministic grounding parse; no new dependency; no change to grounding/rubric/canonical/reward.
