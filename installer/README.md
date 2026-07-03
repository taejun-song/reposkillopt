# RepoSkillOpt CLI Installer

A dependency-free POSIX-shell tool that installs a RepoSkillOpt adapter into a target
repository with one command. It is **optional tooling** — the manual install steps in each
`adapters/<id>/README.md` remain fully valid.

## Quick install (one-liner)

From inside your target repository:

```sh
curl -fsSL https://raw.githubusercontent.com/taejun-song/reposkillopt/main/install.sh | sh -s -- --agent claude-code
```

> `curl … | sh` runs code from the network. If you prefer to audit first, use the
> clone-then-run path below — the install logic is identical.

## Clone, then run (audit-friendly, offline)

```sh
git clone https://github.com/taejun-song/reposkillopt.git
cd /path/to/your/target-repo
/path/to/reposkillopt/installer/reposkillopt-install --agent claude-code
```

## Usage

```text
reposkillopt-install [install] [--agent <id>] [--dest <dir>] [--scaffold] [--force] [--dry-run]
reposkillopt-install --hook [--dest <dir>]
reposkillopt-install --list [--dest <dir>]
reposkillopt-install --uninstall <id|git-hook> [--dest <dir>]
reposkillopt-install --help | --version
```

| Flag | Meaning |
|---|---|
| `--agent <id>` | Target harness: `claude-code`, `codex`, `opencode`, `generic`. Auto-detected if omitted. |
| `--dest <dir>` | Target repo root (default: current dir). **Required** for `generic` (where its two files go). |
| `--scaffold` | Also create `.reposkillopt/{specs,feedback,rollouts,proposals}/` in the target. |
| `--force` | Permit overwrite / downgrade. |
| `--dry-run` | Print intended actions; write nothing. |
| `--hook` | Install the commit-time gate **pre-commit hook** (feature 021). |
| `--list` | List adapters recorded in the target manifest (incl. `git-hook`). |
| `--uninstall <id>` | Remove a previously installed adapter (exact files only); `git-hook` removes the hook. |

### `--hook` — commit-time gate enforcement

`--hook` installs a portable POSIX-`sh` `pre-commit` hook that gates staged `.reposkillopt/`
artifacts and auto-remediates them until they pass (via `reposkillopt-engine gate-commit`). It is
installed into the repo's hooks dir (honoring `core.hooksPath`) and recorded as the `git-hook`
adapter in the manifest, so `--list` shows it and `--uninstall git-hook` removes it.

- **Chains, never clobbers.** A pre-existing `pre-commit` hook is moved to
  `pre-commit.reposkillopt-chained` and run first; its non-zero exit still blocks the commit.
  `--uninstall git-hook` restores it byte-for-byte. Re-installing does not double-chain.
- **Never traps you.** If no keyless provider (or the engine) is reachable, the hook **blocks and
  reports** rather than hanging. Bypass deliberately with `REPOSKILLOPT_HOOK=off git commit ...` or
  git's native `git commit --no-verify`.
- **Not a git repo?** `--hook` warns and skips cleanly (exit 0).

Requires `python3` + the `reposkillopt_engine` package importable at commit time (override the
invocation with `REPOSKILLOPT_ENGINE_CMD`, the provider with `REPOSKILLOPT_PROVIDER`).

## Supported targets

| id | installs to |
|---|---|
| `claude-code` | `<dest>/.claude/skills/repo-skillopt/SKILL.md` |
| `codex` | `<dest>/AGENTS.md` |
| `opencode` | `<dest>/AGENTS.md` |
| `generic` | `<dest>/skill.md` + `<dest>/system-prompt-fragment.md` (requires `--dest`) |

`codex` and `opencode` both use `AGENTS.md`, so they cannot be auto-distinguished — name one
explicitly. When no `--agent` is given and detection is ambiguous or empty, the tool exits
non-zero listing the valid targets and installs nothing (it never guesses).

## Exit codes

`0` ok / already-up-to-date · `1` error · `2` usage · `3` ambiguous/undetected target ·
`4` target not writable · `5` refused downgrade (use `--force`).

## Tests

```sh
installer/tests/run.sh
```

Plain POSIX-`sh` tests; no framework required.

## Known cross-agent differences

None recorded yet. Add observations here as they surface in real use.
