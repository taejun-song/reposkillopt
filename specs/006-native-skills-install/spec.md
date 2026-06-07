# Feature Specification: Install via the Native Agent-Skills Directory

**Feature Branch**: `006-native-skills-install`
**Created**: 2026-06-07
**Status**: Draft
**Input**: User description: "Install RepoSkillOpt as a namespaced skill in each harness's native skills directory instead of overwriting a shared AGENTS.md; add a Cursor target and a cross-tool agents target; make AGENTS.md an explicit, non-destructive legacy mode."

## Clarifications

### Session 2026-06-07

External facts verified from official harness documentation (mid-2026), recorded here so they are explicit:

- The SKILL.md *Agent Skills* directory format (a folder named for the skill, containing `SKILL.md` with `name` + `description` front matter) is now read by Claude Code, Codex, OpenCode, and Cursor.
- Skill-directory locations each harness reads: Claude Code → `.claude/skills/<name>/`; Codex → `.agents/skills/<name>/`; OpenCode → `.opencode/skills/<name>/` (also reads `.claude/` and `.agents/`); Cursor → `.cursor/skills/<name>/` and `.agents/skills/<name>/` (also reads `.claude/`).
- Therefore `.agents/skills/repo-skillopt/` is read by Codex, OpenCode, and Cursor simultaneously; `.claude/skills/repo-skillopt/` is read by Claude Code (and, for compatibility, OpenCode and Cursor).
- The canonical `skills/repo-skillopt/SKILL.md` already satisfies the required front matter, so skill-capable harnesses can load the canonical skill directly — no hand-written `AGENTS.md` prose wrapper is required for them.

Resolved as informed defaults (delegated): the `opencode` and `cursor` named targets install to their **own** native dir (`.opencode/skills/`, `.cursor/skills/`) for least surprise; the separate **`agents`** target is the one-install-covers-many option using `.agents/skills/`. Legacy AGENTS.md, when explicitly chosen, **refuses** on a pre-existing non-RepoSkillOpt file unless `--force`, and backs it up to `AGENTS.md.bak` before writing.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Install without clobbering a user's AGENTS.md (Priority: P1)

A developer whose repository already contains its own `AGENTS.md` installs RepoSkillOpt for Codex (or OpenCode). The skill is placed in a **namespaced skills directory** (`.agents/skills/repo-skillopt/SKILL.md`), and the developer's existing `AGENTS.md` is left **completely untouched**.

**Why this priority**: This removes a real data-loss bug (the installer currently overwrites a pre-existing `AGENTS.md` with no backup) and is the core reason for the feature. It is independently valuable on its own.

**Independent Test**: In a repo containing a non-RepoSkillOpt `AGENTS.md`, run the installer for the Codex target; confirm the skill is installed under a skills directory and the original `AGENTS.md` is byte-for-byte unchanged.

**Acceptance Scenarios**:

1. **Given** a target repo with a pre-existing `AGENTS.md`, **When** the Codex target is installed, **Then** `.agents/skills/repo-skillopt/SKILL.md` is created and the existing `AGENTS.md` is unchanged.
2. **Given** any skill-capable target, **When** it is installed, **Then** the installed file lives under a per-skill **namespaced directory** (never a shared repo-root file) and does not collide with the repo's other files.

### User Story 2 - One install covers several harnesses (Priority: P1)

A developer who uses more than one skill-capable agent installs once to the **cross-tool** location and has the skill picked up by all of them.

**Why this priority**: The newly-standard `.agents/skills/` path is read by Codex, OpenCode, and Cursor at once; exposing it as a single target is the headline simplification the standard enables.

**Independent Test**: Run the installer with the cross-tool target; confirm the skill is written to `.agents/skills/repo-skillopt/SKILL.md`, which the docs confirm Codex, OpenCode, and Cursor all read.

**Acceptance Scenarios**:

1. **Given** a target repo, **When** the cross-tool `agents` target is installed, **Then** `.agents/skills/repo-skillopt/SKILL.md` exists and the manifest records it.
2. **Given** the cross-tool install, **When** the user lists installs, **Then** the `agents` target and its path are reported.

### User Story 3 - Add Cursor; keep AGENTS.md as safe legacy (Priority: P2)

A Cursor user installs to Cursor's native skills directory. Separately, a user who specifically wants the old single-file `AGENTS.md` behavior can still request it — but it never destroys an existing file.

**Why this priority**: Broadens coverage to a major harness and preserves backward compatibility without the destructive behavior. Depends on the skills-directory mechanism from US1.

**Independent Test**: Install the Cursor target and confirm `.cursor/skills/repo-skillopt/SKILL.md`. Then request the legacy AGENTS.md mode in a repo that already has an `AGENTS.md` and confirm it refuses (or backs up) rather than overwriting.

**Acceptance Scenarios**:

1. **Given** the Cursor target, **When** installed, **Then** `.cursor/skills/repo-skillopt/SKILL.md` is created.
2. **Given** the legacy AGENTS.md mode and a pre-existing non-RepoSkillOpt `AGENTS.md`, **When** installed without `--force`, **Then** it refuses with a clear message and changes nothing.
3. **Given** the legacy AGENTS.md mode with `--force`, **When** installed, **Then** the original is preserved as `AGENTS.md.bak` before the new content is written.

### Edge Cases

