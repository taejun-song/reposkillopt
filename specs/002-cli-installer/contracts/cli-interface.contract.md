# Contract — CLI Interface (`installer/reposkillopt-install`)

**Scope**: The command-line surface of the installer — subcommands, flags, output discipline, and exit codes (FR-001…FR-013).
**Consumers**: Users invoking the tool; CI pipelines scripting it; the test suite.

## Invocation

```text
reposkillopt-install [install] [--agent <id>] [--dest <dir>] [--scaffold] [--force] [--dry-run]
reposkillopt-install --list [--dest <dir>]
reposkillopt-install --uninstall <id> [--dest <dir>]
reposkillopt-install --help | --version
```

Also reachable via the one-liner bootstrap: `curl -fsSL <url>/install.sh | sh -s -- <same args>`.

## Flags

| Flag | Arg | Meaning | Default |
|---|---|---|---|
| `--agent` | `<id>` | Target harness: `claude-code`/`codex`/`opencode`/`generic` | auto-detect |
| `--dest` | `<dir>` | Target repo root (for `generic`, the destination dir for the two files) | current directory |
| `--scaffold` | — | Also create `<dest>/.reposkillopt/{specs,feedback,rollouts,proposals}/` | off |
| `--force` | — | Permit overwrite/downgrade | off |
| `--dry-run` | — | Print intended actions; write nothing | off |
| `--list` | — | List adapters recorded in the target manifest | — |
| `--uninstall` | `<id>` | Remove a previously installed adapter | — |
| `--help` / `-h` | — | Usage to stdout, exit 0 | — |
| `--version` | — | Tool version to stdout, exit 0 | — |

## Behavior requirements

1. **Default subcommand** is `install` (FR-001).
2. `--agent` is validated against the four target ids; an unknown id → exit 2 with the valid list (FR-002, FR-004).
3. With no `--agent`, detection runs; **0 or ≥2** candidate targets → exit 3 listing valid targets, **no writes** (FR-005, SC-004).
4. `generic` requires `--dest`; absent → exit 2 with guidance (R6).
5. Install is **atomic** (temp+rename) and **idempotent**; re-installing the same version is a no-op printing "already up to date" (FR-007, FR-010).
6. Installing a **newer** version over an older one updates files + manifest and reports the delta; an **older** version without `--force` → exit 5, unchanged (FR-011).
7. On success, **stdout** prints a summary including the installed path(s) and `canonical_version`, plus the activation next-step; the version line alone lets the user verify the match (FR-009, SC-006).
8. All diagnostics/errors go to **stderr**; stdout carries only the user-facing result.
9. `--dry-run` performs all checks and prints the actions it *would* take but writes nothing (verifiable by an unchanged target).
10. `--list` prints one line per manifest record (`adapter version path[,path] installed_at`); empty/absent manifest → "no adapters installed", exit 0.
11. `--uninstall <id>` removes exactly the files in that record plus the record; nothing else is touched; unknown id in manifest → exit 0 with a "not installed" note (FR-013, SC-007).
12. The tool never writes outside `<dest>` and never modifies files under this project's `skills/` or `adapters/` (FR-016, SC-008).

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success, or already-up-to-date, or informational (`--help`/`--version`/empty `--list`) |
| 1 | Generic/unexpected error |
| 2 | Usage error (unknown flag or `--agent`; `generic` without `--dest`) |
| 3 | Ambiguous or undetected target and no `--agent` given |
| 4 | Target not found or not writable |
| 5 | Refused downgrade without `--force` |

## Acceptance checklist

- [ ] Default (no subcommand) performs an install.
- [ ] Each of the four `--agent` values installs to the documented location.
- [ ] Unknown `--agent` → exit 2 with valid-target list.
- [ ] No `--agent`, single signal → installs the detected target.
- [ ] No `--agent`, zero or conflicting signals → exit 3, no writes.
- [ ] `generic` without `--dest` → exit 2.
- [ ] Re-install same version → exit 0, "already up to date", no file churn.
- [ ] Older version without `--force` → exit 5, unchanged; with `--force` → downgrade recorded.
- [ ] Success summary prints install path + `canonical_version` on stdout; errors on stderr.
- [ ] `--dry-run` leaves the target byte-for-byte unchanged.
- [ ] `--list` / `--uninstall` behave per rows 10–11; uninstall removes exactly the recorded files.
