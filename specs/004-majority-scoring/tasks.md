---
description: "Task list for the N-scorers majority validation gate"
---

# Tasks: N-Scorers Majority Validation Gate

**Input**: Design documents in `/home/deploy/workspace/reposkillopt/specs/004-majority-scoring/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/` (all present).

**Tests**: Methodology + Markdown-artifact feature. Each phase ends with a **validation checkpoint** against the relevant contract — these replace automated tests (mirroring features 001/003). The only executable code is the **optional** aggregation helper (US1), which carries its own shell test.

**Organization**: Tasks are grouped by user story (US1–US4). **No canonical-skill or adapter changes** — everything lands under `rubric/` (canonical stays `0.2.0`).

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no incomplete dependency).
- **[Story]**: User-story label (US1–US4). Setup, Foundational, and Polish carry no label.
- Every task includes an exact file path.

## Path conventions

Paths are relative to the repository root (`/home/deploy/workspace/reposkillopt/`). Gate methodology lives in `rubric/validation-gate.md`; reports in `rubric/gates/`; scoring sheets in `rubric/scoring/`; the optional helper in `rubric/scripts/`. The held-out set + rubric from features 001/003 are reused unchanged.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Scaffold the majority-mode methodology section.

- [X] T001 Add `## Majority mode (N scorers)` and `## Scoring modes` section scaffolds (headings + one-line intent each) to `rubric/validation-gate.md`, after the existing single-scorer content

**Checkpoint**: The methodology doc has the new section headings ready to fill.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The aggregation methodology and N-scorer baselines that every story depends on. **Blocks all user stories.**

**⚠️ CRITICAL**: Blocks all user stories.

- [X] T002 Author the `## Majority mode (N scorers)` methodology in `rubric/validation-gate.md` — roster (odd, ≥3, any independent/blind mix), aggregation (majority; median + low-agreement when `range ≥ 2`), the adjudication rule (contested at/below baseline → adjudicate or `HELD`), and the deterministic `PASS`/`FAIL`/`HELD` verdict rule, per `contracts/majority-gate-report.contract.md`
- [X] T003 [P] Author N-scorer baseline matrices `rubric/scoring/six-1.16.0-0.1.0-majority-baseline.md` and `rubric/scoring/escape-string-regexp-5.0.0-0.1.0-majority-baseline.md` — N=3 per-scorer rows + the aggregated baseline, reusing feature 003's held-out members (illustrative worked examples)

**Checkpoint**: A maintainer has the documented aggregation rule and N-scorer baselines to compare against.

---

## Phase 3: User Story 1 — N-scorer majority aggregation → verdict (Priority: P1) 🎯 MVP

**Goal**: N independent scorers' per-dimension scores aggregate by majority to a verdict; a single outlier cannot flip a dimension when the others agree.

**Independent Test**: A dimension scored `3,3,2` aggregates to `3` (majority); the lone `2` does not change it. Recompute the verdict from the aggregated scores and confirm `PASS` for a no-regression candidate.

### Implementation for User Story 1

- [X] T004 [US1] Author the worked PASS report `rubric/gates/VG-2026-06-02-001-majority-pass.md` (`mode: majority`) per `contracts/majority-gate-report.contract.md` — 3-scorer roster + independence attestation, per-scorer matrix per held-out repo, aggregated table (Baseline | scorer values | Aggregate | Method | Range | Low-agree | vs Baseline) including a contested-but-**above**-baseline dimension flagged non-blocking, and `verdict: PASS`
- [X] T005 [P] [US1] Author the optional `rubric/scripts/majority-aggregate.sh` (POSIX sh) — parse a majority report's aggregated table(s), compute per-dimension majority/median + range, apply the deterministic rule, and print `PASS`/`FAIL`/`HELD`; add `rubric/scripts/test_majority_aggregate.sh`; `chmod +x` both
- [X] T006 [US1] **Validation checkpoint** — run `rubric/scripts/majority-aggregate.sh` against VG-001 (expect `PASS`, matching the recorded verdict); confirm a 1-of-3 outlier does not flip the aggregate (SC-002); confirm per-dimension (not cross-dimension aggregate) comparison (FR-013)

**Checkpoint**: MVP — majority aggregation yields a correct, reproducible verdict robust to one outlier.

---

## Phase 4: User Story 2 — Record the per-scorer matrix, agreement, and the HELD path (Priority: P2)

**Goal**: Disagreement is fully recorded and consequential — including the `HELD` outcome when a contested dimension could mask a regression.

**Independent Test**: Read a majority report — each scorer's 0–3 per dimension, the aggregate, the method, and a flag on any `range ≥ 2` dimension are present; a contested at-or-below-baseline dimension left unadjudicated yields `HELD`.

### Implementation for User Story 2

- [X] T007 [US2] Author the HELD report `rubric/gates/VG-2026-06-02-002-majority-held.md` (`mode: majority`) — a dimension that is low-agreement AND at or below baseline, left unadjudicated, producing `verdict: HELD` that names the contested dimension; full per-scorer matrix + agreement signals per `contracts/majority-gate-report.contract.md`
- [X] T008 [US2] **Validation checkpoint** — apply the report contract to VG-002; run `majority-aggregate.sh` → `HELD`; confirm SC-004 (every `range ≥ 2` dimension flagged) and SC-009 (no PASS on a contested at/below dimension without adjudication)

**Checkpoint**: Disagreement is auditable and the HELD path works end-to-end.

---

## Phase 5: User Story 3 — Independence and roster discipline (Priority: P2)

