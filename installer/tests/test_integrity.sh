# Polish — installed bytes equal source; no file under skills/ or adapters/ is modified.
run_test() {
  d="$WORK"
  before=$(cd "$REPO_ROOT" && find skills adapters -type f -exec cksum {} + | sort)
  "$INSTALL" --agent claude-code --dest "$d" --scaffold >/dev/null || return 1
  assert_same "$d/.claude/skills/repo-skillopt/SKILL.md" "$REPO_ROOT/adapters/claude-code/SKILL.md" "installed bytes equal source" || return 1
  after=$(cd "$REPO_ROOT" && find skills adapters -type f -exec cksum {} + | sort)
  [ "$before" = "$after" ] || { fail "source tree under skills/ or adapters/ was modified"; return 1; }
  return 0
}
