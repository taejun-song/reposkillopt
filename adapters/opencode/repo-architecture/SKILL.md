---
name: repo-architecture
description: Evidence-grounded as-is architecture analysis and change-impact (blast-radius). Activates when the user asks to map the architecture, assess dependencies or coupling, or evaluate "what would change if we…".
canonical_version: 0.1.0
adapter: opencode
---

# RepoSkillOpt — As-Is Architecture Analysis (Canonical Skill)

## Purpose

This is the **repo-specializing analysis layer** of RepoSkillOpt. The generic understanding skill
(`repo-skillopt`) is unchanged — it produces the repo-neutral **Repository Specification**. This skill
*specializes on a specific repository*: it deepens that Repository Specification into an
evidence-grounded view of the *current* architecture and answers "what would a change ripple into?"
— before anything is touched. It produces an **Architecture View** and a **Change-Impact
(blast-radius) Analysis**, and is the *analyze as-is* stage the *plan to-be* skill (`repo-orchestration`)
consumes. The skill's own content is vendor-neutral (no coding-agent runtime dependency); its
*output* is repo-specific.

## Trigger Conditions

Activate when the user asks to **map the architecture**, **assess dependencies/coupling/layering**,
or **evaluate "what would change if we… / is it safe to change X"** — or recognizable equivalents.
Do **not** activate for unrelated requests.

## Prerequisite

A Repository Specification (`.reposkillopt/specs/repository-specification.md`). If absent, state the
prerequisite and point the user to the repository-understanding skill; do **not** fabricate an
architecture from shallow inspection.

## Operating Principles

- **Build on the spec, corroborate against code.** The Repository Specification is the starting
  evidence; verify every architectural claim against the actual files, configs, and call sites.
- **Ground every major claim.** Each carries exactly one label — `**[fact]**`, `**[inference]**`,
  `**[unknown]**`, `**[human]**`; `**[fact]**` MUST carry a resolvable `file:line`/symbol citation.
- **No silent omission.** Unresolvable structure or impact is `**[unknown]**` with the reason, never dropped.
- **Do not overclaim.** Do not describe layers or flows you have not traced; mark inference as inference.
- **Repository facts stay repository-scoped.** Only patterns explicitly marked candidate-for-generic
  may enter the skill-convergence loop.

## Workflow

(a) **Read the Repository Specification** and the entrypoints, manifests, and core modules it cites.

(b) **Architecture View** (`.reposkillopt/architecture/architecture-view.md`, per
`templates/architecture-view.md`): C4-style levels — **Context** (system + external actors),
**Containers** (runtime/deployable units), **Components** (modules within containers) — plus **Key
sequences** (end-to-end flows, cited at each hop) and a **Dependency graph** (cited internal edges).
Every component and edge cites a real `file:line`. Diagrams (`graph`, `sequenceDiagram`) are visual
aids and carry no citations; every node/edge they show also appears as a cited line.

(c) **Change-Impact Analysis** (`.reposkillopt/impact/change-impact-analysis.md`, per
`templates/change-impact-analysis.md`): for the named target/change, the affected **modules, tests,
contracts, and call sites** — each row with a **confidence** label (high|medium|low) tied to evidence
strength (direct cited call site = high; name-resolution/inference = medium; dynamic/unresolved = low
and `**[unknown]**`) and a citation. Locate impact with a fast scanner (`rg`/`grep`) and read only the
matched lines you cite.

(d) **Deterministic completeness gate.** Before finishing, the artifacts MUST pass the deterministic
checks (`check_architecture_view`, `check_impact_analysis`): every component/edge cited and
resolvable; every impact row carries a citation and a confidence label.

## Output Discipline

Labels: `**[fact]**` (verified; cited), `**[inference]**` (state the basis), `**[unknown]**` (also
listed as such), `**[human]**` (cite the Feedback Item id). Citations use `path:line`,
`path:start-end`, `path:Symbol[:line]`, or `cmd:`/`output:`. Trivial recitations need no label.

## Human Feedback Loop

Corrections are recorded as **Feedback Items** (`templates/human-feedback.md`) under
`.reposkillopt/feedback/` and applied to the artifact in place. Repository-specific corrections stay
repository-scoped.

## Skill Convergence Loop

When recurrent feedback (≥3 related items) marked **candidate-for-generic** reveals a weakness in
*this* skill, draft a **Skill Edit Proposal** (`templates/skill-edit-proposal.md`). It may be
accepted **only** after passing the validation gate (`rubric/validation-gate.md`): regenerate the
artifacts for a disjoint held-out reference set with **no per-dimension rubric regression** (see
`rubric/asis-architecture-rubric.md`) and the deterministic checks still passing. Nothing is silently
promoted; acceptance bumps the version + adds a CHANGELOG entry. Mirror every accepted edit into the
four adapters (adapter-equivalence).
