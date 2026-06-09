# Research & Decisions — 008 Benchmark Quality Metrics

## R1. Metric definitions (all deterministic, no LLM)
Let `facts` = count of `**[fact]**` in the spec; `cits` = parsed citations (feature-005), `resolvable` = cits excluding `cmd:`/`output:`, `resolved` = those that resolve (from `GroundingResult`).

- **fact_count** = `facts`.
- **citation_density** = `resolvable / facts` (resolvable citations per fact). If `facts == 0` → reported as `None`/N.A. (not 0, not div-by-zero).
- **labeled_claim_rate** = fraction of `**[fact]**` occurrences immediately followed (within ~90 chars) by a citation or backtick. If `facts == 0` → 1.0 (vacuously clean). Reuses the same window logic as grounding's `_unmarked_fact`, but as a *rate* over all facts, not first-failure.
- **malformed_citation_rate** = `malformed / total_cits`, where **malformed = a citation locator containing a comma** (comma-disjoint line lists like `:39-40,147` — exactly the form the optimizer learns to remove). Detected by a dedicated regex over the spec text (the feature-005 path pattern + a comma in the locator). If `total_cits == 0` → 0.0.
- **section_completeness** = fraction of the 19 `REQUIRED_SECTIONS` that are present **and non-empty** (heading followed by ≥1 non-blank, non-heading line before the next heading).
- **trace_presence** (optional) = 1.0 if both the *Control-flow traces* and *Data-flow traces* sections each contain ≥1 **resolving** citation, else the fraction of the two that do (0, 0.5, 1.0).

**Rationale**: these are precisely the discipline axes the objectiv optimization improved (comma-lists, claim labeling, completeness) and they reuse grounding's parser — no new parsing surface.

## R2. Why malformed = "comma in locator" (not Citation.kind)
feature-005's `parse_citations` *expands* `db.py:1,3,5` into separate valid line citations, so comma-lists don't surface as `kind="malformed"`. To measure them we scan the spec text directly for a path-locator containing a comma. This is deterministic and targets the exact defect; it does not modify grounding.

## R3. Composite quality score
- **Decision**: `quality_score` = equal-weight mean of the components, each mapped to [0,1]:
  `labeled_claim_rate`, `(1 − malformed_citation_rate)`, `section_completeness`, `min(citation_density / 1.0, 1.0)` (≥1 citation per fact = full), and `trace_presence`. Components that are N.A. (e.g. citation_density with 0 facts) are dropped from the mean. The exact formula and weights are printed in the report (FR-004).
- **Rationale**: simple, reproducible, documented; not presented as the headline (citation-resolution stays primary).

## R4. Non-empty section detection
- **Decision**: a section is "present and non-empty" if its `## <name>` heading exists and at least one non-blank line that is not itself a heading appears before the next `## ` heading (or EOF). Case-insensitive heading match, mirroring grounding's `sections_present`.

## R5. Per-check breakdown
- **Decision**: the report already has the 7-check dict in `GroundingResult.checks`; surface each check as its own column/line (not only `checks_pass`). No new computation.

## R6. Optional LLM rubric (off by default)
- **Decision**: a `--rubric` flag (default off) calls the existing `judge.score_spec` and reports the rubric aggregate under a clearly-labeled **"model-scored (non-reproducible)"** section, visually separated from the deterministic metrics. Excluded from deterministic acceptance. Needs a provider (reuses the engine layer).
- **Rationale**: context for those who want it, without contaminating the reproducible story (FR-007).

## R7. Surfacing & back-compat
- **Decision**: `EntryResult` gains a `quality: QualityMetrics` field; `render_report` adds a quality table + per-check lines + new TSV columns appended after the existing ones (existing columns/positions unchanged). Existing report consumers keep working.
- **Rationale**: additive (FR-008, edge: backward compatibility).

## R8. Determinism & tests
- **Decision**: fixtures: (a) a spec with comma-malformed citation + an unlabeled fact + a missing section vs (b) the same spec cleaned — assert (b) scores strictly higher on the relevant metric and the composite (SC-001/FR-011); assert exact values; assert two runs identical (SC-002); assert default run makes no model call (SC-003).
