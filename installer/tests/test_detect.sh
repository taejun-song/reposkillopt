# US2 — detection: single signal installs; ambiguous/none -> exit 3 with no writes.
run_test() {
  # single signal: .claude/ present, no AGENTS.md
  d="$WORK/a"; mkdir -p "$d/.claude"
  "$INSTALL" --dest "$d" >/dev/null 2>&1; assert_exit "$?" 0 "detect claude-code" || return 1
  assert_file "$d/.claude/skills/repo-skillopt/SKILL.md" "detected install placed" || return 1

  # ambiguous: bare AGENTS.md matches both legacy targets (codex-agentsmd + opencode-agentsmd)
  d2="$WORK/b"; mkdir -p "$d2"; : > "$d2/AGENTS.md"
  "$INSTALL" --dest "$d2" >/dev/null 2>&1; assert_exit "$?" 3 "ambiguous exit 3" || return 1
  assert_nofile "$d2/.reposkillopt/.install-manifest" "ambiguous wrote nothing" || return 1

  # none: empty dir
  d3="$WORK/c"; mkdir -p "$d3"
  "$INSTALL" --dest "$d3" >/dev/null 2>&1; assert_exit "$?" 3 "no-signal exit 3" || return 1
  assert_nofile "$d3/.reposkillopt/.install-manifest" "no-signal wrote nothing" || return 1
  return 0
}
