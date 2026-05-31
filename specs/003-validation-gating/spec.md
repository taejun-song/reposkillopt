# Feature Specification: Validation-Gated Skill Convergence

**Feature Branch**: `003-validation-gating`
**Created**: 2026-05-31
**Status**: Draft
**Input**: User description: "Spec the validation-gating idea" — accept a Skill Edit Proposal only if it does not regress per-dimension rubric scores across a held-out set of reference repositories (inspired by microsoft/SkillOpt's held-out validation gate, adapted to RepoSkillOpt's human-in-the-loop, vendor-neutral model).

## Clarifications

### Session 2026-05-31

- Q: How strict should the gate's acceptance criterion be? → A: No per-dimension regression on any held-out repo + deterministic checks pass + the proposal's expected effect realized on ≥1 dimension (or explicitly waived for clarifying edits). (Confirms the FR-004 default.)
- Q: What does the gate score under the candidate version? → A: Regenerate first — re-run the candidate skill against each held-out repo to produce fresh Repository Specifications, then score those (a workflow-stage edit must actually show up in regenerated output).
- Q: How is reproducibility guaranteed given that rubric scoring is a judgment call? → A: A named human **scorer-of-record** produces and records the scores; the PASS/FAIL verdict is a deterministic function of the recorded scores (reproducible = same recorded scores → same verdict).
- Q: When should held-out baseline scores be recomputed? → A: Whenever the released canonical version changes (i.e., after any accepted proposal), so the comparison floor stays current.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Gate a candidate proposal on no-regression (Priority: P1)

A skill maintainer has a `scope: generic` Skill Edit Proposal and, before accepting it, runs the **Validation Gate**: the proposed edit is applied to a candidate (unreleased) skill version, the held-out reference repositories are re-scored with the existing evaluation rubric, and the proposal is accepted only if **no per-dimension score regresses on any held-out repository** and **all deterministic checks still pass**. A passing or failing verdict is produced with the per-dimension before/after evidence.

**Why this priority**: This is the core idea — replacing "accept by judgment alone" with "accept only when measured not to make the skill worse." It is the smallest change that makes acceptance evidence-based, and it delivers value on its own even with a one-repository held-out set.

**Independent Test**: Run the gate twice on the current canonical skill: once with a no-op/clarifying edit (expect PASS — no regression), and once with a deliberately harmful edit that weakens an Operating Principle (expect FAIL, naming the regressed dimension and repository).

**Acceptance Scenarios**:

1. **Given** a candidate proposal and a baseline scoring of the held-out set, **When** the maintainer runs the gate and no per-dimension score drops and all deterministic checks pass, **Then** the gate verdict is PASS and the proposal is eligible for acceptance.
2. **Given** a candidate edit that lowers at least one per-dimension score on at least one held-out repository, **When** the gate runs, **Then** the verdict is FAIL and the report names the regressed dimension(s) and repository(ies).
3. **Given** a candidate edit that breaks a deterministic check (e.g., introduces an unciteable rule), **When** the gate runs, **Then** the verdict is FAIL regardless of per-dimension scores.

---

### User Story 2 - Maintain a held-out reference set disjoint from motivating repos (Priority: P2)

The maintainer keeps a documented, commit-pinned **held-out reference set** reserved for gating. The repositories whose feedback motivated a proposal (its "training" repos) must NOT be in the held-out set, so the gate cannot be satisfied by overfitting to the very repository that prompted the change.

**Why this priority**: Without disjointness the gate is theater — a proposal could be tuned to the one repo it is then validated against. But US1's gate mechanics can be demonstrated before the set is fully formalized, so this is a close second.

**Independent Test**: Inspect the held-out set definition — it lists at least two commit-pinned repositories with baseline scoring sheets; an audit of any accepted proposal confirms none of its `supporting_feedback` repositories appear in the held-out set.

**Acceptance Scenarios**:

1. **Given** the held-out set definition, **When** it is read, **Then** every entry is a repository pinned to a specific commit with a baseline scoring sheet on record.
2. **Given** a proposal whose supporting feedback references a repository that is in the held-out set, **When** the gate is attempted, **Then** the gate is invalid (held) and the report flags the overfitting conflict until the set or proposal is adjusted.

---

### User Story 3 - Record a Validation Gate Report and enforce it in the loop (Priority: P2)

Every gate run produces a **Validation Gate Report** capturing the candidate version, the held-out set and its commit pins, per-dimension baseline-vs-candidate scores per repository, deterministic-check results, and the verdict with rationale. The Skill Convergence Loop is updated so a proposal **cannot reach `status: accepted` without a referenced passing report**.

**Why this priority**: The report is what makes the gate auditable and the enforcement is what makes it binding; both build directly on US1.

