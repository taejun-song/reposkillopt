# Implementation Plan: RepoSkillOpt — Portable Cross-Agent Skill

**Branch**: `001-reposkillopt-skill` | **Date**: 2026-05-31 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification at `/home/deploy/workspace/reposkillopt/specs/001-reposkillopt-skill/spec.md`

## Summary

RepoSkillOpt is delivered as a **skill-first, vendor-neutral Markdown package**, not application code. The deliverable is the canonical skill at `skills/repo-skillopt/SKILL.md` (with semantic version in YAML front matter, per FR-027a), four authoring templates (Repository Specification, Human Feedback, Rollout Log, Skill Edit Proposal), an evaluation rubric (0–3 qualitative + pass/fail deterministic, per FR-029 / FR-030), four adapter examples (Claude Code, Codex, OpenCode, generic) each mirroring the canonical version, one shared open-source reference repository used by every adapter example (FR-031), and a README explaining cross-agent installation. Working artifacts always land under `.reposkillopt/{specs,feedback,rollouts,proposals}/` in target repositories (FR-036a). No SaaS, database, frontend, or model fine-tuning (FR-033). Optional helper scripts may exist but are explicitly out of acceptance scope (Assumptions).

## Technical Context

**Language/Version**: Markdown (CommonMark) with YAML front matter for all canonical and adapter artifacts. Optional helper scripts (not part of MVP acceptance, decision in Phase 0 — OQ-3) may be POSIX `sh`/`bash`.
**Primary Dependencies**: None for the canonical artifact. If optional helper scripts are shipped, they assume only standard tools (`grep`, `find`, `jq` optional) that the project's coding-agent harnesses already rely on.
**Storage**: Filesystem only. Source of truth: `skills/repo-skillopt/SKILL.md`. Working artifacts written by the agent into a target repository's `.reposkillopt/{specs,feedback,rollouts,proposals}/` tree (FR-036a). No database (FR-033).
**Testing**: Adapter-equivalence verification against the canonical skill (FR-025); per-dimension rubric scoring (FR-029); pass/fail deterministic checks (FR-030) — cited path resolution, cited symbol resolution, required-section presence, hallucination flagging, prior-feedback addressing, canonical-section coverage in adapters. The MVP ships these as documented procedures; optional scripted automation is decided in Phase 0.
**Target Platform**: Local developer workstations (Linux, macOS, Windows). Markdown artifacts are platform-agnostic; the only platform-sensitive surface is any optional helper script (kept POSIX `sh` to avoid lock-in).
**Project Type**: **Skill / instruction artifact package.** Does not fit the library / CLI / web / mobile templates; closest analogue is a vendor-neutral prompt/instruction kit. The Project Structure section below documents the chosen layout.
**Performance Goals**: Not application-style. The user-visible performance targets are codified in Success Criteria — notably SC-001 (under 30 minutes of human time for a first Repository Specification on a sample repo) and SC-009 (under 5 minutes of human reading per Skill Edit Proposal).
**Constraints**: Local-first (FR-033, FR-035); vendor-neutral (FR-002); Markdown-first (FR-036); explicit separation between canonical-skill content and adapter packaging, and between generic skill instructions and repository-specific facts (FR-027); bounded, reviewable skill edits (FR-020).
**Scale/Scope**: 1 canonical skill, 1 changelog, 4 templates, 1 evaluation rubric, 4 adapters, 1 shared reference example repository, 4 adapter-specific sample-output trees, 1 README. Total expected size of the MVP deliverable: ~20–30 Markdown files.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The repository's `.specify/memory/constitution.md` is still in unfilled template state (placeholders `[PRINCIPLE_1_NAME]` etc. have not been replaced; no version has been ratified). Per the workflow, there are therefore **no project-specific constitutional gates to evaluate**.

In their absence, this plan adopts the spec's **own** non-negotiable constraints as standing gates for both Phase 0 and the post-Phase-1 re-check:

