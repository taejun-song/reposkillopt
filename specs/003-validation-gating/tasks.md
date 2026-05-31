---
description: "Task list for validation-gated skill convergence"
---

# Tasks: Validation-Gated Skill Convergence

**Input**: Design documents in `/home/deploy/workspace/reposkillopt/specs/003-validation-gating/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/` (all present).

**Tests**: This is a methodology + Markdown-artifact feature. Each phase ends with a **validation checkpoint** that applies the relevant contract — these replace automated tests, mirroring features 001/002. The only executable code is the **optional** verdict helper (US4), which carries its own shell test.

**Organization**: Tasks are grouped by user story (US1–US4) so each is an independently verifiable increment.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no incomplete dependency).
- **[Story]**: User-story label (US1–US4). Setup, Foundational, and Polish carry no label.
- Every task includes an exact file path.

## Path conventions

Paths are relative to the repository root (`/home/deploy/workspace/reposkillopt/`) per `plan.md` → *Project Structure*. Gate artifacts live under `rubric/`; the binding edit touches `skills/`, `adapters/`, and `templates/`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Bring the gate artifact skeleton into existence.

- [X] T001 Create `rubric/gates/` and `rubric/scripts/` directories with placeholder `.gitkeep` files
- [X] T002 [P] Create `rubric/validation-gate.md` skeleton with the section headings required by `contracts/gate-procedure.contract.md` (procedure steps, acceptance criterion, verdict rule, scorer-of-record, optional-helper note)
- [X] T003 [P] Create `rubric/held-out-set.md` skeleton with the front matter + section headings required by `contracts/held-out-set.contract.md` (`## Members`, `## Exclusions`, `## Disjointness rule`)

**Checkpoint**: The two methodology files and the gate directories exist.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The gate methodology + held-out set + baselines that every gate run depends on. **No user story can run a gate until this is complete.**

**⚠️ CRITICAL**: Blocks all user stories.

- [X] T004 Author `rubric/validation-gate.md` fully — the 8-step procedure, the FR-004 acceptance criterion, the deterministic PASS/FAIL/HELD verdict rule from `contracts/validation-gate-report.contract.md`, the scorer-of-record reproducibility rule (FR-011), and the "optional helper, rule-is-normative-in-prose" note (FR-014)
- [X] T005 Author `rubric/held-out-set.md` — choose **≥2 commit-pinned, non-`click`** members (ideally cross-ecosystem per research R5), list them with `baseline_sheet` pointers, put `pallets/click` under `## Exclusions`, and state the disjointness rule (FR-007/008) per `contracts/held-out-set.contract.md`
- [X] T006 Produce a baseline scoring sheet `rubric/scoring/<repo>-0.1.0-baseline.md` for **each** held-out member — regenerate a Repository Specification for that repo under the released `0.1.0` skill and score it with the 15-dimension + 7-check rubric (reuses the `rubric/deterministic-checks.md` scoring-sheet schema)

**Checkpoint**: A maintainer has a documented gate, a pinned held-out set, and a baseline floor for `0.1.0`.

---

## Phase 3: User Story 1 — No-regression gate verdict (Priority: P1) 🎯 MVP

**Goal**: A candidate proposal is gated and yields a PASS when nothing regresses and a FAIL when a dimension regresses — with per-dimension before/after evidence.

**Independent Test**: Produce two gate reports against the held-out set — one for a no-regression candidate (expect PASS) and one for a deliberately harmful candidate that weakens an Operating Principle (expect FAIL naming the regressed dimension + repo) — and confirm each verdict equals the deterministic rule.

### Implementation for User Story 1

- [X] T007 [US1] Produce candidate scoring sheets `rubric/scoring/<repo>-0.1.0+SP-2026-06-01-001-candidate.md` for each held-out member — regenerate each spec under the candidate version (the existing demo proposal `SP-2026-06-01-001` applied) and score it
- [X] T008 [US1] Author the worked PASS report `rubric/gates/VG-2026-06-01-001-skillopt-secondary-structures.md` gating `SP-2026-06-01-001` per `contracts/validation-gate-report.contract.md` — per-dimension baseline-vs-candidate tables per repo, deterministic tables, `effect_realized`, and `verdict: PASS` with rationale; `regenerated_specs` point at each held-out repo's `.reposkillopt/specs/`
- [X] T009 [P] [US1] Author a FAIL demonstration report `rubric/gates/VG-2026-06-01-002-harmful-edit-demo.md` — a deliberately harmful candidate edit that regresses ≥1 dimension on a held-out repo, showing `verdict: FAIL` that names the regressed dimension(s)/check(s) and repo(s)
- [X] T010 [US1] **Validation checkpoint** — apply `contracts/validation-gate-report.contract.md` to VG-001 (PASS) and VG-002 (FAIL); confirm each `verdict` equals the deterministic rule applied to its tables; confirm per-dimension (not aggregate) comparison (FR-005)

