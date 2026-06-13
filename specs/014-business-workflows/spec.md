# Feature Specification: Business-Process Workflow View

**Feature Branch**: `014-business-workflows`
**Created**: 2026-06-13
**Status**: Draft
**Input**: Find every BUSINESS-LOGIC pipeline a codebase has — the end-to-end course of actions for a domain operation (e.g. "place/trade an order → validate → reserve → charge → settle → notify"), NOT CI. A derived view over the ontology (012): enumerate every business entrypoint (route, job, CLI command), trace each as a path to its side effects/persistence, render as grounded mermaid flowcharts in a new section "20. Business workflows". Deterministic skeleton, `rg`-first, no silent omission. Built TDD.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Enumerate every business entrypoint (Priority: P1)

Every business entrypoint — HTTP route, scheduled job, CLI command — is enumerated; none is silently omitted. The enumeration table states a per-kind count and a grand total.

**Independent Test**: On a fixture, assert `enumerate_entrypoints` returns the route + job + CLI command, and the per-kind subtotal equals the raw count.

**Acceptance Scenarios**:
1. **Given** a repo with routes/jobs/CLI commands, **When** entrypoints are enumerated, **Then** each appears with kind + `file:line`, and the table's per-kind counts equal the raw detections (no silent omission).

### User Story 2 - Trace each as a grounded flow (Priority: P1)

Each entrypoint is traced as a course of actions (entrypoint → called services/functions → side effect/persistence) and rendered as a mermaid `flowchart`, every box carrying a `file:line` that resolves.

**Independent Test**: Trace a fixture handler that calls a service which writes a table; assert the flow has steps, each step's `file:line` resolves via grounding.

**Acceptance Scenarios**:
1. **Given** an entrypoint handler that calls in-repo functions, **When** traced, **Then** the flow lists those hops with `file:line`, ending at a side-effect/persistence step when one is reachable.
2. **Given** an untraceable handler (dynamic dispatch), **When** traced, **Then** the step is marked `[unknown]` with a reason — never dropped.

## Requirements *(mandatory)*

- **FR-001**: `enumerate_entrypoints(repo) -> list[Entrypoint]` — derive routes + jobs from `ontology.build_ontology`; detect CLI commands (`@click.command`/`@app.command`/`@cli.command`, argparse subparsers) via `rg`-first. Deterministic, model-free, sorted.
- **FR-002**: `trace_flow(repo, entrypoint) -> Flow` — bounded handler-window read; collect calls that bind to known ontology functions/classes as hops; mark a hop a side-effect/persistence terminal when it touches a data entity / save/commit/write/insert. Best-effort, deterministic.
- **FR-003**: `analyze_workflows(repo) -> WorkflowReport` — every entrypoint enumerated (no silent omission); per-kind counts + total; a flow per entrypoint.
- **FR-004**: `render_workflow_section(report)` — an enumeration **table** (kind · count · entrypoint `file:line`) + a mermaid `flowchart` per flow (deterministically capped; entries beyond the cap stay in the table with an omissions note). Every flow box carries `file:line`.
- **FR-005**: Deterministic & reproducible — same repo ⇒ byte-identical structured output; ordering from the ontology + explicit sorting.
- **FR-006**: New spec section **"20. Business workflows"** (appended after §19, keeping indices 1–19 byte-stable). MUST NOT enter `REQUIRED_SECTIONS`, the rubric, or the reward; section-completeness (denominator 19) is unchanged.
- **FR-007**: `rg`-first scan-don't-read for the agent path; engine reads bounded windows locally. No grounding/rubric/reward/metric-definition change.
- **FR-008**: Built TDD — tests written and red before implementation.

### Key Entities
- **Entrypoint**: `{kind (route|job|cli), name, file, line}`.
- **Flow**: `{entrypoint, steps:[{label, file, line, kind}]}` — kind ∈ entry/call/effect/unknown.
- **WorkflowReport**: `{entrypoints, flows, counts}`.

## Success Criteria *(mandatory)*

- **SC-001**: On `eco-standard-wiki`, every route/job/CLI entrypoint is enumerated (subtotals equal raw `rg` counts), and the discovery flow `POST /…/runs → orchestrator → persists` is reconstructed with each box resolvable.
- **SC-002**: Built twice ⇒ byte-identical structured output; zero model calls in enumeration/skeleton.
- **SC-003**: Every rendered flow box `file:line` resolves via grounding; "Business workflows" does not change section-completeness or any frozen metric (suite green).

## Assumptions
- Flow tracing is best-effort regex/grep (feature 009 posture); deep dataflow/polymorphic dispatch is out of scope and marked `[unknown]`. The deterministic skeleton (enumeration + one-hop calls) is the guarantee; richer prose tracing is the model's best-effort job, instructed by the skill.
