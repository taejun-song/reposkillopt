# Contract — Rollout Log (`.reposkillopt/rollouts/<id>.md`)

**Scope**: A per-session record of what the agent inspected, claimed, was corrected on, and revised.
**Consumers**: Reviewers scoring with the rubric; researchers comparing skill versions (SC-012, User Story 8).

## Filename / id convention

`RL-YYYY-MM-DDTHHMMSS-<adapter>.md`

## Required front matter (FR-017)

```yaml
---
id: RL-YYYY-MM-DDTHHMMSS-<adapter>
agent: <identifier — e.g., "Claude Code">
agent_version: <if known>
adapter: <claude-code|codex|opencode|generic>
skill_version: <semver of canonical SKILL.md the adapter wraps>
canonical_version: <same semver mirrored from adapter>
task: <one-line description of what the user asked>
started: <ISO datetime>
ended: <ISO datetime>
spec_id: <Repository Specification id this rollout produced or revised>
---
```

## Required sections

1. `## Files inspected` — bullet list of paths (with line ranges when applicable).
2. `## Claims produced` — bullet list, each prefixed with its R10 label and any citations.
3. `## Human feedback received this session` — bullet list of Feedback Item ids touched during this rollout (with `(applied|deferred|withdrawn)` annotation each).
4. `## Revisions applied` — bullet list (Spec section → change description).

Optional: `## Notes` — anything cross-cutting (e.g., adapter-specific surprises that may inform a Skill Edit Proposal).

## Rules

- A Rollout Log MUST be produced for every session that creates or revises a Repository Specification.
- `spec_id` MUST resolve to an existing Repository Specification.
- Feedback ids listed under *Human feedback received this session* MUST exist under `.reposkillopt/feedback/`.
- `canonical_version` MUST equal the canonical version mirrored by the adapter in use (FR-027a).

## Acceptance checklist

- [ ] Filename matches the id convention.
- [ ] Front matter present, valid, and consistent with referenced artifacts.
- [ ] All four required sections present.
- [ ] At least one entry in *Files inspected*.
- [ ] At least one entry in *Claims produced*, each carrying an R10 label.
- [ ] Every feedback id listed exists and references this rollout's `spec_id`.
- [ ] *Revisions applied* matches the diff between the prior and current Repository Specification revisions (if any revisions were applied).
