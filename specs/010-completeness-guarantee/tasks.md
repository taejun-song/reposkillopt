# Tasks: Deterministic Completeness Guarantee

**Feature**: `010-completeness-guarantee` | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Paths relative to repo root. `[P]` = parallelizable.

## Phase 1: Setup

- [ ] T001 Baseline: `cd engine && python3 -m unittest discover -s tests -t .` + `python3 -m pyflakes reposkillopt_engine/*.py` (record the pass count as the regression floor).

## Phase 2: User Story 1 — Guaranteed accounting (P1)

**Goal**: a deterministic, idempotent step makes symbol_coverage 100%.
**Independent test**: append → 100%; second run identical.

- [ ] T002 Create `engine/reposkillopt_engine/completeness.py`: `ensure_symbol_completeness(spec_text, repo_path, *, max_chars=20000)` per `contracts/completeness.md` — extract symbols, find/split any existing "Symbols not yet analyzed" section, compute missing (name not in spec AND file not already listed), build/replace the grouped listing (names until budget, then per-file counts; counts line "N defined, M analyzed, N−M listed"); idempotent (no missing → unchanged). Export from `__init__.py`.
- [ ] T003 [P] [US1] `engine/tests/test_completeness.py`: fixture repo + a spec naming a subset → after the step `compute_structure(...).symbol_coverage == 1.0` (SC-001); a 2nd application is byte-identical (SC-002); `analyzed_fraction` equals the original subset (SC-003); no model used; the appended section is grouped by file with the counts line.

## Phase 3: User Story 2 — Honest split (P1)

**Goal**: accounting 100% but analyzed_fraction reflects only the model's real analysis.

- [ ] T004 [US2] Assert in `test_completeness.py` that for a spec analyzing M of N, post-step `analyzed_fraction == M/N` (the appended listing does not count as analysis) while `symbol_coverage == 1.0`. (Covered alongside T003; keep an explicit case.)

## Phase 4: User Story 3 — Both paths (P2)

**Goal**: engine paths complete automatically; agent path via helper.

- [ ] T005 [US3] Wire into the engine: `skillopt_native.optimize_repo` applies the step to `res.best_spec` before return (when `task.repo_path`); `benchmark.run_entry` (generate mode) applies it to the generated spec before grounding/scoring. Score/default mode untouched.
- [ ] T006 [US3] Add `complete-spec --repo --spec [--out]` subcommand in `cli.py` (model-free; writes the completed spec; prints the counts line).
- [ ] T007 [P] [US3] Test (`test_benchmark.py` extend): a generate-mode entry with a stub provider returning a spec that names a subset → `EntryResult.structure.symbol_coverage == 1.0` after the step.

## Phase 5: Canonical skill + adapters

- [ ] T008 Edit `skills/repo-skillopt/SKILL.md`: final workflow stage instructs running the completeness step (or appending the deterministically-computed listing) as the last action — never hand-transcribe. Bump `version` → 0.4.0; add CHANGELOG row.
- [ ] T009 Mirror the T008 edit into all four adapters (`adapters/{claude-code,codex,opencode,generic}/*`), bumping each `canonical_version` → 0.4.0; installer `test_integrity` still green.

## Phase 6: Polish & validation

- [ ] T010 Full engine suite + pyflakes green (no regression vs T001); `grounding.py`/`quality.py` metric definitions unchanged; installer suite green.
- [ ] T011 Live: a generate-mode spec on eco-standard-wiki routed through the completeness step → `symbol_coverage == 100%` (vs ~10% one-shot), appended section grouped+counted, `analyzed_fraction` reflects the real analysis. Record the result.

## Dependencies

- T002 blocks T003–T007.
- US1 (T002–T003) is the core; US2 (T004) an assertion on it; US3 (T005–T007) wires it; T008–T009 the skill side.
- T010–T011 after implementation.

## MVP

T002 + US1 (T003): the deterministic guarantee (symbol_coverage → 100%, idempotent). US3 wires it into the engine + agent paths; T011 proves 100% on the real repo.
