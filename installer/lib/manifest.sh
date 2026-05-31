# manifest.sh — per-target-repo install manifest (contracts/install-manifest.contract.md).
# POSIX sh. TAB-separated: adapter<TAB>version<TAB>paths_csv<TAB>timestamp. Requires util.sh.

TAB=$(printf '\t')

# manifest_path <target_root>
manifest_path() { printf '%s' "$1/.reposkillopt/.install-manifest"; }

# manifest_get <target_root> <adapter> — print the matching record line (or nothing).
manifest_get() {
  _mp=$(manifest_path "$1")
  [ -f "$_mp" ] || return 0
  awk -F "$TAB" -v a="$2" '$1==a {print; exit}' "$_mp"
}

# manifest_version <target_root> <adapter> — print recorded version (or nothing).
manifest_version() {
  manifest_get "$1" "$2" | awk -F "$TAB" '{print $2}'
}

# manifest_upsert <target_root> <adapter> <version> <paths_csv>
manifest_upsert() {
  _mp=$(manifest_path "$1"); _a=$2; _v=$3; _p=$4; _ts=$(timestamp)
  [ "$DRY_RUN" = "1" ] && return 0
  mkdir -p -- "$(dirname -- "$_mp")" || return 1
  _tmp="$_mp.tmp.$$"
  if [ -f "$_mp" ]; then awk -F "$TAB" -v a="$_a" '$1!=a' "$_mp" > "$_tmp"; else : > "$_tmp"; fi
  printf '%s\t%s\t%s\t%s\n' "$_a" "$_v" "$_p" "$_ts" >> "$_tmp"
  mv -- "$_tmp" "$_mp"
}

# manifest_remove_row <target_root> <adapter> — drop the row; remove file if now empty.
manifest_remove_row() {
  _mp=$(manifest_path "$1"); _a=$2
  [ -f "$_mp" ] || return 0
  [ "$DRY_RUN" = "1" ] && return 0
  _tmp="$_mp.tmp.$$"
  awk -F "$TAB" -v a="$_a" '$1!=a' "$_mp" > "$_tmp"
  if [ -s "$_tmp" ]; then mv -- "$_tmp" "$_mp"; else rm -f -- "$_tmp" "$_mp"; fi
}

# manifest_list <target_root> — human-readable rows, or a notice if empty.
manifest_list() {
  _mp=$(manifest_path "$1")
  if [ ! -f "$_mp" ] || [ ! -s "$_mp" ]; then
    say "no adapters installed"
    return 0
  fi
  while IFS="$TAB" read -r _a _v _p _ts; do
    [ -n "$_a" ] && say "$_a  $_v  $_p  $_ts"
  done < "$_mp"
}
