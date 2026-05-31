# Adapter — OpenCode

This adapter wraps the canonical RepoSkillOpt skill (`skills/repo-skillopt/SKILL.md`) for use with [OpenCode](https://github.com/sst/opencode)-style agents that read instructions from a top-level `AGENTS.md` file.

## Install

```sh
cp adapters/opencode/AGENTS.md <target-repo>/AGENTS.md
```

Replace `<target-repo>` with the path of the repository you want the agent to analyze. If the target repo already has an `AGENTS.md` (e.g., a Codex version), the two are effectively interchangeable — both follow the same convention and the metadata block identifies which adapter built each file.

## Verify

```sh
# Canonical version (this project)
grep '^version:' skills/repo-skillopt/SKILL.md

# Adapter version (installed in target)
grep 'canonical_version:' <target-repo>/AGENTS.md
```

Both commands must print the same semver string.

## Activate

Open the OpenCode agent in `<target-repo>` and prompt with any of the FR-004 trigger verbs. The agent reads `AGENTS.md`, activates the RepoSkillOpt skill, walks the seven-stage workflow, and writes a Repository Specification to `<target-repo>/.reposkillopt/specs/repository-specification.md`.

## Provide feedback / Propose skill edits

Identical to the Claude Code flow — see `adapters/claude-code/README.md` § *Provide feedback* and § *Propose skill edits*. The on-disk artifact layout is the same (`.reposkillopt/{specs,feedback,rollouts,proposals}/`).

## Known cross-agent differences

None recorded yet. Add observations here as they surface in real use, following this shape:

```markdown
- **<date>** — <one-line observation>. Impact: <user-visible effect>. Workaround: <if any>.
```

## See also

- Canonical skill: `skills/repo-skillopt/SKILL.md`
- Adapter contract: `specs/001-reposkillopt-skill/contracts/adapter-equivalence.contract.md`
- Sample output for `pallets/click@8.1.7`: `examples/reference-output/opencode/.reposkillopt/specs/repository-specification.md`
