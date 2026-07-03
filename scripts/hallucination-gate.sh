#!/bin/sh
# hallucination-gate.sh — deterministic, model-free hallucination catcher (feature 022).
#
# Zero-install counterpart to the engine's `check-hallucination` (sibling of coverage-gate.sh):
# POSIX sh + grep/sed/awk, no Python, no engine. Reads the repo FROM DISK (never a context window),
# so it cannot itself hallucinate. Flags four classes that citation-resolution alone misses:
#   claim_code_mismatch   — a REAL symbol the claim names is absent from the cited window
#   fabricated_symbol     — a code-like backtick that exists NOWHERE in the repo
#   unlabeled_claim       — a prose line names a real file/symbol but carries no R10 label
#   unsupported_quantity  — a number in a [fact] is absent from the cited window
# Semantic paraphrase (no shared code token) is NOT caught (documented blind spot).
#
# Usage:  scripts/hallucination-gate.sh <repo> <artifact> [--window N] [--max N]
# Exit:   0 = clean · 1 = findings · 2 = bad usage
set -u

REPO=""; ART=""; WINDOW=3; MAX=50
while [ $# -gt 0 ]; do
  case $1 in
    --window) shift; WINDOW=${1:-3} ;;
    --max) shift; MAX=${1:-50} ;;
    -h|--help) sed -n '2,17p' "$0"; exit 0 ;;
    -*) echo "unknown option: $1" >&2; exit 2 ;;
    *) if [ -z "$REPO" ]; then REPO=$1; elif [ -z "$ART" ]; then ART=$1; else echo "extra arg: $1" >&2; exit 2; fi ;;
  esac
  shift
done
[ -n "$REPO" ] && [ -n "$ART" ] || { echo "usage: hallucination-gate.sh <repo> <artifact> [--window N]" >&2; exit 2; }
[ -d "$REPO" ] || { echo "not a directory: $REPO" >&2; exit 2; }
[ -f "$ART" ] || { echo "no artifact: $ART" >&2; exit 2; }

# --- one concatenation of all source files (the on-disk truth we check claims against) ---
ALL=$(mktemp 2>/dev/null || mktemp -t rso)
trap 'rm -f "$ALL"' EXIT
( cd "$REPO"
  if git rev-parse --git-dir >/dev/null 2>&1; then git ls-files; else find . -type f | sed 's|^\./||'; fi |
    grep -E '\.(py|js|jsx|ts|tsx|mjs|go|rb|rs|java|kt|scala)$' |
    grep -Ev '(^|/)(node_modules|\.venv|venv|vendor|dist|build|\.next|__pycache__)/' || true
) | while IFS= read -r f; do [ -f "$REPO/$f" ] && cat "$REPO/$f"; done > "$ALL"

# claim-bearing artifact? (scopes the unlabeled-claim check; mirrors the engine classifier)
KIND_CLAIM=0
case $ART in *repository-specification*|*/specs/*|*architecture*|*impact*) KIND_CLAIM=1 ;; esac
grep -qE '^##[[:space:]]' "$ART" && KIND_CLAIM=1

is_code_like() { # <token>
  t=$1
  case $t in *"/"*|*:*|*" "*) return 1 ;; esac
  case $t in *"()"|*"("*")" ) return 0 ;; esac
  printf '%s' "$t" | grep -qE '[a-z][A-Z]' && return 0
  case $t in *_*) printf '%s' "$t" | grep -qE '^[A-Za-z_][A-Za-z0-9_]*$' && return 0 ;; esac
  printf '%s' "$t" | grep -qE '^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)+$' && return 0
  return 1
}
exists_in_repo() { grep -Fwq -- "${1%%(*}" "$ALL"; }        # <bare token>
resolvable() { # <token>  (real symbol OR existing file)
  case $1 in *"/"*|*.*) f=${1%%:*}; [ -f "$REPO/$f" ] && return 0 ;; esac
  exists_in_repo "$1"
}
window_of() { # <path> <line>  -> prints the ±WINDOW slice
  awk -v L="$2" -v W="$WINDOW" 'NR>=L-W && NR<=L+W' "$REPO/$1" 2>/dev/null
}

N=0
emit() { N=$((N+1)); [ "$N" -le "$MAX" ] && echo "$ART:$1 $2: $3" >&2; }

lineno=0
while IFS= read -r line || [ -n "$line" ]; do
  lineno=$((lineno + 1))
  strip=$(printf '%s' "$line" | sed 's/[[:space:]]*$//')
  toks=$(printf '%s' "$line" | grep -oE '`[^`]+`' | sed 's/`//g')
  has_label=0; printf '%s' "$line" | grep -qE '\*\*\[(fact|inference|unknown|human)\]\*\*' && has_label=1
  is_fact=0;   printf '%s' "$line" | grep -qE '\*\*\[fact\]\*\*' && is_fact=1
  cit=$(printf '%s' "$line" | grep -oE '[A-Za-z0-9_./-]+:[0-9]+' | head -1)
  citpath=${cit%%:*}; citline=${cit##*:}
  win=""; [ -n "$cit" ] && win=$(window_of "$citpath" "$citline")

  # ---- fabricated_symbol (any non-heading/table line) ----
  case $strip in \#*|\|*|'') : ;; *)
    for t in $toks; do
      is_code_like "$t" || continue
      exists_in_repo "$t" && continue
      emit "$lineno" fabricated_symbol "\`${t%%(*}\` not found in repo"
    done ;;
  esac

  if [ "$is_fact" = 1 ] && [ -n "$cit" ]; then
    # ---- claim_code_mismatch: a REAL symbol token absent from the cited window ----
    for t in $toks; do
      case $t in *"/"*|*:*) continue ;; esac       # skip citations/paths
      is_code_like "$t" || continue
      exists_in_repo "$t" || continue              # real symbol (else it's fabricated, handled above)
      bare=${t%%(*}
      printf '%s' "$win" | grep -Fwq -- "$bare" || emit "$lineno" claim_code_mismatch "\`$bare\` not found near $cit"
    done
    # ---- unsupported_quantity: a number (not in a backtick) absent from the window ----
    prose=$(printf '%s' "$line" | sed 's/`[^`]*`/ /g')
    for num in $(printf '%s' "$prose" | grep -oE '[0-9]+'); do
      printf '%s' "$prose" | grep -qE "v$num|$num\." && continue
      printf '%s' "$win" | grep -qw -- "$num" || emit "$lineno" unsupported_quantity "quantity \"$num\" not found near $cit"
    done
  fi

  # ---- unlabeled_claim: prose line naming a real symbol/file, no label ----
  if [ "$KIND_CLAIM" = 1 ] && [ "$has_label" = 0 ]; then
    case $strip in \#*|\|*|\>*|'```'*|'') : ;; *)
      hit=0
      for t in $toks; do resolvable "$t" && hit=1; done
      if [ "$hit" = 1 ]; then
        words=$(printf '%s' "$line" | sed 's/`[^`]*`/ /g' | grep -oE '[A-Za-z]{2,}' | wc -l)
        [ "$words" -ge 4 ] && emit "$lineno" unlabeled_claim "names a real file/symbol but carries no [fact]/[inference]/… label"
      fi ;;
    esac
  fi
done < "$ART"

[ "$N" -eq 0 ] && { echo "clean"; exit 0; }
exit 1
