# targets.sh — the target registry (contracts/target-registry.contract.md). POSIX sh.
# The ONE place a new harness is wired in: add a case to each function below.

TARGET_IDS="claude-code codex opencode generic"

# target_valid <id>
target_valid() {
  case " $TARGET_IDS " in
    *" $1 "*) return 0 ;;
    *) return 1 ;;
  esac
}

# target_source_files <id> — space-separated repo-relative source paths.
target_source_files() {
  case $1 in
    claude-code) printf '%s' "adapters/claude-code/SKILL.md" ;;
    codex)       printf '%s' "adapters/codex/AGENTS.md" ;;
    opencode)    printf '%s' "adapters/opencode/AGENTS.md" ;;
    generic)     printf '%s' "adapters/generic/skill.md adapters/generic/system-prompt-fragment.md" ;;
    *) return 1 ;;
  esac
}

# target_install_rel <id> — install path relative to the target root.
# Empty for generic (files land at the target-root level using their basenames).
target_install_rel() {
  case $1 in
    claude-code) printf '%s' ".claude/skills/repo-skillopt/SKILL.md" ;;
    codex)       printf '%s' "AGENTS.md" ;;
    opencode)    printf '%s' "AGENTS.md" ;;
    generic)     printf '%s' "" ;;
    *) return 1 ;;
  esac
}

# target_detect <id> <dest> — succeed if this target's signal is present.
target_detect() {
  case $1 in
    claude-code) [ -d "$2/.claude" ] ;;
    codex)       [ -f "$2/AGENTS.md" ] ;;
    opencode)    [ -f "$2/AGENTS.md" ] ;;
    generic)     return 1 ;;
    *) return 1 ;;
  esac
}

# target_requires_dest <id> — generic needs an explicit --dest.
target_requires_dest() {
  [ "$1" = "generic" ]
}
