# Feature Specification: One-Command CLI Installer

**Feature Branch**: `002-cli-installer`
**Created**: 2026-05-31
**Status**: Draft
**Input**: User description: "I want this to be installed easily as speckit does with some command in the cli."

## Clarifications

### Session 2026-05-31

- Q: What distribution / runtime model should the installer use? → A: A dependency-free POSIX shell installer run via a one-liner (e.g., `curl … | sh`), plus the in-repo script it invokes — no language runtime required.
- Q: Where should the installer get the adapter files it places into the target repo? → A: Bundled with the installer so it is self-contained, version-pinned, and works fully offline.
- Q: Where should the installer tool itself live and ship? → A: In this repository as a new top-level area, versioned alongside the adapters it installs, clearly marked as optional tooling.
- Q: When no harness is specified and none can be detected, what should the installer do? → A: Exit non-zero with a message listing the valid targets; never guess and never default.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Install an adapter into a target repository with one command (Priority: P1)

An engineer who wants RepoSkillOpt in their project runs a single CLI command, names the agent harness they use, and the installer places the correct adapter file at the correct location for that harness, verifies it, and confirms success — without the engineer needing to know install paths or copy files by hand.

**Why this priority**: This is the whole point of the request — "installed easily … with some command." Today installation is a manual `mkdir` + `cp` + `grep` sequence per the README. A single command is the minimum viable improvement and delivers value on its own.

**Independent Test**: From a clean target repository, run the install command with an explicit harness (e.g., the Claude Code target); confirm the adapter file appears at its documented location, the printed summary states the installed version, and the existing version-match check passes — all in one invocation.

**Acceptance Scenarios**:

1. **Given** a writable target repository and a chosen harness, **When** the user runs the install command, **Then** the correct adapter is placed at that harness's documented location and a success summary (file, path, version) is printed.
2. **Given** the install just completed, **When** the user runs the documented version-match check, **Then** the adapter's `canonical_version` equals the canonical skill `version`.
3. **Given** the same command is run a second time on the same repository, **When** it completes, **Then** there is exactly one adapter install (no duplicate, no corruption).

---

### User Story 2 - Detect the harness so the user need not know paths (Priority: P2)

A user who does not specify a harness runs the installer; it inspects the target repository for recognizable signals (e.g., a Claude-style skills directory, a root agent-instructions file) and selects the matching adapter. If the signals are ambiguous or absent, it asks the user (or requires an explicit flag) rather than guessing.

**Why this priority**: Removing the need to know harness names and paths is what makes it feel "easy," but US1 already delivers a working one-command install with an explicit target, so detection is an enhancement rather than the core.

**Independent Test**: In a repository that contains exactly one harness signal, run the installer with no harness argument; confirm it selects the matching adapter. In a repository with conflicting or no signals, confirm it asks or errors instead of installing to a wrong location.

**Acceptance Scenarios**:

1. **Given** a repository with a single recognizable harness signal, **When** the user runs the installer without naming a harness, **Then** the matching adapter is selected and installed.
2. **Given** a repository with conflicting or no signals, **When** the user runs the installer without naming a harness, **Then** the installer exits non-zero with a message listing the valid targets and installs nothing (it neither guesses nor defaults).

---

### User Story 3 - Scaffold the working-artifact layout (Priority: P2)

During or after install, the user can have the installer create the `.reposkillopt/{specs,feedback,rollouts,proposals}/` directory layout in the target repository, so the agent has a place to write Repository Specifications, Feedback Items, Rollout Logs, and Skill Edit Proposals immediately.

**Why this priority**: It saves a manual step and prevents "directory not found" friction on first run, but the agent can also create these on demand, so it is convenience rather than core.

**Independent Test**: Run the installer with the scaffold option on a repository lacking a `.reposkillopt/` directory; confirm the four subdirectories are created and that re-running does not error or wipe existing contents.

**Acceptance Scenarios**:

1. **Given** a target repository without `.reposkillopt/`, **When** the user runs the installer with scaffolding enabled, **Then** the four subdirectories are created.
2. **Given** a `.reposkillopt/` that already contains artifacts, **When** the installer runs again, **Then** existing files are preserved untouched.

---

### User Story 4 - Verify version and upgrade an existing install (Priority: P2)

A user with an older adapter already installed runs the installer; it recognizes the existing install, compares versions, and upgrades it to the current canonical version, reporting what changed. It warns rather than silently downgrades when the installed version is newer than the package being run.

