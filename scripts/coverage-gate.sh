#!/bin/sh
# coverage-gate.sh — verify every source component is "dealt with" in an artifact.
#
# Portable, dependency-free (POSIX sh + grep/sed/sort/find/git) — no Python, no engine. The
# zero-install counterpart to the engine's symbol-accounting guarantee: it does not *generate*
# coverage, it *verifies* it, so it runs in CI, a pre-commit hook, or a reviewer's box.
#
# A symbol (function/class/…) is "dealt with" if its NAME appears in the artifact, OR its FILE path
# does (the latter covers the "Symbols not yet analyzed" per-file listing). Mirrors the engine's
# `compute_structure` symbol-coverage definition.
#
# Usage:   scripts/coverage-gate.sh <repo> <artifact-file-or-dir> [--files] [--max N]
#   --files   coarser: check every source FILE is mentioned (not every symbol)
#   --max N   list at most N omissions (default 20)
# Exit:   0 = everything covered · 1 = something omitted · 2 = bad usage
set -eu

REPO=""; ART=""; MODE="symbols"; MAX=20
while [ $# -gt 0 ]; do
  case "$1" in
    --files) MODE="files" ;;
    --max) shift; MAX=${1:-20} ;;
    -h|--help) sed -n '2,16p' "$0"; exit 0 ;;
    -*) echo "unknown option: $1" >&2; exit 2 ;;
    *) if [ -z "$REPO" ]; then REPO=$1; elif [ -z "$ART" ]; then ART=$1; else echo "extra arg: $1" >&2; exit 2; fi ;;
  esac
  shift
done
[ -n "$REPO" ] && [ -n "$ART" ] || { echo "usage: coverage-gate.sh <repo> <artifact> [--files] [--max N]" >&2; exit 2; }
[ -d "$REPO" ] || { echo "not a directory: $REPO" >&2; exit 2; }
[ -e "$ART" ] || { echo "no artifact: $ART" >&2; exit 2; }

case "$ART" in /*) ART_ABS=$ART ;; *) ART_ABS=$(pwd)/$ART ;; esac

# --- enumerate source files (git if available, else find), minus vendored/generated ---
list_files() (
  cd "$REPO"
  if git rev-parse --git-dir >/dev/null 2>&1; then git ls-files; else find . -type f | sed 's|^\./||'; fi |
    grep -E '\.(py|js|jsx|ts|tsx|mjs|go|rb|rs|java|kt|scala)$' |
    grep -Ev '(^|/)(node_modules|\.venv|venv|vendor|dist|build|\.next|__pycache__)/' || true
)

# --- "file<TAB>name" for every defined symbol, per-language (best-effort, like structure.py) ---
extract_symbols() (
  cd "$REPO"
  list_files | while IFS= read -r f; do
    case "$f" in
      *.py|*.rb)
        sed -nE 's/^[[:space:]]*(async[[:space:]]+)?def[[:space:]]+([A-Za-z_][A-Za-z0-9_]*).*/\2/p; s/^[[:space:]]*class[[:space:]]+([A-Za-z_][A-Za-z0-9_]*).*/\1/p' "$f" ;;
      *.go)
        sed -nE 's/^[[:space:]]*func[[:space:]]+(\([^)]*\)[[:space:]]*)?([A-Za-z_][A-Za-z0-9_]*).*/\2/p; s/^[[:space:]]*type[[:space:]]+([A-Za-z_][A-Za-z0-9_]*)[[:space:]]+struct.*/\1/p' "$f" ;;
      *.rs)
        sed -nE 's/^[[:space:]]*(pub[[:space:]]+)?(async[[:space:]]+)?fn[[:space:]]+([A-Za-z_][A-Za-z0-9_]*).*/\3/p; s/^[[:space:]]*(pub[[:space:]]+)?(struct|enum|trait)[[:space:]]+([A-Za-z_][A-Za-z0-9_]*).*/\3/p' "$f" ;;
      *.java|*.kt|*.scala)
        sed -nE 's/.*\b(class|interface|enum)[[:space:]]+([A-Za-z_][A-Za-z0-9_]*).*/\2/p' "$f" ;;
      *) # js/ts family
        sed -nE 's/^[[:space:]]*(export[[:space:]]+)?(default[[:space:]]+)?(async[[:space:]]+)?function[[:space:]]*\*?[[:space:]]*([A-Za-z_][A-Za-z0-9_]*).*/\4/p; s/^[[:space:]]*(export[[:space:]]+)?(default[[:space:]]+)?(abstract[[:space:]]+)?class[[:space:]]+([A-Za-z_][A-Za-z0-9_]*).*/\4/p' "$f" ;;
    esac | sed "s|^|$f	|"
  done
)

total=0; covered=0; omitted_file=$(mktemp)
trap 'rm -f "$omitted_file"' EXIT

if [ "$MODE" = files ]; then
  list_files | sort -u | while IFS= read -r f; do echo "	$f"; done > "$omitted_file.in"
else
  extract_symbols | sort -u > "$omitted_file.in"
fi

while IFS='	' read -r f name; do
  [ -n "${name:-}" ] || { [ -n "${f:-}" ] && name=$f || continue; }
  total=$((total + 1))
  target=${name}
  [ "$MODE" = files ] && target=$f
  # covered if the name (symbol) or the file path appears in the artifact
  if grep -rqF -- "$target" "$ART_ABS" 2>/dev/null || { [ "$MODE" = symbols ] && grep -rqF -- "$f" "$ART_ABS" 2>/dev/null; }; then
    covered=$((covered + 1))
  else
    printf '%s\t%s\n' "$f" "$target" >> "$omitted_file"
  fi
done < "$omitted_file.in"
rm -f "$omitted_file.in"

n_omitted=$(wc -l < "$omitted_file" | tr -d ' ')
[ "$total" -gt 0 ] && pct=$(( (covered * 100) / total )) || pct=100
echo "coverage-gate ($MODE): $covered/$total dealt-with (${pct}%) — $n_omitted omitted"
if [ "$n_omitted" -gt 0 ]; then
  echo "omitted (not mentioned in $ART):" >&2
  head -n "$MAX" "$omitted_file" | sed 's/^/  - /' >&2
  [ "$n_omitted" -gt "$MAX" ] && echo "  … ($((n_omitted - MAX)) more)" >&2
  exit 1
fi
exit 0
