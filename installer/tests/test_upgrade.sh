# US4 — version verify + upgrade; refuse downgrade without --force.
# Derives the source version from the adapter so it survives canonical version bumps.
run_test() {
  d="$WORK"
  man="$d/.reposkillopt/.install-manifest"; mkdir -p "$d/.reposkillopt"
  tab=$(printf '\t')

  # The version the installer will record == the adapter's canonical_version.
  src=$(grep -m1 '^canonical_version:' "$REPO_ROOT/adapters/claude-code/SKILL.md" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
  [ -n "$src" ] || { fail "could not read source canonical_version"; return 1; }
  older="0.0.1"   # always below any real release
  newer="9.9.9"   # always above any real release

  # older install recorded -> install (src) upgrades and reports a delta
  printf 'claude-code%s%s%s.claude/skills/repo-skillopt/SKILL.md%s2026-01-01T00:00:00Z\n' "$tab" "$older" "$tab" "$tab" > "$man"
  out=$("$INSTALL" --agent claude-code --dest "$d"); assert_exit "$?" 0 "upgrade exit 0" || return 1
  printf '%s' "$out" | grep -qi "upgraded" || { fail "no upgrade reported"; return 1; }
  v=$(awk -F"$tab" '$1=="claude-code"{print $2}' "$man")
  assert_eq "$v" "$src" "version bumped to source" || return 1

  # equal -> already up to date
  out2=$("$INSTALL" --agent claude-code --dest "$d")
  printf '%s' "$out2" | grep -qi "already up to date" || { fail "equal not reported up-to-date"; return 1; }

  # newer installed, older source, no --force -> exit 5, unchanged
  printf 'claude-code%s%s%s.claude/skills/repo-skillopt/SKILL.md%s2026-01-01T00:00:00Z\n' "$tab" "$newer" "$tab" "$tab" > "$man"
  "$INSTALL" --agent claude-code --dest "$d" >/dev/null 2>&1; assert_exit "$?" 5 "downgrade refused exit 5" || return 1
  v2=$(awk -F"$tab" '$1=="claude-code"{print $2}' "$man")
  assert_eq "$v2" "$newer" "version unchanged after refusal" || return 1

  # with --force -> downgrade recorded
  "$INSTALL" --agent claude-code --dest "$d" --force >/dev/null 2>&1; assert_exit "$?" 0 "forced downgrade exit 0" || return 1
  v3=$(awk -F"$tab" '$1=="claude-code"{print $2}' "$man")
  assert_eq "$v3" "$src" "downgrade recorded with --force" || return 1
  return 0
}
