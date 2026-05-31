#!/bin/sh
# POSIX test runner for the RepoSkillOpt installer.
# Discovers installer/tests/test_*.sh and runs each in its own temp workspace.
# Each test_*.sh must define run_test() and use the helpers exported below.
# Exits non-zero if any test fails.

set -u

TESTS_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$TESTS_DIR/../.." && pwd)
INSTALL="$REPO_ROOT/installer/reposkillopt-install"
BOOTSTRAP="$REPO_ROOT/install.sh"
export TESTS_DIR REPO_ROOT INSTALL BOOTSTRAP

PASS=0
FAIL=0
FAILED_NAMES=""

# --- assertion helpers (used by test files) ---
fail() { printf 'ASSERT FAIL: %s\n' "$*" >&2; return 1; }

assert_eq() { # <actual> <expected> <msg>
  [ "$1" = "$2" ] || fail "$3 (got '$1', want '$2')"; }

assert_exit() { # <got_code> <want_code> <msg>
  [ "$1" = "$2" ] || fail "$3 (exit got $1, want $2)"; }

assert_file() { # <path> <msg>
  [ -f "$1" ] || fail "$2 (missing file $1)"; }

assert_nofile() { # <path> <msg>
  [ ! -e "$1" ] || fail "$2 (unexpected file $1)"; }

assert_same() { # <fileA> <fileB> <msg>
  cmp -s "$1" "$2" || fail "$3 ($1 != $2)"; }

assert_contains() { # <file> <substr> <msg>
  grep -qF "$2" "$1" 2>/dev/null || fail "$3 (no '$2' in $1)"; }

# (helpers are inherited by the sourced test subshell; no export needed.)

# mktemp portability
_mktempd() { mktemp -d 2>/dev/null || mktemp -d -t rso 2>/dev/null; }

run_one() { # <test_file>
  tf=$1
  name=$(basename "$tf" .sh)
  WORK=$(_mktempd) || { printf 'could not mktemp for %s\n' "$name" >&2; return 1; }
  export WORK
  # shellcheck disable=SC1090
  ( . "$tf"; run_test )
  rc=$?
  rm -rf "$WORK"
  if [ "$rc" -eq 0 ]; then
    PASS=$((PASS+1)); printf 'ok   %s\n' "$name"
  else
    FAIL=$((FAIL+1)); FAILED_NAMES="$FAILED_NAMES $name"; printf 'FAIL %s\n' "$name"
  fi
}

for tf in "$TESTS_DIR"/test_*.sh; do
  [ -f "$tf" ] || continue
  run_one "$tf"
done

printf '\n%d passed, %d failed\n' "$PASS" "$FAIL"
if [ "$FAIL" -ne 0 ]; then
  printf 'failed:%s\n' "$FAILED_NAMES" >&2
  exit 1
fi
exit 0
