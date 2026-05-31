# detect.sh — best-effort harness detection (contracts/cli-interface row 3). POSIX sh.
# Requires targets.sh to be sourced first.

# detect_targets <dest> — echo the space-separated set of candidate target ids whose
# detection signal is present in <dest>. May be empty, one, or many (codex+opencode
# both match AGENTS.md → inherently ambiguous; generic never matches).
detect_targets() {
  _dest=$1
  _out=""
  for _id in $TARGET_IDS; do
    if target_detect "$_id" "$_dest"; then
      _out="$_out $_id"
    fi
  done
  # trim leading space
  printf '%s' "${_out# }"
}
