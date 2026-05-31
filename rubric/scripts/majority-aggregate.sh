#!/bin/sh
# majority-aggregate.sh — compute a majority-mode gate verdict from a Majority Gate Report.
# OPTIONAL convenience; the normative rule lives in rubric/validation-gate.md (Majority mode).
#
# Reads every "## Aggregated — <repo>" table, locating the Baseline / Aggregate / Low-agree /
# vs Baseline columns by header, and applies:
#   FAIL if any Aggregate < Baseline on any repo, OR a "## Deterministic" table row records fail.
#   HELD if not FAIL and any dimension is Low-agree AND vs Baseline is equal/below (unadjudicated).
#   PASS otherwise.
# Prints PASS|FAIL|HELD. Exit 0 on success, 2 on usage error.
set -u

if [ $# -ne 1 ] || [ ! -f "$1" ]; then
  echo "usage: majority-aggregate.sh <path-to-majority-report.md>" >&2
  exit 2
fi

awk '
function trim(s){ gsub(/^[ \t]+|[ \t]+$/,"",s); return s }
BEGIN{ inagg=0; indet=0; bi=ai=li=vi=0; fail=0; held=0 }
/^## / {
  inagg = ($0 ~ /^## Aggregated/) ? 1 : 0
  indet = ($0 ~ /^## Deterministic/) ? 1 : 0
  if (inagg) { bi=ai=li=vi=0 }   # reset column map at each new aggregated table
  next
}
{
  if (inagg && $0 ~ /^\|/) {
    if ($0 ~ /^\|[ :|-]+$/) next                       # separator row
    n = split($0, c, "|")
    if (bi==0 && $0 ~ /Dimension/ && $0 ~ /Baseline/) {  # header row: map columns by name
      for (i=1;i<=n;i++) { name=trim(c[i])
        if (name=="Baseline") bi=i
        else if (name=="Aggregate") ai=i
        else if (name=="Low-agree") li=i
        else if (name=="vs Baseline") vi=i
      }
      next
    }
    if (bi>0 && ai>0) {                                  # data row
      b=trim(c[bi]); a=trim(c[ai])
      lo=(li>0?trim(c[li]):"no"); vs=(vi>0?trim(c[vi]):"")
      if (b ~ /^[0-9]+$/ && a ~ /^[0-9]+$/) {
        if (a+0 < b+0) fail=1
        if (lo ~ /yes|true/ && (vs=="equal" || vs=="below")) held=1
      }
    }
  }
  if (indet && $0 ~ /^\|/ && tolower($0) ~ /fail/) fail=1
}
END{ if (fail) print "FAIL"; else if (held) print "HELD"; else print "PASS" }
' "$1"