| Standing gate (from spec) | Required behavior |
|---|---|
| **Vendor neutrality** (FR-002) | Canonical SKILL.md must not name or depend on any single coding-agent runtime. Per-runtime details live only in adapters. |
| **Skill-first scope** (FR-033, FR-034, Assumptions) | No SaaS, database, frontend, deep static analysis, or model fine-tuning anywhere in the design. Helper scripts remain optional and outside acceptance. |
| **Local-first privacy** (FR-035) | The design must not introduce any required external network call. |
| **Bounded skill edits** (FR-019, FR-020) | Every Skill Edit Proposal in the design must be sized for accept/reject in ≤5 minutes of reading (SC-009). |
| **Canonical/adapter separation** (FR-024, FR-025, FR-027) | Adapters are thin wrappers; no required canonical section, principle, workflow stage, or output-discipline rule may be silently dropped or weakened. The adapter-equivalence check applies. |
| **Generic vs repository-scoped separation** (FR-016, FR-022, FR-027) | Repository-specific facts never enter the canonical skill without an explicit scope decision (and only via a Skill Edit Proposal). |
| **Version traceability** (FR-027a) | Canonical SKILL.md carries `version:` in YAML front matter; every adapter carries `canonical_version:` (or an explicit metadata block when the host environment forbids YAML front matter). |
| **Evidence discipline** (FR-007, FR-008, FR-009, FR-011) | The canonical skill must enforce labeling of every major claim (as defined in FR-008) and citations for every "verified fact" claim. |

**Initial gate evaluation**: All gates are intrinsic to the design choices in the spec and are honored by the project structure below. No deviations. The Complexity Tracking table at the bottom is therefore left empty.

## Project Structure

### Documentation (this feature)

```text
specs/001-reposkillopt-skill/
├── plan.md              # This file (/speckit.plan command output)
├── spec.md              # Feature specification (already complete)
├── research.md          # Phase 0 output (this command)
├── data-model.md        # Phase 1 output (this command)
├── quickstart.md        # Phase 1 output (this command)
├── contracts/           # Phase 1 output (this command)
└── tasks.md             # Phase 2 output (/speckit.tasks — NOT created by /speckit.plan)
```

### Source Code (repository root)

Because the deliverable is a Markdown skill package, the "source" layout is the layout of the package itself. All paths are relative to the repository root.

```text
skills/
└── repo-skillopt/
    ├── SKILL.md                                   # Canonical skill (FR-001, FR-003, FR-027a)
    └── CHANGELOG.md                               # Version history per FR-027a

templates/
├── repository-specification.md                    # FR-005, FR-006
├── human-feedback.md                              # FR-013
├── rollout-log.md                                 # FR-017
└── skill-edit-proposal.md                         # FR-019

rubric/
├── evaluation-rubric.md                           # FR-028, FR-029 (0–3 qualitative)
└── deterministic-checks.md                        # FR-030 (pass/fail)

adapters/
├── claude-code/
│   ├── README.md
│   └── SKILL.md                                   # Claude Code skill format adapter
├── codex/
│   ├── README.md
│   └── AGENTS.md                                  # Codex AGENTS.md adapter
├── opencode/
│   ├── README.md
│   └── AGENTS.md                                  # OpenCode AGENTS.md / rules adapter
└── generic/
    ├── README.md
    └── skill.md                                   # Generic Markdown / system-prompt fragment

examples/
├── README.md                                      # Identifies the shared reference repo + pinned commit (FR-031)
└── reference-output/                              # One reference repo, four adapter outputs (FR-031)
    ├── claude-code/.reposkillopt/{specs,feedback,rollouts,proposals}/
    ├── codex/.reposkillopt/{specs,feedback,rollouts,proposals}/
    ├── opencode/.reposkillopt/{specs,feedback,rollouts,proposals}/
    └── generic/.reposkillopt/{specs,feedback,rollouts,proposals}/

README.md                                          # Top-level — cross-agent installation (FR-032)
LICENSE
```

Out of scope for this layout (already present, infrastructure, not part of the deliverable):
- `.specify/` — Spec Kit's own internal directory.
- `.claude/skills/speckit-*` — Spec Kit's authoring skills.
- `specs/` — Spec Kit work products (this plan, the spec, etc.).

