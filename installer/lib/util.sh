# util.sh — shared helpers for reposkillopt-install. POSIX sh. Sourced, not executed.

# Exit codes (contracts/cli-interface.contract.md)
EX_OK=0
EX_ERR=1
EX_USAGE=2
EX_DETECT=3
EX_TARGET=4
EX_DOWNGRADE=5
EX_REFUSED=6   # legacy AGENTS.md mode declined to overwrite a foreign file

# DRY_RUN is set by the CLI; default off.
: "${DRY_RUN:=0}"

# Logging: user-facing summary to stdout; diagnostics/errors to stderr.
say()  { printf '%s\n' "$*"; }
info() { printf '%s\n' "$*" >&2; }
err()  { printf 'error: %s\n' "$*" >&2; }

timestamp() { date -u +%Y-%m-%dT%H:%M:%SZ; }

# read_field <file> <key> — value of a `key: value` line (YAML front matter or
# the HTML-comment metadata block; both store the key at column 0). First match wins.
read_field() {
  [ -f "$1" ] || return 1
  grep -E "^$2:[[:space:]]*" "$1" 2>/dev/null | head -n1 | sed -E "s/^$2:[[:space:]]*//; s/[[:space:]]*$//"
}

# semver_cmp <a> <b> — echoes eq | gt | lt comparing up to three numeric components.
semver_cmp() {
  _i=1
  while [ "$_i" -le 3 ]; do
    _pa=$(printf '%s' "$1" | cut -d. -f"$_i" | tr -cd '0-9'); _pa=${_pa:-0}
    _pb=$(printf '%s' "$2" | cut -d. -f"$_i" | tr -cd '0-9'); _pb=${_pb:-0}
    if [ "$_pa" -gt "$_pb" ]; then echo gt; return 0; fi
    if [ "$_pa" -lt "$_pb" ]; then echo lt; return 0; fi
    _i=$((_i + 1))
  done
  echo eq
}

# _mktemp_in <dir> — temp file inside <dir> (same filesystem → atomic rename).
_mktemp_in() {
  mktemp "$1/.rso.XXXXXX" 2>/dev/null || {
    _t="$1/.rso.$$.$(awk 'BEGIN{srand();printf "%d",srand()*99999}' 2>/dev/null || echo $$)"
    : > "$_t" && printf '%s' "$_t"
  }
}

# copy_atomic <src> <dst> — copy via temp file + rename. Honors DRY_RUN.
copy_atomic() {
  _src=$1; _dst=$2; _dir=$(dirname -- "$_dst")
  if [ "$DRY_RUN" = "1" ]; then info "[dry-run] install $_src -> $_dst"; return 0; fi
  mkdir -p -- "$_dir" || { err "cannot create $_dir"; return 1; }
  _tmp=$(_mktemp_in "$_dir") || { err "cannot create temp in $_dir"; return 1; }
  cp -- "$_src" "$_tmp" || { rm -f -- "$_tmp"; err "copy failed: $_src"; return 1; }
  mv -- "$_tmp" "$_dst" || { rm -f -- "$_tmp"; err "rename failed: $_dst"; return 1; }
  return 0
}
