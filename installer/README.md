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
reposkillopt-install --list [--dest <dir>]
reposkillopt-install --uninstall <id> [--dest <dir>]
reposkillopt-install --help | --version
```

| Flag | Meaning |
|---|---|
| `--agent <id>` | Target harness: `claude-code`, `codex`, `opencode`, `generic`. Auto-detected if omitted. |
| `--dest <dir>` | Target repo root (default: current dir). **Required** for `generic` (where its two files go). |
| `--scaffold` | Also create `.reposkillopt/{specs,feedback,rollouts,proposals}/` in the target. |
| `--force` | Permit overwrite / downgrade. |
| `--dry-run` | Print intended actions; write nothing. |
| `--list` | List adapters recorded in the target manifest. |
| `--uninstall <id>` | Remove a previously installed adapter (exact files only). |

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