**Structure Decision**: Layout is determined by the spec's mandatory artifacts (FR-001, FR-005, FR-013, FR-017, FR-019, FR-023, FR-028, FR-031, FR-032). The four top-level directories (`skills/`, `templates/`, `rubric/`, `adapters/`, `examples/`) mirror the named artifact families in the spec one-to-one and keep canonical content (`skills/`) physically separated from adapter packaging (`adapters/`) and from per-agent reference outputs (`examples/reference-output/`), satisfying FR-027.

## Phase 0 — Research (research.md)

Phase 0 resolves the items below and writes the consolidated findings into `research.md`. Each item must end with a **Decision / Rationale / Alternatives considered** block.

Research tasks:

1. **Reference repository selection (FR-031, clarification Q3).** Choose one small open-source legacy repository (target ~5–20k LOC) that all four adapter examples will analyze. Selection criteria: permissive license, public, stable enough to pin to a specific commit/tag, in a mainstream language (Python or TypeScript preferred), small enough that the canonical workflow can complete in one session, "legacy" enough that evidence-grounded discovery is meaningful. Decision: name + source URL + pinned commit/tag.

2. **Claude Code skill packaging conventions.** Canonical Claude Code skill file location and YAML front matter expectations (name, description, trigger fields). Confirm that `canonical_version:` (the FR-027a mirror field) can coexist with required Claude Code keys.

3. **Codex AGENTS.md conventions.** Confirm Codex `AGENTS.md` placement, structural expectations, and whether YAML front matter is supported. If not, define the explicit metadata block per FR-027a fallback.

4. **OpenCode rules / AGENTS.md conventions.** Same as #3 for OpenCode. Decide between AGENTS.md and the rules format if both exist; pick whichever preserves canonical-skill intent most faithfully.

5. **Generic adapter shape.** Decide between a single Markdown skill file vs a paired system-prompt fragment + Markdown skill. Tradeoff: ease of paste into a custom harness vs richness of structure.

6. **Optional helper scripts — scope (OQ-3, deferred from clarify).** Decide which deterministic checks (FR-030) ship as documented procedures only and which (if any) are worth packaging as small POSIX `sh` scripts in v1 vs deferred. Default per Assumptions: documented-only for MVP.

7. **Cross-agent behavior notes location (OQ-5, deferred from clarify).** Decide whether per-adapter notes live alongside each adapter's `README.md` or in a single shared `adapters/NOTES.md`. Default: per-adapter for v1 unless a shared file proves materially easier.

8. **CHANGELOG format.** Single `CHANGELOG.md` adjacent to `SKILL.md`, Keep-A-Changelog conventions, semver entries — confirm and pin.

9. **Anchor descriptions for the 0–3 rubric (FR-029).** Each of the 15 qualitative dimensions needs short anchor text per score level. Draft anchors so a human reviewer can score in seconds.

10. **Major-claim labeling syntax.** Decide on a compact in-Markdown notation for the FR-008 labels (e.g., `**[fact]**`, `**[inference]**`, `**[unknown]**`, `**[human]**`) so that the deterministic checks in FR-030 can detect them programmatically if scripts are later added.

**Output**: `specs/001-reposkillopt-skill/research.md` with all ten decisions resolved. No `NEEDS CLARIFICATION` may remain.

## Phase 1 — Design & Contracts

**Prerequisites**: `research.md` complete.

