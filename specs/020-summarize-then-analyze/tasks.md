# Tasks: Summarize-Then-Analyze (Map-Reduce Evidence)

**Feature**: `020-summarize-then-analyze` | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

TDD on the deterministic parts (tests RED before implementation). Reuses structure/evidence/grounding/
completeness/judge/providers — no new deps. Opt-in; default paths + frozen metrics unchanged.

## Phase 1: Setup
- [x] T001 Confirm reuse surface: `evidence._list_code_files`/`_read`, `structure.extract_symbols`, `grounding` (parse/_resolve), `completeness.ensure_symbol_completeness`, `judge.generate_spec`, `sanitize`, providers (engine/reposkillopt_engine/).

## Phase 2: Foundational — deterministic core (TDD)
- [x] T002 [P] Write failing tests `engine/tests/test_summarize.py`: `enumerate_source_files` == `_list_code_files` and is reproducible; `normalize_repo_relative` strips an absolute repo prefix + is idempotent + no-op on clean — RED.
- [x] T003 [P] Write failing tests: `summarize_repo` (fake provider) writes a summary for EVERY enumerated file (100% file coverage, incl. an `__init__.py`); a model failure still yields the deterministic skeleton; report fields (files_total==files_summarized, peak≤total) — RED.
- [x] T004 [P] Write failing tests: `assemble_from_summaries` reads all summaries + reports a missing one (no silent partial); `generate_spec_from_summaries` (fake provider) builds a spec whose evidence is the summaries, runs completeness (100% symbol coverage), citations repo-relative — RED.
- [x] T005 Implement `engine/reposkillopt_engine/summarize.py`: `enumerate_source_files`, `_summary_skeleton`, `summarize_file`, `summarize_repo`, `normalize_repo_relative`, `assemble_from_summaries`, `generate_spec_from_summaries`, `FileSummary`/`SummarizeReport` — make T002–T004 GREEN.

## Phase 3: User Story 1 — summarize every file (P1)
- [x] T006 [US1] Add `summarize <repo> [--rollout-provider] [--timeout] [--char-budget]` CLI subcommand in `engine/reposkillopt_engine/cli.py`: writes `.reposkillopt/summaries/`, prints coverage + peak/total.
- [x] T007 [US1] Repo-relative citation enforcement wired into `summarize_file` output (every summary normalized); test that a generated summary's citations resolve via `grounding`.

## Phase 4: User Story 2 — generate-spec from summaries (P1)
- [x] T008 [US2] Add `generate-spec <repo> --skill <s> [--from-summaries] [--section-scoped] [--low-context] [--out]` CLI subcommand routing to single-pack (default), section-scoped, or from-summaries; from-summaries prints peak-vs-total.
- [x] T009 [US2] Wire `generate_spec_from_summaries` → completeness + repo-relative normalization; test the produced spec scores 100% symbol coverage and citations resolve (fake provider).

## Phase 5: Polish & validation
- [x] T010 [P] Test SC-005: with the mode off, default generate path + frozen metrics unchanged; full engine suite green.
- [x] T011 Live validation on a small repo (the engine itself): `summarize` → coverage-gate `--files` 100% (no `__init__` omission) → `generate-spec --from-summaries` → check coverage + resolving citations + peak-vs-total reported.
- [x] T012 [P] Docs: engine README "summarize → generate-from-summaries" section (map-reduce, peak-vs-total, composes with coverage-gate/render/refine-spec); run full suite.

## Dependencies
- Setup → Foundational (T002–T005) → US1 (T006–T007) ∥ US2 (T008–T009) → Polish.
- Tests T002–T004 precede impl T005. T011 needs a model (live); the rest are deterministic/model-free.

## Implementation strategy
MVP = US1 (`summarize`, the map — independently valuable as a per-file index, coverage-gated). Then US2
(the reduce). Deterministic core (Phase 2) built TDD-first; the two demo defects (silent file omission;
absolute-path citations) are closed by T003 (100% file coverage) and T002/T007 (repo-relative enforcement).
