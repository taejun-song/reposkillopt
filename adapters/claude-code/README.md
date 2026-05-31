# Adapter — Claude Code

This adapter wraps the canonical RepoSkillOpt skill (`skills/repo-skillopt/SKILL.md`) for use inside [Claude Code](https://claude.com/claude-code).

## Install

```sh
mkdir -p <target-repo>/.claude/skills/repo-skillopt
cp adapters/claude-code/SKILL.md <target-repo>/.claude/skills/repo-skillopt/SKILL.md
```

Replace `<target-repo>` with the path of the repository you want the agent to analyze (e.g., `~/work/click`).

## Verify

```sh
# Canonical version (this project)
grep '^version:' skills/repo-skillopt/SKILL.md

# Adapter version (installed in target)
grep '^canonical_version:' <target-repo>/.claude/skills/repo-skillopt/SKILL.md
```

Both commands must print the same semver string. If they diverge, the adapter is stale — copy the current adapter file again.

## Activate

Open the agent in `<target-repo>` and prompt with any of the FR-004 trigger verbs:

> "Help me understand this repository."

or

> "Map the architecture of this codebase."

or

> "What would change if I modified the X module? Is it safe?"

The skill activates, walks through the seven-stage workflow defined in `SKILL.md` → *Repository Understanding Workflow*, and writes a Repository Specification to `<target-repo>/.reposkillopt/specs/repository-specification.md`. Subsequent sessions append rollout logs, feedback items, and (when invoked) skill edit proposals to the sibling directories.

## Provide feedback

After the agent produces or revises a spec, just tell it what's wrong, missing, or mis-named. Examples:

- "Correction: `click.decorators.group` is the user-facing entrypoint, not `click.core.Group`."
- "You missed `tests/test_basic.py` entirely — please inspect it."
- "In our codebase, 'job' always means a Kafka consumer."

The agent records each piece of feedback to `<target-repo>/.reposkillopt/feedback/` using the Human Feedback template, marks the `scope` (repository-scoped vs candidate-for-generic), revises the spec, and updates the rollout log. See `skills/repo-skillopt/SKILL.md` → *Human Feedback Loop* for the full contract.

## Propose skill edits

When several candidate-for-generic feedback items accumulate, prompt:

> "Summarize recurring feedback in `.reposkillopt/feedback/` and propose any bounded edits to the canonical skill."

The agent produces one or more Skill Edit Proposals at `<target-repo>/.reposkillopt/proposals/SP-YYYY-MM-DD-NNN-*.md`. You decide accept / reject per proposal; accepted proposals are applied to `skills/repo-skillopt/SKILL.md` in the RepoSkillOpt project (not in the target repo).

## Known cross-agent differences

Add observations here as they surface in real use, with each entry following this shape:

```markdown
- **<date>** — <one-line observation>. Impact: <user-visible effect>. Workaround: <if any>.
```

- **2026-06-01** — Walkthrough consistency (not a runtime difference): `quickstart.md` Step 4 uses an illustrative correction ("`click.core.Group` is the primary entrypoint") that the committed reference spec never makes — the reference spec correctly states Click has *no* application entrypoint of its own. Impact: a user following Step 4 verbatim against `pallets/click@8.1.7` will not find that exact claim to correct, because the skill already gets it right. Workaround: treat Step 4 as a *template* for the feedback flow; the real reference correction is `FB-2026-05-31-001` (decorator-factory vs invocable-Command), which is the entrypoint-shaped feedback the skill actually elicited.

## See also

- Canonical skill: `skills/repo-skillopt/SKILL.md`
- Adapter contract: `specs/001-reposkillopt-skill/contracts/adapter-equivalence.contract.md`
- Full walkthrough: `specs/001-reposkillopt-skill/quickstart.md`
- Sample output for `pallets/click@8.1.7`: `examples/reference-output/claude-code/.reposkillopt/specs/repository-specification.md`