**Independent Test**: Produce one PASS report and one FAIL report for sample proposals; confirm a proposal with no report (or a failing one) cannot be marked accepted, while a proposal referencing a passing report can be.

**Acceptance Scenarios**:

1. **Given** a completed gate run, **When** the report is written, **Then** it records candidate version, held-out repos + pins, per-dimension baseline vs candidate, deterministic results, and a PASS/FAIL verdict with rationale.
2. **Given** a proposal with no referenced passing report, **When** acceptance is attempted, **Then** acceptance is refused and the proposal stays `proposed` (or is rejected/held).
3. **Given** a proposal referencing a passing report, **When** it is accepted, **Then** the existing version-bump + CHANGELOG flow proceeds unchanged.

---

### User Story 4 - Reproducible, version-comparable gating (Priority: P3)

A researcher can re-run the gate for a different candidate version against the same held-out set and read per-dimension deltas across versions, extending the project's version-comparison capability.

**Why this priority**: Long-term value for tracking skill quality over versions, but secondary to having a working, enforced gate.

**Independent Test**: Run the gate for two candidate versions against the same held-out set; confirm the two reports share a schema and that per-dimension deltas between versions can be read directly from them without re-deriving baselines.

**Acceptance Scenarios**:

1. **Given** the same candidate version and held-out set, **When** the gate is run twice, **Then** it yields the same verdict (reproducible).
2. **Given** two candidate versions gated against the same held-out set, **When** their reports are compared, **Then** per-dimension deltas are readable directly from the recorded scores.

---

### Edge Cases

