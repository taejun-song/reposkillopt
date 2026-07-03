# Tasks: Deterministic Hallucination Catcher (Claim-Support Verifier)

**Feature**: `022-hallucination-gate` (stacked on `021-commit-gate-hook`) | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

TDD on every deterministic part (tests RED before implementation). Reuses grounding (frozen)/structure/
quality/refine/commit_gate/benchmark — **no new deps**. Model-free; `grounding` and all metric
definitions unchanged.

## Phase 1: Setup

- [x] T001 Confirm the reuse surface + signatures in the header of `engine/reposkillopt_engine/hallucination.py`: `grounding.parse_citations`/`Citation`(raw,path,kind,line,symbol)/`_resolve` (frozen), `structure.extract_symbols`(name,file,line)/`_read`, `evidence._list_code_files`, `commit_gate.classify_artifact`, `refine.spec_gaps`, `quality` label notion. Note the D2 code-like rule + D6 window default (3).

## Phase 2: Foundational — the deterministic catcher (TDD) — BLOCKS all user stories

- [x] T002 [P] Write failing tests `engine/tests/test_hallucination.py::TestTokens`: the D2 "code-like identifier" rule (snake_case/CamelCase/dotted/call-form/path/known-symbol are code-like; plain words `TODO`/`note`/`Redis` are NOT) and checkable-token extraction from a `[fact]` span — RED.
- [x] T003 [P] Write failing tests `…::TestClaimCodeMismatch`: a `[fact]` whose code token is absent from the cited file within ±window ⇒ `claim_code_mismatch` finding at the claim line; a `[fact]` whose token IS in the window ⇒ no finding; a prose-only claim (no code token) ⇒ no finding (blind spot honored) — RED.
- [x] T004 [P] Write failing tests `…::TestFabricatedSymbol`: a backticked code-like identifier absent from `extract_symbols` names AND the file tree ⇒ `fabricated_symbol`; a real symbol/path ⇒ none; a non-code-like backtick (`TODO`) ⇒ none; empty-symbol repo falls back to file-tree match — RED.
- [x] T005 [P] Write failing tests `…::TestUnlabeledClaim`: on a repo_spec-kind artifact, a prose line naming a resolvable symbol/file with no R10 label ⇒ `unlabeled_claim`; a labeled line / a heading / a table row / an accounting line ⇒ none; a non-claim-bearing kind ⇒ none — RED.
- [x] T006 [P] Write failing tests `…::TestUnsupportedQuantity`: a number in a `[fact]` absent from the cited window ⇒ `unsupported_quantity`; a number present in the window ⇒ none; citation line digits / version tokens are excluded — RED.
- [x] T007 [P] Write failing tests `…::TestDeterminismAndClean`: `detect_hallucinations` output is byte-identical across two runs (sorted by (line,kind,token)); a genuinely grounded, fully-labeled spec ⇒ `[]` (SC-002/SC-003) — RED.
- [x] T008 Implement `engine/reposkillopt_engine/hallucination.py` to make T002–T007 GREEN: `Finding`/`CheckKind`, `_code_like`, `_checkable_tokens`, `_window_lines`, the four checks, and `detect_hallucinations(repo, artifact_path, text, *, window=3)` (classify via `commit_gate.classify_artifact`; reuse `parse_citations`/`_resolve`/`extract_symbols`; sorted output).

## Phase 3: User Story 1 — catch mis-cited claims (P1) 🎯 MVP

**Goal**: flag a claim whose code token isn't at the cited span; don't flag a supported one.
**Independent test**: mismatch fixture → one `claim_code_mismatch`; supported fixture → none.

- [x] T009 [US1] Add the `check-hallucination` CLI (`cmd_check_hallucination` + parser `--repo/--file/--window/--json`) in `engine/reposkillopt_engine/cli.py`; print `<file>:<line> <kind>: <reason>` per finding or `clean`; exit 0/1/2.
- [x] T010 [US1] Test `…::TestCheckHallucinationCli`: mismatch artifact ⇒ exit 1 + a `claim_code_mismatch` line; clean artifact ⇒ exit 0 + `clean`; missing file ⇒ exit 2.

## Phase 4: User Story 2 — invented symbols, dropped labels, fabricated quantities (P1)

**Goal**: the other three checks catch their class and spare clean input.
**Independent test**: one fixture per class ⇒ the expected finding kind; clean ⇒ none. (Checks implemented in T008; this story proves them end-to-end via the CLI + a combined fixture.)

- [x] T011 [US2] Test `…::TestAllKindsOnCombinedSpec`: a single spec carrying one instance of each of the four classes ⇒ exactly four findings, one per kind, each at the right line; the clean counterpart ⇒ zero. (Locks SC-001 recall=1.0 + SC-002 precision=1.0 on the fixtures.)

## Phase 5: User Story 3 — zero-install shell gate + parity (P2)

