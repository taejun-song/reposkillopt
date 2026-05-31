# US3 — --scaffold creates the four dirs; existing artifacts preserved; dry-run creates nothing.
run_test() {
  d="$WORK"
  "$INSTALL" --agent claude-code --dest "$d" --scaffold >/dev/null || return 1
  for sub in specs feedback rollouts proposals; do
    [ -d "$d/.reposkillopt/$sub" ] || { fail "scaffold missing $sub"; return 1; }
  done

  # preservation: add an artifact, then trigger another install+scaffold (different agent, not yet recorded)
  echo keep > "$d/.reposkillopt/specs/keepme.md"
  "$INSTALL" --agent codex --dest "$d" --scaffold >/dev/null || return 1
  assert_file "$d/.reposkillopt/specs/keepme.md" "scaffold preserved file" || return 1
  assert_eq "$(cat "$d/.reposkillopt/specs/keepme.md")" "keep" "scaffold preserved content" || return 1

  # dry-run scaffold creates nothing
  d2="$WORK/dry"; mkdir -p "$d2"
  "$INSTALL" --agent claude-code --dest "$d2" --scaffold --dry-run >/dev/null || return 1
  assert_nofile "$d2/.reposkillopt/specs" "dry-run created no scaffold" || return 1
  return 0
}
