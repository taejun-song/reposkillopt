# Contract: pre-commit hook + installer lifecycle

A portable POSIX-`sh` `pre-commit` hook (no Bash-only features) installed by the existing CLI
installer. The hook is thin: detect → honor bypass → chain → delegate to `gate-commit`.

## Hook behavior (`installer/hooks/pre-commit`)

On each commit, in order:

1. **Chain first (D6)** — if a chained backup is recorded/present, run it preserving exit status:
   `sh "$CHAINED" "$@"; rc=$?; [ "$rc" -ne 0 ] && exit "$rc"`. The pre-existing hook still blocks
   the commit on its own failure (FR-012).
2. **Bypass (FR-011)** — if `REPOSKILLOPT_HOOK=off`, exit 0 immediately (no-op). (git's native
   `--no-verify` skips the hook entirely, before this runs.)
3. **Detect (FR-001)** — `git diff --cached --name-only --diff-filter=ACM` filtered to `.reposkillopt/`.
   If empty → exit 0 (source-only commits untouched; SC-002). No model call, no gate run.
4. **Delegate** — invoke the engine:
   `python3 -m reposkillopt_engine gate-commit --repo "$ROOT" --staged <files…>` (provider `auto`).
   Propagate its exit code (0 → commit proceeds; non-zero → commit blocked).
5. **Engine unreachable (D4)** — if `python3` or the engine package is not importable, print a
   block-and-report message (optionally run the dependency-free `scripts/coverage-gate.sh` if present)
   plus bypass instructions, and exit non-zero. Never hang.

The hook prints, on any block, exactly how to bypass: `REPOSKILLOPT_HOOK=off git commit …` or
`git commit --no-verify`.

## Installer lifecycle (`installer/lib/hook.sh` + `reposkillopt-install`)

```
reposkillopt-install --hook [--dest <dir>]        # install the pre-commit hook into <dest>'s git repo
reposkillopt-install --list  [--dest <dir>]        # shows the git-hook row if installed
reposkillopt-install --uninstall git-hook [--dest <dir>]   # remove hook, restore any chained backup
```

- **Install** — resolve the hooks dir via `git rev-parse --git-path hooks`. If a `pre-commit` already
  exists, `copy_atomic` it to `pre-commit.reposkillopt-chained` (the recorded backup). Install the hook
  (executable). Record `manifest_upsert(target, "git-hook", <version>, "<hook_path>[,<backup_path>]")`.
  Not a git repo → warn and skip (graceful, like the rest of the installer).
- **List** — `manifest_list` shows `git-hook <version> <paths> <timestamp>`.
- **Uninstall** — read the row; remove the installed hook; if a backup path is recorded, restore it to
  `pre-commit` (exact bytes); `manifest_remove_row(target, "git-hook")`. Result: repo is back to its
  prior hook state (FR-013/SC-006/SC-007).
- **Idempotency / re-install** — installing when already installed updates the row (and does not
  double-chain: if the current `pre-commit` is our hook, the existing recorded backup is preserved).

## Portability & test contract

- Hook and `hook.sh` use only POSIX `sh`; tests (`installer/tests/test_hook.sh`) pass under **`bash`
  and `dash`**.
- Tested deterministic behaviors: detect-filters-to-`.reposkillopt`, bypass env no-op, chained hook
  runs + its non-zero blocks, manifest row written on install, uninstall removes hook **and** restores
  the chained backup exactly, re-install does not double-chain. (The live model remediation is covered
  by the engine quickstart run, not the shell tests.)
