# Implementation Plan: One-Command CLI Installer

**Branch**: `002-cli-installer` | **Date**: 2026-05-31 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-cli-installer/spec.md`

## Summary

Add a dependency-free POSIX-shell installer that places the correct RepoSkillOpt adapter into a target repository with a single command — the CLI equivalent of the manual `mkdir`/`cp`/`grep` flow in the per-adapter READMEs. The tool ships in this repository as a clearly-marked optional top-level area, bundles the adapter files it installs (so installing into a target is fully offline), supports an ephemeral `curl … | sh` one-shot path and a persistent direct-invocation path, and exposes `install` / `list` / `uninstall` subcommands with harness auto-detection that errors (never guesses) when ambiguous. It never modifies the canonical skill and preserves vendor-neutrality (per the Clarifications and FR-016/FR-017).

## Technical Context

**Language/Version**: POSIX `sh` (portable shell; no Bash-only features required). Authored/tested under `bash` and `dash`.
**Primary Dependencies**: Standard POSIX command-line utilities only — `sh`, `cp`, `mkdir`, `rm`, `grep`, `sed`, `printf`, `find`. No language runtime, no package manager, no third-party libraries. `jq` is **not** required (manifest uses a line-based format).
**Storage**: Filesystem only. A per-target-repo **install manifest** at `<target>/.reposkillopt/.install-manifest` records what was installed (adapter, version, file paths, timestamp) to drive idempotency, list, upgrade, and uninstall.
**Testing**: Shell test scripts under `installer/tests/` runnable with plain POSIX `sh` (no framework dependency); `bats-core` MAY be used if present but is not required. Tests are optional tooling, consistent with the project's "tests not part of MVP acceptance" stance — each phase still ends with a manual validation checkpoint against the contracts.
**Target Platform**: POSIX shells on Linux and macOS; Windows via WSL or Git-Bash. No OS-specific code paths beyond standard utilities.
**Project Type**: Single-project CLI tool (no frontend/backend split).
**Performance Goals**: An install/list/uninstall completes in well under a second of wall-clock; SC-001 budget is < 1 minute of human time end-to-end.
**Constraints**: Offline-capable for the install step (adapters bundled); idempotent re-runs; atomic writes (target is left fully installed or unchanged — never half-written); no network except the optional one-shot fetch of the installer package; MUST NOT modify the canonical skill or any adapter source content.
**Scale/Scope**: Small and bounded — 4 adapter targets, 3 subcommands (`install`, `list`, `uninstall`), and a handful of flags (`--agent`, `--dest`, `--scaffold`, `--list`, `--uninstall`, `--force`, `--dry-run`).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status of the constitution**: `.specify/memory/constitution.md` is the unratified template (placeholder principles only). There are therefore no formally ratified gates to evaluate. In their place, this plan is gated against the project's established **non-negotiables** (from feature 001 / `CLAUDE.md`), which function as the de-facto constitution:

| Gate (project non-negotiable) | Verdict | Notes |
|---|---|---|
| **Vendor neutrality** of `skills/repo-skillopt/SKILL.md` (FR-002) | ✅ Pass | Installer copies adapter files verbatim; never edits the canonical skill or adapters. Mentions of specific harnesses live only in the target-registry data, which mirrors the existing per-adapter READMEs (non-normative). |
| **Adapter-equivalence integrity** (FR-024/025) | ✅ Pass | Installer is a *transport*; it does not transform adapter content, so equivalence is untouched. A deterministic check verifies installed bytes equal source bytes. |
| **Skill-first scope** — helper scripts optional & outside acceptance (FR-033) | ✅ Pass (justified) | This feature deliberately adds the project's first executable tool. It is explicitly **optional** (manual README install remains valid), shipped in a clearly-marked top-level area, and not a precondition for the skill's use (FR-017). The user explicitly requested it. |
| **No SaaS / DB / frontend / fine-tune** | ✅ Pass | Pure POSIX shell over the local filesystem. No service, no database, no UI. |
| **Working artifacts under target `.reposkillopt/`** (FR-036a) | ✅ Pass | The install manifest lives at `<target>/.reposkillopt/.install-manifest`; no installer state is written into this project. |
| **R10 label discipline** | N/A | Applies to Repository Specifications, not to tool code. |

No violations requiring Complexity Tracking. Re-checked after Phase 1 — see "Post-Design Constitution Re-Check" below.

## Project Structure

### Documentation (this feature)

```text
specs/002-cli-installer/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── cli-interface.contract.md
│   ├── target-registry.contract.md
│   └── install-manifest.contract.md
└── tasks.md             # Phase 2 output (/speckit.tasks — NOT created here)
```

### Source Code (repository root)

```text
install.sh                       # Thin bootstrap entrypoint (the curl|sh target). Resolves
                                 # its own location → repo root, then execs installer/reposkillopt-install.

installer/                       # Optional tooling area (NEW top-level), versioned with the adapters.
├── reposkillopt-install         # Main POSIX-sh CLI: argument parsing + install/list/uninstall dispatch.
├── lib/
│   ├── targets.sh               # Target registry: harness → (source files, install location, detection signal).
│   ├── detect.sh                # Best-effort harness detection from target-repo signals.
│   ├── manifest.sh              # Read/write/compare the target-repo install manifest.
│   └── util.sh                  # Logging (stderr), atomic copy (temp+rename), version read, error/exit codes.
├── README.md                    # Tool usage, the one-liner, supported targets, "optional tooling" note.
└── tests/
    ├── run.sh                   # POSIX test runner (no framework required).
    ├── test_install.sh          # install: each target, idempotency, atomicity, version match.
    ├── test_detect.sh           # detection: single signal, ambiguous → error, none → error.
    ├── test_manifest.sh         # list/uninstall: exact-file removal, manifest integrity.
    └── fixtures/                # Throwaway target-repo skeletons used by the tests.

adapters/                        # EXISTING — the bundled source of truth the installer copies from.
README.md                        # EXISTING — add an "Install (CLI)" section pointing at the one-liner.
```

**Structure Decision**: Single-project CLI. The installer is a new, self-contained top-level area (`install.sh` + `installer/`) that reads adapter files from the existing `adapters/` tree (that *is* the bundling — the one-shot path ships the repo/tarball, so `adapters/` travels with the tool). No changes to `skills/`, `templates/`, `rubric/`, `examples/`, or `specs/`. The only edit to an existing file is a new "Install (CLI)" section in the top-level `README.md`.

## Complexity Tracking

> No constitution violations to justify. Section intentionally empty.

## Post-Design Constitution Re-Check

Re-evaluated after Phase 1 (data-model, contracts, quickstart):

- The contracts confirm the installer only **reads** `adapters/` and **writes** to the target repo (adapter files + `<target>/.reposkillopt/.install-manifest`). No write path touches `skills/`, `adapters/`, or any canonical artifact → vendor-neutrality and adapter-equivalence gates still pass.
- The `install-manifest` lives under the target's `.reposkillopt/` → target-artifact-layout gate still passes.
- No new external dependency, service, or storage engine introduced → scope gate still passes.

No new violations. Ready for `/speckit.tasks`.