**Checkpoint**: MVP — the gate produces correct PASS/FAIL verdicts grounded in per-dimension evidence.

---

## Phase 4: User Story 2 — Held-out set disjoint from motivating repos (Priority: P2)

**Goal**: The held-out set is pinned, ≥2, and provably disjoint from any gated proposal's motivating repositories.

**Independent Test**: Read the set definition — every member is commit-pinned with a baseline sheet; an audit of `SP-2026-06-01-001`'s `supporting_feedback` confirms none of its repos (all `click`) appear in the held-out set.

### Implementation for User Story 2

- [X] T011 [US2] Add a `## Disjointness audit` subsection to `rubric/held-out-set.md` documenting the audit procedure and recording the result for `SP-2026-06-01-001` (its `supporting_feedback` is `click`-only; held-out set excludes `click` → disjoint) per FR-008
- [X] T012 [US2] **Validation checkpoint** — apply `contracts/held-out-set.contract.md`; verify SC-004 (0 overlap), ≥2 commit-pinned members, `click` excluded, and a baseline sheet on record for each member at `0.1.0`

**Checkpoint**: The held-out set is rigorous and overfitting-proof.

---

## Phase 5: User Story 3 — Gate Report artifact + binding enforcement (Priority: P2)

**Goal**: The report schema is reusable, and a proposal cannot reach `status: accepted` without a referenced passing report — made normative in the canonical skill and mirrored across adapters.

**Independent Test**: The proposal template carries the `validation_gate_report` field; the canonical Skill Convergence Loop states the PASS-required rule; all four adapters mirror it at `canonical_version: 0.2.0`; the existing accepted demo proposal references its passing report.

### Implementation for User Story 3

- [X] T013 [P] [US3] Extend `templates/skill-edit-proposal.md` — add the optional `validation_gate_report:` front-matter field and document that a PASS report is required before `status: accepted` (FR-006, data-model entity 6)
- [X] T014 [US3] Edit `skills/repo-skillopt/SKILL.md` *Skill Convergence Loop* — add the additive rule "a proposal may move to `status: accepted` only when it references a passing Validation Gate Report (`rubric/validation-gate.md`); the report authorizes, not replaces, the version-bump flow"; bump front-matter `version: 0.1.0` → `0.2.0` (vendor-neutral; FR-002/013)
- [X] T015 [US3] Update `skills/repo-skillopt/CHANGELOG.md` — add a `## [0.2.0]` entry under `### Added` describing the validation-gate rule
- [X] T016 [P] [US3] Mirror the new rule into `adapters/claude-code/SKILL.md` and set `canonical_version: 0.2.0`
- [X] T017 [P] [US3] Mirror the new rule into `adapters/codex/AGENTS.md` and set `canonical_version: 0.2.0`
- [X] T018 [P] [US3] Mirror the new rule into `adapters/opencode/AGENTS.md` and set `canonical_version: 0.2.0`
- [X] T019 [P] [US3] Mirror the new rule into `adapters/generic/skill.md` and set `canonical_version: 0.2.0`
- [X] T020 [US3] Add `validation_gate_report: VG-2026-06-01-001` to `examples/reference-output/claude-code/.reposkillopt/proposals/SP-2026-06-01-001-accepted.md` (the accepted demo proposal now references its passing gate; keep the existing "illustrative — canonical stays unchanged" note intact)
- [X] T021 [US3] **Validation checkpoint** — apply `contracts/gate-procedure.contract.md`; re-run `contracts/adapter-equivalence.contract.md` (from feature 001) across all four adapters; confirm `canonical_version: 0.2.0` resolves to the bumped canonical `version`; vendor-neutrality sweep of the new SKILL.md text

**Checkpoint**: The gate is binding and adapter-equivalence holds at `0.2.0`.

---

## Phase 6: User Story 4 — Reproducible, version-comparable gating (Priority: P3)

**Goal**: The verdict is mechanically reproducible from a report, and gate outcomes are comparable across candidate versions by per-dimension deltas.

**Independent Test**: Run the optional helper against VG-001 (PASS) and VG-002 (FAIL) and confirm its output matches the recorded verdicts; confirm two reports' per-dimension deltas are readable side by side.

### Implementation for User Story 4

