#!/bin/sh
# Test for gate-verdict.sh — confirms the computed verdict matches each report's recorded verdict.
set -u
DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(CDPATH= cd -- "$DIR/../.." && pwd)
GV="$DIR/gate-verdict.sh"
GATES="$ROOT/rubric/gates"

fail=0
check() { # <report> <expected>
  got=$(sh "$GV" "$1")
  rec=$(sed -n 's/^verdict:[[:space:]]*//p' "$1" | head -n1)
  if [ "$got" = "$2" ] && [ "$got" = "$rec" ]; then
    printf 'ok   %s -> %s (matches recorded)\n' "$(basename "$1")" "$got"
  else
    printf 'FAIL %s: computed=%s expected=%s recorded=%s\n' "$(basename "$1")" "$got" "$2" "$rec" >&2
    fail=1
  fi
}

check "$GATES/VG-2026-06-01-001-secondary-structures.md" PASS
check "$GATES/VG-2026-06-01-002-harmful-edit-demo.md" FAIL

# usage error path
sh "$GV" /nonexistent >/dev/null 2>&1
[ $? -eq 2 ] && printf 'ok   usage error -> exit 2\n' || { printf 'FAIL usage error path\n' >&2; fail=1; }

[ "$fail" -eq 0 ] && echo "all gate-verdict tests passed" || exit 1
