# Tasks: Install via the Native Agent-Skills Directory

**Feature**: `006-native-skills-install` | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Paths relative to repo root. `[P]` = parallelizable.

## Phase 1: Setup

- [x] T001 Establish the installer test baseline: `cd installer && sh tests/run.sh` (record current pass count as the regression floor).

## Phase 2: Foundational (the target registry — blocks the rest)

- [x] T002 In `installer/lib/targets.sh`: extend `TARGET_IDS` to `claude-code codex opencode cursor agents generic codex-agentsmd opencode-agentsmd` and update `target_source_files`, `target_install_rel`, `target_detect`, `target_requires_dest` per `contracts/target-registry.md` (codex/opencode/cursor/agents source the canonical `skills/repo-skillopt/SKILL.md`; legacy `*-agentsmd` source the AGENTS.md adapters). Add a `target_is_agentsmd <id>` helper.

## Phase 3: User Story 1 — Install without clobbering AGENTS.md (P1)

**Goal**: skill-capable targets install into a namespaced skills dir; a foreign `AGENTS.md` is never touched.
**Independent test**: install `codex` in a repo with its own `AGENTS.md`; skill lands under `.agents/skills/repo-skillopt/`, `AGENTS.md` unchanged.

- [x] T003 [US1] Verify the main install path in `installer/reposkillopt-install` places `codex`/`opencode`/`cursor`/`agents` at their namespaced paths and that the version fallback resolves `_srcver` from the canonical skill (no code change expected — confirm, adjust only if needed).
- [x] T004 [P] [US1] `installer/tests/test_skill_dir_targets.sh`: for each of codex/opencode/cursor/agents/claude-code, assert the installed file path; assert installed content equals the expected source; assert a pre-existing `AGENTS.md` in the dest is byte-for-byte unchanged (SC-001); assert offline (no network) (SC-005).

## Phase 4: User Story 2 — One install covers several harnesses (P1)

**Goal**: the cross-tool `agents` target.
**Independent test**: install `agents`; file at `.agents/skills/repo-skillopt/SKILL.md`; manifest + `--list` report it.

- [x] T005 [US2] Confirm the `agents` target end-to-end: install → manifest record → `--list` shows id+path → `--dry-run` prints the destination. (Covered by registry from T002; add assertions in `test_skill_dir_targets.sh`.)

## Phase 5: User Story 3 — Cursor target + safe legacy AGENTS.md (P2)

**Goal**: cursor target; AGENTS.md legacy mode never destroys a foreign file.
**Independent test**: cursor lands at `.cursor/skills/…`; legacy mode refuses/【backs up】 a foreign `AGENTS.md`.

- [x] T006 [US3] In `installer/reposkillopt-install`: add the **AGENTS.md guard** in the install path (only when `target_is_agentsmd`): if dest `AGENTS.md` exists and no manifest record for this target → refuse with `EX_REFUSED` unless `--force`; under `--force` copy → `AGENTS.md.bak` then write. A managed AGENTS.md (manifest match) upgrades in place. Wire `EX_REFUSED` into the exit-code list + usage. Honor `--dry-run` (print intended action, write nothing).
- [x] T007 [US3] In `installer/reposkillopt-install` `cmd_uninstall`: after `rm -f` of a recorded path under a `repo-skillopt/` dir, `rmdir` that dir if empty (ignore-if-nonempty); never touch siblings (FR-008).
- [x] T008 [P] [US3] `installer/tests/test_agents_md_safety.sh`: (a) `codex-agentsmd` into a repo with a foreign `AGENTS.md`, no `--force` → exits `EX_REFUSED`, file unchanged (SC-003); (b) with `--force` → `AGENTS.md.bak` created, new content written; (c) a RepoSkillOpt-managed `AGENTS.md` upgrades in place; (d) `cursor` install → `.cursor/skills/repo-skillopt/SKILL.md`; (e) install→list→uninstall of a dir target leaves the repo pristine incl. removed `repo-skillopt/` dir (SC-004).

## Phase 6: Polish, docs, regression

- [x] T009 Full installer suite green (`installer/tests/run.sh`) incl. the existing tests (no regression vs T001).
- [x] T010 [P] Update `README.md` install table: skill-dir paths per harness, the cross-tool `.agents/skills/` row, and a note that AGENTS.md is now opt-in legacy (and non-destructive). State which harnesses read each location (FR-011).
- [x] T011 [P] Light update to `adapters/codex/README.md` + `adapters/opencode/README.md`: skill-dir install is primary; AGENTS.md retained for legacy (FR-012). Do not modify the canonical skill (FR-013).
- [x] T012 Sanity: a real offline install of `agents` into a throwaway repo that already has an `AGENTS.md`; confirm both outputs (skill present, AGENTS.md untouched), then `--uninstall` restores it.

## Dependencies

- T002 blocks T003–T008.
- US1 (T003–T004) and US2 (T005) share the registry; independent of US3's guard.
- US3 (T006–T008) adds the guard + uninstall behavior.
- T009–T012 after implementation.

## MVP

T002 + US1 (T003–T004) is the MVP: namespaced skill-dir installs that stop touching `AGENTS.md`. US2 adds the cross-tool target; US3 adds Cursor + the safe legacy mode.
