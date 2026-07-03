#!/bin/sh
# Tests for scripts/hallucination-gate.sh — deterministic, no Python for the gate itself.
# The PARITY block additionally invokes the engine (if importable) and asserts the shell gate and
# `check-hallucination` agree on clean-vs-flagged + finding kinds for the shared fixtures.
# (No `set -e`: the gate is invoked on cases that intentionally exit non-zero.)
set -u
HERE=$(cd "$(dirname "$0")/../.." && pwd)
GATE="$HERE/scripts/hallucination-gate.sh"
ENGINE="$HERE/engine"
fails=0
check() { if eval "$2"; then echo "ok   - $1"; else echo "FAIL - $1"; fails=$((fails+1)); fi; }

REPO=$(mktemp -d); mkdir -p "$REPO/pkg"
printf 'def create_app():\n    return 1\n\n\nclass Service:\n    def run(self):\n        return 2\n' > "$REPO/pkg/app.py"

hdr() { printf '# Repository Specification\n\n## Architecture\nOverview.\n\n'; }

# --- fixtures (one clean + one per class) ---
FX=$REPO/.reposkillopt/specs; mkdir -p "$FX"

{ hdr; printf '**[fact]** the `create_app` factory `pkg/app.py:1`\n'; } > "$FX/clean.md"
{ hdr; printf '**[fact]** the `create_app` factory `pkg/app.py:6`\n'; } > "$FX/mismatch.md"
{ hdr; printf '**[fact]** uses `create_sessionX` `pkg/app.py:1`\n'; } > "$FX/fabricated.md"
{ hdr; printf 'The `create_app` factory builds the app and returns it.\n'; } > "$FX/unlabeled.md"
{ hdr; printf '**[fact]** exposes 7 routes `pkg/app.py:1`\n'; } > "$FX/quantity.md"

# 1) clean -> exit 0
sh "$GATE" "$REPO" "$FX/clean.md" >/dev/null 2>&1; check "clean fixture -> exit 0" "[ $? -eq 0 ]"

# 2) each class -> exit 1 + the right kind
for pair in "mismatch:claim_code_mismatch" "fabricated:fabricated_symbol" "unlabeled:unlabeled_claim" "quantity:unsupported_quantity"; do
  fx=${pair%%:*}; kind=${pair##*:}
  out=$(sh "$GATE" "$REPO" "$FX/$fx.md" 2>&1); rc=$?
  check "$fx -> exit 1" "[ $rc -eq 1 ]"
  check "$fx -> reports $kind" "printf '%s' \"\$out\" | grep -q $kind"
done

# 3) usage error -> exit 2
sh "$GATE" "$REPO" >/dev/null 2>&1; check "missing arg -> exit 2" "[ $? -eq 2 ]"

# 4) PARITY with the engine (skip if engine not importable)
if PYTHONPATH="$ENGINE" python3 -c "import reposkillopt_engine" >/dev/null 2>&1; then
  for fx in clean mismatch fabricated unlabeled quantity; do
    sh "$GATE" "$REPO" "$FX/$fx.md" >/dev/null 2>&1; g_rc=$?
    PYTHONPATH="$ENGINE" python3 -m reposkillopt_engine check-hallucination --repo "$REPO" --file "$FX/$fx.md" >/dev/null 2>&1; e_rc=$?
    # both clean (0) or both flagged (1)
    check "parity verdict: $fx" "[ \$( [ $g_rc -eq 0 ] && echo 0 || echo 1 ) -eq \$( [ $e_rc -eq 0 ] && echo 0 || echo 1 ) ]"
    if [ "$fx" != clean ]; then
      gk=$(sh "$GATE" "$REPO" "$FX/$fx.md" 2>&1 | sed -E 's/.* ([a-z_]+): .*/\1/' | sort -u)
      ek=$(PYTHONPATH="$ENGINE" python3 -m reposkillopt_engine check-hallucination --repo "$REPO" --file "$FX/$fx.md" 2>&1 | sed -E 's/.* ([a-z_]+): .*/\1/' | sort -u)
      check "parity kinds: $fx" "[ \"\$(printf '%s' \"$gk\")\" = \"\$(printf '%s' \"$ek\")\" ]"
    fi
  done
else
  echo "ok   - parity skipped (engine not importable)"
fi

[ "$fails" -eq 0 ] || { echo "$fails failed"; exit 1; }
echo "all hallucination-gate tests passed"
exit 0
