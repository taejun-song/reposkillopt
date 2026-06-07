# 006 US3 — legacy AGENTS.md safety + namespaced uninstall.
run_test() {
  # (a) foreign AGENTS.md, no --force -> refuse (exit 6), file unchanged
  d="$WORK/foreign"; mkdir -p "$d"; printf 'user agent rules\n' > "$d/AGENTS.md"
  before=$(cat "$d/AGENTS.md")
  "$INSTALL" --agent codex-agentsmd --dest "$d" >/dev/null 2>&1
  assert_exit "$?" 6 "foreign AGENTS.md refused with EX_REFUSED" || return 1
  assert_eq "$(cat "$d/AGENTS.md")" "$before" "refused install left AGENTS.md unchanged" || return 1
  assert_nofile "$d/AGENTS.md.bak" "no backup written on refusal" || return 1

  # (b) --force -> backup original to .bak, then write the adapter
  "$INSTALL" --agent codex-agentsmd --dest "$d" --force >/dev/null 2>&1 || { fail "--force install failed"; return 1; }
  assert_file "$d/AGENTS.md.bak" "backup created under --force" || return 1
  assert_eq "$(cat "$d/AGENTS.md.bak")" "$before" "backup preserves original bytes" || return 1
  assert_same "$d/AGENTS.md" "$REPO_ROOT/adapters/codex/AGENTS.md" "AGENTS.md now the adapter" || return 1

  # (c) a RepoSkillOpt-managed AGENTS.md upgrades in place (idempotent re-install, no new refusal)
  out=$("$INSTALL" --agent codex-agentsmd --dest "$d"); rc=$?
  assert_exit "$rc" 0 "managed AGENTS.md re-install exit 0" || return 1
  printf '%s' "$out" | grep -qi "already up to date" || { fail "managed re-install not idempotent"; return 1; }

  # (d) namespaced uninstall removes the file AND the empty repo-skillopt/ dir, nothing else
  d2="$WORK/uni"; mkdir -p "$d2/.agents/skills/other-skill"   # a sibling skill that must survive
  : > "$d2/.agents/skills/other-skill/SKILL.md"
  "$INSTALL" --agent agents --dest "$d2" >/dev/null || return 1
  assert_file "$d2/.agents/skills/repo-skillopt/SKILL.md" "agents installed" || return 1
  "$INSTALL" --uninstall agents --dest "$d2" >/dev/null || return 1
  assert_nofile "$d2/.agents/skills/repo-skillopt/SKILL.md" "skill file removed" || return 1
  [ -d "$d2/.agents/skills/repo-skillopt" ] && { fail "empty repo-skillopt/ dir not removed"; return 1; } || true
  assert_file "$d2/.agents/skills/other-skill/SKILL.md" "sibling skill untouched" || return 1
  return 0
}
