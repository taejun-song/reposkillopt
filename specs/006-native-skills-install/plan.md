# Implementation Plan: Install via the Native Agent-Skills Directory

**Branch**: `006-native-skills-install` | **Date**: 2026-06-07 | **Spec**: [spec.md](./spec.md)

## Summary

Install RepoSkillOpt as a **namespaced skill directory** (`<skills-root>/repo-skillopt/SKILL.md`) into each harness's native skills location — matching the now-standard Agent Skills format — instead of overwriting a shared `AGENTS.md`. Add a `cursor` target and a cross-tool `agents` target (`.agents/skills/` is read by Codex + OpenCode + Cursor). Keep `AGENTS.md` as an explicit, **non-destructive** legacy mode (refuse foreign files unless `--force`; back up to `.bak`). Almost all of this lands in the existing `installer/lib/targets.sh` registry plus a guard + uninstall tweak in the main script.

## Technical Context

**Language/Version**: POSIX `sh` (the existing installer). No new language.
**Primary Dependencies**: none new — reuses `installer/lib/{targets,manifest,util,detect}.sh`, `read_field`, `copy_atomic`, the manifest, and the version gate.
**Storage**: filesystem only; the per-repo `.reposkillopt/.install-manifest` (unchanged format) records the new targets.
**Testing**: the existing `installer/tests/` POSIX harness (`run.sh` + `test_*.sh`); add cases per target + AGENTS.md protection + namespaced uninstall.
**Target Platform**: any POSIX shell; offline from a clone.
**Project Type**: single (the shell installer + docs).
**Constraints**: offline-capable (FR-009), idempotent manifest, atomic writes, **no canonical-skill content change** (FR-013), **never silently destroy a foreign AGENTS.md** (FR-005).
**Scale/Scope**: small, well-contained — a target-registry extension + two guard behaviors + tests + docs.

## Constitution Check

Constitution is an unfilled template — no ratified gates. Project non-negotiables that apply:
- **Canonical neutrality / no content change** — satisfied: this changes only *where/how* the skill installs; `skills/repo-skillopt/SKILL.md` is untouched (FR-013). ✅
- **Skill-first, helpers optional, no new deps** — installer is POSIX sh, no deps added. ✅
- **Adapter-equivalence** — preserved: AGENTS.md adapters are retained for legacy use (FR-012). ✅

No violations; Complexity Tracking empty.

## Project Structure

### Documentation (this feature)

```text
specs/006-native-skills-install/
├── spec.md  ├── plan.md  ├── research.md
├── data-model.md  ├── contracts/target-registry.md  ├── quickstart.md
└── checklists/requirements.md
```

### Source Code (repository root)

```text
installer/
├── lib/targets.sh            # CHANGED: add cursor, agents, legacy AGENTS.md targets;
│                             #          map codex/opencode/cursor/agents -> skills dir, source = canonical SKILL.md
├── reposkillopt-install      # CHANGED: AGENTS.md protection guard (refuse/backup) for legacy mode;
│                             #          uninstall removes the namespaced repo-skillopt/ dir
├── lib/manifest.sh           # unchanged (format already carries target + version + paths)
└── tests/
    ├── test_skill_dir_targets.sh   # NEW: each new target's path; canonical content; offline
    ├── test_agents_md_safety.sh    # NEW: refuse foreign AGENTS.md; --force backs up; managed upgrade in place
    └── (existing tests must stay green)

README.md                     # CHANGED: install table — skill-dir paths + cross-tool .agents/skills/
adapters/*/README.md          # CHANGED (light): note skill-dir install is now primary; AGENTS.md is legacy
```

**Structure Decision**: single package; the target registry (`targets.sh`) is by design the one wiring point, so the change stays cohesive and table-driven.

## Phase 0 / Phase 1 outputs

- `research.md` — the path/standard decisions and the version-fallback finding.
- `data-model.md` — the target registry entries + manifest record + legacy-guard states.
- `contracts/target-registry.md` — the exact `targets.sh` function outputs per id, and the AGENTS.md-guard contract.
- `quickstart.md` — install/list/uninstall for the new targets + the safety demo.

## Complexity Tracking

None — additive registry entries + two guarded behaviors; no new dependency, no canonical change.
