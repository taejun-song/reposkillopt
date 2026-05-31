# Quickstart — RepoSkillOpt CLI Installer

**Audience**: An engineer who wants to drop a RepoSkillOpt adapter into a target repository with one command, instead of the manual `mkdir`/`cp`/`grep` flow.

**Estimated time**: < 1 minute (SC-001).

> This describes the *planned* installer for feature `002-cli-installer`. It is **optional tooling** — the manual install in each `adapters/<id>/README.md` remains fully valid.

## Prerequisites

- A POSIX shell (`sh`/`bash`/`dash`) and standard utilities (`cp`, `mkdir`, `grep`). No language runtime.
- The RepoSkillOpt repo available — either cloned locally, or fetched on the fly by the one-liner.

## Path A — Ephemeral one-liner (no persistent install)

From inside your target repository:

```sh
curl -fsSL https://raw.githubusercontent.com/taejun-song/reposkillopt/main/install.sh | sh -s -- --agent claude-code
```

This fetches the bundled installer, copies the Claude Code adapter to `.claude/skills/repo-skillopt/SKILL.md`, writes the install manifest, and prints a summary with the installed `canonical_version`.

## Path B — Clone, then run (audit-friendly, fully offline after clone)

```sh
git clone https://github.com/taejun-song/reposkillopt.git
cd /path/to/your/target-repo
/path/to/reposkillopt/installer/reposkillopt-install --agent claude-code
```

## Common commands

```sh
# Auto-detect the harness (works when exactly one signal is present, e.g. a .claude/ dir):
reposkillopt-install

# Install for a specific harness and also scaffold the working-artifact dirs:
reposkillopt-install --agent codex --scaffold

# Generic harness requires an explicit destination for its two files:
reposkillopt-install --agent generic --dest docs/agent

# Preview without writing anything:
reposkillopt-install --agent claude-code --dry-run

# See what is installed in this repo:
reposkillopt-install --list

# Remove a previously installed adapter (exact files only):
reposkillopt-install --uninstall claude-code
```

## Verify the install

```sh
# The installer already prints the version; you can re-confirm the match:
grep '^version:' /path/to/reposkillopt/skills/repo-skillopt/SKILL.md
grep -E '^(canonical_version:|canonical_version)' .claude/skills/repo-skillopt/SKILL.md
# Both should show the same semver.

reposkillopt-install --list
# → claude-code  0.1.0  .claude/skills/repo-skillopt/SKILL.md  <timestamp>
```

## What to expect at the boundaries

- **No harness named and none (or more than one) detected** → the tool exits non-zero and lists the valid targets; it installs nothing. Re-run with `--agent <id>`.
- **`codex` vs `opencode`** both use a root `AGENTS.md`, so a bare `AGENTS.md` can't be auto-resolved — name the target explicitly.
- **Re-running** the same install is safe: same version → "already up to date"; newer version → upgrade with a reported delta; older version → refused unless `--force`.
- **Interruption** leaves the target either fully installed or unchanged — never half-written.

## After installing

Open your agent in the target repo and prompt: *"Help me understand this repository."* The skill activates and writes a Repository Specification under `<target>/.reposkillopt/specs/`. See the top-level `README.md` and `specs/001-reposkillopt-skill/quickstart.md` for the full skill walkthrough.
