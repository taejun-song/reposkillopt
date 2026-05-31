# US6 — --list and --uninstall: list shows records; uninstall removes exactly recorded files.
run_test() {
  d="$WORK"
  "$INSTALL" --agent claude-code --dest "$d" >/dev/null || return 1
  echo hello > "$d/unrelated.txt"

  lst=$("$INSTALL" --list --dest "$d")
  printf '%s' "$lst" | grep -q "claude-code" || { fail "list missing claude-code"; return 1; }

  "$INSTALL" --uninstall claude-code --dest "$d" >/dev/null || return 1
  assert_nofile "$d/.claude/skills/repo-skillopt/SKILL.md" "uninstall removed adapter file" || return 1
  assert_file "$d/unrelated.txt" "uninstall left unrelated file" || return 1

  lst2=$("$INSTALL" --list --dest "$d")
  printf '%s' "$lst2" | grep -qi "no adapters installed" || { fail "manifest not empty after uninstall"; return 1; }

  # uninstalling something not installed is a clean no-op (exit 0)
  "$INSTALL" --uninstall codex --dest "$d" >/dev/null 2>&1; assert_exit "$?" 0 "uninstall-not-installed exit 0" || return 1
  return 0
}
