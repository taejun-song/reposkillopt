---
name: repo-orchestration
description: Evidence-grounded to-be design (ADRs + design doc) and an implementation orchestration plan (a machine-readable task ledger). Activates when the user asks to design a target state, plan the work, or produce a task plan for a goal.
version: 0.1.0
---

# RepoSkillOpt — To-Be Design & Implementation Orchestration (Canonical Skill)

## Purpose

This skill consumes the **as-is artifacts** (Architecture View + Change-Impact Analysis) and a
stated **goal**, and produces (a) a reviewable target-state design — **ADRs** + a concise **Design
Doc** grounded in the as-is evidence — and (b) an **implementation orchestration plan**: a
machine-readable **Task Ledger** decomposed into small, independent, individually acceptance-tested
sub-tasks with declared dependencies and a topological order. The plan is an **artifact, not an
executor** — any orchestrator can drive it; this skill never executes the implementation.
Vendor-neutral: no dependency on any particular coding-agent runtime.

## Trigger Conditions

Activate when the user asks to **design a target state / to-be**, **plan the work / decompose into
tasks**, or **produce an implementation plan for goal X** — or recognizable equivalents. Do **not**
activate for unrelated requests, and do **not** execute the resulting plan.

## Prerequisite

The as-is artifacts (Architecture View, Change-Impact Analysis) and a stated goal. If the as-is is
missing, point the user to the as-is architecture skill first; do not design against an ungrounded
picture of the current system.

## Operating Principles

- **Ground the design in the as-is.** Every design claim is traceable to as-is evidence (`file:line`
  via the cited as-is artifacts). Mark inference as `**[inference]**`, unknowns as `**[unknown]**`.
- **Decide explicitly.** Contested choices become ADRs that weigh ≥2 options — no silent defaults.
- **Plan, don't execute.** The Task Ledger is a portable artifact; this skill writes it and stops.
- **Independent, acceptance-tested tasks.** Each sub-task is small enough to be executed and
  reviewer-verified on its own, with declared dependencies; if a task isn't independently
  acceptance-testable, split it.
- **Repository facts stay repository-scoped.** Only candidate-for-generic patterns enter convergence.

## Workflow

(a) **Read the as-is artifacts + the goal.** Identify constraints and the affected blast-radius.

(b) **ADRs** (`.reposkillopt/decisions/ADR-NNN-<slug>.md`, per `templates/adr.md`): one decision
each — Context, **Options considered (≥2, pros/cons)**, Decision, Consequences. A goal that conflicts
with an as-is constraint is recorded as an ADR trade-off, not papered over.

(c) **Design Doc** (`.reposkillopt/design/design-doc.md`, per `templates/design-doc.md`): Goal,
Target-state overview, **How it maps onto the as-is** (each change tied to the current
component/flow it touches, cited), Risks & trade-offs (link the ADRs), Out of scope.

(d) **Task Ledger** (`.reposkillopt/plan/task-ledger.md`, per `templates/task-ledger.md`): the work
as a table — `id | goal | acceptance | depends_on` — each task independent + individually
acceptance-tested, dependencies declared, the dependency graph **acyclic**, and the front-matter
`topological_order` listing every id with each dependency before its dependent.

(e) **Deterministic gate.** The artifacts MUST pass the deterministic checks (`check_adr`,
`check_task_ledger`): ≥2 options per ADR; every task has a goal + acceptance; deps exist; graph
acyclic; topological order valid.

## Output Discipline

Same R10 labels and citation forms as the as-is skill; design claims cite the as-is artifacts they
rest on. Trivial recitations need no label.

## Human Feedback Loop

Corrections to a decision or to the task decomposition are recorded as **Feedback Items**
(`templates/human-feedback.md`) under `.reposkillopt/feedback/` and applied to the artifact in place.

## Skill Convergence Loop

Recurrent **candidate-for-generic** feedback (≥3 related items) becomes a **Skill Edit Proposal**
(`templates/skill-edit-proposal.md`), accepted **only** after the validation gate
(`rubric/validation-gate.md`): regenerate artifacts for a disjoint held-out set with **no
per-dimension rubric regression** (see `rubric/tobe-orchestration-rubric.md`) and deterministic
checks still passing. Nothing is silently promoted; acceptance bumps the version + CHANGELOG and is
mirrored into the four adapters.
