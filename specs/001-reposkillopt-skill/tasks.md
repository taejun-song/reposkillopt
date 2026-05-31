---

description: "Task list for RepoSkillOpt MVP — portable cross-agent skill package"
---

# Tasks: RepoSkillOpt — Portable Cross-Agent Skill Package

**Input**: Design documents in `/home/deploy/workspace/reposkillopt/specs/001-reposkillopt-skill/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md` (all present).

**Tests**: The spec does **not** request automated tests. Each phase ends with a **validation checkpoint** that applies the relevant contract checklist by reading the produced artifacts; these checkpoints replace traditional test tasks for this Markdown-first project.

**Organization**: Tasks are grouped by user story so each story can be delivered as an independently testable increment.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks).
- **[Story]**: User-story phase label (US1–US8). Setup, Foundational, and Polish phases carry no story label.
- Every task includes an exact file path.

## Path conventions

All paths are relative to the repository root (`/home/deploy/workspace/reposkillopt/`) and follow the layout in `plan.md` → *Project Structure → Source Code*.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Bring the project skeleton into existence.

- [X] T001 Create top-level directory layout per `plan.md` — `skills/repo-skillopt/`, `templates/`, `rubric/`, `adapters/{claude-code,codex,opencode,generic}/`, `examples/reference-output/{claude-code,codex,opencode,generic}/.reposkillopt/{specs,feedback,rollouts,proposals}/`
- [X] T002 [P] Add `LICENSE` at the repository root (Apache-2.0 or MIT — author's choice, recorded in the LICENSE file itself)
- [X] T003 [P] Create `skills/repo-skillopt/CHANGELOG.md` scaffold using Keep-A-Changelog format with an unfilled `## [0.1.0] — 2026-05-31` section header

**Checkpoint**: Directory tree and license exist; the project compiles in the trivial sense (Markdown files placed at well-known paths).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Author the canonical skill, the four authoring templates, and the top-level README. Every user story below depends on these.

**⚠️ CRITICAL**: No user-story work can begin until this phase is complete.

- [X] T004 [P] Author `templates/repository-specification.md` per `contracts/repository-specification.contract.md` — front-matter schema (`spec_id`, `target_repository`, `target_repository_url`, `target_repository_commit`, `skill_version`, `adapter`, `created`, `revised`, `revision`, `status`), all 19 required sections from FR-005, label/citation rules using the R10 notation, optional `## Change log` appendix
- [X] T005 [P] Author `templates/human-feedback.md` per `contracts/feedback-item.contract.md` — `FB-YYYY-MM-DD-NNN-<slug>.md` filename convention, FR-013 front matter (`id`, `timestamp`, `author`, `type` enum, `references`, `scope`, `status`), `## Feedback` and `## Suggested action` sections
- [X] T006 [P] Author `templates/rollout-log.md` per `contracts/rollout-log.contract.md` — `RL-YYYY-MM-DDTHHMMSS-<adapter>.md` convention, FR-017 front matter, the four required sections (`Files inspected`, `Claims produced`, `Human feedback received this session`, `Revisions applied`)
- [X] T007 [P] Author `templates/skill-edit-proposal.md` per `contracts/skill-edit-proposal.contract.md` — `SP-YYYY-MM-DD-NNN-<slug>.md` convention, FR-019/FR-020 front matter including `review_time_estimate_minutes ≤ 5`, the six `edit_kind` values, the three required sections (`Proposed text`, `Diff against current canonical`, `Justification`), explicit preservation rule for rejected proposals
- [X] T008 Author canonical `skills/repo-skillopt/SKILL.md` v0.1.0 per `contracts/canonical-skill.contract.md` (depends on T004–T007 because the Repository Specification Format, Human Feedback Loop, Skill Convergence Loop, and Rollout Log references all point at the templates by path) — YAML front matter with `name: repo-skillopt`, `description:` (must include the FR-004 trigger verbs), `version: 0.1.0`; the nine required sections in order; all FR-007–FR-011 principles; FR-012 workflow stages (a)–(g); FR-005 spec format list; FR-013–FR-016 feedback rules; FR-018–FR-022 convergence rules; FR-008 output discipline using the R10 label notation; **no mention of any specific agent runtime in normative content** (FR-002)
- [X] T009 Author top-level `README.md` per FR-032 (depends on T008) — what RepoSkillOpt is; the canonical skill location; the four adapter directories (placeholders for adapters not yet shipped); the `.reposkillopt/{specs,feedback,rollouts,proposals}/` layout convention from FR-036a; pointer to `specs/001-reposkillopt-skill/quickstart.md`; explicit Limitations section stating "no universal repository understanding; no replacement for human code review; limited initial language coverage" per AC-10 / SC-011
- [X] T010 Update `skills/repo-skillopt/CHANGELOG.md` to fill the `## [0.1.0] — 2026-05-31` section with `### Added` entries enumerating the canonical skill and the four templates
- [X] T011 **Validation checkpoint** — run the `contracts/canonical-skill.contract.md` acceptance checklist against `skills/repo-skillopt/SKILL.md`; fix any failing item; confirm vendor-neutrality (FR-002), R10 notation (FR-008), and template references (FR-006/FR-013/FR-017/FR-019) all pass

**Checkpoint**: Canonical skill, four templates, changelog, and top-level README exist and pass the canonical-skill contract. User-story phases may now proceed in parallel.

---

## Phase 3: User Story 1 — Install and use the canonical skill (Priority: P1) 🎯 MVP

**Goal**: An engineer can drop the Claude Code adapter into a target environment, ask the agent to understand a repository, and observe the FR-012 workflow execute and a Repository Specification appear under `.reposkillopt/specs/`.

**Independent Test**: Per `quickstart.md` steps 1–2, install `adapters/claude-code/SKILL.md` into a clean target environment with `pallets/click@8.1.7` checked out; issue "Help me understand this repository"; verify the skill activates and produces a Repository Specification at `.reposkillopt/specs/repository-specification.md` containing every section in FR-005.

### Implementation for User Story 1

- [X] T012 [P] [US1] Author `adapters/claude-code/SKILL.md` per Phase 0 R2 and `contracts/adapter-equivalence.contract.md` — YAML front matter with `name: repo-skillopt`, `description:` (includes FR-004 trigger verbs), `canonical_version: 0.1.0`, `adapter: claude-code`; all nine canonical sections preserved in order; no normative content references any other vendor (FR-002, FR-024, FR-025)
- [X] T013 [P] [US1] Author `adapters/claude-code/README.md` — install path (`<target-repo>/.claude/skills/repo-skillopt/SKILL.md`), how to activate via prompt, verification commands, "Known cross-agent differences" placeholder section per Phase 0 R7
- [X] T014 [US1] Cross-link the Claude Code install steps from the top-level `README.md` (update `README.md` to add a "Quick start (Claude Code)" subsection that mirrors `specs/001-reposkillopt-skill/quickstart.md` steps 1–3)
- [X] T015 [US1] **Validation checkpoint** — apply `contracts/adapter-equivalence.contract.md` checklist (all 14 rows) to `adapters/claude-code/SKILL.md`; confirm `canonical_version` resolves; confirm no canonical section, principle, or rule was dropped or weakened

**Checkpoint**: User Story 1 is complete — the Claude Code adapter installs and (when run) activates per the FR-004 triggers. SC-005 partial coverage achieved (1 of 4 adapters).

---

## Phase 4: User Story 2 — Produce an evidence-grounded Repository Specification (Priority: P1)

**Goal**: The agent (Claude Code adapter from US1) produces a structured Repository Specification with all 19 FR-005 sections, every major claim carrying an R10 label, and every `**[fact]**` claim citing a resolvable repository artifact in `pallets/click@8.1.7`.

**Independent Test**: Sample at least 10 citations in the produced spec; every cited path resolves to an existing file in `click@8.1.7`; every cited symbol can be located. Spec contains all 19 sections (SC-004). At least 90% of major claims labeled (SC-002), at least 95% of `**[fact]**` citations resolve (SC-003).

### Implementation for User Story 2

- [X] T016 [US2] Author `examples/reference-output/claude-code/.reposkillopt/specs/repository-specification.md` revision 1 — populate against `pallets/click@8.1.7`; front matter `spec_id: click-8.1.7`, `target_repository: pallets/click`, `target_repository_url: https://github.com/pallets/click`, `target_repository_commit: 8.1.7`, `skill_version: 0.1.0`, `adapter: claude-code`, `created: 2026-05-31`, `revised: 2026-05-31`, `revision: 1`, `status: revised`; all 19 sections from FR-005; every major claim prefixed with one of `**[fact]**`/`**[inference]**`/`**[unknown]**`/`**[human]**`; every `**[fact]**` followed by at least one citation (`path:line`, `path:symbol`, or `cmd:`/`output:`); Evidence index de-duplicated
- [X] T017 [P] [US2] Author `examples/reference-output/claude-code/.reposkillopt/rollouts/RL-2026-05-31T100000-claude-code.md` documenting the rollout that produced T016 — FR-017 front matter, the four required sections, `spec_id: click-8.1.7`
- [X] T018 [US2] **Validation checkpoint** — apply `contracts/repository-specification.contract.md` acceptance checklist to T016; verify SC-002 (≥90% labeled), SC-003 (≥95% citations resolve at commit `8.1.7`), SC-004 (all 19 sections present); apply `contracts/rollout-log.contract.md` to T017

**Checkpoint**: User Story 2 is complete — a working reference Repository Specification exists, validated against the contracts and the success criteria.

---

## Phase 5: User Story 3 — Provide human feedback that improves the current specification (Priority: P1)

**Goal**: Three Feedback Items (covering three distinct types — `correction`, `missing-context`, `terminology`) are recorded against the US2 spec; the spec is revised to revision 2 incorporating all three; one Feedback Item is `scope: repository-scoped` to demonstrate FR-016 scope discipline.

**Independent Test**: Each of the three Feedback Items exists under `.reposkillopt/feedback/`, has the correct `type` and `scope`, and is referenced in the spec's Change log. The terminology item (scoped `repository-scoped`) does NOT trigger any canonical-skill edit. SC-007: all three feedback items reflected in revision 2 and recorded with traceable ids.

### Implementation for User Story 3

- [X] T019 [P] [US3] Author `examples/reference-output/claude-code/.reposkillopt/feedback/FB-2026-05-31-001-entrypoint-correction.md` — `type: correction`, `scope: repository-scoped`, references a specific claim in the spec, body has `## Feedback` and `## Suggested action`, `status: applied`
- [X] T020 [P] [US3] Author `examples/reference-output/claude-code/.reposkillopt/feedback/FB-2026-05-31-002-missing-context.md` — `type: missing-context`, `scope: candidate-for-generic` (signals a possible canonical improvement), references the relevant section, `status: applied`
- [X] T021 [P] [US3] Author `examples/reference-output/claude-code/.reposkillopt/feedback/FB-2026-05-31-003-terminology.md` — `type: terminology`, `scope: repository-scoped`, demonstrates repo-specific vocabulary that MUST NOT enter the canonical skill (FR-016), `status: applied`
- [X] T022 [US3] Revise `examples/reference-output/claude-code/.reposkillopt/specs/repository-specification.md` to revision 2 (depends on T016, T019–T021) — increment `revision` to `2`, update `revised`, apply all three feedback items: replace superseded claims with cited corrections, add the missing context with fresh citations, add the terminology note as a `**[human]**` claim citing `FB-2026-05-31-003`, append a `## Change log` appendix entry naming the three Feedback Item ids
- [X] T023 [US3] Author `examples/reference-output/claude-code/.reposkillopt/rollouts/RL-2026-05-31T140000-claude-code.md` documenting the revision-2 session — `spec_id: click-8.1.7`, list each Feedback Item id under *Human feedback received this session* with `(applied)`, list revisions under *Revisions applied*
- [X] T024 [US3] **Validation checkpoint** — apply `contracts/feedback-item.contract.md` to T019–T021; verify SC-007 (all three feedback items reflected in revision 2 and recorded); confirm the `repository-scoped` items did not silently leak into `skills/repo-skillopt/SKILL.md`

**Checkpoint**: User Story 3 is complete — the human feedback loop works end-to-end on the reference repo and scope discipline is demonstrated. **MVP is complete after this checkpoint** (US1 + US2 + US3 = the three P1 stories).

---

## Phase 6: User Story 4 — Export the canonical skill to multiple agent harnesses (Priority: P2)

**Goal**: The remaining three adapters (Codex, OpenCode, generic) exist and each passes the adapter-equivalence check. Each adapter has a corresponding sample reference output tree.

**Independent Test**: For each of Codex / OpenCode / generic: adapter file exists at the documented path; `canonical_version` resolves to `0.1.0`; every row of `contracts/adapter-equivalence.contract.md` passes; a sample Repository Specification for `pallets/click@8.1.7` exists under `examples/reference-output/<adapter>/.reposkillopt/specs/`. SC-005: 4 of 4 adapters shipped and verified.

### Implementation for User Story 4

- [X] T025 [P] [US4] Author `adapters/codex/AGENTS.md` — HTML-comment metadata block (`canonical_version: 0.1.0`, `adapter: codex`) per Phase 0 R3; all nine canonical sections preserved in order; no YAML front matter
- [X] T026 [P] [US4] Author `adapters/codex/README.md` — install location for Codex (typically the target repo's root `AGENTS.md`), activation notes, "Known cross-agent differences" placeholder
- [X] T027 [P] [US4] Author `adapters/opencode/AGENTS.md` — same shape as T025 with `adapter: opencode` per Phase 0 R4
- [X] T028 [P] [US4] Author `adapters/opencode/README.md` — install location for OpenCode, activation notes, "Known cross-agent differences" placeholder
- [X] T029 [P] [US4] Author `adapters/generic/skill.md` — YAML front matter (`canonical_version: 0.1.0`, `adapter: generic`); full canonical content per Phase 0 R5
- [X] T030 [P] [US4] Author `adapters/generic/system-prompt-fragment.md` — ~10-line snippet that a custom harness can paste into its system message to activate the skill (references `skill.md` by relative path)
- [X] T031 [P] [US4] Author `adapters/generic/README.md` — how to integrate the two-file generic adapter into a custom harness
- [X] T032 [P] [US4] Produce `examples/reference-output/codex/.reposkillopt/specs/repository-specification.md` for `pallets/click@8.1.7` — same content shape as T016 but with `adapter: codex`
- [X] T033 [P] [US4] Produce `examples/reference-output/codex/.reposkillopt/rollouts/RL-2026-05-31T120000-codex.md` per `contracts/rollout-log.contract.md`
- [X] T034 [P] [US4] Produce `examples/reference-output/opencode/.reposkillopt/specs/repository-specification.md` for `pallets/click@8.1.7` with `adapter: opencode`
- [X] T035 [P] [US4] Produce `examples/reference-output/opencode/.reposkillopt/rollouts/RL-2026-05-31T130000-opencode.md`
- [X] T036 [P] [US4] Produce `examples/reference-output/generic/.reposkillopt/specs/repository-specification.md` for `pallets/click@8.1.7` with `adapter: generic`
- [X] T037 [P] [US4] Produce `examples/reference-output/generic/.reposkillopt/rollouts/RL-2026-05-31T150000-generic.md`
- [X] T038 [US4] Update top-level `README.md` to add per-adapter install sections for Codex, OpenCode, and generic (depends on T012–T013 already covering Claude Code), each pointing at its respective `adapters/<target>/README.md`
- [X] T039 [US4] **Validation checkpoint** — apply `contracts/adapter-equivalence.contract.md` 14-row checklist to each of `adapters/{codex,opencode,generic}/`; verify SC-005 (4 of 4 adapters pass equivalence) and SC-006 (100% canonical-section coverage in every adapter)

**Checkpoint**: User Story 4 is complete — cross-agent portability shipped and validated.

---

## Phase 7: User Story 5 — Distinguish verified facts from hypotheses (Priority: P2)

**Goal**: The R10 label discipline (FR-008) is demonstrated end-to-end across the four reference specs; no claim presents a hypothesis as a fact; sampling 20 claims across the reference outputs confirms 100% carry one of the four labels.

**Independent Test**: Sample 20 claims drawn from the four `examples/reference-output/<adapter>/.reposkillopt/specs/repository-specification.md` files; every claim carries one of `**[fact]**`/`**[inference]**`/`**[unknown]**`/`**[human]**`; every `**[fact]**` has a citation that resolves at `click@8.1.7`.

### Implementation for User Story 5

- [X] T040 [US5] Audit all four reference Repository Specifications (`examples/reference-output/{claude-code,codex,opencode,generic}/.reposkillopt/specs/repository-specification.md`) — sample at least 5 claims per file (20 total), confirm every claim carries an R10 label; for any unlabeled or mislabeled claim, fix it in place
- [X] T041 [US5] Audit the canonical `skills/repo-skillopt/SKILL.md` *Output Discipline* section — confirm the four label values and the citation requirement are stated unambiguously; if any value or rule is missing, edit SKILL.md and bump version to `0.1.1` (patch) and record the patch in `CHANGELOG.md`
- [X] T042 [US5] **Validation checkpoint** — confirm rubric dimensions 5 (Hallucination avoidance), 9 (Fact-vs-hypothesis distinction) would score 3/3 against any of the four reference specs; if any would score below 2, fix the underlying spec content

**Checkpoint**: User Story 5 is complete — fact/hypothesis discipline is observably enforced across the shipped reference outputs.

---

## Phase 8: User Story 6 — Refine the Repository Specification across iterations (Priority: P2)

**Goal**: Demonstrate that revisions accumulate (not regenerate from scratch). Produce a revision 3 of the Claude Code reference spec that incorporates a fourth Feedback Item and preserves all prior `**[human]**` claims; the Change log records each revision's deltas.

**Independent Test**: Revision 3 builds on revision 2 (not a fresh draft); prior `**[human]**` claims from FB-001/002/003 still appear in revision 3 (unless explicitly replaced); Change log lists three rows; SC-007 holds across the chain.

### Implementation for User Story 6

- [X] T043 [P] [US6] Author `examples/reference-output/claude-code/.reposkillopt/feedback/FB-2026-06-01-004-quality-rating.md` — `type: quality-rating`, `scope: candidate-for-generic`, references the architecture section of revision 2, `status: applied`
- [X] T044 [US6] Revise `examples/reference-output/claude-code/.reposkillopt/specs/repository-specification.md` to revision 3 (depends on T022 and T043) — increment `revision` to `3`, update `revised`, address FB-004, preserve every prior `**[human]**` claim unless explicitly replaced (in which case mark superseded), append a new row to the Change log
- [X] T045 [P] [US6] Author `examples/reference-output/claude-code/.reposkillopt/rollouts/RL-2026-06-01T100000-claude-code.md` documenting the revision-3 session — *Human feedback received this session* names `FB-2026-06-01-004 (applied)`, *Revisions applied* names the spec sections that changed
- [X] T046 [US6] **Validation checkpoint** on `examples/reference-output/claude-code/.reposkillopt/specs/repository-specification.md` — diff revisions 2 and 3; confirm prior `**[human]**` claims survive; confirm SC-007 (every open Feedback Item under `examples/reference-output/claude-code/.reposkillopt/feedback/` is addressed or explicitly deferred)

**Checkpoint**: User Story 6 is complete — multi-session continuity is demonstrated on the reference outputs.

---

## Phase 9: User Story 7 — Convert recurrent feedback into bounded, reviewable skill edits (Priority: P3)

**Goal**: Demonstrate the convergence loop. Produce three Skill Edit Proposals — one accepted, one rejected (preserved), one flagged as repository-scoped — each citing supporting Feedback Items.

**Independent Test**: All three proposals exist under `examples/reference-output/claude-code/.reposkillopt/proposals/`; each has `review_time_estimate_minutes ≤ 5`; supporting `FB-` ids resolve; the rejected proposal is preserved with `decision_rationale`; the repository-scoped proposal is flagged or rewritten per FR-022 and NOT applied to canonical SKILL.md.

### Implementation for User Story 7

- [X] T047 [P] [US7] Author `examples/reference-output/claude-code/.reposkillopt/proposals/SP-2026-06-01-001-accepted.md` — `target_section: Repository Understanding Workflow`, `edit_kind: ADD` (or `SPECIALIZE`), `scope: generic`, `supporting_feedback: [FB-2026-05-31-002, FB-2026-06-01-004]` (the two `candidate-for-generic` items), `review_time_estimate_minutes: 3`, `status: accepted`, `decided: 2026-06-01`, `decision_rationale: ...`, plus the three required sections (`Proposed text`, `Diff against current canonical`, `Justification`)
- [X] T048 [P] [US7] Author `examples/reference-output/claude-code/.reposkillopt/proposals/SP-2026-06-01-002-rejected.md` — `edit_kind: GENERALIZE` (or `REORDER`), `scope: generic`, supporting feedback, `review_time_estimate_minutes: 4`, `status: rejected`, `decided: 2026-06-01`, `decision_rationale:` explains why generalization would hurt; **file is preserved** per FR-021
- [X] T049 [P] [US7] Author `examples/reference-output/claude-code/.reposkillopt/proposals/SP-2026-06-01-003-flagged-repo-scoped.md` — `scope: repository-scoped`, `supporting_feedback: [FB-2026-05-31-001, FB-2026-05-31-003]` (both repository-scoped feedback items), `status: rejected` with `decision_rationale:` noting "repository-scoped — not eligible for canonical SKILL.md per FR-016/FR-022; route to per-repository notes instead", per FR-022
- [X] T050 [US7] Edit `examples/reference-output/claude-code/.reposkillopt/proposals/SP-2026-06-01-001-accepted.md` — add a top-level paragraph at the start explicitly noting that for the MVP demonstration the acceptance is illustrative and the canonical version in `skills/repo-skillopt/SKILL.md` remains `0.1.0` (no actual canonical edit is applied from this sample proposal — this prevents the demo data from accidentally drifting the real source of truth)
- [X] T051 [US7] **Validation checkpoint** — apply `contracts/skill-edit-proposal.contract.md` to T047–T049; verify SC-008 (at least one bounded proposal cites the recurring feedback) and SC-009 (every proposal's `review_time_estimate_minutes ≤ 5`); verify the rejected and flagged proposals are preserved

**Checkpoint**: User Story 7 is complete — the convergence loop is demonstrated end-to-end with accept / reject / flag-as-repo-scoped tracks.

---

## Phase 10: User Story 8 — Compare skill versions for evaluation (Priority: P3)

**Goal**: Ship the rubric and demonstrate a scoring sheet for the reference output, so per-dimension score comparisons across skill versions become mechanically possible (SC-012).

**Independent Test**: `rubric/evaluation-rubric.md` lists all 15 FR-028 dimensions with the 0–3 anchors from Phase 0 R9. `rubric/deterministic-checks.md` lists all seven FR-030 checks. A sample scoring sheet exists under `rubric/scoring/` for the revision-2 Claude Code reference output.

### Implementation for User Story 8

- [X] T052 [P] [US8] Author `rubric/evaluation-rubric.md` per `contracts/evaluation-rubric.contract.md` — all 15 FR-028 dimensions in FR-028 order, each with a one-sentence definition and the four anchor lines (0/1/2/3) from Phase 0 R9; explicit statement that aggregate scores MUST NOT replace per-dimension scores in version comparison
- [X] T053 [P] [US8] Author `rubric/deterministic-checks.md` per `contracts/evaluation-rubric.contract.md` — all seven FR-030 checks with explicit pass criteria, scoring-sheet schema (front matter + two tables)
- [X] T054 [US8] Produce `rubric/scoring/click-8.1.7-claude-code-rev2.md` — sample scoring sheet for the revision-2 Claude Code reference output (T022); front matter links back to `spec_id: click-8.1.7`, `rollout_id: RL-2026-05-31T140000-claude-code`, `skill_version: 0.1.0`, `adapter: claude-code`; 15-row qualitative table; 7-row deterministic table; aggregate sum (advisory)
- [X] T055 [US8] **Validation checkpoint** on `rubric/scoring/click-8.1.7-claude-code-rev2.md` — confirm SC-012 (a researcher could repeat T054 against a hypothetical `skill_version: 0.2.0` row and produce per-dimension deltas using the same schema)

**Checkpoint**: User Story 8 is complete — evaluation rubric and a worked example exist; the project supports version comparison.

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency sweeps and success-criterion verification.

- [X] T056 Update top-level `README.md` to add links to `rubric/evaluation-rubric.md`, `rubric/deterministic-checks.md`, every per-adapter `README.md`, and `specs/001-reposkillopt-skill/quickstart.md`
- [X] T057 [P] Vendor-neutrality sweep of `skills/repo-skillopt/SKILL.md` — grep for "Claude", "Codex", "OpenCode", "Copilot"; any normative occurrence is a defect to fix (FR-002)
- [X] T058 [P] Re-run `contracts/adapter-equivalence.contract.md` across `adapters/{claude-code,codex,opencode,generic}/` to catch any drift introduced during Phases 7–10
- [X] T059 [P] Success-criterion verification — author `specs/001-reposkillopt-skill/SC-VERIFICATION.md` recording, for each of SC-001 through SC-012, the artifact or measurement that demonstrates the criterion is met (or the gap, if not)
- [X] T060 [P] Project-level acceptance verification — walk AC-01 through AC-10 from `specs/001-reposkillopt-skill/spec.md` and confirm each is satisfied by the shipped artifacts; append results to `specs/001-reposkillopt-skill/SC-VERIFICATION.md`
- [X] T061 Run the quickstart walkthrough (`specs/001-reposkillopt-skill/quickstart.md`) end-to-end manually against `pallets/click@8.1.7` using the Claude Code adapter; record any friction in the per-adapter README's "Known cross-agent differences" section

---

## Dependencies & Execution Order

### Phase dependencies

- **Setup (Phase 1)**: No dependencies — start immediately.
- **Foundational (Phase 2)**: Depends on Setup. **Blocks all user-story phases** because every adapter wraps the canonical SKILL.md and every reference output uses the four templates.
- **User Stories (Phase 3+)**: Depend on Foundational. Within these, dependencies are:
  - **US1, US2, US4** can each begin immediately after Foundational (parallel-eligible).
  - **US3** depends on US2 (it revises the spec produced by US2).
  - **US5** depends on US2 + US4 (it audits all four reference specs).
  - **US6** depends on US3 (revision 3 builds on revision 2).
  - **US7** depends on US6 (proposals cite the feedback items accumulated by US3 + US6).
  - **US8** depends on US3 (the sample scoring sheet targets revision 2).
- **Polish (Phase 11)**: Depends on all user-story phases being complete.

### Within each user story

- Authoring tasks marked [P] can run in parallel (different files).
- The validation checkpoint at the end of each phase is sequential (depends on all preceding tasks in that phase).

### Parallel opportunities

- **Phase 1 setup**: T002, T003 are parallel after T001.
- **Phase 2 foundational**: T004, T005, T006, T007 all parallel; T008 depends on them; T009 depends on T008; T010 depends on T008; T011 depends on T008.
- **Phase 3 US1**: T012, T013 are parallel; T014 depends on T012/T013.
- **Phase 4 US2**: T016, T017 are parallel (different files).
- **Phase 5 US3**: T019, T020, T021 are parallel; T022 depends on all three; T023 depends on T022.
- **Phase 6 US4**: T025–T037 are largely parallel (different files); T038 depends on the per-adapter READMEs; T039 depends on all adapters being authored.
- **Phase 9 US7**: T047, T048, T049 are parallel.
- **Phase 10 US8**: T052, T053 are parallel; T054 depends on T052+T053.
- **Phase 11 polish**: T057, T058, T059, T060 are parallel.

### MVP scope

The **minimum publishable MVP** is Phase 1 + Phase 2 + Phase 3 (US1) + Phase 4 (US2) + Phase 5 (US3). After that checkpoint, RepoSkillOpt is usable on one adapter (Claude Code) with a working evidence-grounded spec and a working feedback loop. Subsequent phases broaden adapter coverage (US4), tighten quality (US5), demonstrate longer-horizon refinement (US6), exercise the convergence loop (US7), and ship the rubric (US8).

---

## Parallel Example: Phase 2 Foundational

The four template files can be authored simultaneously by one agent (in one message with parallel tool calls) or by several developers:

```text
Task: Author templates/repository-specification.md per the Repository Specification contract
Task: Author templates/human-feedback.md per the Feedback Item contract
Task: Author templates/rollout-log.md per the Rollout Log contract
Task: Author templates/skill-edit-proposal.md per the Skill Edit Proposal contract
```

Once those four are complete, T008 (canonical `SKILL.md`) and then T009 (top-level `README.md`) run in sequence.

---

## Implementation Strategy

### MVP first (P1 stories only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories).
3. Complete Phase 3 (US1) — Claude Code adapter installable.
4. Complete Phase 4 (US2) — evidence-grounded spec produced for `pallets/click@8.1.7`.
5. Complete Phase 5 (US3) — feedback loop demonstrated.
6. **STOP and VALIDATE**: run the quickstart end-to-end. Project is publishable as v0.1.0 MVP.

### Incremental delivery beyond MVP

1. Add US4 — cross-agent portability (Codex, OpenCode, generic).
2. Add US5 — fact/hypothesis audit pass.
3. Add US6 — multi-revision continuity.
4. Add US7 — convergence-loop demonstration.
5. Add US8 — evaluation rubric and worked scoring example.

### Parallel-team strategy

With multiple authors:

1. Team completes Phases 1–2 together.
2. After the Foundational checkpoint:
   - Author A: US1 → US3 (Claude Code track + feedback loop).
   - Author B: US4 (Codex / OpenCode / generic adapters and their sample outputs).
   - Author C: US8 (rubric and worked scoring sheet).
3. After all P1 stories complete, US5/US6/US7 are integrated by whoever finishes their track first.

---

## Notes

- [P] tasks operate on different files with no incomplete prerequisites.
- [Story] labels map every task to a single user story for traceability against `spec.md`.
- Validation checkpoints at the end of each phase are **manual reviewer checks** against the corresponding contract file in `contracts/` — they are this project's substitute for automated tests.
- Commit after each task or logical group; the project has no build step, so each commit is the deliverable.
- Avoid: vague tasks, leaking specific agent runtime names into normative canonical content (FR-002), promoting `scope: repository-scoped` feedback into the canonical skill (FR-016, FR-022), shipping an adapter whose `canonical_version` does not resolve to an existing canonical version (FR-027a).
