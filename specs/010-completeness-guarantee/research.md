# Research & Decisions — 010 Completeness Guarantee

## R1. The transform
- **Decision**: `ensure_symbol_completeness(spec_text, repo_path) -> str`:
  1. `syms = extract_symbols(repo)` (feature 009).
  2. Locate any existing `## Symbols not yet analyzed` (or `### …`) section; split spec into the analyzed body vs that section.
  3. A symbol is **accounted** if its name appears in the spec, OR its file is already listed in the existing section. Compute `missing` = symbols not accounted.
  4. If `missing` is empty → return `spec_text` unchanged (**idempotent**).
  5. Else build a fresh "Symbols not yet analyzed" listing: group `missing` by file; per file emit `- path: name1, name2, …` (or `- path: N symbols` when the file has many names / the total would exceed the size cap). Prepend a counts line `N defined, M analyzed, N−M listed` where M = symbols named in the analyzed body.
  6. Replace the existing section if present, else append the section at end of *Core modules* (or end of document).
- **Rationale**: reuses feature-009 accounting; idempotent because after appending, every file is listed → next run finds no missing.

## R2. Idempotency proof
- After the step, every symbol is either named in the body or its file is in the section. On a re-run, `accounted` is true for all → `missing` empty → return unchanged. Tests assert byte-identical on the 2nd application.

## R3. Guaranteed-vs-analyzed honesty (no metric change)
- **Decision**: the appended listing places names under the *Symbols not yet analyzed* section, which `compute_structure` already excludes from the analyzed body. So `symbol_coverage` → 100% (file listed), `analyzed_fraction` stays = (named in analyzed body)/total — unchanged by the listing. No metric definition changes (FR-005/FR-010).

## R4. Boundedness on huge repos
- **Decision**: per-file lines always present (so every file → 100% accounting); names included until a size cap (default ~20k chars), then per-file counts; truncation recorded in a trailing note. Accounting stays 100% because file-presence (not names) is what `compute_structure` credits.

## R5. Where it's wired
- **Decision**:
  - `skillopt_native.optimize_repo`: apply to `res.best_spec` before returning (the emitted output).
  - `benchmark.run_entry` (generate mode): apply to the generated spec before grounding/scoring, so engine-path generate-mode specs are complete and the report shows `symbol_coverage = 100%` with the real `analyzed_fraction`.
  - **Not** applied to a pre-written spec scored in default/score mode (that measures the spec as authored).
- **Rationale**: FR-006 covers engine spec producers; score mode is a measurement of given specs, untouched.

## R6. Agent path
- **Decision**: `cli.py` gains `complete-spec --repo <path> --spec <path> [--out]` running `ensure_symbol_completeness`. The canonical skill's final workflow stage instructs the agent to run it (or append the deterministically-computed listing) as the last action and never hand-transcribe. Skill edit mirrored to the 4 adapters; `version`/`canonical_version` → 0.4.0; CHANGELOG row.
- **Rationale**: the guarantee must hold in the agent path too (FR-007); a small optional helper fits the project's helper stance.

## R7. Determinism & tests
- **Decision**: fixtures — a repo with a known symbol set; a spec mentioning a subset. Assert: after the step `compute_structure(...).symbol_coverage == 1.0`; `analyzed_fraction` equals the original subset; a 2nd application is byte-identical; no model used.
