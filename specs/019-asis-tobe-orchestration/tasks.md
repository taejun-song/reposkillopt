# Tasks: As-Is Analysis → To-Be Design → Implementation Orchestration

**Feature**: `019-asis-tobe-orchestration` | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

TDD for the checker module (tests before implementation, per the project's TDD preference). Skills
are Markdown; each new skill is mirrored to all 4 adapters with `canonical_version` parity. Reuses
`grounding`, the existing `rubric/` + validation gate, and `templates/` conventions — no new deps.

## Phase 1: Setup

- [x] T001 Confirm reuse surface: `grounding.parse_citations`/`_resolve`, `rubric/validation-gate.md` + held-out set, the `templates/` + adapter conventions, and the `.reposkillopt/` artifact dirs — no new dependency (engine/ + repo root).

## Phase 2: Foundational — deterministic checker module (blocks both skills' gates)

- [x] T002 [P] Write failing tests `engine/tests/test_artifact_checks.py` for `check_task_ledger` (acceptance+deps present; missing dep id; cycle detected; invalid topological_order) — RED.
- [x] T003 [P] Write failing tests in `engine/tests/test_artifact_checks.py` for `check_architecture_view` (uncited/unresolved component or edge fails), `check_impact_analysis` (row missing citation or confidence fails), `check_adr` (<2 options fails) — RED.
- [x] T004 Implement `engine/reposkillopt_engine/artifact_checks.py`: `CheckResult`, `check_architecture_view`, `check_impact_analysis`, `check_task_ledger` (DAG acyclicity + topo validation), `check_adr` — reuse `grounding`; make T002+T003 GREEN.
- [x] T005 Add `check-artifact --kind {architecture|impact|adr|ledger} --file <f> [--repo <r>]` subcommand in `engine/reposkillopt_engine/cli.py` (architecture/impact take `--repo` for citation resolution).
- [x] T006 [P] Add the five artifact templates consistent with the existing set: `templates/architecture-view.md`, `templates/change-impact-analysis.md`, `templates/adr.md`, `templates/design-doc.md`, `templates/task-ledger.md` (per data-model.md).

## Phase 3: User Story 1 — As-is architecture analysis & blast-radius (P1)

**Goal**: a cited Architecture View + Change-Impact Analysis from a Repository Specification.
**Independent test**: `check_architecture_view` + `check_impact_analysis` pass on a generated artifact; every `[fact]` resolves.

- [x] T007 [US1] Author `skills/repo-architecture/SKILL.md` (vendor-neutral): purpose, activation verbs, prerequisite (Repository Specification), workflow producing the Architecture View (C4 levels + sequences + dependency graph) and Change-Impact Analysis (confidence + citations), R10 + no-silent-omission discipline; `version: 0.1.0`. Per `contracts/asis-architecture.skill.md`.
- [x] T008 [P] [US1] Add `skills/repo-architecture/CHANGELOG.md` with the `[0.1.0]` entry.
- [x] T009 [P] [US1] Add `rubric/asis-architecture-rubric.md` — 0–3 dimensions (architectural correctness, evidence grounding, blast-radius completeness, confidence calibration, unknown honesty, level coherence) + the deterministic checks (`check_architecture_view`, `check_impact_analysis`).
- [x] T010 [US1] Mirror `repo-architecture` into all 4 adapters (`adapters/{claude-code,codex,opencode,generic}/`) with `canonical_version: 0.1.0`, adapter-equivalence preserved.

## Phase 4: User Story 2 — To-be design & orchestration plan (P1)

**Goal**: ADRs + Design Doc + a machine-readable, dependency-ordered Task Ledger from as-is + a goal.
**Independent test**: `check_adr` + `check_task_ledger` pass; ledger graph acyclic with valid topo order; ledger is parseable by an orchestrator.

- [x] T011 [US2] Author `skills/repo-orchestration/SKILL.md` (vendor-neutral): activation, consumes as-is artifacts + goal, produces ADRs + Design Doc + Task Ledger (independent acceptance-tested tasks, declared deps, acyclic + topo order); **artifact-not-executor** rule; `version: 0.1.0`. Per `contracts/tobe-orchestration.skill.md`.
- [x] T012 [P] [US2] Add `skills/repo-orchestration/CHANGELOG.md` with the `[0.1.0]` entry.
- [x] T013 [P] [US2] Add `rubric/tobe-orchestration-rubric.md` — 0–3 dimensions (decision quality, design–evidence traceability, task independence, acceptance crispness, dependency/topo correctness, scope discipline) + the checks (`check_adr`, `check_task_ledger`).
- [x] T014 [US2] Mirror `repo-orchestration` into all 4 adapters with `canonical_version: 0.1.0`, adapter-equivalence preserved.

## Phase 5: User Story 3 — Gated convergence for the new skills (P2)

**Goal**: corrections recorded + gated; regressing edits rejected; no parallel machinery.
**Independent test**: a Skill Edit Proposal for a new skill is rejected when the held-out rubric regresses.

- [x] T015 [US3] In both new `SKILL.md` (+ adapters), reference the existing Feedback Item + Skill Edit Proposal flow and the validation gate (no forked machinery): corrections → Feedback Items; only candidate-for-generic → gated proposal; nothing silently promoted.
- [x] T016 [US3] Extend `rubric/validation-gate.md` (or add a short note) so the gate covers the two new skills. **Regeneration is agent-driven** (the candidate skill re-produces the Architecture View / Task Ledger / etc. for each held-out repo, exactly as features 003/004 regenerate the Repository Specification — no new engine generate path is required); the gate then requires **no per-dimension rubric regression AND the deterministic checks (`artifact_checks`) pass**; reject + record otherwise. (closes U1)
- [x] T016a [US3] Verify SC-004: construct a deliberately-regressing candidate skill edit (e.g. drops a rubric dimension's behavior) and assert the gate **rejects** it (held-out rubric regresses or a deterministic check fails), with the regression recorded — a model-free fixture test where possible. (closes C1 / SC-004)

## Phase 6: Polish & validation

- [x] T017 [P] Adapter-equivalence + version-parity check: both new skills present in all 4 adapters at matching `canonical_version`; the existing `repo-skillopt` contract unchanged. Also spot-check FR-014: the new generic skills contain no repository-specific facts (vendor/repo-neutral normative content). (closes C2)
- [x] T018 Live validation (model-free where possible): generate an Architecture View + Task Ledger for an in-repo example (the engine itself or eco-standard-wiki), run `check-artifact` for each kind, confirm all checks pass and citations resolve. Record under `rubric/benchmarks/` or the feature dir.
- [x] T019 [P] Update `README.md` + `engine/README.md`: the three-stage chain (understand → analyze → plan/orchestrate), the two new skills, and `check-artifact`. Run the full engine suite.

## Dependencies

- Setup (T001) → Foundational (T002–T006) → US1/US2 (can proceed in parallel) → US3 → Polish.
- T002+T003 (tests) precede T004 (impl); T004 precedes T005 and the rubric check-references (T009, T013).
- US1 (T007–T010) and US2 (T011–T014) are independent once the checker module + templates exist.
- US3 (T015–T016) depends on both skills existing. Polish last.

## Parallel example

```
After T004+T006: run US1 and US2 authoring concurrently —
  T007/T008/T009 (repo-architecture)   ||   T011/T012/T013 (repo-orchestration)
then T010 || T014 (adapter mirroring), then T015–T016 (shared gate wiring).
```

## Implementation strategy

MVP = **US1** (the as-is Architecture View + Change-Impact, backed by `check_architecture_view`/
`check_impact_analysis`) — independently valuable. Then US2 (to-be + ledger), then US3 (gated
convergence). The checker module + templates (Phase 2) are the shared foundation built TDD-first.
