# Optional helper scripts

Portable, dependency-free helpers (POSIX `sh` + `grep`/`sed`/`sort`/`find`/`git`). They are **outside
MVP acceptance** — the engine is the source of truth — but useful where Python isn't available.

## `coverage-gate.sh` — no-silent-omission verifier

Verifies that **every source component is "dealt with"** in an artifact — the zero-install
counterpart to the engine's symbol-accounting guarantee. It does not *generate* coverage, it
*verifies* it, so it drops into CI, a pre-commit hook, or a reviewer's box with no Python.

```sh
scripts/coverage-gate.sh <repo> <artifact-file-or-dir> [--files] [--max N]
```

A symbol (function/class) is covered if its **name** appears in the artifact, OR its **file path**
does (covering the "Symbols not yet analyzed" per-file listing) — the same definition the engine's
`compute_structure` symbol-coverage uses. `--files` checks file-level coverage instead. Prints
`covered/total (pct)` and exits **0** if everything is covered, **1** (listing the omissions) if
not, **2** on bad usage.

```sh
# CI / pre-commit example: fail if the spec silently drops any symbol
scripts/coverage-gate.sh . .reposkillopt/specs/repository-specification.md
```

Best-effort regex extraction (py/js/ts/go/rb/rs/java/kt/scala), matching `structure.py`'s posture;
common-name coincidences are a documented limitation (it is a lint, not a proof). Tests:
`sh scripts/tests/test_coverage_gate.sh` (passes under `sh` and `dash`).
