# Feature Specification: As-Is Analysis → To-Be Design → Implementation Orchestration

**Feature Branch**: `019-asis-tobe-orchestration`
**Created**: 2026-06-21
**Status**: Draft
**Input**: Extend RepoSkillOpt from "understand the as-is" into a three-stage capability — **analyze as-is → plan to-be → orchestrate implementation** — via two new evidence-grounded, vendor-neutral skills that build on the existing Repository Specification and reuse the existing human-feedback + bounded skill-convergence machinery (Feedback Items, Skill Edit Proposals, the validation gate against a held-out reference set, rubric scoring, deterministic checks).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - As-is architecture analysis & blast-radius (Priority: P1)

A maintainer wants a deeper, evidence-grounded view of the *current* system than the Repository Specification gives, and to know — before touching anything — exactly what a proposed change would ripple into.

**Why this priority**: This is the foundation the to-be stage consumes; on its own it already delivers value (architecture map + change-impact). It is independently testable against any repo that has a Repository Specification.

**Independent Test**: Given a repo + its Repository Specification, the as-is skill produces an **Architecture View** (component/container map at C4-style levels, key sequences/flows, dependency graph) and a **Change-Impact Analysis** for a named target, where every claim cites a concrete `file:line`/symbol and unknowns are marked.

**Acceptance Scenarios**:
1. **Given** a Repository Specification, **When** the user asks to "map the architecture", **Then** the skill writes an Architecture View whose every component/edge cites real `file:line` evidence, with C4-style levels (context → container → component) and the dependency graph.
2. **Given** a proposed change or target area, **When** the user asks "what would change if we…", **Then** the skill writes a Change-Impact Analysis listing the affected modules, tests, contracts, and call sites — each with a **confidence** label and citations, unknowns marked `[unknown]`.
3. **Given** a human correction to any claim, **When** recorded, **Then** it becomes a Feedback Item, is applied to the artifact, and is **not** promoted to the skill unless explicitly marked candidate-for-generic and gated.

### User Story 2 - To-be design & implementation orchestration plan (Priority: P1)

Given the as-is view and a stated goal, an architect wants a reviewable target-state design *and* a plan an unattended orchestrator can drive — without the skill executing anything.

**Why this priority**: It is the payoff of the three-stage chain. It depends on US1's artifacts but is independently testable given an as-is view + a goal.

**Independent Test**: Given an Architecture View + Change-Impact Analysis + a goal, the to-be skill produces **ADRs** + a **Design Doc** grounded in the as-is evidence, and a **Task Ledger**: a portable, machine-readable decomposition into small independent sub-tasks, each with its own acceptance test, declared dependencies, and a valid topological order.

**Acceptance Scenarios**:
1. **Given** a goal + as-is artifacts, **When** the user asks to design the to-be, **Then** the skill writes one or more ADRs (decision, context, options weighed, consequences) and a concise Design Doc, each claim traceable to as-is evidence.
2. **Given** the design, **When** the skill produces the Task Ledger, **Then** every sub-task has a crisp goal, an explicit acceptance test, declared dependencies, and the ledger's dependency graph is **acyclic** with a stated topological order; the ledger is machine-readable so any orchestrator can drive it.
3. **Given** a human correction to a decision or to the task decomposition, **When** recorded, **Then** it is a Feedback Item applied to the artifact, gated before it can alter a skill.

### User Story 3 - Feedback recorded, gated convergence for the new skills (Priority: P2)

The same bounded self-improvement applies to both new skills: corrections accumulate as Feedback Items; recurrent, generalizable patterns become Skill Edit Proposals that **must pass the validation gate** (regenerate artifacts for a disjoint held-out set with no per-dimension rubric regression and deterministic checks still passing) before they touch a skill.

**Independent Test**: A proposed edit to a new skill that improves the motivating repo but **regresses** the rubric on the held-out reference set is **rejected** by the gate; an edit that holds the gate is accepted and bumps the skill version.

**Acceptance Scenarios**:
1. **Given** ≥3 related Feedback Items marked candidate-for-generic, **When** a Skill Edit Proposal is drafted and gated, **Then** it is accepted only if the held-out regeneration shows no per-dimension rubric regression and deterministic checks pass.
2. **Given** a candidate edit that regresses any rubric dimension on the held-out set, **When** gated, **Then** it is rejected with the regression recorded (no silent promotion).

### Edge Cases

- **No Repository Specification yet** → the as-is skill states the prerequisite and points to the understanding skill; it does not fabricate an architecture.
- **Unresolvable impact** (dynamic dispatch, reflection, config-driven wiring) → marked `[unknown]`/low-confidence with the reason, never silently dropped.
- **Goal conflicts with as-is constraints** → an ADR records the conflict and the trade-off rather than papering over it.
- **A sub-task that isn't independently acceptance-testable** → it must be split until each piece is, or flagged.
- **Repository-specific decision** → stays repository-scoped; never promoted into a generic skill.

## Requirements *(mandatory)*

### Functional Requirements — Skill 1 (As-Is Architecture Analysis)

- **FR-001**: The skill MUST consume the existing Repository Specification and produce an **Architecture View** artifact with C4-style levels (context, container, component), key sequences/flows, and a dependency graph — every component, container, and edge cited to a real `file:line`/symbol.
- **FR-002**: The skill MUST produce a **Change-Impact ("blast-radius") Analysis** for a named target/change: the affected modules, tests, contracts, and call sites, each with a **confidence** label and citations; unresolvable impact is marked `[unknown]` with a reason.
- **FR-003**: Every major claim MUST carry an R10 label (`[fact]`/`[inference]`/`[unknown]`/`[human]`); `[fact]` MUST carry a citation. Trivial recitations need no label.
- **FR-004**: The skill MUST activate on architecture-mapping, dependency/coupling-assessment, and "what would change if we…" requests — and not on out-of-scope requests.