- **Re-install / upgrade**: re-installing the same target updates the skill in place and the version gate still applies (up-to-date / upgrade / refuse-downgrade), keyed off the manifest, for the new directory targets.
- **Uninstall**: uninstalling a directory target removes the skill file (and its now-empty `repo-skillopt/` dir) and the manifest entry, without touching unrelated files.
- **Dry-run**: shows the exact destination path(s) for the new targets without writing.
- **A RepoSkillOpt-managed AGENTS.md already present**: legacy mode recognizes its own prior install (via manifest) and upgrades in place — the refuse/backup rule applies only to *foreign* `AGENTS.md` files.
- **Offline**: every new target installs from a local clone with no network.
- **Existing skills directory already present** (the repo has other skills under `.claude/skills/` or `.agents/skills/`): RepoSkillOpt installs alongside them under its own `repo-skillopt/` subdir, touching nothing else.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The installer MUST install the skill for skill-capable harnesses into a **per-skill namespaced directory** named `repo-skillopt/` containing `SKILL.md`, never as a shared repo-root file.
- **FR-002**: Target → location mapping MUST be: `claude-code` → `.claude/skills/repo-skillopt/SKILL.md` (unchanged); `codex` → `.agents/skills/repo-skillopt/SKILL.md`; `opencode` → `.opencode/skills/repo-skillopt/SKILL.md`; `cursor` (new) → `.cursor/skills/repo-skillopt/SKILL.md`; `agents` (new, cross-tool) → `.agents/skills/repo-skillopt/SKILL.md`.
- **FR-003**: The skill **content** installed for skill-capable targets MUST be the canonical skill (`skills/repo-skillopt/SKILL.md`), which already carries the required `name` + `description` front matter; no per-harness prose rewrite is required for them.
- **FR-004**: Installing any skill-capable target MUST NOT create, modify, or delete a repository-root `AGENTS.md`.
- **FR-005**: A legacy AGENTS.md install mode MUST remain available but MUST NOT silently overwrite a pre-existing `AGENTS.md` that RepoSkillOpt did not install: it MUST refuse with a clear message unless `--force`, and under `--force` MUST preserve the original as `AGENTS.md.bak` before writing.
- **FR-006**: Legacy AGENTS.md mode MUST still upgrade a *RepoSkillOpt-managed* `AGENTS.md` in place (recognized via the manifest), without the refuse/backup friction.
- **FR-007**: The install manifest, `--list`, `--uninstall`, `--dry-run`, and the version gate (up-to-date / upgrade / refuse-downgrade) MUST work for every new target, including correct removal of the namespaced directory on uninstall.
- **FR-008**: `--uninstall` of a directory target MUST remove only the RepoSkillOpt skill file and its `repo-skillopt/` directory (if empty), never sibling skills or unrelated files.
- **FR-009**: All new targets MUST install fully offline from a local clone; the `install.sh` online bootstrap path MUST continue to work unchanged.
- **FR-010**: With no explicit target, behavior MUST remain explicit-or-refuse when ambiguous (no guessing among several skill-capable harnesses) — consistent with today.
- **FR-011**: The README install table and adapter guidance MUST be updated to describe skill-directory installs and the cross-tool `.agents/skills/` path; documentation MUST state which harnesses read each location.
- **FR-012**: The existing AGENTS.md adapter files MUST be retained (not deleted) for explicit legacy use; adapter-equivalence for anything still using AGENTS.md MUST be preserved.
- **FR-013**: The canonical skill's *content* MUST NOT be changed by this feature — only how and where it is installed.

### Key Entities *(include if feature involves data)*

- **Install target**: a named harness/profile (`claude-code`, `codex`, `opencode`, `cursor`, `agents`, plus the legacy AGENTS.md mode) that maps to a destination location and a source artifact.
- **Skill install (directory form)**: the `repo-skillopt/` directory + `SKILL.md` placed under a harness's skills root; the unit recorded in the manifest.
- **Install manifest**: the per-target-repo record of what was installed (target, version, path) driving idempotency, list, upgrade, uninstall — extended to the new directory targets.
- **Legacy AGENTS.md install**: the opt-in single-file mode, with refuse/backup protection for foreign files.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Installing any skill-capable target in a repo that already has an `AGENTS.md` leaves that `AGENTS.md` byte-for-byte unchanged (0 modifications).
- **SC-002**: A single install of the cross-tool `agents` target places the skill at one path that the documentation confirms 3 harnesses (Codex, OpenCode, Cursor) read.
- **SC-003**: Choosing the legacy AGENTS.md mode against a foreign pre-existing `AGENTS.md` results in **no data loss** in 100% of cases — either a refusal (no change) or a `.bak` preservation before write.
- **SC-004**: For every new target, install → list → uninstall returns the repository to its pre-install state (no leftover RepoSkillOpt files, no manifest entry).
- **SC-005**: Every new target installs with no network access (offline from a clone).
- **SC-006**: The installer test suite passes, including new cases for each target's path, the AGENTS.md-protection rule, and namespaced uninstall.

## Assumptions

- The skill-directory paths above reflect the harnesses' documented behavior as of mid-2026 (Claude Code `.claude/skills/`, Codex/Cursor/OpenCode reading `.agents/skills/`, plus each tool's own dir). If a harness changes its paths, only the target→location mapping needs updating.
- The canonical `SKILL.md` front matter (`name: repo-skillopt`, a `description`) is sufficient for these harnesses to discover and activate the skill; no additional required fields are assumed.
- "Namespaced, collision-free" is satisfied by the `repo-skillopt/` subdirectory; multiple skills coexisting under a shared skills root is the harnesses' normal behavior.
- The existing POSIX-sh installer architecture (targets/detect/manifest libs, atomic copy, version gate) is reused; no new runtime dependency is introduced.
- The legacy AGENTS.md mode is opt-in; the default recommendation becomes the skill-directory install.