**Goal**: Rosters are odd, ≥3, with roles and an attested independence; non-independent rows are excluded/redone.

**Independent Test**: Both reports list an odd ≥3 roster with `kind` per scorer and an independence attestation; the methodology documents excluding/redoing a scorer who saw others' scores.

### Implementation for User Story 3

- [X] T009 [US3] Confirm both reports (`VG-2026-06-02-001`, `-002`) carry an odd ≥3 roster with `kind` per scorer + `independence_attestation`, and add an `### Independence` subsection to `rubric/validation-gate.md` documenting the blind-submission requirement and the breach rule (exclude or redo the affected row)
- [X] T010 [US3] **Validation checkpoint** — inspect `rubric/gates/VG-2026-06-02-001-majority-pass.md` and `rubric/gates/VG-2026-06-02-002-majority-held.md`: confirm SC-005 (independence attested in each; the breach rule documented in `rubric/validation-gate.md`) and that each roster is odd and ≥3

**Checkpoint**: Majority votes are independent — the property that makes them meaningful.

---

## Phase 6: User Story 4 — Single vs majority mode selection (Priority: P3)

**Goal**: The project documents when majority mode is required vs when single mode suffices, with `mode` recorded in every report.

**Independent Test**: The mode-selection rule classifies a high-stakes edit (touches Operating Principles) as majority-required and a low-risk clarifying edit as single-eligible; every report states its `mode`.

### Implementation for User Story 4

- [X] T011 [US4] Author the `## Scoring modes` content in `rubric/validation-gate.md` per `contracts/scoring-modes.contract.md` — `single` vs `majority`, the required-when list (Operating-Principles edit / previously failed gate / low single-scorer confidence), `mode` recorded in every report, N-scaling, and the explicit note that majority mode needs **no canonical/adapter change**; include one majority-required and one single-eligible worked classification
- [X] T012 [US4] **Validation checkpoint** — apply `contracts/scoring-modes.contract.md`; confirm SC-007 (a reviewer can classify a given edit) and FR-010 (every report records `mode`)

**Checkpoint**: Cost is proportional to stakes; mode is explicit on every report.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Cross-references, integrity, and the no-canonical-change guarantee.

- [X] T013 [P] Add a one-line pointer to majority mode in the top-level `README.md` *Evaluation* section (alongside the existing validation-gate note), linking `rubric/validation-gate.md` → *Majority mode*
- [X] T014 [P] Run `rubric/scripts/test_majority_aggregate.sh` (full); ensure green; fix any failures
- [X] T015 [P] Confirm **no canonical/adapter change**: `git diff --stat` shows zero changes under `skills/` and `adapters/`, and `skills/repo-skillopt/SKILL.md` `version:` is still `0.2.0` (vendor-neutrality + adapter-equivalence preserved by construction)
- [X] T016 Run `specs/004-majority-scoring/quickstart.md` end-to-end as a methodology dry-run against VG-001 (PASS) and VG-002 (HELD) and the baselines; record any friction in `rubric/validation-gate.md`

---

## Dependencies & Execution Order

### Phase dependencies

- **Setup (Phase 1)**: no dependencies.
- **Foundational (Phase 2)**: depends on Setup. **Blocks all user stories** (aggregation rule + baselines).
- **User Stories**:
  - **US1 (P1)** depends only on Foundational.
  - **US2 (P2)** depends on Foundational + the US1 helper (T005) to verify `HELD`.
  - **US3 (P2)** annotates the reports authored in US1/US2; depends on those existing.
  - **US4 (P3)** depends only on Foundational (the modes section); independent of US1–US3.
- **Polish (Phase 7)**: depends on the desired stories being complete.

### Within each user story

- [P] tasks are different files; validation checkpoints are sequential.

### Same-file sequencing (NOT parallel)

- `rubric/validation-gate.md` is edited by T001, T002, T009, T011, T013 → these run sequentially.
- `rubric/gates/` reports: T004 and T007 are different files (parallel-eligible across stories).

### Parallel opportunities

- **Phase 2**: T003 (scoring sheets) parallel with T002 (methodology).
- **US1**: T005 (helper) parallel with T004 (report).
- **Polish**: T013, T014, T015 parallel.

---

## Parallel Example: User Story 1

```text
Task: T004 Author VG-2026-06-02-001-majority-pass.md (rubric/gates/)
Task: T005 Author rubric/scripts/majority-aggregate.sh + test (different files)
# Then T006 runs the helper against the report and checks the outlier property.
```

---

## Implementation Strategy

### MVP first (P1 only)

1. Complete Phase 1 (Setup) + Phase 2 (Foundational — aggregation rule + N-scorer baselines).
2. Complete Phase 3 (US1): worked PASS report + the aggregation helper proving an outlier can't flip a dimension.
3. **STOP and VALIDATE**: `majority-aggregate.sh` reproduces the recorded verdict. This is the publishable MVP of the variant.

### Incremental delivery beyond MVP

1. Add US2 — disagreement recording + the `HELD` adjudication path.
2. Add US3 — independence + roster discipline.
3. Add US4 — single-vs-majority mode-selection rule.

### Notes

- This feature deliberately makes **no change to `skills/` or `adapters/`** — majority mode is scoring methodology under the existing generic gate rule, so there is no version bump and no adapter-equivalence pass (T015 verifies this).
- Held-out scores are **illustrative worked examples** (consistent with feature 003); the methodology, schema, and verdict rule are the real deliverable.
- Avoid: a cross-dimension aggregate deciding the verdict (FR-013), an even roster, or a PASS on a contested at/below dimension without adjudication (SC-009).