**Why this priority**: Keeping adapters in sync with the canonical skill is the long-term maintenance value, but it only matters after the first install exists, so it follows US1.

**Independent Test**: Install an older adapter version, then run the installer from a newer package; confirm it reports the version delta and updates the adapter to the new version; run it again and confirm it reports "already up to date."

**Acceptance Scenarios**:

1. **Given** an older adapter is installed, **When** the user runs a newer installer, **Then** the adapter is updated and the version change is reported.
2. **Given** the installed adapter already matches the package version, **When** the installer runs, **Then** it reports "already up to date" and makes no changes.

---

### User Story 5 - Run the installer without permanently installing the tool (Priority: P3)

A user runs the installer as a one-shot command that fetches and executes the tool without leaving a permanently installed program behind — mirroring the no-friction "run it directly" experience of spec-kit's installer.

**Why this priority**: It lowers the barrier to first use, but a persistent install of the tool achieves the same installs, so it is a convenience tier.

**Independent Test**: On a machine without the tool persistently installed, run the documented one-shot command; confirm it installs an adapter into a target repository and leaves no required persistent tool footprint.

**Acceptance Scenarios**:

1. **Given** the tool is not persistently installed, **When** the user runs the one-shot command, **Then** an adapter is installed into the target repository in a single invocation.

---

### User Story 6 - List and uninstall adapters (Priority: P3)

A user can list which adapters the installer has placed in a target repository and remove a previously installed adapter, with the uninstall removing exactly what the installer added and nothing else.

**Why this priority**: Lifecycle management is useful for keeping environments clean, but is secondary to getting installed in the first place.

**Independent Test**: Install an adapter, run the list command and confirm it appears, run uninstall and confirm only the installed adapter file(s) are removed while unrelated repository files remain.

**Acceptance Scenarios**:

1. **Given** an adapter was installed, **When** the user runs the list command, **Then** the installed adapter and its version are shown.
2. **Given** an adapter was installed, **When** the user runs uninstall, **Then** exactly the files the installer placed are removed and nothing else is touched.

---

### Edge Cases

- **Target not writable or missing**: the installer reports a clear error and makes no partial changes.
- **Ambiguous or absent harness detection**: more than one (or no) harness signal present and no harness named — the installer exits non-zero listing the valid targets rather than guessing or defaulting.
- **Codex vs OpenCode collision**: both targets install to a root agent-instructions file, so a detected file of that kind is inherently ambiguous between them — treated as the ambiguous-detection case above (requires an explicit target).
- **Unknown or misspelled harness name**: the installer lists the valid targets and exits without changes.
- **Generic adapter (multi-file)**: the generic target ships more than one file (skill plus system-prompt fragment); install must place all required files together or none.
- **Existing newer adapter**: running an older installer over a newer install warns and does not silently downgrade.
- **Run outside any repository**: the installer still works against an explicit target path, and does not require the target to be a git repository.
- **Offline run**: because adapters are bundled with the installer, installing into a target repo works fully offline once the installer itself is present; only the initial one-shot fetch of the installer package needs network, and when that fetch fails it reports a clear message and suggests obtaining the installer another way (clone/download).
- **Interrupted install**: a partial run leaves the target either fully installed or unchanged, never half-written.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The project MUST provide a single CLI command that installs a selected adapter into a target repository in one invocation.
- **FR-002**: The installer MUST support every shipped adapter target (Claude Code, Codex, OpenCode, and the generic adapter).
- **FR-003**: For the selected target, the installer MUST place the adapter at that target's documented install location, including all files a multi-file adapter requires.
- **FR-004**: The user MUST be able to specify the target harness explicitly via a command argument.
- **FR-005**: When the target harness is not specified, the installer MUST attempt to detect it from the target repository; if detection is ambiguous or empty, it MUST exit non-zero with a message listing the valid targets and MUST NOT install — it MUST NOT guess a target and MUST NOT silently default to one.
- **FR-006**: After install, the installer MUST report the installed adapter's `canonical_version` and MUST make it verifiable that this value matches the canonical skill `version`.
- **FR-007**: The installer MUST be idempotent: re-running it on an already-equipped repository MUST NOT create duplicate or corrupted installs.
- **FR-008**: The installer MUST be able to scaffold the `.reposkillopt/{specs,feedback,rollouts,proposals}/` layout in the target repository, without overwriting existing artifacts.
- **FR-009**: On success, the installer MUST print a summary (what was installed, where, which version) and the next action needed to activate the skill.
- **FR-010**: On failure (unwritable target, unknown harness, missing files), the installer MUST exit with a clear message and MUST leave the target unchanged (no partial writes).
- **FR-011**: The installer MUST recognize an existing install and support upgrading it to the current version, reporting the version delta and refusing to silently downgrade.
- **FR-012**: The installer MUST support being run without a permanent installation of the tool itself (a one-shot/ephemeral path, e.g., a `curl … | sh` one-liner), in addition to a persistent path where the in-repo script is invoked directly after cloning/downloading.
- **FR-013**: The installer MUST be able to list adapters it has installed in a target repository and to uninstall them, removing exactly the files it placed.
- **FR-014**: The installer MUST bundle the adapter files it installs (rather than fetching them at install time) so that installing into a target repository works fully offline; the only permitted network use is the optional one-shot fetch of the installer package itself.
- **FR-015**: The installer MUST NOT require the target to be a git repository, but MUST work correctly when it is one.
- **FR-016**: The installer MUST NOT modify the canonical skill, alter adapter source content, or weaken the vendor-neutrality of the canonical skill; it is optional tooling layered on top of the existing artifacts.
- **FR-017**: The installer MUST be implemented as a dependency-free POSIX-shell tool that requires no language runtime beyond a standard shell and ordinary command-line utilities, and MUST ship in this repository as a clearly-marked, optional top-level tooling area versioned alongside the adapters it installs.

