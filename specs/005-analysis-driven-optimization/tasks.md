# Tasks: Real-Analysis-Driven Per-Repo Skill Optimization

**Feature**: `005-analysis-driven-optimization` | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Paths are relative to repo root. `[P]` = parallelizable (different files, no incomplete-dep).

## Phase 1: Setup

- [x] T001 Confirm engine test baseline green: `cd engine && python -m unittest discover -s tests -t .` and `python -m pyflakes reposkillopt_engine/*.py` (record current pass count as the regression floor).

## Phase 2: Foundational (blocking prerequisites)

- [x] T002 Add `EvidencePack`, `Citation`, `GroundingResult` dataclasses — `EvidencePack` in `engine/reposkillopt_engine/evidence.py`, `Citation`/`GroundingResult` in `engine/reposkillopt_engine/grounding.py` (fields per data-model.md). Module skeletons only; no logic yet.

## Phase 3: User Story 1 — Optimize against real repository evidence (P1)

**Goal**: a cached, bounded evidence pack from the real repo replaces the 8 KB digest.
**Independent test**: pack built once, references real paths, bounded, omissions recorded.

- [x] T003 [US1] Implement `build_evidence_pack(repo_path, *, char_budget=60000, max_files=25, max_file_lines=400)` in `engine/reposkillopt_engine/evidence.py`: repo name, README head, manifest contents, top-level + source tree (exclude `.git`/`node_modules`/vendor), file-type histogram, **line-numbered** contents of key files (entrypoints + manifests + largest source files), targeted grep hits; enforce `char_budget`, populate `omitted`.
- [x] T004 [P] [US1] `engine/tests/test_evidence.py`: pack bounded to budget; `omitted` non-empty when truncated; `included_files` are real repo-relative paths; line-numbered blocks present (build against a small tmp repo fixture).
- [x] T005 [US1] Wire `RepoTask.pack` (new field) in `engine/reposkillopt_engine/skillopt_native.py`; `_score_skill` generates from `task.pack.text` with fallback to `task.digest`. (Keeps fake-provider path working.)

## Phase 4: User Story 2 — Reward grounded specs, penalize hallucinated (P1)

**Goal**: deterministic citation-resolution against the real repo, folded into the reward.
**Independent test**: grounded spec out-scores fabricated-citation spec.

- [x] T006 [US2] Implement `parse_citations(spec_text)` + `resolve_citation(repo_path, c)` in `engine/reposkillopt_engine/grounding.py` per research R3 (forms: `path:line`, `path:start-end`, `path:Symbol`, `path:Symbol:line`; `cmd:`/`output:` excluded; malformed→unresolved). No LLM/network.
- [x] T007 [US2] Implement `ground_spec(repo_path, spec_text, *, hallucination_threshold=0.9)` → `GroundingResult`: `rate`, the 7 `checks` (citation-bearing deterministic; `prior_feedback_addressed`/`adapter_preserves_intent` default True), `failures` list (concrete strings).
- [x] T008 [P] [US2] `engine/tests/test_grounding.py`: (a) `file:line` in/out of range; (b) `file:Symbol` present/absent; (c) `cmd:` excluded from rate; (d) **SC-001/FR-008**: identical specs differing only in citation targets — grounded `rate` strictly > fabricated; (e) failure messages name the offending citation/section.
- [x] T009 [US2] In `_score_skill` (`skillopt_native.py`): call `ground_spec`, **override** `card.checks` with `ground.checks`, compute `rubric_norm = Σ dim.aggregate/(15*3)`, `det_rate = mean(ground.checks)`, `reward = 0.5*rubric_norm + 0.5*det_rate`; return `(reward, spec, card, ground)`.
- [x] T010 [P] [US2] Update `engine/tests/test_skillopt_native.py`: combined-reward math; a spec with all checks passing + perfect rubric → reward 1.0; fabricated-citation spec scores lower than grounded for the same rubric.

## Phase 5: User Story 3 — Gap-driven edits + dual outputs (P2)

**Goal**: real failures steer reflect; run emits specialized skill + best spec.
**Independent test**: reflect receives failure strings; both outputs written; canonical untouched.

- [x] T011 [US3] In `optimize_repo` (`skillopt_native.py`): set the reflect `fail_reason` from the current spec's `ground.failures` (capped/deduped, fallback to generic if none); thread `ground` through the round.
- [x] T012 [US3] Add `best_spec: str` and `best_reward: float` to `NativeResult`; update on each new best (carry the accepted candidate's spec forward).
- [x] T013 [US3] In `cmd_optimize_repo` (`engine/reposkillopt_engine/cli.py`): build `pack=build_evidence_pack(repo)`; write `res.skill_text` → `<repo>/.reposkillopt/best_skill.md` and `res.best_spec` → `<repo>/.reposkillopt/specs/optimized-repository-specification.md`; print accepted count, `best_reward`, citation rate. Never write the canonical skill (FR-011).
- [x] T014 [P] [US3] Test (`test_skillopt_native.py`): `optimize_repo` with a fake provider populates `best_spec`/`best_reward` and completes with `accepted==0` without error (FR-013).

## Phase 6: Polish & live validation

- [x] T015 Full engine suite + pyflakes green (no regression vs T001 floor).
- [x] T016 Live end-to-end on `eco-standard-wiki` (keyless, 2026-06-07): **1 accepted of 2 rounds** (round 1 `accept_new_best`), reward **0.775**, citation resolution **95%** (182/192). Both outputs written; canonical untouched. The accepted edit is repo-specialized — bans language-module-path citations (e.g. `eco.cli.main:app`) and comma-list line numbers, both of which grounding flagged as unresolved on this repo. Contrast: the pre-005 digest-based run was 0/2.
- [x] T017 Update `engine/README` / `CLAUDE.md` "Recent Changes" note if present; ensure quickstart commands match the shipped CLI.

## Dependencies

- T002 blocks T003–T013.
- US1 (T003–T005) and US2 (T006–T010) share `skillopt_native.py` at T005/T009 → keep those sequential; the pure new modules (evidence/grounding) and their tests are independent `[P]`.
- US3 (T011–T014) depends on US1+US2 (needs pack + ground).
- T016 (live) depends on all implementation (T015 green).

## MVP

US1 + US2 (T003–T010) is the MVP: real evidence pack + grounded reward. US3 adds the gap-driven reflect signal and the second output. T016 is the proof on eco-standard-wiki.
