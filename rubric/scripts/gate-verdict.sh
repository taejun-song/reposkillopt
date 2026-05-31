#!/bin/sh
# gate-verdict.sh — compute a validation-gate verdict from a Validation Gate Report.
# OPTIONAL convenience tool; the normative rule lives in rubric/validation-gate.md.
#
# Rule (deterministic, from the report's recorded tables):
#   FAIL if any per-dimension delta cell is negative (candidate < baseline) on any member,
#        OR any deterministic-checks table row records a `fail`.
#   PASS otherwise.
# Prints PASS or FAIL to stdout. Exits 0 on success; 2 on usage error.
set -u

if [ $# -ne 1 ] || [ ! -f "$1" ]; then
  echo "usage: gate-verdict.sh <path-to-VG-report.md>" >&2
  exit 2
fi
report=$1

# 1. Any negative per-dimension delta in a table row? (handles ASCII '-' and U+2212 '−',
#    with optional markdown bold/space, followed by a non-zero digit.)
neg_delta=0
if grep -E '^\|' "$report" | grep -Eq '[-−][[:space:]*]*[1-9]'; then
  neg_delta=1
fi

# 2. Any `fail` recorded inside the Deterministic checks section's table rows?
det_fail=$(awk '
  /^## / { indet = ($0 ~ /Deterministic checks/) ? 1 : 0 }
  indet && /^\|/ && tolower($0) ~ /fail/ { found=1 }
  END { print (found ? 1 : 0) }
' "$report")

if [ "$neg_delta" -eq 1 ] || [ "$det_fail" -eq 1 ]; then
  echo FAIL
else
  echo PASS
fi
exit 0