- [X] T022 [US4] Author the optional `rubric/scripts/gate-verdict.sh` — POSIX-sh that parses a report's per-dimension and deterministic tables and prints `PASS`/`FAIL` per the deterministic rule in `contracts/validation-gate-report.contract.md`; include a sibling `rubric/scripts/test_gate_verdict.sh`
- [X] T023 [US4] Add a `## Comparing versions` section to `rubric/validation-gate.md` — how to re-run the gate for a different candidate version against the same held-out set and read per-dimension deltas across reports (extends SC-006/SC-007 and feature 001's SC-012)
- [X] T024 [US4] **Validation checkpoint** — run `rubric/scripts/gate-verdict.sh` against VG-001 and VG-002; confirm output equals the recorded `verdict` (SC-005 reproducibility); confirm the helper is not required by any acceptance step (FR-014)

**Checkpoint**: Gate outcomes are reproducible and comparable across versions.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency and discoverability.

- [X] T025 [P] Update the top-level `README.md` *Evaluation* section to link `rubric/validation-gate.md` and `rubric/held-out-set.md`, and note that accepting a `scope: generic` skill edit now requires a passing validation gate
- [X] T026 [P] Vendor-neutrality sweep — grep the SKILL.md gating addition and all four adapters for runtime names ("Claude", "Codex", "OpenCode", "Copilot"); any normative occurrence is a defect (FR-002)
- [X] T027 [P] Re-run `contracts/adapter-equivalence.contract.md` across `adapters/{claude-code,codex,opencode,generic}/` to catch drift introduced by the `0.2.0` edit
- [X] T028 Run `specs/003-validation-gating/quickstart.md` end-to-end as a methodology dry-run against the produced VG reports; record any friction in `rubric/validation-gate.md`

---

## Dependencies & Execution Order

### Phase dependencies

- **Setup (Phase 1)**: no dependencies — start immediately.
- **Foundational (Phase 2)**: depends on Setup. **Blocks all user stories** (no gate can run without the methodology doc, the held-out set, and baselines).
- **User Stories**:
  - **US1 (P1)** depends only on Foundational (it runs gates against the foundational set + baselines).
  - **US2 (P2)** hardens the held-out set authored in Foundational; depends on Foundational, independent of US1.
  - **US3 (P2)** makes the gate binding; depends on US1 existing (it references the worked PASS report `VG-2026-06-01-001` from T008).
  - **US4 (P3)** depends on US1's reports (T008/T009) to verify the helper.
- **Polish (Phase 7)**: depends on US3 (the `0.2.0` edit) being complete.

### Within each user story

- Authoring tasks marked [P] run in parallel (different files).
- Validation checkpoints are sequential (depend on that story's tasks).

### Parallel opportunities

- **Phase 1**: T002, T003 parallel after T001.
- **US1**: T009 (FAIL report) parallel with T007/T008 (different files).
- **US3 adapters**: T016, T017, T018, T019 all parallel (different adapter files); T014/T015 (canonical + changelog) precede them.
- **Polish**: T025, T026, T027 parallel.

---

## Parallel Example: User Story 3 (adapter mirroring)

```text
# After T014 (SKILL.md edit + version bump) and T015 (CHANGELOG):
Task: T016 Mirror gating rule into adapters/claude-code/SKILL.md (canonical_version 0.2.0)
Task: T017 Mirror gating rule into adapters/codex/AGENTS.md (canonical_version 0.2.0)
Task: T018 Mirror gating rule into adapters/opencode/AGENTS.md (canonical_version 0.2.0)
Task: T019 Mirror gating rule into adapters/generic/skill.md (canonical_version 0.2.0)
# Then T021 re-runs adapter-equivalence across all four.
```

---

## Implementation Strategy

### MVP first (P1 only)

1. Complete Phase 1 (Setup) and Phase 2 (Foundational — methodology + held-out set + baselines).
2. Complete Phase 3 (US1): worked PASS + FAIL gate reports with correct deterministic verdicts.
3. **STOP and VALIDATE**: the gate demonstrably accepts no-regression edits and rejects regressions. This is the publishable MVP of the idea.

### Incremental delivery beyond MVP

1. Add US2 — disjointness audit hardening (overfitting-proof held-out set).
2. Add US3 — make the gate **binding** in the canonical skill + all four adapters (`0.2.0`) and wire the proposal template. *(Highest surface area: 4-adapter equivalence + version bump.)*
3. Add US4 — optional verdict helper + version-comparison docs (reproducibility).

### Notes

- [P] tasks operate on different files with no incomplete prerequisite.
- T014, T020, T023, T028 each edit a single shared file and are sequential where they touch the same file.
- The `0.2.0` bump (US3) is the riskiest change — do the four adapter mirrors together and immediately re-run adapter-equivalence (T021/T027).
- Avoid: an aggregate gate (FR-005), gating a `repository-scoped` proposal, putting `click` in the held-out set (FR-008), or letting the SKILL.md addition name any runtime (FR-002).
