# Contract — Quality Metrics (008)

## `engine/reposkillopt_engine/quality.py` (NEW)

```python
@dataclass
class QualityMetrics:
    fact_count: int
    citation_density: float | None
    labeled_claim_rate: float
    malformed_citation_rate: float
    section_completeness: float
    trace_presence: float
    quality_score: float

def compute_quality(spec_text: str, ground: GroundingResult, repo_path: str) -> QualityMetrics: ...
```

- **Pure & deterministic**: derived from `spec_text` + the already-computed `ground` (+ repo only for trace-citation resolution, reusing grounding). **No LLM, no randomness** (SC-002/SC-003).
- `fact_count` = count of `**[fact]**`.
- `citation_density` = `ground.resolvable_total / fact_count`, or `None` if `fact_count == 0`.
- `labeled_claim_rate` = (`[fact]` claims with a citation/backtick within ~90 chars) / `fact_count`; `1.0` if `fact_count == 0`.
- `malformed_citation_rate` = (citations whose locator contains a comma) / (total citations); `0.0` if none. Detected by a dedicated regex `<path>:<loc-with-comma>` over the spec — does **not** alter grounding.
- `section_completeness` = (required sections present AND non-empty) / 19. Non-empty = ≥1 non-blank non-heading line before the next `## `.
- `trace_presence` = fraction (0/0.5/1.0) of {Control-flow traces, Data-flow traces} sections each containing ≥1 resolving citation.
- `quality_score` = equal-weight mean of `[labeled_claim_rate, 1−malformed_citation_rate, section_completeness, min(citation_density,1.0), trace_presence]`, dropping the citation-density term when `fact_count == 0`.

**Contract test (SC-001/FR-011)**: for two specs of one repo with identical `ground.rate`, the one with a comma-malformed citation + an unlabeled fact + a missing section scores **strictly lower** `quality_score`.

## `engine/reposkillopt_engine/benchmark.py` (CHANGED)

- `EntryResult` gains `quality: QualityMetrics` and `rubric_score: float | None = None`.
- `run_entry(...)`: after `ground_spec`, call `compute_quality(spec_text, ground, repo_path)` → `res.quality`. When `with_rubric` is set (and a provider given), also call `judge.score_spec` → `res.rubric_score` (the only model call; off by default).
- `render_report(...)`: add the quality table + the 7 checks individually; append the new TSV columns; if any `rubric_score` present, a separate **"model-scored (non-reproducible)"** block.
- `run_benchmark(...)`: add `with_rubric: bool = False` passthrough.

## CLI (`cli.py`)

```
reposkillopt-engine benchmark … [--rubric]   # off by default; enables the optional model-scored signal
```
- Default run: **no model call**, deterministic metrics only.
- `--rubric` requires `--rollout-provider` (reuses the existing provider for the scorer).

## Invariants
- Citation-resolution rate stays the **headline** (FR-006). New metrics are additive; existing report/TSV columns and positions unchanged (FR-008).
- `grounding.py`, the rubric, the canonical skill, and the optimizer reward are **unchanged** (FR-009).
