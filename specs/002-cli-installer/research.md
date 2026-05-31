# Phase 0 Research — One-Command CLI Installer

All four top-level unknowns were resolved during `/speckit.clarify` (see `spec.md` → *Clarifications*). This document records the **remaining design decisions** needed before task generation. Each entry: Decision / Rationale / Alternatives considered.

## R1 — Distribution & runtime (confirmed from Clarifications)

- **Decision**: Dependency-free POSIX `sh`. A thin `install.sh` bootstrap at the repo root is the `curl … | sh` target; it resolves the repo root and execs `installer/reposkillopt-install`. A persistent path is "clone/download, then run `installer/reposkillopt-install` directly".
- **Rationale**: Adapters are just files to copy; a shell tool needs no runtime, matching the Markdown-first, zero-dependency ethos and the project's POSIX-sh tooling convention. The one-liner reproduces spec-kit's "no local install needed" feel.
- **Alternatives**: Python/uvx (closest to spec-kit, but adds a runtime for a file-copy task); Node/npx; prebuilt Go/Rust binary (adds a release pipeline). All rejected as heavier than the task warrants.

## R2 — Adapter source = bundled (confirmed from Clarifications)

- **Decision**: The installer copies adapter files from the **in-repo `adapters/` tree**, which travels with the tool. The `curl|sh` one-shot path fetches a repo tarball (so `adapters/` is present); the persistent path already has it. No run-time download of individual adapter files.
- **Rationale**: Self-contained, version-pinned, offline after the single package fetch. Avoids drift between "what the tool installs" and "what the repo ships".
- **Alternatives**: Fetch adapters from GitHub at install time (needs network, can drift); duplicate adapter copies inside `installer/` (duplication/maintenance hazard). Rejected.

## R3 — Install-manifest format & location

- **Decision**: One manifest per target repo at `<target>/.reposkillopt/.install-manifest`. Line-based, one record per installed adapter:
  `adapter<TAB>canonical_version<TAB>comma_separated_relative_paths<TAB>iso8601_timestamp`.
  Parsed with `grep`/`cut`/`while read` — **no `jq`**.
