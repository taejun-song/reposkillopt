# Tasks: Deterministic Quality Metrics for the Benchmark

**Feature**: `008-benchmark-quality-metrics` | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Paths relative to repo root. `[P]` = parallelizable.

## Phase 1: Setup

- [ ] T001 Baseline: `cd engine && python3 -m unittest discover -s tests -t .` + `python3 -m pyflakes reposkillopt_engine/*.py` (record the pass count as the regression floor).

## Phase 2: Foundational (the quality module)

- [ ] T002 Create `engine/reposkillopt_engine/quality.py`: `QualityMetrics` dataclass + `compute_quality(spec_text, ground, repo_path)` per `contracts/quality.md` — fact_count, citation_density (None if 0 facts), labeled_claim_rate, malformed_citation_rate (comma-locator regex), section_completeness (present **and** non-empty), trace_presence, and the documented composite `quality_score`. Deterministic, no LLM. Export from `__init__.py`.

## Phase 3: User Story 1 — Lift visible on already-grounded repos (P1)

**Goal**: two specs with identical grounding but different discipline get different quality metrics.
**Independent test**: cleaner spec scores strictly higher composite.

- [ ] T003 [P] [US1] `engine/tests/test_quality.py`: fixtures (a) spec with a comma-malformed citation + an unlabeled `[fact]` + a missing section vs (b) the cleaned spec, **same** citation-resolution; assert each metric's exact value and that (b)'s `quality_score` > (a)'s (SC-001/FR-011); assert `fact_count==0` → `citation_density is None`, `labeled_claim_rate==1.0`; assert determinism (two calls identical).

## Phase 4: User Story 2 — Fuller reproducible report (P1)

**Goal**: metrics + per-check breakdown in report + TSV, reproducibly.

- [ ] T004 [US2] In `engine/reposkillopt_engine/benchmark.py`: add `quality: QualityMetrics` (and `rubric_score: float|None=None`) to `EntryResult`; in `run_entry`, after `ground_spec`, call `compute_quality(...)` → `res.quality`.
- [ ] T005 [US2] In `render_report`: add a quality table (per entry: density, labeled-claim, malformed, completeness, trace, composite), surface the **7 checks individually**, and append the new TSV columns after the existing ones (existing columns/positions unchanged). Print the composite-score formula.
- [ ] T006 [P] [US2] Extend `engine/tests/test_benchmark.py`: assert `EntryResult.quality` populated; assert `render_report` output contains the quality columns, the individual checks, and the appended TSV columns (round-trip a value); assert determinism of the new fields.

## Phase 5: User Story 3 — Optional model-scored signal (P3)

**Goal**: opt-in `--rubric`, off by default, clearly labeled non-reproducible.

- [ ] T007 [US3] Thread `with_rubric` through `run_benchmark`/`run_entry` (call `judge.score_spec` only when enabled + provider present → `res.rubric_score`); add `--rubric` to the `benchmark` CLI (requires `--rollout-provider`); `render_report` adds a separate **"model-scored (non-reproducible)"** block only when present.
- [ ] T008 [P] [US3] Test: default run sets `rubric_score=None` and makes **no** model call (stub provider that raises if called); the report shows only deterministic metrics (SC-003).

## Phase 6: Polish & validation

- [ ] T009 Full engine suite + pyflakes green (no regression vs T001); `grounding.py` byte-unchanged (FR-009).
- [ ] T010 Re-run the seed grounding benchmark; confirm the new quality columns appear and the report is reproducible.
- [ ] T011 Re-run a small A/B (click + objectiv local, generate mode) and confirm the quality metrics now differentiate canonical vs optimized on objectiv where citation-resolution was flat (SC-005). (LLM; record the result.)

## Dependencies

- T002 blocks T003–T008.
- US1 (T003) validates the module; US2 (T004–T006) surfaces it; US3 (T007–T008) adds the opt-in rubric.
- T009–T011 after implementation.

## MVP

T002 + US1 (T003) + US2 (T004–T006): the deterministic quality metrics, surfaced reproducibly in the report. US3 is the optional model-scored extra; T011 is the objectiv re-validation.
