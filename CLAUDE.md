# reposkillopt Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-05-31

## Active Technologies

- Markdown (CommonMark) with YAML front matter for all canonical and adapter artifacts. Optional helper scripts (not part of MVP acceptance, decision in Phase 0 — OQ-3) may be POSIX `sh`/`bash`. + None for the canonical artifact. If optional helper scripts are shipped, they assume only standard tools (`grep`, `find`, `jq` optional) that the project's coding-agent harnesses already rely on. (001-reposkillopt-skill)

## Project Structure

```text
backend/
frontend/
tests/
```

## Commands

# Add commands for Markdown (CommonMark) with YAML front matter for all canonical and adapter artifacts. Optional helper scripts (not part of MVP acceptance, decision in Phase 0 — OQ-3) may be POSIX `sh`/`bash`.

## Code Style

Markdown (CommonMark) with YAML front matter for all canonical and adapter artifacts. Optional helper scripts (not part of MVP acceptance, decision in Phase 0 — OQ-3) may be POSIX `sh`/`bash`.: Follow standard conventions

## Recent Changes

- 001-reposkillopt-skill: Added Markdown (CommonMark) with YAML front matter for all canonical and adapter artifacts. Optional helper scripts (not part of MVP acceptance, decision in Phase 0 — OQ-3) may be POSIX `sh`/`bash`. + None for the canonical artifact. If optional helper scripts are shipped, they assume only standard tools (`grep`, `find`, `jq` optional) that the project's coding-agent harnesses already rely on.

<!-- MANUAL ADDITIONS START -->

## Project at a glance (manual)

**RepoSkillOpt** is a portable, skill-first Markdown package, not application code.

### Real layout (overrides the auto-generated tree above)

```text
skills/repo-skillopt/{SKILL.md,CHANGELOG.md}    # Canonical skill, source of truth
templates/{repository-specification,human-feedback,rollout-log,skill-edit-proposal}.md
rubric/{evaluation-rubric,deterministic-checks}.md
adapters/{claude-code,codex,opencode,generic}/  # Thin wrappers around the canonical skill
examples/reference-output/{claude-code,codex,opencode,generic}/.reposkillopt/...
README.md
```

### Non-negotiables when editing this project

- Vendor neutrality of `skills/repo-skillopt/SKILL.md` (FR-002): no mention of any specific coding-agent runtime in normative content.
- Adapter-equivalence (FR-024, FR-025): adapters preserve every required canonical section, principle, workflow stage, and output-discipline rule.
- Skill-first scope (FR-033, Assumptions): no SaaS, database, frontend, model fine-tuning. Helper scripts are optional and outside acceptance.
- Working artifacts produced by agents using the skill live under `.reposkillopt/{specs,feedback,rollouts,proposals}/` of the *target* repository (FR-036a) — never inside this project.
- Major claim labels follow Phase 0 R10 (`**[fact]**`, `**[inference]**`, `**[unknown]**`, `**[human]**`); `**[fact]**` always carries a citation.
- Canonical skill carries `version:` (semver) in YAML front matter; every adapter mirrors it as `canonical_version:` (FR-027a).

### Where the design lives

- Spec: `specs/001-reposkillopt-skill/spec.md`
- Plan: `specs/001-reposkillopt-skill/plan.md`
- Research decisions: `specs/001-reposkillopt-skill/research.md`
- Artifact schemas: `specs/001-reposkillopt-skill/data-model.md`
- Contracts (canonical-skill, adapter-equivalence, repo-spec, feedback, rollout, proposal, rubric): `specs/001-reposkillopt-skill/contracts/`
- Quickstart walkthrough: `specs/001-reposkillopt-skill/quickstart.md`

<!-- MANUAL ADDITIONS END -->
