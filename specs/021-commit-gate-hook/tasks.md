# Tasks: Commit-Time Gate Hook (Auto-Remediating Pre-Commit Enforcement)

**Feature**: `021-commit-gate-hook` | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

TDD on the deterministic parts (tests RED before implementation): gate selection, the bounded
gate-set-monotonic loop, re-stage accounting, the no-provider fallback, and the hook
chaining/exit-status/bypass. Reuses refine/judge/grounding/completeness/quality/structure/
artifact_checks/providers/coverage-gate.sh + installer/lib/{manifest,util,targets}.sh — **no new deps**.
Opt-in per repo; frozen `grounding` and all metric definitions unchanged.

## Phase 1: Setup

- [x] T001 Confirm the reuse surface compiles/imports as planned: `refine.{spec_gaps,refine_once,score_spec}`, `judge.revise_spec`, `grounding.ground_spec`, `completeness.ensure_symbol_completeness`, `quality/structure.compute_structure`, `artifact_checks.{check_architecture_view,check_impact_analysis,check_adr,check_task_ledger}`, `providers.make_provider` (keyless ids claude-cli/opencode-cli/ollama), `scripts/coverage-gate.sh`, and `installer/lib/{manifest,util,targets}.sh` (manifest_upsert/remove_row/list, copy_atomic, read_field). Note exact signatures in `engine/reposkillopt_engine/commit_gate.py` header.

## Phase 2: Foundational — deterministic engine core (TDD) — BLOCKS all user stories

- [x] T002 [P] Write failing tests `engine/tests/test_commit_gate.py::TestClassifyAndSelect`: `classify_artifact(path,text)` returns `repo_spec|architecture|impact|adr|ledger|other` for representative path+content fixtures, and `select_gates(kind)` returns the D1 table subset (repo_spec→{coverage,grounding,completeness}; architecture→{check_artifact,grounding}; adr→{check_artifact}; other→{grounding}). Deterministic/reproducible — RED.
- [x] T003 [P] Write failing tests `…::TestRunGates`: `run_gates(repo,path,text)` returns a `GateReport` whose `passing` set and `all_pass` match hand-computed verdicts on a grounded vs under-grounded spec fixture (reuses ground_spec/compute_structure/coverage-gate.sh/artifact_checks); a clean artifact ⇒ `all_pass=True` with no model involved — RED.
- [x] T004 [P] Write failing tests `…::TestMonotonicBoundedLoop` using fake providers: a candidate that drops a previously-passing gate is **rejected** (`regressed=True`, never carried/re-staged); the loop stops at the round budget; the loop stops early on a no-improvement round; on convergence `RemediationResult.converged=True` and `changed=True`; the carried artifact's `passing` set is non-decreasing across rounds (SC-005) — RED.
- [x] T005 [P] Write failing tests `…::TestProviderFallback`: `detect_keyless_provider('auto', timeout)` returns `None` when no candidate is available (monkeypatch `shutil.which`→None and the ollama probe→fail) and rejects api-key ids; with provider `None`, `gate_commit(...)` runs gates, sets `degraded=True`, performs **no** model call, and returns exit 1 with per-gate report (no hang) — RED.
- [x] T006 [P] Write failing tests `…::TestRestageAccounting` (with `--no-restage`/injectable git): only artifacts whose staged content changed appear in `restaged`; an already-passing artifact is never re-staged and triggers no model call (FR-003); the converged text equals what passed the gates (FR-014) — RED.
- [x] T007 Implement `engine/reposkillopt_engine/commit_gate.py` to make T002–T006 GREEN: `ArtifactKind`/`Gate` constants, `GateVerdict`/`GateReport`/`RemediationRound`/`RemediationResult`/`CommitGateOutcome` dataclasses, `classify_artifact`, `select_gates`, `run_gates` (coverage via `scripts/coverage-gate.sh` subprocess; grounding via `ground_spec`; completeness via `compute_structure`; check_artifact via `artifact_checks`), `remediate` (wrap `refine_once`+`ensure_symbol_completeness` with the gate-set-monotonic acceptance rule + termination, D2/D3), `detect_keyless_provider` (D4), and `gate_commit` (orchestrate; read index via `git show :<path>`; re-stage via `git add`; D5).

## Phase 3: User Story 1 — auto-fix before commit (P1) 🎯 MVP

**Goal**: a failing staged artifact is remediated and re-staged so the commit lands passing.
**Independent test**: stage an under-grounded spec with a reachable provider → committed spec passes all gates; report shows rounds taken.

- [x] T008 [US1] Add the `gate-commit` subcommand in `engine/reposkillopt_engine/cli.py` (`cmd_gate_commit` + parser: `--repo`, `--skill`, `--staged …`, `--rollout-provider auto|<keyless>`, `--rounds` default 3, `--timeout`, `--no-restage`) wiring to `commit_gate.gate_commit`; map outcomes to exit codes 0/1/2 per the contract; print the per-artifact, per-gate report and (on block) the bypass instructions.
- [x] T009 [US1] Test `engine/tests/test_commit_gate.py::TestGateCommitCli`: convergent case (fake `_SpecStub`-style provider) ⇒ exit 0, artifact in `restaged`, final spec all-pass; already-clean case ⇒ exit 0, empty `restaged`, zero model calls; non-convergent case ⇒ exit 1 with residual-gate report and nothing re-staged.