1. **Data model (`data-model.md`).** This project has no application data model, but it does have **artifact schemas**. Document the structure of each working artifact:
   - **Canonical Skill** — required YAML front matter fields (`name`, `description`, `version`, optional `triggers`), required sections per FR-003, claim-labeling syntax, citation format.
   - **Adapter** — required front matter or metadata block per FR-027a (`canonical_version`), packaging conventions per target, any required deviations from the canonical structure (and the equivalence-check proof for each).
   - **Repository Specification** — required sections per FR-005 (all 19), claim-label syntax, citation format, Evidence Index format. Defines what "filled in" looks like.
   - **Human Feedback Item** — fields per FR-013 (identifier, timestamp, author, type, referenced claim ids, feedback text, suggested action, scope: repo-only vs candidate-for-generic).
   - **Rollout Log** — fields per FR-017 (agent identity, skill version, task, files inspected, claims produced, feedback received, revisions applied).
   - **Skill Edit Proposal** — fields per FR-019 (target section, edit kind, proposed text, supporting feedback ids, expected effect, scope, risk notes, decision: accepted/rejected, decision rationale).
   - **Identifier conventions** — how feedback items, rollout logs, and proposals are uniquely named on disk (date prefix + slug recommended).
   - **State transitions** — Repository Specification revision lifecycle (draft → revised → superseded); Skill Edit Proposal lifecycle (proposed → accepted/rejected).

2. **Contracts (`contracts/`).** This project's "interfaces" are not REST endpoints; they are the contracts between the project and each consumer:
   - `contracts/canonical-skill.contract.md` — the contract a canonical SKILL.md must satisfy (required sections, required front matter, output-discipline rules). Acceptance: a checklist a reviewer can apply to any candidate canonical file.
   - `contracts/adapter-equivalence.contract.md` — the FR-025 adapter-equivalence check, written as a deterministic checklist mapping each canonical required item to its preservation requirement in any adapter.
   - `contracts/repository-specification.contract.md` — required sections (FR-005), label-syntax rules (FR-008), citation rules (FR-009), Evidence Index rules.
   - `contracts/feedback-item.contract.md` — required fields and scope rules (FR-013, FR-016).
   - `contracts/rollout-log.contract.md` — required fields (FR-017).
   - `contracts/skill-edit-proposal.contract.md` — required fields, edit-kind enum, boundedness rule (FR-019, FR-020).
   - `contracts/evaluation-rubric.contract.md` — 15 qualitative dimensions × 0–3 scale (FR-029), pass/fail deterministic checks (FR-030), score-recording format that supports SC-012 per-dimension delta comparisons.

   Each contract file ends with an explicit acceptance checklist that a reviewer can run against a candidate artifact without re-running the agent.

3. **Quickstart (`quickstart.md`).** Install-and-use walkthrough against the reference repository chosen in Phase 0, **using one adapter** (Claude Code is the default unless Phase 0 finds it less universal). Sections:
   - Prerequisites (agent harness installed, reference repo cloned and pinned to the recorded commit).
   - Install: copy `adapters/claude-code/SKILL.md` into the target environment.
   - Run: issue the activation prompt; observe the Repository Specification appear in `.reposkillopt/specs/`.
   - Provide feedback: write a Feedback Item to `.reposkillopt/feedback/`, ask the agent to revise.
   - (Optional) Propose skill edits: invoke the convergence loop against the feedback log; observe `.reposkillopt/proposals/`.
   - Where to read next (links to canonical skill, rubric, contracts).

4. **Agent context update.** Run `.specify/scripts/bash/update-agent-context.sh claude` to add new technology and structural choices from this plan into the project's Claude-specific context file. Preserve any manual additions.

**Output**: `data-model.md`, `contracts/*.contract.md`, `quickstart.md`, and an updated agent context file.

## Post-Design Constitution Re-check

To be performed after Phase 1 artifacts exist. Apply the same eight standing gates from the table above to:
- the artifact schemas in `data-model.md`,
- each contract in `contracts/`,
- the install-and-use flow in `quickstart.md`.

Pay particular attention to:
- **Vendor neutrality** — no contract may reference a single agent harness in its body; per-adapter notes belong only in adapter files.
- **Bounded skill edits** — the `skill-edit-proposal.contract.md` must explicitly require boundedness (≤5 min review per SC-009).
- **Generic/repo-scoped separation** — `feedback-item.contract.md` must require an explicit scope field.

Any violation surfaced in the re-check must either be fixed in the design or recorded in **Complexity Tracking** below with justification.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|

*(none — no deviations identified in either the initial check or the planned post-Phase-1 re-check)*
