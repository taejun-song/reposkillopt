# US5 — install.sh bootstrap: runs the installer from an arbitrary CWD and passes args through.
# (The network fetch path is not exercised here — only the local exec path + arg passthrough.)
run_test() {
  d="$WORK/t"; mkdir -p "$d/.claude"
  ( cd / && "$BOOTSTRAP" --agent claude-code --dest "$d" ) >/dev/null 2>&1
  assert_exit "$?" 0 "bootstrap exit 0" || return 1
  assert_file "$d/.claude/skills/repo-skillopt/SKILL.md" "bootstrap installed via passthrough" || return 1
  assert_same "$d/.claude/skills/repo-skillopt/SKILL.md" "$REPO_ROOT/adapters/claude-code/SKILL.md" "bootstrap bytes equal" || return 1
  return 0
}
