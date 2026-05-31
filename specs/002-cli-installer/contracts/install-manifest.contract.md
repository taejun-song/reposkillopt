# Contract — Install Manifest (`<target>/.reposkillopt/.install-manifest`)

**Scope**: The per-target-repo record of what the installer placed, enabling idempotency, list, upgrade, and exact uninstall (FR-007, FR-011, FR-013).
**Consumers**: `installer/lib/manifest.sh`; `--list`/`--uninstall`; the test suite.

## Location

`<target_root>/.reposkillopt/.install-manifest` — created on first install; lives under the target's `.reposkillopt/` working-artifact area (never inside this project).

## Format

UTF-8 text, one record per line, fields TAB-separated, no header:

```text
<adapter>\t<canonical_version>\t<comma_separated_relative_paths>\t<iso8601_timestamp>
```

Example:

```text
claude-code	0.1.0	.claude/skills/repo-skillopt/SKILL.md	2026-05-31T12:00:00Z
generic	0.1.0	docs/agent/skill.md,docs/agent/system-prompt-fragment.md	2026-05-31T12:05:00Z
```

## Field rules

| Field | Rule |
|---|---|
| `adapter` | One of the four target ids; **primary key** — at most one row per adapter. |
| `canonical_version` | Semver recorded from the source adapter at (re)install time. |
| `paths` | Comma-separated, target-root-relative; lists exactly the files placed; 1 (claude-code/codex/opencode) or 2 (generic). |
| `timestamp` | ISO-8601 UTC of the last successful (re)install. |

## Operations

- **Read/parse**: line-based with `while IFS=$(printf '\t') read`; no `jq` dependency.
- **Upsert (install)**: if a row for `adapter` exists, replace it (atomic temp+rename of the manifest); else append. Guarantees no duplicate rows (FR-007).
- **List**: print each row in a human-readable form (CLI contract row 10).
- **Uninstall**: read the row, delete exactly its `paths`, then remove the row; if it was the last row, the empty manifest file MAY be removed. Never deletes a path not listed in the row (FR-013, SC-007).
- **Atomicity**: every manifest mutation is written to a sibling temp file and `mv`-renamed into place; a failed write leaves the prior manifest intact.

## Invariants

- The manifest is the **only** authority for uninstall; the tool never guesses files to remove from the filesystem.
- Paths are always relative to `target_root` so the manifest is portable if the repo moves.
- The manifest records only files the installer wrote; it never lists user-authored files.

## Acceptance checklist

- [ ] First install creates the manifest under `<target>/.reposkillopt/`.
- [ ] Each adapter has at most one row (re-install upserts, never duplicates).
- [ ] `paths` lists exactly the placed files (1 or 2).
- [ ] `--uninstall` removes precisely those paths and the row, nothing else.
- [ ] Manifest mutations are atomic (interrupted write leaves prior manifest valid).
- [ ] Parser works with POSIX `sh` and no `jq`.
