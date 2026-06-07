# Tasks: Grounding Benchmark Harness

**Feature**: `007-grounding-benchmark` | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Paths relative to repo root. `[P]` = parallelizable.

## Phase 1: Setup

- [ ] T001 Baseline: `cd engine && python3 -m unittest discover -s tests -t .` + `python3 -m pyflakes reposkillopt_engine/*.py` (record the pass count as the regression floor).

## Phase 2: Foundational (the benchmark module skeleton + manifest)

- [ ] T002 Create `engine/reposkillopt_engine/benchmark.py` with the dataclasses (`BenchmarkEntry`, `EntryResult`, `Aggregate`, `BenchmarkReport`) and `parse_manifest(text)` (TAB `name<TAB>repo<TAB>spec`; skip `#`/blank; error on malformed). Export the public names from `__init__.py`.

## Phase 3: User Story 1 — Measure grounding across a suite (P1)

**Goal**: score (repo, spec) pairs by citation-resolution rate + the 7 checks; aggregate.
**Independent test**: known-citation fixtures → exact rates + aggregate.

- [ ] T003 [US1] Implement `ensure_repo(repo, scratch)` (local path → (path, HEAD/`local`); `url@commit` → shallow fetch+checkout → (path, commit); raise on failure) and `run_entry(entry, scratch, mode='score', …)` (read spec → `ground_spec`; capture resolved/total/rate/checks/checks_pass/failures; any exception → `EntryResult.error`, never raises) in `benchmark.py`.
- [ ] T004 [US1] Implement `aggregate(results)` (mean/median rate via stdlib `statistics`, `checks_pass_share`, `skipped`) and `run_benchmark(manifest_text, mode, date, …)` (parse → per-entry → aggregate → `BenchmarkReport`).
- [ ] T005 [P] [US1] `engine/tests/test_benchmark.py`: build 2-3 tiny fixture repos (a file with N lines + a symbol) + specs with known-resolving and known-broken citations; assert exact `resolved/total`, `rate`, `checks_pass`; assert `aggregate` mean/median equal hand-computed; assert score mode makes **no** model call (use a provider stub that fails if called); assert determinism (two runs identical).

## Phase 4: User Story 2 — Reproducible report (P1)

**Goal**: the dated `rubric/benchmarks/` artifact.
**Independent test**: report contains per-entry rows, pins, aggregate, reproduce cmd, machine-readable TSV.

- [ ] T006 [US2] Implement `render_report(report, manifest_path)` → Markdown (YAML front matter + human table + aggregate + reproduce command + machine-readable fenced TSV block) per `contracts/benchmark.md`.
- [ ] T007 [US2] Add the `benchmark` subcommand in `engine/reposkillopt_engine/cli.py` (`--manifest`, `--mode`, `--out`, `--date`, `--skill`, `--rollout-provider`): run, write `rubric/benchmarks/<date>-grounding.md` (or `--out`), print the aggregate; `--mode generate` requires `--skill` + `--rollout-provider`.
- [ ] T008 [P] [US2] Extend `test_benchmark.py`: assert `render_report` output contains each entry's name+pin+rate, the aggregate, the reproduce command, and a parseable TSV block (split it back and check the numbers round-trip).

## Phase 5: User Story 3 — Generate mode (P2)

**Goal**: regenerate the spec for the current skill, then ground it.
**Independent test**: generate mode on one tiny repo produces a fresh spec via the engine and grounds it.

- [ ] T009 [US3] In `run_entry`, implement `mode='generate'`: `build_evidence_pack(repo)` + `generate_spec(provider, skill_text, name, pack.text)` → `ground_spec`. Reuse the engine provider layer. (LLM path; not in deterministic acceptance.)
- [ ] T010 [P] [US3] `test_benchmark.py`: generate mode with a **stub provider** returning a canned spec citing a real fixture file → asserts a fresh spec was grounded and the rate is reported (keeps the test deterministic without a real model).

## Phase 6: Seed suite, docs, live run

- [ ] T011 Create `rubric/benchmarks/seed-manifest.tsv` (pinned `url@commit` rows for `pallets/click` + held-out reference repos, each pointing at the shipped `examples/reference-output/.../specs/repository-specification.md`; commit pins from each spec's `target_repository_commit`) and `rubric/benchmarks/README.md` (what it measures, how to run/reproduce).
- [ ] T012 Full engine suite + pyflakes green (no regression vs T001).
- [ ] T013 Live: run the seed manifest end to end (clones the pinned repos), confirm `rubric/benchmarks/<date>-grounding.md` is written with per-repo rates + aggregate; record the headline number. (Network for clones.)

## Dependencies

- T002 blocks T003–T009.
- US1 (T003–T005) → US2 (T006–T008) → US3 (T009–T010).
- T011–T013 after the harness works.

## MVP

T002 + US1 (T003–T005): the model-free scorer + aggregate over a manifest. US2 adds the report + CLI; US3 adds generate mode; T013 produces the first real number.
