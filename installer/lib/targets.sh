# targets.sh — the target registry (contracts/target-registry.contract.md). POSIX sh.
# The ONE place a new harness is wired in: add a case to each function below.
#
# Skill-capable harnesses now read the standard Agent Skills directory format
# (a `<name>/SKILL.md` folder). We install the canonical skill into each harness's
# native skills dir — namespaced and collision-free — instead of overwriting a
# shared repo-root AGENTS.md. `.agents/skills/` is read by Codex, OpenCode, and
# Cursor at once; `.claude/skills/` by Claude Code. AGENTS.md lives on only as an
# explicit, non-destructive legacy mode (the `*-agentsmd` targets).

TARGET_IDS="claude-code codex opencode cursor agents generic codex-agentsmd opencode-agentsmd"

# target_valid <id>
target_valid() {
  case " $TARGET_IDS " in
    *" $1 "*) return 0 ;;
    *) return 1 ;;
  esac
}

# target_source_files <id> — space-separated repo-relative source paths.
# Skill-dir targets ship the canonical skill directly (the format is now standard).
target_source_files() {
  case $1 in
    claude-code)               printf '%s' "adapters/claude-code/SKILL.md" ;;
    codex|opencode|cursor|agents) printf '%s' "skills/repo-skillopt/SKILL.md" ;;
    generic)                   printf '%s' "adapters/generic/skill.md adapters/generic/system-prompt-fragment.md" ;;
    codex-agentsmd)            printf '%s' "adapters/codex/AGENTS.md" ;;
    opencode-agentsmd)         printf '%s' "adapters/opencode/AGENTS.md" ;;
    *) return 1 ;;
  esac
}

# target_install_rel <id> — install path relative to the target root.
# Empty for generic (files land at the target-root level using their basenames).
target_install_rel() {
  case $1 in
    claude-code)        printf '%s' ".claude/skills/repo-skillopt/SKILL.md" ;;
    codex)              printf '%s' ".agents/skills/repo-skillopt/SKILL.md" ;;
    opencode)           printf '%s' ".opencode/skills/repo-skillopt/SKILL.md" ;;
    cursor)             printf '%s' ".cursor/skills/repo-skillopt/SKILL.md" ;;
    agents)             printf '%s' ".agents/skills/repo-skillopt/SKILL.md" ;;
    generic)            printf '%s' "" ;;
    codex-agentsmd|opencode-agentsmd) printf '%s' "AGENTS.md" ;;
    *) return 1 ;;
  esac
}

# target_detect <id> <dest> — succeed if this target's signal is present.
target_detect() {
  case $1 in
    claude-code)        [ -d "$2/.claude" ] ;;
    codex|agents)       [ -d "$2/.agents" ] ;;
    opencode)           [ -d "$2/.opencode" ] ;;
    cursor)             [ -d "$2/.cursor" ] ;;
    codex-agentsmd|opencode-agentsmd) [ -f "$2/AGENTS.md" ] ;;
    generic)            return 1 ;;
    *) return 1 ;;
  esac
}

# target_requires_dest <id> — generic needs an explicit --dest.
target_requires_dest() {
  [ "$1" = "generic" ]
}

# target_is_agentsmd <id> — true for the legacy single-file AGENTS.md targets.
target_is_agentsmd() {
  case $1 in
    codex-agentsmd|opencode-agentsmd) return 0 ;;
    *) return 1 ;;
  esac
}
