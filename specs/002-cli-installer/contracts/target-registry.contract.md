# Contract — Target Registry (`installer/lib/targets.sh`)

**Scope**: The static mapping from a harness id to the files to copy, where to put them, and how to detect it (FR-002, FR-003, FR-005). This is the one place a new adapter is wired in.
**Consumers**: `reposkillopt-install` (install/detect), the test suite, future adapter authors.

## Required entries

Exactly the four shipped targets, each defining:

| Key | Required | Meaning |
|---|---|---|
| `source_files` | yes | Space-separated relative paths under the repo (must exist) |
| `install_location` | yes | Destination template relative to `--dest` (literal path, or `<dest>` for generic) |
| `detection_signal` | yes | Shell predicate over `--dest`, or `none` |
| `metadata_kind` | yes | `yaml-frontmatter` or `html-comment` — how to read `canonical_version` |

## Fixed mapping (MUST match the per-adapter READMEs)

| id | source_files | install_location | detection_signal | metadata_kind |
|---|---|---|---|---|
| `claude-code` | `adapters/claude-code/SKILL.md` | `.claude/skills/repo-skillopt/SKILL.md` | `[ -d "$dest/.claude" ]` | yaml-frontmatter |
| `codex` | `adapters/codex/AGENTS.md` | `AGENTS.md` | `[ -f "$dest/AGENTS.md" ]` | html-comment |
| `opencode` | `adapters/opencode/AGENTS.md` | `AGENTS.md` | `[ -f "$dest/AGENTS.md" ]` | html-comment |
| `generic` | `adapters/generic/skill.md adapters/generic/system-prompt-fragment.md` | `<dest>` (explicit `--dest` required) | `none` | yaml-frontmatter |

## Rules

- The four ids are the complete, validated set for `--agent` (CLI contract row 2).
- `codex` and `opencode` deliberately **share** `AGENTS.md`; therefore any detection that yields both is **ambiguous** and the tool must error (CLI contract row 3) — the registry MUST NOT encode a tiebreak.
- `generic.detection_signal` MUST be `none` (never auto-detected; R6).
- Adding a new harness = adding one row here; no other file changes (R-Open Questions).
- The registry MUST NOT contain harness-specific *normative skill content* — only transport metadata (paths/signals). Adapter content stays in `adapters/` (FR-016).

## Acceptance checklist

- [ ] Exactly the four ids are present, no more.
- [ ] Every `source_files` path exists in the repo.
- [ ] `install_location` values equal the locations documented in each `adapters/<id>/README.md`.
- [ ] `codex` and `opencode` map to the same `AGENTS.md` and encode no disambiguation.
- [ ] `generic` has two source files, `none` detection, and is install-only with `--dest`.
- [ ] `metadata_kind` correctly reflects where each adapter stores `canonical_version`.
