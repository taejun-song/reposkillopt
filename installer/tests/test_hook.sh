# Feature 021 — pre-commit gate hook: install/chain/bypass/detect/uninstall (US2/US3/US4).
# Deterministic + model-free: the engine is stubbed via REPOSKILLOPT_ENGINE_CMD; only the hook's
# control flow and the installer lifecycle are exercised. Runs under bash AND dash (via run.sh).

_mkrepo() { # <dir>
  mkdir -p "$1" && git init -q "$1" \
    && git -C "$1" config user.email t@t && git -C "$1" config user.name t
}

_stub_engine() { # <path> <exit_code> — writes a stub that records a call and exits <code>
  printf '#!/bin/sh\necho CALLED >> "%s.calls"\nexit %s\n' "$1" "$2" > "$1"
  chmod +x "$1"
}

run_test() {
  command -v git >/dev/null 2>&1 || { echo "skip: git unavailable"; return 0; }

  # ---------- Case 1: install (no foreign hook) — marker + manifest row ----------
  r1="$WORK/r1"; _mkrepo "$r1"
  "$INSTALL" --hook --dest "$r1" >/dev/null || { fail "install --hook failed"; return 1; }
  h1="$r1/.git/hooks/pre-commit"
  assert_file "$h1" "hook installed" || return 1
  grep -q "reposkillopt-pre-commit-marker" "$h1" || { fail "marker missing in hook"; return 1; }
  assert_nofile "$r1/.git/hooks/pre-commit.reposkillopt-chained" "no backup when no foreign hook" || return 1
  "$INSTALL" --list --dest "$r1" | grep -q "git-hook" || { fail "list missing git-hook row"; return 1; }

  # ---------- Case 2: source-only commit is a no-op (engine NOT called) ----------
  echo "x = 1" > "$r1/src.py"; git -C "$r1" add src.py
  st="$WORK/eng_noop"; _stub_engine "$st" 0
  ( cd "$r1" && REPOSKILLOPT_ENGINE_CMD="sh $st" sh "$h1" ); rc=$?
  assert_exit "$rc" 0 "source-only commit no-op exit 0" || return 1
  assert_nofile "$st.calls" "engine not called on source-only commit" || return 1

  # stage a .reposkillopt artifact for the remaining engine-path checks
  mkdir -p "$r1/.reposkillopt/specs"; echo "# spec" > "$r1/.reposkillopt/specs/s.md"
  git -C "$r1" add .reposkillopt/specs/s.md

  # ---------- Case 3: engine exit code is propagated (blocks the commit) ----------
  stf="$WORK/eng_fail"; _stub_engine "$stf" 1
  ( cd "$r1" && REPOSKILLOPT_ENGINE_CMD="sh $stf" sh "$h1" ); rc=$?
  assert_exit "$rc" 1 "engine non-zero blocks commit" || return 1
  assert_file "$stf.calls" "engine called when .reposkillopt staged" || return 1

  # ---------- Case 4: bypass env makes the hook a no-op even with a failing engine ----------
  ( cd "$r1" && REPOSKILLOPT_HOOK=off REPOSKILLOPT_ENGINE_CMD="sh $stf" sh "$h1" ); rc=$?
  assert_exit "$rc" 0 "REPOSKILLOPT_HOOK=off bypass exit 0" || return 1

  # ---------- Case 5: engine unreachable -> block-and-report, no hang ----------
  mkdir -p "$WORK/fakebin"; printf '#!/bin/sh\nexit 1\n' > "$WORK/fakebin/python3"; chmod +x "$WORK/fakebin/python3"
  ( cd "$r1" && unset REPOSKILLOPT_ENGINE_CMD; PATH="$WORK/fakebin:$PATH" sh "$h1" ); rc=$?
  assert_exit "$rc" 1 "engine-unreachable blocks (exit 1)" || return 1

  # ---------- Case 6: chaining — a pre-existing hook is preserved and blocks ----------
  r2="$WORK/r2"; _mkrepo "$r2"
  fhook="$r2/.git/hooks/pre-commit"
  printf '#!/bin/sh\nexit 3\n' > "$fhook"; chmod +x "$fhook"
  foreign_saved="$WORK/foreign.saved"; cp "$fhook" "$foreign_saved"
  "$INSTALL" --hook --dest "$r2" >/dev/null || { fail "install over foreign failed"; return 1; }
  assert_file "$r2/.git/hooks/pre-commit.reposkillopt-chained" "foreign hook chained to backup" || return 1
  assert_same "$r2/.git/hooks/pre-commit.reposkillopt-chained" "$foreign_saved" "backup == original foreign" || return 1
  # the chained foreign hook (exit 3) must block before any gating
  stok="$WORK/eng_ok"; _stub_engine "$stok" 0
  ( cd "$r2" && REPOSKILLOPT_ENGINE_CMD="sh $stok" sh "$r2/.git/hooks/pre-commit" ); rc=$?
  assert_exit "$rc" 3 "chained foreign hook non-zero blocks first" || return 1
  assert_nofile "$stok.calls" "engine not reached when chained hook blocks" || return 1

  # ---------- Case 7: re-install does not double-chain ----------
  "$INSTALL" --hook --dest "$r2" >/dev/null || { fail "re-install failed"; return 1; }
  assert_same "$r2/.git/hooks/pre-commit.reposkillopt-chained" "$foreign_saved" "re-install keeps original backup (no double-chain)" || return 1

  # ---------- Case 8: uninstall restores the chained hook exactly + drops the row ----------
  "$INSTALL" --uninstall git-hook --dest "$r2" >/dev/null || { fail "uninstall git-hook failed"; return 1; }
  assert_same "$r2/.git/hooks/pre-commit" "$foreign_saved" "uninstall restored original foreign hook byte-for-byte" || return 1
  assert_nofile "$r2/.git/hooks/pre-commit.reposkillopt-chained" "backup removed after restore" || return 1
  "$INSTALL" --list --dest "$r2" 2>/dev/null | grep -q "git-hook" && { fail "git-hook row not removed"; return 1; }

  # uninstall with no foreign hook removes our hook entirely
  "$INSTALL" --uninstall git-hook --dest "$r1" >/dev/null || { fail "uninstall (no-foreign) failed"; return 1; }
  assert_nofile "$r1/.git/hooks/pre-commit" "our hook removed when nothing to restore" || return 1

  # ---------- Case 9: non-git dir — warn + skip, no hook, exit 0 ----------
  r3="$WORK/r3"; mkdir -p "$r3"
  "$INSTALL" --hook --dest "$r3" >/dev/null 2>&1; rc=$?
  assert_exit "$rc" 0 "non-git --hook skips cleanly" || return 1
  assert_nofile "$r3/.git/hooks/pre-commit" "no hook created in non-git dir" || return 1

  return 0
}
