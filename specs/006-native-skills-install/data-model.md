# Data Model — 006 Native Agent-Skills Install

## Target registry (the rows in `targets.sh`)

| id | source file(s) | install path (rel to target root) | detect signal | requires --dest |
|---|---|---|---|---|
| `claude-code` | `adapters/claude-code/SKILL.md` | `.claude/skills/repo-skillopt/SKILL.md` | `.claude/` | no |
| `codex` | `skills/repo-skillopt/SKILL.md` | `.agents/skills/repo-skillopt/SKILL.md` | `.agents/` | no |
| `opencode` | `skills/repo-skillopt/SKILL.md` | `.opencode/skills/repo-skillopt/SKILL.md` | `.opencode/` | no |
| `cursor` *(new)* | `skills/repo-skillopt/SKILL.md` | `.cursor/skills/repo-skillopt/SKILL.md` | `.cursor/` | no |
| `agents` *(new, cross-tool)* | `skills/repo-skillopt/SKILL.md` | `.agents/skills/repo-skillopt/SKILL.md` | `.agents/` | no |
| `generic` | `adapters/generic/skill.md` + `system-prompt-fragment.md` | (basenames at root) | — | yes |
| `codex-agentsmd` *(new, legacy)* | `adapters/codex/AGENTS.md` | `AGENTS.md` | `AGENTS.md` | no |
| `opencode-agentsmd` *(new, legacy)* | `adapters/opencode/AGENTS.md` | `AGENTS.md` | `AGENTS.md` | no |

- `codex`/`opencode`/`cursor`/`agents` source the **canonical** skill (R2); version is resolved by the existing fallback (R3).

## Install manifest record (unchanged shape)
`<target_root>/.reposkillopt/.install-manifest`, one TAB-separated line per installed target:
`<target_id>\t<version>\t<install_paths_csv>\t<iso_timestamp>`
- New targets record their namespaced path, e.g. `codex\t0.2.0\t.agents/skills/repo-skillopt/SKILL.md\t<ts>`.

## Legacy AGENTS.md guard — states
For a legacy `*-agentsmd` target writing `AGENTS.md`:

| Destination AGENTS.md | `--force`? | Action |
|---|---|---|
| absent | — | write (fresh install) |
| present, **RepoSkillOpt-managed** (manifest match) | — | upgrade in place (version gate applies) |
| present, **foreign** | no | **refuse** (exit `EX_REFUSED`), change nothing |
| present, **foreign** | yes | copy → `AGENTS.md.bak`, then write |

## Uninstall (directory targets)
- remove the recorded file (`…/repo-skillopt/SKILL.md`), then `rmdir` `…/repo-skillopt/` if empty; remove the manifest line. Sibling skills and the shared skills root are never touched.
