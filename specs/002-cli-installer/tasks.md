---
description: "Task list for the RepoSkillOpt one-command CLI installer"
---

# Tasks: One-Command CLI Installer

**Input**: Design documents in `/home/deploy/workspace/reposkillopt/specs/002-cli-installer/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/` (all present).

**Tests**: Test tasks ARE included. This feature ships executable code that writes into a user's repository (research R9: skipping tests is unacceptable here). Tests are POSIX-`sh` scripts under `installer/tests/`, runnable with no framework; each phase still ends with a manual validation checkpoint against the contracts.

**Organization**: Tasks are grouped by user story (US1–US6) so each can be implemented and tested independently.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependency on an incomplete task).
- **[Story]**: User-story label (US1–US6). Setup, Foundational, and Polish carry no story label.
- Every task includes an exact file path.

## Path conventions

All paths are relative to the repository root (`/home/deploy/workspace/reposkillopt/`) and follow `plan.md` → *Project Structure → Source Code*. The installer is a new top-level area (`install.sh` + `installer/`); it reads from the existing `adapters/` tree and writes only into a target repo.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Bring the installer skeleton into existence.

- [X] T001 Create the installer directory layout — `installer/`, `installer/lib/`, `installer/tests/`, `installer/tests/fixtures/` — with empty placeholder files (`installer/reposkillopt-install`, `installer/lib/{util,targets,detect,manifest}.sh`) per `plan.md` Project Structure
- [X] T002 [P] Create `installer/README.md` scaffold — tool purpose, the (placeholder) one-liner, supported targets, and the "optional tooling — manual README install remains valid" note (FR-017)
- [X] T003 [P] Create `installer/tests/run.sh` — POSIX test runner that discovers `installer/tests/test_*.sh`, runs each in an isolated temp workspace, and prints a pass/fail tally with a non-zero exit on any failure

**Checkpoint**: Directory tree and runnable (empty) test harness exist.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The shared plumbing every subcommand routes through. **No user story can begin until this is complete.**

**⚠️ CRITICAL**: Blocks all user stories.

- [X] T004 Implement `installer/lib/util.sh` — stderr logging helpers, exit-code constants (0–5 per `contracts/cli-interface.contract.md`), atomic write (`copy_atomic`: temp file in dest dir + `mv`), a `DRY_RUN`-aware write wrapper, `read_version` helpers for both `yaml-frontmatter` and `html-comment` metadata kinds, a semver-compare helper, and a UTC ISO-8601 timestamp helper
- [X] T005 [P] Implement `installer/lib/targets.sh` — the four-target registry (`source_files`, `install_location`, `detection_signal`, `metadata_kind`) exactly per `contracts/target-registry.contract.md`, with accessor functions and a validated id list
- [X] T006 Implement `installer/reposkillopt-install` CLI skeleton — source `util.sh` + `targets.sh`; parse all flags (`--agent`, `--dest`, `--scaffold`, `--force`, `--dry-run`, `--list`, `--uninstall`, `--help/-h`, `--version`); dispatch (default `install`, `--list`, `--uninstall`); `--help`/`--version` to stdout (exit 0); unknown flag/agent → usage error exit 2 (depends on T004, T005)

**Checkpoint**: `reposkillopt-install --help`, `--version`, and unknown-flag handling work; library functions are unit-callable.

---

## Phase 3: User Story 1 — Install an adapter with one command (Priority: P1) 🎯 MVP

**Goal**: From a target repo, `reposkillopt-install --agent <id>` places the correct adapter at its documented location, writes the manifest, verifies the version, and prints a summary — in one invocation.

**Independent Test**: In a clean fixture repo, run `reposkillopt-install --agent claude-code`; confirm the file lands at `.claude/skills/repo-skillopt/SKILL.md`, the summary prints the path and `canonical_version`, exit is 0, and a second run reports "already up to date".

### Tests for User Story 1