### Key Entities *(include if feature involves data)*

- **Adapter target (harness)**: One of the supported environments (Claude Code, Codex, OpenCode, generic). Each has a documented install location and a set of one or more files to place.
- **Install record**: The trace of what the installer placed in a target repository — which adapter, which version, where, and when — sufficient to support list, idempotent re-run, upgrade, and uninstall.
- **Target repository**: The repository (or directory) being equipped with an adapter, and under which the `.reposkillopt/` working-artifact layout lives.
- **Canonical version reference**: The single source-of-truth `version` of the canonical skill that every installed adapter's `canonical_version` must match.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user installs an adapter into a target repository with one command in under one minute, without reading installation docs or knowing the install path.
- **SC-002**: The installer supports all four shipped adapters; for each, the installed file(s) land at the documented location and pass the documented version-match check.
- **SC-003**: Re-running the installer on an already-equipped repository produces no duplicate and no broken install in 100% of runs (idempotent).
- **SC-004**: When the harness is unspecified and undetectable, the installer performs zero installs to a wrong location — it always asks or errors first.
- **SC-005**: A user can install an adapter without permanently installing the tool, using a single one-shot command.
- **SC-006**: After install, the printed summary alone lets the user confirm the adapter version matches the canonical skill, with no additional lookup steps.
- **SC-007**: A user can list installed adapters and uninstall one; uninstall removes exactly the files the installer placed and leaves all other repository files intact.
- **SC-008**: Across install, upgrade, and uninstall, the canonical skill and adapter source content are byte-for-byte unchanged (vendor-neutrality and source integrity preserved).

## Assumptions

- The supported targets are the four adapters the project already ships, at the install locations documented in their per-adapter READMEs; new adapters become installable as they are added.
- "Installed easily as spec-kit does" is delivered as a dependency-free POSIX-shell tool offering both a no-persistent-install one-shot runner (a `curl … | sh` one-liner) and a persistent path (invoke the in-repo script directly after clone/download) — see *Clarifications* and FR-017.
- The installer is **optional tooling**, outside the skill-first acceptance core; it ships in this repository as a clearly-marked top-level area versioned with the adapters, must not change the canonical skill, must preserve vendor-neutrality, and shipping it is not a precondition for the skill itself being usable (manual install via the README remains valid).
- The installer bundles the adapter files it installs, so installing into a target is fully offline; only the optional one-shot fetch of the installer itself uses the network.
- Working artifacts continue to live under the target repository's `.reposkillopt/{specs,feedback,rollouts,proposals}/` layout.
- Harness detection relies on observable signals in the target repository (for example, a Claude-style skills directory or a root agent-instructions file); detection is best-effort and always defers to an explicit user choice.
- The environment provides whatever standard, widely-available runtime the chosen distribution path needs; the feature introduces no hosted service, database, or frontend.
- The user has permission to write into the target repository or directory.