### Functional Requirements — Skill 2 (To-Be Design & Orchestration Plan)

- **FR-005**: The skill MUST consume the as-is artifacts + a stated goal and produce **ADRs** (decision, context, options weighed, consequences) and a concise **Design Doc**, every claim traceable to as-is evidence.
- **FR-006**: The skill MUST produce a **Task Ledger**: the work decomposed into small, **independent**, individually acceptance-tested sub-tasks, each with a crisp goal + explicit acceptance, **declared dependencies**, and a valid **topological order**. The dependency graph MUST be acyclic.
- **FR-007**: The Task Ledger MUST be an **artifact** (portable + machine-readable), **not an executor** — consumable by any orchestrator/unattended runner; the skill MUST NOT execute the implementation.

### Functional Requirements — Shared machinery (reuse, do not fork)

- **FR-008**: Both skills MUST accept human corrections as first-class input, recorded as **Feedback Items** (existing `human-feedback.md` template/flow), applied to the artifact in place.
- **FR-009**: Only feedback explicitly marked **candidate-for-generic** MAY enter the skill-convergence loop, via a **Skill Edit Proposal** (existing template); nothing is silently promoted; repository-specific facts stay repository-scoped.
- **FR-010**: A Skill Edit Proposal for either new skill MUST pass the existing **validation gate** — regenerate artifacts for a disjoint **held-out reference set** with **no per-dimension rubric regression** and deterministic checks still passing — before acceptance; a regressing edit MUST be rejected and recorded.
- **FR-011**: Each new skill MUST ship **rubric dimensions** (so quality is measurable) and **deterministic checks** appropriate to its artifacts (e.g., every architecture component cites a file; every impact entry cites a call site; every task has acceptance + declared dependencies; the task graph is acyclic; ADRs weigh ≥2 options).
- **FR-012**: Each new skill MUST be **vendor-neutral** (no dependency on any specific coding-agent runtime) and mirrored to the four adapters (claude-code, codex, opencode, generic) with adapter-equivalence and a `version:`/`canonical_version:`.
- **FR-013**: New **artifact templates** MUST be added — Architecture View, Change-Impact Analysis, ADR, Design Doc, Task Ledger — consistent with the existing template set; artifacts live under the target repo's `.reposkillopt/` in fixed subdirectories.
- **FR-014**: The feature MUST NOT change the contract of the existing repository-understanding skill, MUST NOT execute implementations, and MUST NOT promote repository-specific facts into the generic skills.

### Key Entities

- **Architecture View**: C4-level component/container map + sequences + dependency graph, every node/edge cited.
- **Change-Impact Analysis**: target → affected {modules, tests, contracts, call sites} with confidence + citations.
- **ADR**: a single decision with context, options weighed, consequences.
- **Design Doc**: concise target-state narrative grounded in as-is evidence.
- **Task Ledger**: machine-readable list of independent sub-tasks {id, goal, acceptance, dependencies}, with a topological order; the dependency graph is a DAG.
- **Feedback Item / Skill Edit Proposal / Validation Gate Report**: existing entities, reused.

## Success Criteria *(mandatory)*

- **SC-001**: Given a repo + Repository Specification, the as-is skill produces an Architecture View + Change-Impact Analysis where **100% of `[fact]` claims carry a resolvable `file:line` citation** and unknowns are marked.
- **SC-002**: Given an as-is view + a goal, the to-be skill produces ADRs + a Design Doc + a Task Ledger in which **every sub-task has an acceptance test and declared dependencies**, and the dependency graph is **acyclic with a valid topological order** (deterministically checkable).
- **SC-003**: A human correction to any artifact is **recorded, applied, and gated** — it cannot alter a skill without a Skill Edit Proposal passing the validation gate.
- **SC-004**: A candidate skill edit that **regresses any rubric dimension** on the held-out reference set is **rejected** by the gate (no silent promotion); a non-regressing edit is accepted and bumps the version.
- **SC-005**: Each new skill is mirrored to all four adapters with matching `canonical_version`, and the existing understanding skill's contract is unchanged.

## Assumptions

- **Two-layer model (per the maintainer's intent):** the **generic** `repo-skillopt` understanding skill is kept **unchanged** (it produces the repo-neutral Repository Specification); the as-is **`repo-architecture`** skill is the **repo-specializing analysis layer** that consumes that spec and deepens it for a specific repository. `repo-orchestration` (to-be) is a separate skill. All are new, separate `skills/<name>/SKILL.md` + four adapters + version — no edit to the generic skill's contract (the FR-014 non-goal is honored).
- "Machine-readable task ledger" = Markdown + YAML front matter with a structured task table (and optionally a deterministic JSON projection, consistent with the existing render/projection pattern); no new runtime dependency.
- The as-is skill MAY reuse the existing deterministic engine analyzers (ontology, business workflows, the §16 change-impact map) as *evidence inputs*, but the deliverable is **skill-first** (Markdown + templates + rubric); engine support is optional, not required for acceptance.
- "Held-out reference set", "validation gate", "rubric scoring", and "deterministic checks" reuse the existing `rubric/` machinery and feature-003/004 gate; each new skill contributes its own rubric dimensions + checks into that machinery.
- Confidence labels on impact entries are qualitative (high/medium/low) tied to evidence strength (direct call-site citation = high; name-resolution/inference = medium; dynamic/unresolved = low/`[unknown]`).