## Phase 4: User Story 2 — never trap the developer (P1)

**Goal**: graceful degradation + bypass; no hang.
**Independent test**: no provider → block-and-report promptly; env toggle and `--no-verify` both let the commit through.

- [x] T010 [US2] Author the portable hook `installer/hooks/pre-commit` (POSIX sh): chain-first (preserve exit status), `REPOSKILLOPT_HOOK=off` no-op, detect staged `.reposkillopt/` via `git diff --cached --name-only --diff-filter=ACM`, delegate to `python3 -m reposkillopt_engine gate-commit … --rollout-provider auto`, and block-and-report (no hang) if `python3`/engine is unreachable — printing bypass instructions on any block.
- [x] T011 [US2] Test `installer/tests/test_hook.sh` (run under bash AND dash): source-only commit ⇒ hook no-op (exit 0, no engine call); `REPOSKILLOPT_HOOK=off` ⇒ no-op; staged `.reposkillopt/` artifact with a stubbed `gate-commit` returning non-zero ⇒ hook blocks (propagates exit); engine-unreachable path prints block-and-report + bypass and exits non-zero without hanging.

## Phase 5: User Story 3 — chain a pre-existing hook (P2)

**Goal**: install over an existing pre-commit hook without clobbering it; uninstall restores it.
**Independent test**: existing hook that exits non-zero still blocks after install; uninstall restores it byte-for-byte.

- [x] T012 [US3] Implement `installer/lib/hook.sh`: `hook_install` (resolve `git rev-parse --git-path hooks`; if a `pre-commit` exists, `copy_atomic` it to `pre-commit.reposkillopt-chained`; install the hook executable; `manifest_upsert` adapter `git-hook` with `paths_csv=<hook>[,<backup>]`), `hook_uninstall` (remove hook; restore recorded backup exactly; `manifest_remove_row`), `hook_list` passthrough; not-a-git-repo ⇒ warn+skip; re-install does not double-chain.
- [x] T013 [US3] Test `installer/tests/test_hook.sh` (bash AND dash) for chaining: with a pre-existing pre-commit hook that exits 1, after `hook_install` a commit still runs it and is blocked; the chained backup is recorded in the manifest; `hook_uninstall` restores the original `pre-commit` byte-for-byte and removes our hook; re-install over our own hook preserves the original backup (no double-chain).

## Phase 6: User Story 4 — installer lifecycle (P2)

**Goal**: install/list/uninstall the hook through the existing installer + manifest.
**Independent test**: install → list shows git-hook row + manifest records it; uninstall → row and hook gone.

- [x] T014 [US4] Wire `installer/reposkillopt-install`: add `--hook` (MODE=hook → `hook_install`), route `--list` to also show the git-hook row (via existing `manifest_list`), and `--uninstall git-hook` → `hook_uninstall`; update `usage()`; source `lib/hook.sh`.
- [x] T015 [US4] Test `installer/tests/test_hook.sh` (bash AND dash) for lifecycle: `--hook` install into a temp git repo writes the hook + a `git-hook` manifest row; `--list` shows it; `--uninstall git-hook` removes the hook and the row (exact-removal vs the recorded paths); install into a non-git dir warns and skips without error.

## Phase 7: Polish & validation

- [x] T016 [P] Add `installer/tests/test_hook.sh` to the installer test runner (`installer/tests/run.sh`) and confirm the whole installer suite + the engine `unittest` suite are green under both bash and dash.
- [x] T017 [P] Docs: `engine/README.md` — a "Commit-time enforcement: `gate-commit`" section (gate-selection table, bounded+monotonic+nondeterminism honesty, exit codes); `installer/README.md` — `--hook` install/list/uninstall, chaining, `core.hooksPath`, and the two bypasses.
- [x] T018 Live validation on a small repo: install the hook, stage a deliberately under-grounded spec, `git commit` → observe in-hook remediation converge and the commit land with all gates passing (report rounds + re-staged set); then stage an unfixable artifact / disable the provider → observe block-and-report + bypass; finally uninstall and confirm restore. Record real numbers (rounds, before/after gate sets) honestly.

## Dependencies

- Setup (T001) → Foundational core T002–T007 (tests T002–T006 precede impl T007) → user stories.
- US1 (T008–T009) depends only on the engine core. US2 hook (T010–T011) depends on the `gate-commit` CLI (T008). US3 (T012–T013) and US4 (T014–T015) are the installer subsystem: T012 (hook.sh) precedes T014 (installer wiring); both precede T016. US4 reuses the chaining from US3.
- Polish T016–T018 last. T018 needs a live keyless provider; everything else is deterministic/model-free.

## Parallel opportunities

- T002–T006 are independent test files/classes → author in parallel ([P]).
- After T007: US1 engine-CLI work (T008) and US2 hook authoring (T010) can proceed in parallel; the installer libs T012 and docs T017 are independent ([P]).

## Implementation strategy

**MVP = US1** (the `gate-commit` engine entrypoint + auto-remediate-and-restage) — independently
valuable and fully unit-testable without a hook. US2 adds the portable hook + graceful degradation
(the safety guarantee). US3/US4 add the installer lifecycle (chain + manifest). The deterministic core
(Phase 2) is built TDD-first; the gate-set-monotonic non-regression and the no-hang fallback are the
two highest-risk invariants and are pinned by T004/T005 before any implementation.
