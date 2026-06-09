# Data Model — 008 Benchmark Quality Metrics

## QualityMetrics (new, per scored spec)
| field | type | notes |
|---|---|---|
| `fact_count` | int | number of `**[fact]**` claims |
| `citation_density` | float \| None | resolvable citations per fact; `None` if `fact_count == 0` |
| `labeled_claim_rate` | float | fraction of `[fact]` claims immediately followed by a citation (1.0 if no facts) |
| `malformed_citation_rate` | float | fraction of citations with a comma-disjoint locator (`:39-40,147`); 0.0 if no citations |
| `section_completeness` | float | fraction of the 19 required sections present **and non-empty** |
| `trace_presence` | float | 0 / 0.5 / 1.0 — Control-flow & Data-flow trace sections each with ≥1 resolving citation |
| `quality_score` | float | documented equal-weight mean of the above (N.A. components dropped), in [0,1] |

- All fields are deterministic functions of (spec_text, GroundingResult, repo) — reproducible, no LLM.

## EntryResult (extended — feature 007)
Adds:
| field | type | notes |
|---|---|---|
| `quality` | QualityMetrics | the deterministic quality block |
| `rubric_score` | float \| None | OPTIONAL model-scored aggregate (only when `--rubric`); else `None` |

Existing fields (name, pin, resolved, total, rate, checks, checks_pass, failures, error) unchanged.

## BenchmarkReport (extended)
- Human report gains a **quality** table (per entry: citation density, labeled-claim rate, malformed rate, section completeness, trace presence, composite quality score) and the **7 checks individually**.
- If `--rubric` was on: a clearly-labeled **"model-scored (non-reproducible)"** section with the rubric aggregate.
- Machine-readable TSV: existing columns unchanged; **appended** columns `quality_score	citation_density	labeled_claim_rate	malformed_rate	section_completeness` (+ `rubric_score` only when enabled).

## Composite score (documented in the report)
`quality_score = mean(present_of[ labeled_claim_rate, 1 − malformed_citation_rate, section_completeness, min(citation_density,1.0), trace_presence ])`
where `citation_density`-derived term is dropped when `fact_count == 0`.
