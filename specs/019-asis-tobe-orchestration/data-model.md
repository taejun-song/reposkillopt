# Phase 1 — Data Model: Artifact Schemas

All artifacts are Markdown + YAML front matter, under the target repo's `.reposkillopt/`. Every
`[fact]` claim carries a resolvable `file:line` citation (R10).

## Architecture View  (`architecture/architecture-view.md`)
Front matter: `repo, commit, source_spec, created, status`.
Sections: **Context** (system + external actors), **Containers** (deployable/runtime units),
**Components** (modules within containers), **Key sequences** (numbered flows, cited per hop),
**Dependency graph** (mermaid `graph` + a cited edge list). Every component/container/edge cites a
`file:line`. Unknowns marked `[unknown]`.
**Invariant (check_architecture_view)**: every component and edge line carries a resolvable citation.

## Change-Impact Analysis  (`impact/change-impact-analysis.md`)
Front matter: `repo, commit, target (the change/area), created`.
Body: a table per impact kind — **modules, tests, contracts, call sites** — rows of
`{item, why, confidence(high|medium|low), evidence(file:line)}`; unresolved impact under `[unknown]`.
**Invariant (check_impact_analysis)**: every impact row has a citation **and** a confidence label.

## ADR  (`decisions/ADR-NNN-<slug>.md`)
Front matter: `id, title, status(proposed|accepted|superseded), date`.
Sections: **Context**, **Options considered** (≥2, each with pros/cons), **Decision**, **Consequences**.
**Invariant (check_adr)**: ≥2 options; a Decision and Consequences present.

## Design Doc  (`design/design-doc.md`)
Front matter: `repo, goal, asis_refs, created`.
Sections: **Goal**, **Target-state overview**, **How it maps onto the as-is** (each mapping cited to
as-is evidence), **Risks & trade-offs** (link ADRs), **Out of scope**.

## Task Ledger  (`plan/task-ledger.md`)
Front matter: `repo, goal, design_ref, topological_order: [T001, T002, …]`.
Body: a task table — `| id | goal | acceptance | depends_on |` — one row per sub-task.
Rules: tasks are **independent + individually acceptance-tested**; `depends_on` lists task ids; the
dependency graph is a **DAG**; `topological_order` lists every id with each dep before its dependent.
**Invariant (check_task_ledger)**: every task has non-empty `goal` + `acceptance`; `depends_on` ids
exist; graph acyclic; `topological_order` covers all ids and respects every edge.

## Reused entities (unchanged)
- **Feedback Item** (`templates/human-feedback.md`) — a correction to any artifact above.
- **Skill Edit Proposal** (`templates/skill-edit-proposal.md`) — generalizable pattern, gated.
- **Validation Gate Report** (`rubric/validation-gate.md`) — held-out regeneration result.