- [X] T007 [P] [US1] Write `installer/tests/test_install.sh` — for each of `claude-code`/`codex`/`opencode`/`generic` (the last with `--dest`): installs to the documented location, installed bytes equal source, summary prints path + `canonical_version` on stdout; plus `--dry-run` writes nothing, unknown `--agent` → exit 2, `generic` without `--dest` → exit 2, re-install same version → exit 0 no file churn

### Implementation for User Story 1

- [X] T008 [US1] Implement `installer/lib/manifest.sh` (create/read/upsert) — resolve `<dest>/.reposkillopt/.install-manifest`, read records, upsert (replace-or-append, atomic temp+rename) per `contracts/install-manifest.contract.md`
- [X] T009 [US1] Implement the install flow in `installer/reposkillopt-install` — require/resolve target, verify `<dest>` exists and is writable (else exit 4), read canonical version (`skills/repo-skillopt/SKILL.md`) and the source adapter's `canonical_version`, atomically place the file(s), upsert the manifest, and print the success summary (path + version + activation next step) (depends on T008)
- [X] T010 [US1] Implement idempotency and dry-run in the install flow in `installer/reposkillopt-install` — same recorded version → "already up to date" no-op; `--dry-run` performs all checks but writes nothing (depends on T009)
- [X] T011 [US1] Implement `generic`-target handling in the install flow — require `--dest`, place both `skill.md` and `system-prompt-fragment.md`, and record both paths in the manifest (depends on T009)
- [X] T012 [US1] **Validation checkpoint** — run `installer/tests/test_install.sh` and `contracts/cli-interface.contract.md` rows 1–9 against the install flow; fix failures

**Checkpoint**: MVP — single-command explicit install works for all four adapters and is idempotent.

---

## Phase 4: User Story 2 — Detect the harness (Priority: P2)

**Goal**: With no `--agent`, the installer detects the target from repo signals; ambiguous or absent → exit 3 listing valid targets (never guesses).

**Independent Test**: In a repo containing only `.claude/`, run with no `--agent` → installs claude-code. In a repo with a bare `AGENTS.md` (codex+opencode) or no signal → exit 3, nothing written.

### Tests for User Story 2

- [X] T013 [P] [US2] Write `installer/tests/test_detect.sh` — single signal (`.claude/`) → installs claude-code; bare `AGENTS.md` → exit 3 no writes; no signal → exit 3 no writes; valid-target list printed to stderr

### Implementation for User Story 2

- [X] T014 [US2] Implement `installer/lib/detect.sh` — evaluate each target's `detection_signal` over `<dest>` and return the candidate set (codex+opencode both match `AGENTS.md`; generic never matches) (depends on T005)
- [X] T015 [US2] Wire detection into the install flow in `installer/reposkillopt-install` — when no `--agent`, call detect; exactly 1 candidate → use it; 0 or ≥2 → exit 3 listing valid targets with no writes (depends on T014, T009)
- [X] T016 [US2] **Validation checkpoint** — run `installer/tests/test_detect.sh` and `contracts/cli-interface.contract.md` row 3; confirm SC-004 (zero silent mis-installs)

**Checkpoint**: Detection works for the single unambiguous case and safely errors otherwise.

---

## Phase 5: User Story 3 — Scaffold the working-artifact layout (Priority: P2)

**Goal**: `--scaffold` creates `<dest>/.reposkillopt/{specs,feedback,rollouts,proposals}/` without overwriting existing artifacts.

**Independent Test**: On a repo without `.reposkillopt/`, run install `--scaffold` → the four subdirs exist; re-run with existing artifacts present → they are untouched.

### Tests for User Story 3

- [X] T017 [P] [US3] Write `installer/tests/test_scaffold.sh` — `--scaffold` creates the four subdirs; pre-existing files are preserved; re-run is idempotent; `--dry-run` creates nothing

### Implementation for User Story 3

- [X] T018 [US3] Implement `--scaffold` in the install flow in `installer/reposkillopt-install` — create the four `.reposkillopt/` subdirs under `<dest>` if absent, never overwriting; honor `--dry-run` (depends on T009)
- [X] T019 [US3] **Validation checkpoint** — run `installer/tests/test_scaffold.sh`; confirm FR-008 (no overwrite of existing artifacts)