- **Pure clarifying edit** (no intended score change): passes the no-regression criterion; the "realizes expected effect" expectation is waived for clarifying edits, recorded as such in the report.
- **Held-out repo not scoreable** (e.g., language/ecosystem outside current coverage): recorded as `N/A`, not counted as a regression, but flagged as a coverage gap in the report.
- **Mixed result** (improves on one held-out repo, regresses on another): FAIL — any per-dimension regression on any held-out repository blocks acceptance.
- **Scorer disagreement** (a reviewer disputes the scorer-of-record's dimension score): the report names the single scorer-of-record whose recorded scores are authoritative; a dispute is resolved by the scorer-of-record re-scoring (and re-recording), never by averaging into an aggregate.
- **Overfitting conflict**: a proposal's supporting-feedback repository is also in the held-out set → gate is invalid/held (US2 scenario 2).
- **Repository-scoped proposal**: never eligible regardless of gate outcome — the existing scope discipline still rejects it before gating applies.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The project MUST define a **Validation Gate** that evaluates a `scope: generic` Skill Edit Proposal before it can be accepted into the canonical skill.
- **FR-002**: The gate MUST use the existing evaluation rubric — the 15 per-dimension scores and the 7 deterministic checks — and MUST NOT introduce a separate or competing scoring system.
- **FR-003**: The gate MUST first **regenerate** a fresh Repository Specification for each held-out repository by running the candidate skill version (the one with the proposed edit applied), then score those regenerated outputs — it MUST NOT score stale or pre-existing spec text, so that an edit to a workflow stage is actually reflected in the measured output.
- **FR-004**: The acceptance criterion MUST be: **no per-dimension score regresses** on any held-out repository versus its baseline, **AND** all deterministic checks still pass, **AND** at least one dimension reflects the proposal's stated `expected_effect` (or the proposal explicitly waives improvement, e.g., a clarifying edit, with recorded rationale).
- **FR-005**: Per-dimension scores MUST be compared individually; an aggregate (sum or mean) MUST NOT be used as the gate criterion (consistent with the rubric's FR-029 rule).
- **FR-006**: A Skill Edit Proposal MUST NOT reach `status: accepted` without a referenced **passing** Validation Gate Report.
- **FR-007**: The held-out reference set MUST be documented and commit-pinned (each repository identified at a specific commit) with a baseline scoring sheet on record for the current released skill version. Baselines MUST be recomputed whenever the released canonical version changes (i.e., after any accepted proposal), so the comparison floor always reflects the current released version.
- **FR-008**: The held-out set MUST be **disjoint** from the repositories whose feedback motivated the proposal, and this disjointness MUST be auditable from the proposal's `supporting_feedback` and the set definition.
- **FR-009**: Each gate run MUST produce a **Validation Gate Report** recording: candidate version, held-out repositories with commit pins, per-dimension baseline-vs-candidate scores per repository, deterministic-check results, and a PASS/FAIL verdict with rationale.
- **FR-010**: A failing gate MUST record exactly which dimension(s) or check(s) regressed and on which repository(ies).
- **FR-011**: Gating MUST be reproducible at the level of the **recorded scores**: the PASS/FAIL verdict MUST be a deterministic function of the per-dimension and deterministic-check scores recorded by a named **scorer-of-record**, so that anyone re-evaluating the same recorded scores reaches the same verdict. (Regeneration and scoring are judgment steps; the recorded scores, not the regeneration run, are the authoritative, reproducible input to the verdict.)
- **FR-012**: Failed candidates and their reports MUST be preserved (not deleted), extending the existing rejected-proposal preservation rule.
- **FR-013**: A passing gate MUST authorize — not bypass — the existing acceptance flow; applying the edit and bumping the canonical version still happen through the normal accepted-proposal path with a CHANGELOG entry.
- **FR-014**: The gate MUST remain vendor-neutral and skill-first — methodology plus Markdown artifacts only, with no hosted service, database, model fine-tuning, or automated training loop.
- **FR-015**: A maintainer MUST be able to reproduce the verdict by reading the report's recorded scores (the decision is human-auditable, not opaque).
- **FR-016**: The gate MUST support comparing outcomes across candidate versions by exposing per-dimension deltas readable from the reports.

### Key Entities *(include if feature involves data)*

- **Validation Gate**: The procedure and the no-regression acceptance criterion (FR-004). Not a service — a documented, reproducible decision rule applied with the rubric.
- **Held-out Reference Set**: A documented, commit-pinned collection of repositories reserved for gating, each with a baseline scoring sheet for the current released skill version; disjoint from any motivating repos.
- **Candidate Skill Version**: The canonical skill with a proposed edit applied, unreleased, used only to produce candidate scores for the gate.
- **Baseline Scores**: The per-dimension and per-check scores of the current released skill version on the held-out set (the comparison floor).
- **Validation Gate Report**: The decision artifact recording candidate version, held-out set + pins, the **scorer-of-record**, a reference to the regenerated candidate Repository Specifications, per-dimension baseline-vs-candidate scores per repository, deterministic results, and the PASS/FAIL verdict with rationale; referenced by the proposal.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A maintainer can run the gate on a candidate proposal and obtain a PASS/FAIL verdict grounded in recorded per-dimension before/after scores, in a single working session.
- **SC-002**: 100% of accepted `scope: generic` proposals carry a referenced passing Validation Gate Report (no acceptance without a gate).
- **SC-003**: A deliberately harmful edit that regresses at least one dimension is rejected by the gate in 100% of trials.
- **SC-004**: The held-out set is commit-pinned and provably disjoint from every accepted proposal's supporting-feedback repositories (0 overlap).
- **SC-005**: The verdict is reproducible from the recorded scores — anyone re-evaluating the scorer-of-record's recorded per-dimension and deterministic-check scores reaches the same PASS/FAIL every time.
- **SC-006**: Per-dimension baseline-vs-candidate deltas are recorded for every gated dimension; no aggregate is used in place of the per-dimension comparison.
- **SC-007**: A researcher can compare two candidate versions' reports and read per-dimension deltas without re-deriving baselines.
- **SC-008**: Introducing the gate adds no hosted service, database, or model fine-tuning; it runs locally using the existing rubric artifacts.

## Assumptions

- Scoring is performed by a named **scorer-of-record** (a human reviewer, who may be assisted by an agent) **applying the existing rubric** (`rubric/evaluation-rubric.md` + `rubric/deterministic-checks.md`) on the 0–3 per-dimension scale; "no regression" means no dimension's candidate score is lower than its baseline. The recorded scores — not the regeneration run — are the authoritative, reproducible input to the verdict.
- The gate **regenerates** fresh Repository Specifications for the held-out repositories under the candidate version before scoring (FR-003), and **recomputes baselines** when the released canonical version changes (FR-007).
- The held-out set is seeded from the existing `pallets/click@8.1.7` reference output plus at least one additional commit-pinned repository, so disjointness from motivating repos is achievable and meaningful.
- The default gate criterion is the FR-004 rule (no per-dimension regression + deterministic checks pass + expected effect realized or explicitly waived); it is recorded so it can be tightened (e.g., to require strict improvement on the targeted dimension) without changing the artifact shapes.
- This feature is **methodology + artifacts** layered onto the existing Skill Convergence Loop from feature 001; it does **not** add an automated optimizer, reward model, or training loop — it is a human-run, reproducible accept gate inspired by held-out validation, not a port of any external training framework.
- Only `scope: generic` proposals are gated; `scope: repository-scoped` proposals remain ineligible for canonical acceptance under the existing scope discipline and never reach the gate.
- Working artifacts (gate reports, held-out scoring sheets) live in this project's `rubric/` and the feature's own design directory, consistent with where the rubric and scoring sheets already live; per-repository gate runs against a target repo still use that repo's `.reposkillopt/` where applicable.
- The maintainer has the released skill's baseline scoring sheets available (or can produce them once and reuse them across gate runs of the same released version).
