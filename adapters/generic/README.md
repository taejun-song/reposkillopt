# Adapter — generic (custom local agent)

This adapter wraps the canonical RepoSkillOpt skill (`skills/repo-skillopt/SKILL.md`) for use with custom or local coding-agent harnesses that don't have a built-in skill-loading convention. It ships as **two files**:

- `skill.md` — the full Markdown skill (with YAML front matter).
- `system-prompt-fragment.md` — a ~15-line snippet to paste into your harness's system message that points at `skill.md` and tells the agent when to activate it.

## Install

There are two install patterns; pick whichever fits your harness.

### Pattern A — harness loads a skill file

If your harness can be configured to load a Markdown skill file (most can — under a `skills/`, `prompts/`, or `instructions/` directory), copy `skill.md` there:

```sh
cp adapters/generic/skill.md <your-harness-skills-dir>/repo-skillopt.md
```

### Pattern B — harness uses a system/developer message only

If your harness only accepts a system or developer message, copy `skill.md` to a stable location and paste the contents of `system-prompt-fragment.md` into your system message, replacing `<absolute path>` with the location of `skill.md`:

```sh
cp adapters/generic/skill.md ~/.config/<your-harness>/skills/repo-skillopt.md
# then edit your harness's system message, pasting in system-prompt-fragment.md
# with <absolute path> -> ~/.config/<your-harness>/skills
```

## Verify

```sh
# Canonical version (this project)
grep '^version:' skills/repo-skillopt/SKILL.md

# Adapter version
grep '^canonical_version:' adapters/generic/skill.md
```

Both must print the same semver string.

## Activate

Issue any prompt containing one of the FR-004 trigger verbs (`understand` / `map` / `document` / `onboard` / `refactor` / `modify` / `assess` a repository). The agent should follow the workflow defined in `skill.md` and write artifacts to `<target-repo>/.reposkillopt/{specs,feedback,rollouts,proposals}/`.

## Known cross-agent differences

- Custom harnesses vary in how aggressively they apply trigger conditions. If the skill fails to activate on a prompt that should match FR-004 triggers, prepend the trigger condition explicitly (e.g., "Activate the repo-skillopt skill and …").

## See also

- Canonical skill: `skills/repo-skillopt/SKILL.md`
- Adapter contract: `specs/001-reposkillopt-skill/contracts/adapter-equivalence.contract.md`
- Sample output for `pallets/click@8.1.7`: `examples/reference-output/generic/.reposkillopt/specs/repository-specification.md`
