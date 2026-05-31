# US1 — explicit install for each target, byte-equality, summary, dry-run, usage errors, idempotency.
run_test() {
  out=$("$INSTALL" --agent claude-code --dest "$WORK") || return 1
  assert_file "$WORK/.claude/skills/repo-skillopt/SKILL.md" "claude-code installed" || return 1
  assert_same "$WORK/.claude/skills/repo-skillopt/SKILL.md" "$REPO_ROOT/adapters/claude-code/SKILL.md" "claude-code bytes equal" || return 1
  printf '%s' "$out" | grep -q "canonical_version" || { fail "summary lacks version"; return 1; }

  # idempotent re-install
  out2=$("$INSTALL" --agent claude-code --dest "$WORK"); rc=$?
  assert_exit "$rc" 0 "reinstall exit 0" || return 1
  printf '%s' "$out2" | grep -qi "already up to date" || { fail "reinstall not idempotent"; return 1; }

  # codex / opencode
  d2="$WORK/codex"; mkdir -p "$d2"
  "$INSTALL" --agent codex --dest "$d2" >/dev/null || return 1
  assert_same "$d2/AGENTS.md" "$REPO_ROOT/adapters/codex/AGENTS.md" "codex bytes equal" || return 1
  d3="$WORK/oc"; mkdir -p "$d3"
  "$INSTALL" --agent opencode --dest "$d3" >/dev/null || return 1
  assert_same "$d3/AGENTS.md" "$REPO_ROOT/adapters/opencode/AGENTS.md" "opencode bytes equal" || return 1

  # generic places two files
  d4="$WORK/gen"; mkdir -p "$d4"
  "$INSTALL" --agent generic --dest "$d4" >/dev/null || return 1
  assert_same "$d4/skill.md" "$REPO_ROOT/adapters/generic/skill.md" "generic skill bytes" || return 1
  assert_same "$d4/system-prompt-fragment.md" "$REPO_ROOT/adapters/generic/system-prompt-fragment.md" "generic fragment bytes" || return 1

  # dry-run writes nothing
  d5="$WORK/dry"; mkdir -p "$d5"
  "$INSTALL" --agent claude-code --dest "$d5" --dry-run >/dev/null || return 1
  assert_nofile "$d5/.claude/skills/repo-skillopt/SKILL.md" "dry-run wrote no file" || return 1
  assert_nofile "$d5/.reposkillopt/.install-manifest" "dry-run wrote no manifest" || return 1

  # unknown agent -> exit 2
  "$INSTALL" --agent bogus --dest "$WORK" >/dev/null 2>&1; assert_exit "$?" 2 "unknown agent exit 2" || return 1
  # generic without --dest -> exit 2
  ( cd "$WORK" && "$INSTALL" --agent generic >/dev/null 2>&1 ); assert_exit "$?" 2 "generic needs --dest" || return 1
  # non-existent target -> exit 4
  "$INSTALL" --agent claude-code --dest "$WORK/nope" >/dev/null 2>&1; assert_exit "$?" 4 "missing dest exit 4" || return 1
  return 0
}
