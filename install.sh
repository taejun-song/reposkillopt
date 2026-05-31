#!/bin/sh
# install.sh — one-line bootstrap for the RepoSkillOpt CLI installer.
#
# Local / cloned use:
#   ./install.sh --agent claude-code
# Ephemeral use (no persistent install):
#   curl -fsSL https://raw.githubusercontent.com/taejun-song/reposkillopt/main/install.sh | sh -s -- --agent claude-code
#
# It resolves the installer next to itself when run from a clone/download, otherwise it
# fetches a pinned tarball of the repo to a temp dir and runs from there. All arguments are
# passed straight through to installer/reposkillopt-install.
set -u

RSO_REF="${RSO_REF:-main}"
RSO_REPO="${RSO_REPO:-taejun-song/reposkillopt}"

# Case 1: running from a clone/download — the installer sits next to this script.
_self_dir=""
case "${0:-}" in
  ''|sh|-sh|dash|-dash|/bin/sh|bash|-bash) : ;;        # piped: $0 is the shell, no path
  *) _self_dir=$(CDPATH= cd -- "$(dirname -- "$0")" 2>/dev/null && pwd) ;;
esac

if [ -n "$_self_dir" ] && [ -x "$_self_dir/installer/reposkillopt-install" ]; then
  exec "$_self_dir/installer/reposkillopt-install" "$@"
fi

# Case 2: ephemeral — fetch a tarball and run from a temp dir.
_tmp=$(mktemp -d 2>/dev/null || mktemp -d -t rso) || { echo "error: cannot create temp dir" >&2; exit 1; }
trap 'rm -rf "$_tmp"' EXIT INT TERM
_url="https://codeload.github.com/$RSO_REPO/tar.gz/refs/heads/$RSO_REF"

if command -v curl >/dev/null 2>&1; then
  curl -fsSL "$_url" -o "$_tmp/rso.tgz" || { echo "error: download failed ($_url)" >&2; echo "hint: clone the repo and run installer/reposkillopt-install directly" >&2; exit 1; }
elif command -v wget >/dev/null 2>&1; then
  wget -qO "$_tmp/rso.tgz" "$_url" || { echo "error: download failed ($_url)" >&2; exit 1; }
else
  echo "error: need curl or wget for the ephemeral path; clone the repo instead" >&2
  exit 1
fi

tar -xzf "$_tmp/rso.tgz" -C "$_tmp" || { echo "error: extract failed" >&2; exit 1; }
_root=$(find "$_tmp" -maxdepth 1 -type d -name 'reposkillopt-*' | head -n1)
[ -n "$_root" ] || { echo "error: unexpected archive layout" >&2; exit 1; }

exec "$_root/installer/reposkillopt-install" "$@"