**Checkpoint**: Scaffolding is available and safe.

---

## Phase 6: User Story 4 — Verify version and upgrade (Priority: P2)

**Goal**: Recognize an existing install, compare versions, upgrade with a reported delta, and refuse to silently downgrade (exit 5 unless `--force`).

**Independent Test**: Install an older version, run a newer installer → upgrade + delta reported; run again → "already up to date"; force an older source over a newer install without `--force` → exit 5 unchanged; with `--force` → downgrade recorded.

### Tests for User Story 4

- [X] T020 [P] [US4] Write `installer/tests/test_upgrade.sh` — older→newer upgrades and reports the delta; equal → up to date; newer-installed + older-source without `--force` → exit 5 unchanged; with `--force` → downgrade recorded

### Implementation for User Story 4

- [X] T021 [US4] Implement version comparison and upgrade/downgrade handling in `installer/reposkillopt-install` (using the semver helper in `installer/lib/util.sh` and the manifest version) — report the version delta on upgrade; refuse downgrade with exit 5 unless `--force` (depends on T009, T008)
- [X] T022 [US4] **Validation checkpoint** — run `installer/tests/test_upgrade.sh`; confirm FR-011 and exit-code 5 behavior

**Checkpoint**: Adapters can be kept in sync with the canonical version safely.

---

## Phase 7: User Story 5 — Run without a persistent install (Priority: P3)

**Goal**: A `curl … | sh` one-liner installs an adapter in one shot; the install logic is identical to the persistent path.

**Independent Test**: From an arbitrary working directory, run `install.sh` (piped) → an adapter is installed into the target repo; arguments pass through.

### Tests for User Story 5

- [X] T023 [P] [US5] Write `installer/tests/test_bootstrap.sh` — running `install.sh` from an arbitrary CWD installs correctly and passes args through; the fetch path is simulated with a local tarball fixture (no live network in tests)

### Implementation for User Story 5

- [X] T024 [US5] Implement `install.sh` bootstrap at the repo root — resolve its own location → repo root and `exec installer/reposkillopt-install "$@"`; support `sh -s -- <args>` piping; when run as a fetched one-shot, unpack to a temp dir and run from there (depends on T006)
- [X] T025 [US5] Update `installer/README.md` and the top-level `README.md` with the `curl … | sh` one-liner and the audit-friendly clone-then-run path, including the trust note from research R10 (depends on T024)
- [X] T026 [US5] **Validation checkpoint** — run `installer/tests/test_bootstrap.sh`; confirm SC-005 (single one-shot command, no required persistent footprint)

**Checkpoint**: The "easy install" one-liner works end-to-end.

---

## Phase 8: User Story 6 — List and uninstall (Priority: P3)

**Goal**: `--list` shows installed adapters; `--uninstall <id>` removes exactly the recorded files and the manifest row, nothing else.

**Independent Test**: Install an adapter, `--list` shows it; `--uninstall` removes only its file(s) and row while unrelated repo files remain.

### Tests for User Story 6

- [X] T027 [P] [US6] Write `installer/tests/test_manifest_ops.sh` — `--list` prints rows / "no adapters installed"; `--uninstall` removes exactly the recorded paths + row; unrelated files untouched; removing the last row leaves a valid/empty manifest

### Implementation for User Story 6

- [X] T028 [US6] Implement `--list` in `installer/lib/manifest.sh` + `installer/reposkillopt-install` — print one human-readable line per record; empty/absent manifest → "no adapters installed", exit 0 (depends on T008)
- [X] T029 [US6] Implement `--uninstall <id>` in `installer/lib/manifest.sh` + `installer/reposkillopt-install` — delete exactly the record's paths, then remove the row; unknown id → exit 0 with "not installed" note (depends on T008)
- [X] T030 [US6] **Validation checkpoint** — run `installer/tests/test_manifest_ops.sh`; confirm SC-007 (exact-file removal) and `contracts/install-manifest.contract.md` operations

