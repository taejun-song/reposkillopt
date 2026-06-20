# Phase 0 — Research & Decisions

## D1. Two separate skills, not edits to `repo-skillopt`
**Decision**: Ship two new canonical skills (`repo-architecture`, `repo-orchestration`), each with its
own `SKILL.md` + four adapters + version + CHANGELOG.
**Rationale**: The spec's non-goal forbids changing the understanding skill's contract; separate
activation surfaces (architecture vs design/plan) and separate rubric dimensions keep concerns clean.
**Alternatives**: one mega-skill (rejected — couples three stages, bloats one prompt, breaks the
non-goal); sections inside `repo-skillopt` (rejected — changes its contract).

## D2. Skill names & activation
**Decision**: `repo-architecture` activates on "map the architecture / assess dependencies-coupling /
what would change if we…"; `repo-orchestration` on "design the to-be / plan the work / produce a task
plan for goal X". Both vendor-neutral, by `description:` only.
**Rationale**: Matches the spec's stated triggers; mirrors how `repo-skillopt` activates.

## D3. Task Ledger format (portable + machine-readable, not an executor)
**Decision**: Markdown + YAML front matter + a structured task table; each task carries
`id, goal, acceptance, depends_on[]`. The front matter states the `topological_order` (a list of ids)
and the doc is self-describing so any orchestrator can parse it. An optional deterministic JSON
projection (like the existing `render --view structured`) can be emitted, no new dependency.
**Rationale**: Consistent with the existing template+projection pattern; human-reviewable AND
machine-drivable; the DAG/topo are explicit so a checker can verify them.
**Alternatives**: pure JSON (rejected — not human-reviewable in a PR); a DSL (rejected — new dep).

## D4. Deterministic checks (stdlib module backing the gate)
**Decision**: `artifact_checks.py` (stdlib) provides model-free checks, reusing `grounding`:
- `check_architecture_view` — every component/edge line carries a resolvable `file:line`.
- `check_impact_analysis` — every affected entry carries a citation + a confidence label.
- `check_task_ledger` — every task has `acceptance` + `depends_on`; the dependency graph is **acyclic**;
  the stated `topological_order` is valid (every dep precedes its dependent; covers all task ids).
- `check_adr` — each ADR weighs **≥2 options** and states a decision + consequences.
Each returns `{passed: bool, failures: [...]}` — the deterministic half of the gate for these skills.
**Rationale**: Makes the spec's "deterministic checks still pass" concrete, executable, and TDD-able;
reuses citation resolution rather than re-implementing it.

## D5. Validation-gate & rubric reuse
**Decision**: Reuse `rubric/validation-gate.md` + the held-out reference set (features 003/004). Each
new skill adds a rubric file (its 0–3 dimensions) + the checks above. A Skill Edit Proposal for a new
skill is accepted only if, on the disjoint held-out set, no per-dimension rubric score regresses AND
its deterministic checks still pass.
**Rationale**: FR-010/FR-011 — same bounded convergence, no parallel machinery.

## D6. Artifact locations
**Decision**: under the target repo's `.reposkillopt/`: `architecture/architecture-view.md`,
`impact/change-impact-analysis.md`, `decisions/ADR-NNN-*.md`, `design/design-doc.md`,
`plan/task-ledger.md`. Matches the existing `{specs,feedback,rollouts,proposals}` convention.

## D7. Confidence labels
**Decision**: qualitative `high|medium|low`, tied to evidence strength — direct cited call-site = high;
name-resolution/inference = medium; dynamic/unresolved = low and also `[unknown]`. Deterministic check
requires a label present on every impact entry (not that the level is "correct").

## D8. Rubric dimensions (per skill)
**Decision**:
- *repo-architecture* (0–3 each): architectural correctness, evidence grounding, blast-radius
  completeness, confidence calibration, unknown honesty, level coherence (C4).
- *repo-orchestration* (0–3 each): decision quality (options weighed), design–evidence traceability,
  task independence, acceptance crispness, dependency/topo correctness, scope discipline (no execution).
**Rationale**: Measurable per FR-011; mirrors the existing 0–3 rubric style.
