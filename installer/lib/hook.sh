# hook.sh — install/uninstall the commit-time pre-commit hook (feature 021). POSIX sh. Requires
# util.sh (copy_atomic, say/info/err) and manifest.sh (manifest_get/upsert/remove_row). Recorded
# under the adapter id `git-hook`. Chains (never clobbers) a pre-existing pre-commit hook.

HOOK_ADAPTER="git-hook"
HOOK_MARKER="reposkillopt-pre-commit-marker"

# hook_dir <root> — absolute hooks dir (honors core.hooksPath + worktrees), or empty if not a git repo.
hook_dir() {
  _r=$1
  git -C "$_r" rev-parse --git-dir >/dev/null 2>&1 || return 1
  _hp=$(git -C "$_r" rev-parse --git-path hooks 2>/dev/null) || return 1
  case $_hp in
    /*) printf '%s' "$_hp" ;;
    *)  printf '%s/%s' "$_r" "$_hp" ;;
  esac
}

# hook_install <root> <src_hook> <tool_version>
hook_install() {
  _root=$1; _src=$2; _ver=$3
  _hd=$(hook_dir "$_root") || { info "not a git repository; skipped hook install: $_root"; return 0; }
  _dest="$_hd/pre-commit"
  _backup="$_hd/pre-commit.reposkillopt-chained"
  _backup_csv=""

  if [ -e "$_dest" ]; then
    if grep -q "$HOOK_MARKER" "$_dest" 2>/dev/null; then
      # Re-install over our own hook: keep any existing chained backup (do NOT double-chain).
      [ -e "$_backup" ] && _backup_csv=",$_backup"
    else
      # A foreign pre-commit hook exists — move it aside and chain it.
      copy_atomic "$_dest" "$_backup" || { err "could not back up existing hook"; return 1; }
      _backup_csv=",$_backup"
    fi
  fi

  copy_atomic "$_src" "$_dest" || { err "could not install hook"; return 1; }
  [ "$DRY_RUN" = "1" ] || chmod +x "$_dest" 2>/dev/null || :
  manifest_upsert "$_root" "$HOOK_ADAPTER" "$_ver" "$_dest$_backup_csv"
  say "Installed pre-commit hook -> $_dest"
  [ -n "$_backup_csv" ] && say "Chained existing hook -> $_backup"
  return 0
}

# hook_uninstall <root>
hook_uninstall() {
  _root=$1
  _rec=$(manifest_get "$_root" "$HOOK_ADAPTER")
  if [ -z "$_rec" ]; then say "$HOOK_ADAPTER not installed at $_root"; return 0; fi
  _paths=$(printf '%s' "$_rec" | awk -F "$TAB" '{print $3}')
  _hook=$(printf '%s' "$_paths" | cut -d, -f1)
  _backup=$(printf '%s' "$_paths" | awk -F, 'NF>1{print $2}')
  if [ "$DRY_RUN" = "1" ]; then
    info "[dry-run] rm $_hook${_backup:+ ; restore $_backup -> $_hook}"
  else
    rm -f -- "$_hook"
    if [ -n "$_backup" ] && [ -e "$_backup" ]; then
      mv -- "$_backup" "$_hook" && say "Restored chained hook -> $_hook"
    fi
  fi
  manifest_remove_row "$_root" "$HOOK_ADAPTER"
  say "Uninstalled $HOOK_ADAPTER from $_root"
  return 0
}
