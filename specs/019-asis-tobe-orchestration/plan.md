# Implementation Plan: As-Is Analysis → To-Be Design → Implementation Orchestration

**Branch**: `019-asis-tobe-orchestration` | **Date**: 2026-06-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/019-asis-tobe-orchestration/spec.md`

## Summary

Add **two new vendor-neutral canonical skills** that extend RepoSkillOpt from *understand-the-as-is*
into *analyze as-is → plan to-be → orchestrate implementation*, plus their artifact templates,
rubric dimensions, and the **deterministic checks** that back the existing validation gate:

- **`repo-architecture`** — consumes the Repository Specification, emits an **Architecture View**
  (C4-style levels + sequences + dependency graph) and a **Change-Impact Analysis** (blast-radius),
  every claim cited to `file:line`, confidence-labeled, unknowns marked.
- **`repo-orchestration`** — consumes the as-is artifacts + a goal, emits **ADRs** + a **Design Doc**
  and a machine-readable **Task Ledger** (independent, acceptance-tested sub-tasks, declared deps,
  acyclic + topologically ordered). The ledger is an *artifact, not an executor*.

Both reuse the existing human-feedback + bounded skill-convergence machinery (Feedback Items, Skill
Edit Proposals, the held-out validation gate, rubric scoring) — **no parallel machinery**. Each new
skill contributes its own rubric dimensions and deterministic checks; a small **stdlib checker
module** makes those checks executable and TDD-able (e.g. task-ledger DAG acyclicity, every impact
entry cited). No change to the existing `repo-skillopt` contract.

## Technical Context

**Language/Version**: Markdown (CommonMark + YAML front matter) for the two skills, four adapters
each, and five artifact templates — the primary deliverable. Optional Python ≥ 3.10 (stdlib only)
for the deterministic artifact checkers, reusing `grounding.parse_citations`/`_resolve`.
**Primary Dependencies**: none new. Reuses `grounding` (citation resolution), the existing
`rubric/` + validation-gate (features 003/004), and the template/adapter conventions.
**Storage**: filesystem. New artifacts live under the **target repo's** `.reposkillopt/` in fixed
subdirs (`architecture/`, `impact/`, `decisions/`, `design/`, `plan/`).
**Testing**: stdlib `unittest` for the checkers (deterministic, model-free); skill/adapter
parity + the existing gate methodology for the skills.
**Project Type**: skill-first Markdown package + an optional engine (existing layout).
**Performance Goals**: checks are grep/parse over one artifact — sub-second; goal is *measurable
quality*, not throughput.
**Constraints**: vendor-neutral skills; adapter-equivalence (4 adapters mirror each skill);
deterministic & reproducible checks; stdlib-only; no execution of implementations; repository facts
stay repository-scoped; the understanding skill's contract is unchanged.
**Scale/Scope**: 2 skills × (SKILL.md + 4 adapters + CHANGELOG + rubric) + 5 templates + 1 checker
module + tests; validated on the in-repo engine + eco-standard-wiki as evidence repos.

## Constitution Check

*The committed `constitution.md` is unfilled (placeholders); these gates are the project's actual
non-negotiables from `CLAUDE.md`.*

- **Vendor neutrality** — PASS: both new `SKILL.md` carry no runtime-specific content; activation is
  by description/verbs only.
- **Adapter-equivalence (FR-024/025)** — PASS: each skill is mirrored to claude-code/codex/opencode/
  generic, every required section/principle/workflow/output rule preserved; `canonical_version` parity.
- **Skill-first scope** — PASS: deliverable is Markdown skills + templates + rubric. The Python
  checkers are *optional helpers* (outside MVP acceptance), stdlib-only, no SaaS/DB/runtime.
- **R10 claim labels + grounding** — PASS: artifacts use `[fact]`/`[inference]`/`[unknown]`/`[human]`;
  `[fact]` carries a `file:line` citation resolvable by the existing grounding checker.
- **Reuse, don't fork** — PASS: Feedback Items, Skill Edit Proposals, the validation gate, rubric,
  and held-out set are reused; each skill only *adds* rubric dimensions + checks.
- **No heavy deps / deterministic** — PASS: stdlib only; checks are model-free and reproducible.

No violations → Complexity Tracking not required.

## Project Structure

### Documentation (this feature)

```text
specs/019-asis-tobe-orchestration/
├── plan.md              # this file
├── research.md          # Phase 0 — naming, ledger format, check design, gate reuse
├── data-model.md        # Phase 1 — artifact schemas (Architecture View, Impact, ADR, Design, Ledger)
├── quickstart.md        # Phase 1 — how the three stages chain
├── contracts/
│   ├── asis-architecture.skill.md     # activation, sections, rubric dims, deterministic checks
│   ├── tobe-orchestration.skill.md     # activation, sections, rubric dims, deterministic checks
│   └── artifact-checks.contract.md     # the stdlib checker API
└── tasks.md             # Phase 2 (/speckit.tasks)
```

### Source Code (repository root)

```text
skills/
├── repo-architecture/   { SKILL.md, CHANGELOG.md }     # NEW — as-is skill (vendor-neutral)
└── repo-orchestration/  { SKILL.md, CHANGELOG.md }     # NEW — to-be skill (vendor-neutral)

adapters/{claude-code,codex,opencode,generic}/          # each gains the two new skills, mirrored

templates/
├── architecture-view.md            # NEW
├── change-impact-analysis.md       # NEW
├── adr.md                          # NEW
├── design-doc.md                   # NEW
└── task-ledger.md                  # NEW

rubric/
├── asis-architecture-rubric.md     # NEW — dimensions + deterministic checks
└── tobe-orchestration-rubric.md    # NEW — dimensions + deterministic checks
(reuses rubric/validation-gate.md + the held-out set)

engine/reposkillopt_engine/
└── artifact_checks.py              # NEW (optional helper) — deterministic checks:
                                    #   check_architecture_view, check_impact_analysis,
                                    #   check_task_ledger (DAG acyclic + topo + acceptance/deps),
                                    #   check_adr; reuses grounding for citation resolution
engine/tests/test_artifact_checks.py # NEW — TDD
```

**Structure Decision**: Mirror the existing `repo-skillopt` skill layout for each new skill;
artifacts and templates follow the existing `.reposkillopt/` + `templates/` conventions; the only
code is one stdlib checker module that makes the gate's deterministic checks executable.

## Complexity Tracking

> No constitution violations — section omitted.