**Goal**: a dependency-free gate runs the same checks and agrees with the engine.
**Independent test**: shell gate and engine agree (verdict + kinds) on shared fixtures; gate runs under bash and dash.

- [x] T012 [US3] Implement `scripts/hallucination-gate.sh` (POSIX sh + grep/sed/awk; sibling to coverage-gate.sh): the four checks with the D2/D6 rules; args `<repo> <artifact> [--window N] [--max N]`; exit 0 clean / 1 findings / 2 usage; print `<artifact>:<line> <kind>: …`.
- [x] T013 [US3] Write `scripts/tests/test_hallucination_gate.sh` (runs under bash AND dash): the four checks on fixtures; and a PARITY check that the shell gate and `check-hallucination` agree on clean-vs-flagged + finding kinds for the shared fixture set.

## Phase 6: User Story 4 — wire into the loop + commit gate (P2)

**Goal**: findings become gaps the loop fixes; the commit gate blocks/remediates unsupported claims.
**Independent test**: refine reduces findings (never increases); commit gate FAILs on an unsupported claim, PASSes once clean.

- [x] T014 [US4] Edit `engine/reposkillopt_engine/refine.py`: `spec_gaps(repo, spec)` additionally yields one gap string per `hallucination.detect_hallucinations` finding (purely additive; existing gaps unchanged).
- [x] T015 [US4] Edit `engine/reposkillopt_engine/commit_gate.py`: add a `HALLUCINATION` gate id; `select_gates` includes it for `repo_spec`/`architecture`/`impact`; `run_gates` adds a verdict `detect_hallucinations(...) == []` with reasons from the findings.
- [x] T016 [US4] Tests: `engine/tests/test_hallucination.py::TestWiring` — `spec_gaps` includes hallucination gaps on a hallucinated spec; `commit_gate.run_gates` returns a failing `hallucination` verdict for an unsupported-claim repo_spec and passing once clean; `refine`-style loop with a fake fixing provider yields a non-increasing finding count (SC-005).

## Phase 7: User Story 5 — mutation benchmark (P3)

**Goal**: measure per-class recall + overall precision; write a calibration report.
**Independent test**: recall/precision equal the values computed from the known injection set.

- [x] T017 [P] [US5] Write failing tests `engine/tests/test_halluc_bench.py`: each mutator (flip_citation_line/rename_cited_symbol/invent_api/strip_label/alter_quantity) injects a detectable instance of its class at a known site; `run_mutation_benchmark` returns per-class recall == flagged/injected and precision == (clean⇒1.0) — computed vs the known set (SC-006) — RED.
- [x] T018 [US5] Implement `engine/reposkillopt_engine/halluc_bench.py` (mutators + `run_mutation_benchmark` + `CalibrationReport` writer under `rubric/benchmarks/`) and the `halluc-bench` CLI (`--repo/--spec/--window/--model/--out`) in cli.py — make T017 GREEN.

## Phase 8: Polish & validation

- [x] T019 [P] Add `scripts/tests/test_hallucination_gate.sh` to the shell test runner; confirm the full engine `unittest` suite + the shell suite are green under bash and dash; `grounding`/rubric/reward unchanged (SC-007).
- [x] T020 [P] Docs: `engine/README.md` — a "Hallucination catcher" section (the four checks, the blind spot, the shell gate, loop/commit-gate wiring, the mutation benchmark + per-model calibration).
- [x] T021 Live validation on a small repo: write an intentionally hallucinated spec (one of each class), run `check-hallucination` (flags all four) and the shell gate (parity), then run `refine-spec` with a real keyless provider and confirm the finding count drops toward zero; run `halluc-bench` and record the real per-class recall/precision. Report honestly.

## Dependencies

- Setup (T001) → catcher core T002–T008 (tests precede impl T008) → user stories.
- US1 (T009–T010) and US2 (T011) need only T008. US3 shell gate (T012–T013) is independent of the engine wiring. US4 (T014–T016) needs T008 (+ commit_gate from feature 021, present on this branch). US5 (T017–T018) needs T008.
- Polish T019–T021 last. T021 needs a live provider; everything else is deterministic/model-free.

## Parallel opportunities

- T002–T007 are independent test classes → author in parallel ([P]).
- After T008: the shell gate (T012), the benchmark tests (T017), and docs (T020) proceed in parallel with the CLI/wiring work.

## Implementation strategy

**MVP = US1 + US2** (the catcher + CLI proving all four checks with recall=1.0/precision=1.0 on the
fixtures) — independently valuable and fully model-free. US3 adds the zero-install parity gate; US4
makes it enforced (loop + commit gate); US5 is the meta-loop that measures and tunes it per model. The
determinism (T007) and the precision guards (clean ⇒ no findings, T011) are the highest-risk invariants
and are pinned by tests before implementation.