- **Rationale**: Drives idempotency (re-install updates the row in place), `list` (print rows), `upgrade` (compare versions), and `uninstall` (remove exactly the listed paths). A flat line format is the most portable choice with no dependency. Lives under `.reposkillopt/` to satisfy the target-artifact-layout rule and to be naturally covered by the existing `.gitignore` of working artifacts.
- **Alternatives**: JSON manifest (needs `jq` or fragile shell parsing); no manifest / re-derive from filesystem (can't reliably know which files the tool placed vs. the user authored → unsafe uninstall). Rejected.

## R4 — Atomicity & idempotency

- **Decision**: Write each adapter file to a temp path in the **same directory** then `mv` into place (atomic rename on POSIX). The manifest is updated only after all of a target's files are in place. A run either completes fully or leaves the target unchanged; on any mid-run error the tool removes temp files and exits non-zero without touching the manifest. Re-installing the same version is a no-op that reports "already up to date"; re-installing a different version overwrites and updates the manifest row.
- **Rationale**: Satisfies FR-007 (idempotent) and FR-010 (no partial writes) with standard tools.
- **Alternatives**: In-place overwrite (risks half-written files on interruption). Rejected.

## R5 — Harness detection signals (best-effort; defers to explicit choice)

- **Decision**: Detection maps observable target-repo signals to a target:
  - `claude-code` ← a `.claude/` directory exists.
  - `codex` / `opencode` ← a root `AGENTS.md` exists — **but both share this file**, so a bare `AGENTS.md` is *ambiguous* and resolves to the "ambiguous" outcome, not a guess.
  - `generic` ← never auto-detected (no canonical location).
  When 0 or ≥2 candidate targets remain and no `--agent` was given, the tool **exits non-zero listing valid targets** (FR-005 / SC-004). Detection is only a convenience over an explicit `--agent`.
- **Rationale**: The single unambiguous case (`.claude/`) is worth automating; everything else is safer as an explicit choice than a wrong install location.
- **Alternatives**: Heuristics to disambiguate Codex vs OpenCode (e.g., marker comments) — brittle and out of scope; defaulting to one — violates "never guess". Rejected.

## R6 — Generic target handling

- **Decision**: The `generic` target has no canonical install location and ships two files (`skill.md` + `system-prompt-fragment.md`). It therefore **requires `--dest <dir>`**; the tool copies both files there and records both paths in the manifest. Without `--dest`, `--agent generic` errors with guidance.
- **Rationale**: Honors the per-adapter README ("per harness convention") while keeping installs explicit and uninstall exact.
- **Alternatives**: Invent a default generic location (e.g., `.reposkillopt/skill/`) — presumptuous; install only one of the two files — breaks the adapter. Rejected.

## R7 — CLI surface & exit codes

- **Decision**:
  - Subcommands/flags: `install` (default), `--agent <claude-code|codex|opencode|generic>`, `--dest <dir>` (target repo root or, for generic, the file destination), `--scaffold` (create `.reposkillopt/{specs,feedback,rollouts,proposals}/`), `--force` (allow downgrade/overwrite), `--dry-run` (print actions, write nothing), `--list`, `--uninstall <agent>`, `-h/--help`, `--version`.
  - Exit codes: `0` success / already-up-to-date; `1` generic error; `2` usage error (unknown flag/agent); `3` ambiguous-or-undetected target with no `--agent`; `4` target not writable / not found; `5` refused downgrade without `--force`.
  - Output discipline: human-readable summary to **stdout**; diagnostics/errors to **stderr**; the success summary always prints the installed path and `canonical_version` so the user can verify the match from output alone (SC-006).
- **Rationale**: Distinct exit codes make the tool scriptable/CI-friendly and make the test contract crisp.
- **Alternatives**: Single nonzero code for all failures (harder to test/script). Rejected.

## R8 — Version verification

- **Decision**: The tool reads the canonical `version:` from `skills/repo-skillopt/SKILL.md` and the adapter's `canonical_version` from the source adapter file (YAML front matter or the HTML-comment metadata block, depending on target). On install it records the version in the manifest and prints it; on upgrade it compares the manifest version to the source version and reports the delta; it refuses to write an older version over a newer one unless `--force`.
- **Rationale**: Implements FR-006/FR-011 and gives the user the SC-006 self-check from output.
- **Alternatives**: Trust filenames / skip verification. Rejected (defeats the version-sync purpose).

## R9 — Testing approach

- **Decision**: Plain POSIX `sh` test scripts under `installer/tests/`, driven by `installer/tests/run.sh`, operating on throwaway fixture directories under a temp dir. They assert: correct placement per target, byte-equality of installed vs source files, idempotent re-run, atomic no-partial-write on induced failure, ambiguous/undetected → exit 3, list/uninstall exactness, and `--dry-run` writes nothing. `bats-core` is used opportunistically if present, but the suite must pass with `sh` alone.
- **Rationale**: Keeps tests dependency-free and aligned with the project's "no required test framework" stance, while still giving each phase a runnable checkpoint.
- **Alternatives**: Require `bats` (adds a dependency); no tests (this is now executable code that can silently corrupt a user's repo — unacceptable). Rejected.

## R10 — One-liner bootstrap safety

- **Decision**: The `curl|sh` one-liner downloads a pinned tarball/ref of the repo to a temp dir and runs `installer/reposkillopt-install` from there; it passes user arguments through. The README documents inspecting the script before piping to `sh` and offers the clone-then-run path as the audit-friendly alternative.
- **Rationale**: Matches the expected "easy install" UX while being honest about `curl|sh` trust, and keeps the install logic identical on both paths.
- **Alternatives**: Only a one-liner (no auditable path); only clone-then-run (loses the "easy" feel). Both rejected in favor of offering both.

## Open questions

None blocking. New adapters become installable by adding a row to the target registry (`installer/lib/targets.sh`) — no architectural change required.
