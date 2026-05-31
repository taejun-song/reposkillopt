# RepoSkillOpt

A **portable, skill-first** package that teaches any coding-agent harness — Claude Code, Codex, OpenCode, GitHub Copilot-style agents, custom local agents — a disciplined workflow for understanding legacy repositories through evidence-grounded analysis, recurrent human feedback, and bounded skill convergence.

RepoSkillOpt is not a service, not a CLI, not a database, and not a model fine-tune. It is a vendor-neutral Markdown skill plus a small set of templates, adapter examples, and an evaluation rubric.

## What you get

```text
skills/repo-skillopt/SKILL.md      # The canonical skill — single source of truth
skills/repo-skillopt/CHANGELOG.md  # Semantic version history

templates/                         # Authoring templates the skill references
├── repository-specification.md
├── human-feedback.md
├── rollout-log.md
└── skill-edit-proposal.md

rubric/                            # Evaluation rubric (qualitative + deterministic)
├── evaluation-rubric.md
└── deterministic-checks.md

adapters/                          # Thin per-environment wrappers around the canonical skill
├── claude-code/SKILL.md
├── codex/AGENTS.md
├── opencode/AGENTS.md
└── generic/{skill.md, system-prompt-fragment.md}

examples/reference-output/         # Sample outputs against pallets/click@8.1.7 for each adapter
└── {claude-code,codex,opencode,generic}/.reposkillopt/
    ├── specs/                     # Sample Repository Specifications
    ├── feedback/                  # Sample Feedback Items
    ├── rollouts/                  # Sample Rollout Logs
    └── proposals/                 # Sample Skill Edit Proposals

.gitignore                         # Excludes local working artifacts and build-time tooling (.claude/, .specify/, CLAUDE.md)
```

## How to use it across agents

### Working-artifact layout

When you (or an agent) use this skill on a *target* repository, the skill writes its working artifacts under a fixed layout at that repository's root:

```text
<target-repo>/.reposkillopt/
├── specs/         # The Repository Specifications the agent produces
├── feedback/      # Your feedback items (one Markdown file per item)
├── rollouts/      # One log per agent session
└── proposals/     # Bounded edits proposed for the canonical skill
```

Every adapter writes to and reads from this same layout, so artifacts produced under one adapter remain readable by another.

### Quick start (Claude Code)

1. Copy the Claude Code adapter into the target environment:
   ```sh
   mkdir -p <target-repo>/.claude/skills/repo-skillopt
   cp adapters/claude-code/SKILL.md <target-repo>/.claude/skills/repo-skillopt/SKILL.md
   ```
2. Verify the adapter's `canonical_version` matches the canonical skill:
   ```sh
   grep '^version:' skills/repo-skillopt/SKILL.md
   grep '^canonical_version:' <target-repo>/.claude/skills/repo-skillopt/SKILL.md
   # Both should print the same semver.
   ```
3. Open Claude Code in `<target-repo>` and prompt:
   > "Help me understand this repository."

   The skill activates, executes the seven-stage workflow, and writes a Repository Specification to `<target-repo>/.reposkillopt/specs/repository-specification.md`.

4. Provide corrections as prose; the agent records each one to `.reposkillopt/feedback/` and revises the spec. See `adapters/claude-code/README.md` for the full flow.

### Other agent harnesses

| Harness | Adapter file | Install location |
|---|---|---|
| Claude Code | `adapters/claude-code/SKILL.md` | `<target-repo>/.claude/skills/repo-skillopt/SKILL.md` |
| Codex | `adapters/codex/AGENTS.md` | `<target-repo>/AGENTS.md` |
| OpenCode | `adapters/opencode/AGENTS.md` | `<target-repo>/AGENTS.md` |
| Generic / custom | `adapters/generic/skill.md` + `system-prompt-fragment.md` | per harness convention |

See each adapter's own guide for installation specifics and "Known cross-agent differences":

- `adapters/claude-code/README.md`
- `adapters/codex/README.md`
- `adapters/opencode/README.md`
- `adapters/generic/README.md`

For a full end-to-end walkthrough against `pallets/click@8.1.7`, see `specs/001-reposkillopt-skill/quickstart.md`.

## How to provide feedback

Feedback is a first-class input. After the agent produces a Repository Specification:

1. Tell the agent what is wrong, missing, mis-named, or under-supported.
2. The agent writes a Feedback Item to `<target-repo>/.reposkillopt/feedback/FB-YYYY-MM-DD-NNN-<slug>.md` using `templates/human-feedback.md` and assigns it a `type` (correction / missing-context / terminology / quality-rating / …) and a `scope`:
   - `repository-scoped` — stays in this target repository only; never enters the canonical skill.
   - `candidate-for-generic` — may be cited by a future Skill Edit Proposal targeting the canonical skill.
3. The agent revises the Repository Specification and updates the rollout log.

## How to propose canonical skill edits

When several Feedback Items point at the same gap in the canonical skill, ask the agent to summarize the pattern and propose edits:

1. The agent writes one or more Skill Edit Proposals to `<target-repo>/.reposkillopt/proposals/SP-YYYY-MM-DD-NNN-<slug>.md` using `templates/skill-edit-proposal.md`.
2. Each proposal is bounded (≤5 minutes of human review), categorized as `ADD` / `REPLACE` / `DELETE` / `REORDER` / `SPECIALIZE` / `GENERALIZE`, and references the supporting Feedback Item ids.
3. A maintainer accepts or rejects each proposal. Accepted edits are applied to `skills/repo-skillopt/SKILL.md` (in this repository) and bump the canonical `version:`. Rejected proposals are preserved with rationale.

## Evaluation

See `rubric/evaluation-rubric.md` (15 qualitative dimensions, scored 0–3) and `rubric/deterministic-checks.md` (7 pass/fail checks). The rubric is technology-agnostic and is the same instrument used to compare canonical skill versions over time.

## Versioning

The canonical skill follows [Semantic Versioning](https://semver.org/). The `version:` field in `skills/repo-skillopt/SKILL.md` is the source of truth; every adapter mirrors it via its `canonical_version:` field (in YAML front matter or, for environments that forbid YAML front matter, in an HTML-comment metadata block at the top of the adapter file). Changes are recorded in `skills/repo-skillopt/CHANGELOG.md` using [Keep a Changelog](https://keepachangelog.com/) conventions.

## Limitations

RepoSkillOpt does **not** claim universal repository understanding. In particular:

- The skill ships with adapters and reference outputs for one open-source legacy repository (`pallets/click@8.1.7`). Other ecosystems work — the skill is language-agnostic — but examples will grow over time.
- The skill is **not** a replacement for human code review. It produces a structured, evidence-grounded artifact that an engineer can trust and act on; it does not approve changes on anyone's behalf.
- Initial language coverage is limited by example, not by design. Languages, frameworks, and project types beyond those exercised in `examples/` may surface gaps that subsequent feedback rounds can address.
- The skill performs no deep static analysis; it relies on what an ordinary agent harness can read with file and shell access.
- The skill runs entirely locally and does not exfiltrate repository contents to external services unless your chosen agent harness is independently configured to do so.

## License

Apache-2.0. See `LICENSE`.

## Design documents

- Specification: `specs/001-reposkillopt-skill/spec.md`
- Implementation plan: `specs/001-reposkillopt-skill/plan.md`
- Phase-0 research decisions: `specs/001-reposkillopt-skill/research.md`
- Artifact schemas: `specs/001-reposkillopt-skill/data-model.md`
- Contracts: `specs/001-reposkillopt-skill/contracts/`
- Quickstart walkthrough: `specs/001-reposkillopt-skill/quickstart.md`
