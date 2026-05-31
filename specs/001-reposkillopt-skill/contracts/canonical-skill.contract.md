# Contract — Canonical Skill (`skills/repo-skillopt/SKILL.md`)

**Scope**: The single source-of-truth canonical skill (FR-001).
**Consumers**: All adapters; all evaluation tooling; human reviewers.

## Required front matter

```yaml
---
name: repo-skillopt
description: <one-line; must include FR-004 trigger conditions>
version: <semver MAJOR.MINOR.PATCH>
---
```

## Required sections (in this order, per FR-003)

1. `# RepoSkillOpt — Canonical Skill`
2. `## Purpose` — states the skill's goal in the language of FR-001 / FR-003.
3. `## Trigger Conditions` — enumerates the FR-004 verbs (understand, map, document, onboard to, refactor, modify, assess) and explicitly excludes activation outside them.
4. `## Operating Principles` — contains one bullet for each of FR-007, FR-008, FR-009, FR-010, FR-011 (no README-only reliance; evidence grounding; four-way labels; citations for facts; explicit unknowns; concrete-over-pattern).
5. `## Repository Understanding Workflow` — lists FR-012 stages (a)–(g) in order, each as its own subsection or labeled bullet.
6. `## Repository Specification Format` — references the Repository Specification template by path and reproduces the FR-005 section list.
7. `## Human Feedback Loop` — describes FR-013 / FR-014 / FR-015 / FR-016 behavior. Must explicitly require that feedback items are recorded *before* being applied (FR-014) and that repository-specific facts are NOT silently promoted (FR-016).
8. `## Skill Convergence Loop` — describes FR-018 / FR-019 / FR-020 / FR-021 / FR-022 behavior. Must name the six edit kinds (ADD, REPLACE, DELETE, REORDER, SPECIALIZE, GENERALIZE) and state the boundedness requirement.
9. `## Output Discipline` — requires the R10 label notation for every major claim (FR-008, as defined there) and citations for `**[fact]**` claims (FR-009).

## Acceptance checklist (apply by reading the file)

A canonical SKILL.md passes when every item below is true:

- [ ] Front matter `name`, `description`, and `version` all present and non-empty.
- [ ] `version` is a syntactically valid semver string.
- [ ] `description` contains the FR-004 trigger verbs (understand / map / document / onboard / refactor / modify / assess) or recognizable equivalents.
- [ ] All nine required sections are present, in order.
- [ ] *Trigger Conditions* enumerates the FR-004 verbs and states the skill must NOT activate outside them.
- [ ] *Operating Principles* contains one bullet (or equivalent) for each rule in FR-007, FR-008, FR-009, FR-010, FR-011.
- [ ] *Repository Understanding Workflow* lists all seven FR-012 stages in order.
- [ ] *Repository Specification Format* references the template and lists the 19 FR-005 sections.
- [ ] *Human Feedback Loop* names the Human Feedback Template, requires recording-before-applying, and forbids silent promotion of repo-specific facts to the canonical skill.
- [ ] *Skill Convergence Loop* names the six edit kinds and states FR-020 boundedness (≤5-minute review per SC-009).
- [ ] *Output Discipline* requires the R10 label notation for major claims and requires citations for `**[fact]**` claims.
- [ ] The file mentions no specific agent runtime (Claude Code, Codex, OpenCode, Copilot, etc.) in any normative section — vendor neutrality per FR-002. (Runtime names may appear only in examples explicitly marked as illustrative.)
- [ ] The file's behavior, if followed, would produce a Repository Specification matching `contracts/repository-specification.contract.md`.

A canonical SKILL.md fails if any check above is unchecked.
