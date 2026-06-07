# Contract — Target Registry & AGENTS.md Guard (006)

## `installer/lib/targets.sh`

`TARGET_IDS` becomes: `claude-code codex opencode cursor agents generic codex-agentsmd opencode-agentsmd`

```sh
target_source_files <id>   # repo-relative source path(s)
  claude-code        -> adapters/claude-code/SKILL.md
  codex|opencode|cursor|agents -> skills/repo-skillopt/SKILL.md      # the canonical skill
  generic            -> adapters/generic/skill.md adapters/generic/system-prompt-fragment.md
  codex-agentsmd     -> adapters/codex/AGENTS.md
  opencode-agentsmd  -> adapters/opencode/AGENTS.md

target_install_rel <id>    # path under the target root
  claude-code  -> .claude/skills/repo-skillopt/SKILL.md
  codex        -> .agents/skills/repo-skillopt/SKILL.md
  opencode     -> .opencode/skills/repo-skillopt/SKILL.md
  cursor       -> .cursor/skills/repo-skillopt/SKILL.md
  agents       -> .agents/skills/repo-skillopt/SKILL.md
  generic      -> ""                                   # basenames at root
  codex-agentsmd|opencode-agentsmd -> AGENTS.md

target_detect <id> <dest>
  claude-code -> [ -d <dest>/.claude ];   codex|agents -> [ -d <dest>/.agents ]
  opencode    -> [ -d <dest>/.opencode ]; cursor       -> [ -d <dest>/.cursor ]
  *-agentsmd  -> [ -f <dest>/AGENTS.md ];  generic     -> false

target_requires_dest <id>  -> true only for generic
target_is_agentsmd <id>    # NEW helper: true for codex-agentsmd | opencode-agentsmd
```

- **Contract**: adding/altering a harness touches only `targets.sh` (the existing design invariant).

## AGENTS.md guard (in `reposkillopt-install`, install path)

Applies only when `target_is_agentsmd "$AGENT"` is true and the destination is `AGENTS.md`:

```
dest = <root>/AGENTS.md
if dest exists and manifest_get(root, AGENT) is empty:   # foreign, not ours
    if not --force:  err "refusing to overwrite existing AGENTS.md (not installed by RepoSkillOpt); use --force"; exit EX_REFUSED
    else:            copy_atomic(dest, dest.bak)          # preserve before write
# managed (manifest match) or absent -> proceed (version gate still applies)
```

- New exit code `EX_REFUSED` (documented in usage). Dry-run prints what it *would* do (refuse / back up) and writes nothing.
- **MUST** never modify `AGENTS.md` for any non-`*-agentsmd` target (FR-004).

## Uninstall (directory targets)

```
for each recorded path p:  rm -f <root>/p
if p is under a repo-skillopt/ dir:  rmdir <root>/<…>/repo-skillopt  (ignore if non-empty)
remove the manifest line
```
- **MUST** remove only RepoSkillOpt's own file + its `repo-skillopt/` dir; never siblings (FR-008).

## Invariants
- Offline (no network) for all targets (FR-009); manifest format unchanged (FR-007); canonical skill content unchanged (FR-013); existing installer tests stay green.
