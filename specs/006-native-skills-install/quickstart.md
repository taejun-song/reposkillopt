# Quickstart — 006 Native Agent-Skills Install

## Install into the native skills directory (no AGENTS.md touched)

```sh
# one install that Codex, OpenCode, and Cursor all read:
installer/reposkillopt-install --agent agents --dest /path/to/target-repo
#  -> /path/to/target-repo/.agents/skills/repo-skillopt/SKILL.md

# or a specific harness's own dir:
installer/reposkillopt-install --agent cursor   --dest .   #  .cursor/skills/repo-skillopt/SKILL.md
installer/reposkillopt-install --agent codex    --dest .   #  .agents/skills/repo-skillopt/SKILL.md
installer/reposkillopt-install --agent opencode --dest .   #  .opencode/skills/repo-skillopt/SKILL.md
installer/reposkillopt-install --agent claude-code --dest . #  .claude/skills/repo-skillopt/SKILL.md (unchanged)
```

A pre-existing `AGENTS.md` in the repo is **never touched** by any of these.

## Legacy single-file AGENTS.md (opt-in, safe)

```sh
installer/reposkillopt-install --agent codex-agentsmd --dest .
#  if AGENTS.md exists and isn't ours -> refuses:
#  "refusing to overwrite existing AGENTS.md (not installed by RepoSkillOpt); use --force"
installer/reposkillopt-install --agent codex-agentsmd --dest . --force
#  -> backs up AGENTS.md -> AGENTS.md.bak, then writes
```

## List / uninstall

```sh
installer/reposkillopt-install --dest . --list
installer/reposkillopt-install --dest . --uninstall agents
#  -> removes .agents/skills/repo-skillopt/SKILL.md and the now-empty repo-skillopt/ dir
```

## Validate the feature

```sh
cd installer && sh tests/run.sh        # all green, incl. new skill-dir + AGENTS.md-safety tests
```

Acceptance signals:
- `test_skill_dir_targets`: each new target lands at its documented path; content is the canonical skill; installs offline.
- `test_agents_md_safety`: foreign `AGENTS.md` refused without `--force`; `--force` produces `AGENTS.md.bak`; a managed AGENTS.md upgrades in place.
- install → list → uninstall leaves the repo pristine (SC-004).
