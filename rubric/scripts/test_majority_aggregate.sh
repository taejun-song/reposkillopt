#!/bin/sh
# Test for majority-aggregate.sh — computed verdict must match each report's recorded verdict.
set -u
DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(CDPATH= cd -- "$DIR/../.." && pwd)
MA="$DIR/majority-aggregate.sh"
GATES="$ROOT/rubric/gates"

fail=0
check() { # <report> <expected>
  got=$(sh "$MA" "$1")
  rec=$(sed -n 's/^verdict:[[:space:]]*//p' "$1" | head -n1)
  if [ "$got" = "$2" ] && [ "$got" = "$rec" ]; then
    printf 'ok   %s -> %s (matches recorded)\n' "$(basename "$1")" "$got"
  else
    printf 'FAIL %s: computed=%s expected=%s recorded=%s\n' "$(basename "$1")" "$got" "$2" "$rec" >&2
    fail=1
  fi
}

check "$GATES/VG-2026-06-02-001-majority-pass.md" PASS
check "$GATES/VG-2026-06-02-002-majority-held.md" HELD

# usage error path
sh "$MA" /nonexistent >/dev/null 2>&1
[ $? -eq 2 ] && printf 'ok   usage error -> exit 2\n' || { printf 'FAIL usage error path\n' >&2; fail=1; }

[ "$fail" -eq 0 ] && echo "all majority-aggregate tests passed" || exit 1
