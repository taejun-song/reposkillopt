# Research & Decisions — 006 Native Agent-Skills Install

## R1. Skill-directory paths per harness (verified, official docs, mid-2026)
- **Decision**: map targets to native skill dirs — claude-code→`.claude/skills/`, codex→`.agents/skills/`, opencode→`.opencode/skills/`, cursor→`.cursor/skills/`, plus a cross-tool `agents`→`.agents/skills/`.
- **Rationale**: docs confirm Codex scans `.agents/skills/` (CWD→repo root); OpenCode reads `.opencode/`, `.claude/`, and `.agents/`; Cursor reads `.cursor/` and `.agents/` (+ `.claude/` for compat). So `.agents/skills/repo-skillopt/` is read by Codex + OpenCode + Cursor at once.
- **Alternatives**: route everything to `.agents/skills/` only (rejected — `opencode`/`cursor` users expect their own dir; we offer both: a native per-tool target *and* the shared `agents` target).

## R2. What content gets installed
- **Decision**: skill-capable targets install the **canonical** `skills/repo-skillopt/SKILL.md` directly (it already has `name` + `description` front matter). claude-code keeps its existing adapter source for continuity (FR-002 "unchanged").
- **Rationale**: the format is now a cross-tool standard; a per-harness AGENTS.md prose wrapper is no longer needed for skill-capable tools. Fewer artifacts to keep equivalent.
- **Alternatives**: per-harness adapter copies (rejected — unnecessary divergence now that the format is shared).

## R3. Version detection for the new (canonical) source — no change needed
- **Finding**: the installer reads `_srcver=read_field(<source>, canonical_version)`, then `[ -n "$_srcver" ] || _srcver=$(canonical_version)` which reads `version:` from `skills/repo-skillopt/SKILL.md` (`reposkillopt-install:69,115-122`).
- **Decision**: the new targets source the canonical skill (which has `version:`, not `canonical_version:`), so `read_field` returns empty and the fallback supplies the canonical version. The version gate keeps working unchanged.

## R4. AGENTS.md protection (legacy mode)
- **Decision**: keep `codex`/`opencode` mapped to skill dirs by default; expose the old single-file behavior only via explicit legacy targets (e.g. `codex-agentsmd`, `opencode-agentsmd`). On install, if the destination `AGENTS.md` exists and is **not** RepoSkillOpt-managed (no manifest record for that target), **refuse** (new exit code) unless `--force`; with `--force`, copy the original to `AGENTS.md.bak` first, then write.
- **Rationale**: removes the data-loss bug (FR-005) while preserving an escape hatch. A RepoSkillOpt-managed AGENTS.md (manifest match) upgrades in place with no friction (FR-006).
- **Alternatives**: append a managed `<!-- reposkillopt -->` block into the user's AGENTS.md (deferred — more parsing; refuse/backup is simpler and safe now).

## R5. Uninstall of directory targets
- **Decision**: after removing the recorded skill file, `rmdir` the now-empty `repo-skillopt/` directory (ignore-if-nonempty). Never touch sibling skills or the shared skills root (FR-008).
- **Rationale**: leaves the repo exactly as before install (SC-004).

## R6. Detection (`target_detect`) for auto-mode
- **Decision**: codex/agents → `.agents` present; opencode → `.opencode` present; cursor → `.cursor` present; claude-code → `.claude` (unchanged). Ambiguity (several present) keeps today's explicit-or-refuse behavior (FR-010).
- **Rationale**: detection is a convenience; correctness comes from explicit `--agent`.

## R7. Backwards compatibility
- **Decision**: existing `claude-code` and `generic` targets unchanged; existing AGENTS.md adapter files retained (FR-012). Manifest format unchanged. Existing installer tests must stay green.