**Checkpoint**: Full install lifecycle (install → list → upgrade → uninstall) is demonstrable.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final integrity sweeps and documentation.

- [X] T031 [P] Add an "Install (CLI)" section to the top-level `README.md` pointing at the one-liner and `installer/README.md`, and listing the four targets and their locations
- [X] T032 [P] Write `installer/tests/test_integrity.sh` — assert installed files are byte-for-byte equal to their `adapters/<id>/` source (SC-008) and that no file under `skills/` or `adapters/` is modified by any operation (FR-016)
- [X] T033 [P] Make scripts executable and lint — `chmod +x install.sh installer/reposkillopt-install`; run `shellcheck` on all shell files if available and resolve warnings (POSIX-portability)
- [X] T034 Run the full suite via `installer/tests/run.sh`; ensure all `test_*.sh` pass; fix any failures
- [X] T035 Execute `specs/002-cli-installer/quickstart.md` end-to-end against a throwaway fixture repo for all four adapters; record any friction in `installer/README.md`

---

## Dependencies & Execution Order

### Phase dependencies

- **Setup (Phase 1)**: no dependencies — start immediately.
- **Foundational (Phase 2)**: depends on Setup. **Blocks all user stories** (every subcommand routes through `util.sh`, `targets.sh`, and the CLI skeleton).
- **User Stories (Phase 3+)**: depend on Foundational. Then:
  - **US1 (P1)** is the base install path; US3, US4 extend the US1 install flow and so depend on US1 (T009).
  - **US2 (P2)** adds detection onto the US1 install flow (depends on US1's T009).
  - **US5 (P3)** wraps the CLI (depends on Foundational T006; independent of US2–US4).
  - **US6 (P3)** uses the manifest from US1 (depends on US1's T008); otherwise independent.
- **Polish (Phase 9)**: depends on the desired user stories being complete.

### Within each user story

- The test task ([P]) can be authored in parallel with or before implementation.
- The validation checkpoint is sequential (depends on that story's implementation tasks).

### Parallel opportunities

- **Phase 1**: T002, T003 in parallel after T001.
- **Phase 2**: T005 in parallel with T004; T006 depends on both.
- **Story tests** (T007, T013, T017, T020, T023, T027) are all [P] — different files.
- **Polish**: T031, T032, T033 in parallel.

---

## Parallel Example: User Story 1

```text
# Author the US1 test alongside implementation (different files):
Task: T007 Write installer/tests/test_install.sh
Task: T008 Implement installer/lib/manifest.sh (create/read/upsert)
# Then T009 → T010 → T011 in sequence (same file: installer/reposkillopt-install), then T012 checkpoint.
```

---

## Implementation Strategy

### MVP first (P1 only)

1. Complete Phase 1 (Setup) and Phase 2 (Foundational — CRITICAL).
2. Complete Phase 3 (US1): single-command explicit install for all four adapters, idempotent, version-verified.
3. **STOP and VALIDATE**: run `installer/tests/test_install.sh`. At this point `reposkillopt-install --agent <id>` is a usable one-command installer — the publishable MVP.

### Incremental delivery beyond MVP

1. Add US2 — harness auto-detection (drops the need to know `--agent`).
2. Add US3 — `--scaffold` the `.reposkillopt/` layout.
3. Add US4 — version verification + safe upgrade/downgrade.
4. Add US5 — the `curl | sh` one-liner (the headline "easy install" UX).
5. Add US6 — `--list` / `--uninstall` lifecycle management.

### Notes

- [P] tasks operate on different files with no incomplete prerequisites.
- Tasks T009, T010, T011, T015, T018, T021 all edit `installer/reposkillopt-install` → they are sequential, not [P].
- Tasks T008, T028, T029 all edit `installer/lib/manifest.sh` → sequential.
- Commit after each task or logical group; there is no build step.
- Avoid: writing outside `<dest>`, modifying `skills/` or `adapters/`, guessing a target when detection is ambiguous (exit 3), or introducing any runtime dependency beyond POSIX utilities.
