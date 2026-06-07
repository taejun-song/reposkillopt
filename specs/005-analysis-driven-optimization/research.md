# Research & Decisions — 005 Real-Analysis-Driven Optimization

## R1. Evidence pack vs. per-candidate re-exploration
- **Decision**: Build one bounded evidence pack per run (cached on `RepoTask`), reuse for every candidate/round.
- **Rationale**: A real agent exploration of a 10k-file repo is minutes of work; doing it per candidate per round is hours/run and was the reason the original took the 8 KB shortcut. Caching gives real grounding at bounded cost (one expensive pass + cheap reuse).
- **Alternatives**: (a) full agent re-exploration per candidate — rejected (cost, non-goal). (b) keep 8 KB digest — rejected (the defect we're fixing).

## R2. What goes in the evidence pack
- **Decision**: `REPOSITORY` name; README head; manifests (full small ones, head of large); top-level tree; source dir tree (depth-limited, vendor dirs excluded); file-type histogram; **line-numbered contents of "key files"** (entrypoints + manifests + a capped number of largest/most-central source files); selected `grep` results for entrypoint/route/CLI markers. Bounded to a char budget (default 60 000); an explicit `=== OMITTED (budget) ===` note records truncation.
- **Rationale**: Line-numbered contents are essential — the model can only emit resolvable `file:line` citations if it saw real line numbers. Targeted greps surface entrypoints cheaply.
- **Alternatives**: raw `git ls-files` dump (too large, low signal); AST parsing (language-specific, violates "stdlib + grep only").

## R3. Citation resolution algorithm (deterministic, no LLM — SC-006)
- **Decision**: Regex-extract citations of the forms after a `**[fact]**`/inline backtick: `path:line`, `path:start-end`, `path:Symbol`, `path:Symbol:line`. Resolve:
  - `path:line` → file exists AND `1 ≤ line ≤ wc -l`.
  - `path:start-end` → file exists AND `1 ≤ start ≤ end ≤ wc -l`.
  - `path:Symbol` / `path:Symbol:line` → file exists AND the literal `Symbol` token occurs in the file (case-sensitive); if a line is also given, it must be in range.
  - `cmd:`/`output:` → excluded from the rate (not credited/penalized).
  - anything else → unresolved.
- **Rationale**: Matches the Clarifications rule; textual symbol match avoids per-language parsing while still catching fabrication. Paths resolved relative to the repo root.
- **Edge**: paths with a trailing `:line` ambiguity (Windows drive letters not a concern here); a token that is purely numeric after the last `:` is treated as a line number, else as a Symbol.

## R4. Which of the 7 checks become deterministic
- **Decision**: Compute deterministically from (spec, repo):
  - `cited_paths_exist` — all extracted file paths exist.
  - `cited_symbols_exist` — all `:Symbol` citations resolve.
  - `no_hallucinated_refs` — citation-resolution rate ≥ threshold (default 0.9) i.e. ≤10% unresolved.
  - `sections_present` — all 19 required section headings appear in the spec.
  - `unsupported_claims_marked` — every `**[fact]**` is followed (same line/next token) by a citation; every non-trivial claim carries one of the four labels (heuristic on `**[fact|inference|unknown|human]**`).
  - `prior_feedback_addressed`, `adapter_preserves_intent` — **not derivable** from a single per-repo optimization pass; default `True` (treated as not-applicable here). Documented so they don't silently mask grounding.
- **Rationale**: Keeps the 7-check shape (no rubric change, FR-007/non-goal) while making the citation-bearing ones real.

## R5. Reward formula
- **Decision**: `reward = 0.5 × rubric_norm + 0.5 × det_rate`, where `rubric_norm = Σ dim.aggregate / (15 × 3)` (existing) and `det_rate = mean(7 deterministic check bools)`. The ScoreCard returned to the gate carries the **deterministic** checks (overriding the LLM's check guesses), keeping the gate honest.
- **Rationale**: Equal weight per Clarifications; grounding can't be gamed by fluent prose.
- **Alternatives**: hard floor / disqualify below a citation rate — deferred (the weighted term + the existing gate already penalize regressions; a hard gate can be added later if needed).

## R6. Failure signal into reflect (FR-009)
- **Decision**: `grounding` returns a list of concrete failure strings (e.g. `cited "api/app.py:999" — file has 75 lines`, `section "Data model" missing`, `"[fact]" claim without citation near "..."`). The current skill's top failures become the reflect `fail_reason` (capped, deduped), replacing the generic "improve modeling" string.
- **Rationale**: Specific, repo-grounded reasons produce repo-specialized edits (the project's goal) instead of generic ones.

## R7. Outputs (FR-010) & canonical safety (FR-011)
- **Decision**: write specialized skill → `<repo>/.reposkillopt/best_skill.md` (existing path; `canonical_version` mirrored), best spec → `<repo>/.reposkillopt/specs/optimized-repository-specification.md`. `NativeResult` gains `best_spec`. The canonical `skills/repo-skillopt/SKILL.md` is read-only input.
- **Rationale**: reuse the established `.reposkillopt/` convention; the spec is the second promised deliverable.

## R8. Backwards compatibility
- **Decision**: keep `build_repo_digest` for the fake-provider unit path and as a fallback when evidence-pack building yields too little; `RepoTask.digest` stays, add `RepoTask.pack`. Existing deterministic tests keep passing.
- **Rationale**: avoid breaking the fake-provider tests and the simple path; additive change.
