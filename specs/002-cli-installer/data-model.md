# Phase 1 Data Model — One-Command CLI Installer

The installer is a stateless shell tool; its only persistent "data" is (a) a static **target registry** baked into the tool and (b) a per-target-repo **install manifest** it reads and writes. The entities below define those plus the conceptual objects the spec names.

## Entity 1 — Target (harness)

A supported coding-agent environment the installer can equip. The set is static, defined in `installer/lib/targets.sh`.

| Field | Type | Description | Validation |
|---|---|---|---|
| `id` | enum | `claude-code` \| `codex` \| `opencode` \| `generic` | Must be one of the four; `--agent` is validated against this set. |
| `source_files` | list[relpath] | Adapter file(s) under `adapters/<id>/` to copy | Each path must exist in the repo; ≥1; `generic` has 2. |
| `install_location` | template | Where files land in the target repo | Fixed per target except `generic` (requires `--dest`). |
| `detection_signal` | predicate \| none | Target-repo signal that suggests this target | `generic` = none (never auto-detected). |
| `metadata_kind` | enum | Where `canonical_version` is read from in the source file | `yaml-frontmatter` (claude-code, generic) \| `html-comment` (codex, opencode). |

Fixed values:

| id | source_files | install_location | detection_signal |
|---|---|---|---|
| `claude-code` | `adapters/claude-code/SKILL.md` | `<dest>/.claude/skills/repo-skillopt/SKILL.md` | `<dest>/.claude/` exists |
| `codex` | `adapters/codex/AGENTS.md` | `<dest>/AGENTS.md` | `<dest>/AGENTS.md` exists *(shared → ambiguous)* |
| `opencode` | `adapters/opencode/AGENTS.md` | `<dest>/AGENTS.md` | `<dest>/AGENTS.md` exists *(shared → ambiguous)* |
| `generic` | `adapters/generic/skill.md`, `adapters/generic/system-prompt-fragment.md` | `<--dest>/` (required) | none |

## Entity 2 — Install Record (manifest row)

One line in `<target>/.reposkillopt/.install-manifest` per installed adapter. Drives idempotency, list, upgrade, and uninstall.

| Field | Type | Description | Validation |
|---|---|---|---|
| `adapter` | enum | The `Target.id` that was installed | One of the four; unique key within a manifest (one row per adapter). |
| `canonical_version` | semver | Version recorded at install time | Read from the source adapter at install. |
| `paths` | list[relpath] | Exact files the installer placed, relative to target root | Non-empty; these and only these are removed on uninstall. |
| `installed_at` | ISO-8601 | Timestamp of the install/upgrade | Updated on every successful (re)install. |

**Serialized form** (TAB-separated, one record per line):

```text
claude-code	0.1.0	.claude/skills/repo-skillopt/SKILL.md	2026-05-31T12:00:00Z
```

**Uniqueness**: `adapter` is the primary key. Re-installing the same adapter replaces its row (no duplicates — FR-007).

## Entity 3 — Target Repository

The directory being equipped (the `--dest`, defaulting to the current directory).

| Field | Type | Description | Validation |
|---|---|---|---|
| `root` | dirpath | Target repository/working directory root | Must exist and be writable (else exit 4). |
| `manifest_path` | filepath | `<root>/.reposkillopt/.install-manifest` | Created on first install. |
| `is_git` | bool | Whether `root` is a git repo | Informational only; not required (FR-015). |

## Entity 4 — Canonical Version Reference

The single source-of-truth version every installed adapter must match.

| Field | Type | Description | Validation |
|---|---|---|---|
| `value` | semver | `version:` in `skills/repo-skillopt/SKILL.md` | Read at install; compared against the adapter's `canonical_version`. |

## Relationships

```text
Canonical Version Reference --(must equal)--> Target.canonical_version (source adapter metadata)
Target --(produces on install)--> Install Record  (1 Target : 1 Record per Target Repository)
Target Repository --(owns)--> Install Manifest --(contains)--> 0..4 Install Records
Install Record --(lists)--> 1..2 placed files in the Target Repository
```

## State transitions (per adapter, within a target repository)

```text
        (no row)
           │  install
           ▼
       INSTALLED ──── install same version ───▶ INSTALLED (no-op, "already up to date")
           │  install newer version
           ▼
       INSTALLED' (row updated, files overwritten atomically, version delta reported)
           │  install older version, no --force
           ▼
        REFUSED (exit 5, unchanged)        ── with --force ──▶ INSTALLED'' (downgrade recorded)
           │  uninstall
           ▼
        (row + listed files removed)  ──▶ (no row)
```

## Validation rules summary (traceable to FRs)

- A target id outside the four → usage error, exit 2 (FR-002, FR-004).
- Missing `--agent` with 0 or ≥2 detected targets → exit 3, install nothing (FR-005, SC-004).
- `generic` without `--dest` → usage error (R6).
- Target root not writable/missing → exit 4, no changes (FR-010).
- Older-than-installed version without `--force` → exit 5, no changes (FR-011).
- Uninstall removes exactly `Install Record.paths` and the row, nothing else (FR-013, SC-007).
- Installed file bytes equal source adapter bytes (FR-016, SC-008).
- Manifest and scaffolded dirs live only under `<target>/.reposkillopt/` (FR-036a inheritance).
