#!/bin/sh
# Tests for scripts/coverage-gate.sh — deterministic, no Python.
# (No `set -e`: the gate is invoked on cases that intentionally exit non-zero.)
set -u
HERE=$(cd "$(dirname "$0")/../.." && pwd)
GATE="$HERE/scripts/coverage-gate.sh"
fails=0
check() { if eval "$2"; then echo "ok   - $1"; else echo "FAIL - $1"; fails=$((fails+1)); fi; }

REPO=$(mktemp -d); mkdir -p "$REPO/pkg"
printf 'def create_app():\n    return 1\n\n\nclass Service:\n    pass\n' > "$REPO/pkg/app.py"

# 1) artifact mentions both symbols -> PASS (exit 0)
printf '# Spec\ncreate_app and Service are both analyzed.\n' > "$REPO/full.md"
sh "$GATE" "$REPO" "$REPO/full.md" >/dev/null 2>&1; rc=$?
check "all symbols covered -> exit 0" "[ $rc -eq 0 ]"

# 2) artifact omits Service -> FAIL (exit 1) and names it
printf '# Spec\nonly create_app is analyzed.\n' > "$REPO/partial.md"
out=$(sh "$GATE" "$REPO" "$REPO/partial.md" 2>&1); rc=$?
check "omitted symbol -> exit 1" "[ $rc -eq 1 ]"
check "omitted symbol is named" "printf '%s' \"\$out\" | grep -q Service"

# 3) file-path listing (Symbols not yet analyzed) covers via path -> PASS
printf '# Spec\n## Symbols not yet analyzed\n- pkg/app.py: 2 symbols\n' > "$REPO/listed.md"
sh "$GATE" "$REPO" "$REPO/listed.md" >/dev/null 2>&1; rc=$?
check "file-path listing covers symbols -> exit 0" "[ $rc -eq 0 ]"

# 4) --files mode (path mentioned) -> PASS
sh "$GATE" "$REPO" "$REPO/listed.md" --files >/dev/null 2>&1; rc=$?
check "--files mode -> exit 0" "[ $rc -eq 0 ]"

# 5) bad usage (missing artifact) -> exit 2
sh "$GATE" "$REPO" >/dev/null 2>&1; rc=$?
check "missing artifact arg -> exit 2" "[ $rc -eq 2 ]"

[ "$fails" -eq 0 ] && echo "ALL PASS" || { echo "$fails FAILED"; exit 1; }
