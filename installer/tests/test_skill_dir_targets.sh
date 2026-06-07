# 006 US1/US2 — skill-directory targets: native paths, canonical content, AGENTS.md untouched, offline.
run_test() {
  canon="$REPO_ROOT/skills/repo-skillopt/SKILL.md"

  # each skill-capable target lands at its documented namespaced path with canonical content
  for spec in "cursor:.cursor/skills/repo-skillopt/SKILL.md" \
              "agents:.agents/skills/repo-skillopt/SKILL.md" \
              "codex:.agents/skills/repo-skillopt/SKILL.md" \
              "opencode:.opencode/skills/repo-skillopt/SKILL.md"; do
    id=${spec%%:*}; rel=${spec#*:}
    d="$WORK/$id"; mkdir -p "$d"
    out=$("$INSTALL" --agent "$id" --dest "$d") || { fail "install $id failed"; return 1; }
    assert_file "$d/$rel" "$id placed at $rel" || return 1
    assert_same "$d/$rel" "$canon" "$id content == canonical skill" || return 1
    printf '%s' "$out" | grep -q "$rel" || { fail "$id summary lacks path"; return 1; }
  done

  # SC-001: a pre-existing foreign AGENTS.md is never touched by a skill-dir install
  d="$WORK/withagents"; mkdir -p "$d"; printf 'my own rules\n' > "$d/AGENTS.md"
  before=$(cat "$d/AGENTS.md")
  "$INSTALL" --agent agents --dest "$d" >/dev/null || return 1
  assert_file "$d/.agents/skills/repo-skillopt/SKILL.md" "agents installed alongside AGENTS.md" || return 1
  assert_eq "$(cat "$d/AGENTS.md")" "$before" "foreign AGENTS.md unchanged" || return 1

  # --list reports the new target + path
  "$INSTALL" --dest "$d" --list | grep -q ".agents/skills/repo-skillopt/SKILL.md" || { fail "--list lacks agents path"; return 1; }

  # dry-run writes nothing
  d2="$WORK/dry"; mkdir -p "$d2"
  "$INSTALL" --agent cursor --dest "$d2" --dry-run >/dev/null || return 1
  assert_nofile "$d2/.cursor/skills/repo-skillopt/SKILL.md" "cursor dry-run wrote nothing" || return 1

  # offline: the installer makes no network calls (sanity — no curl/wget invoked in lib)
  grep -rqE 'curl|wget' "$REPO_ROOT/installer/reposkillopt-install" "$REPO_ROOT/installer/lib/" \
    && { fail "installer references network tools"; return 1; } || true
  return 0
}
