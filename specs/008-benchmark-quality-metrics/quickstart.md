# Quickstart — 008 Benchmark Quality Metrics

## Run (deterministic, no model)

```sh
cd engine
python3 -m reposkillopt_engine benchmark --manifest ../rubric/benchmarks/seed-manifest.tsv --date YYYY-MM-DD
```

The report now shows, per repo, alongside the headline citation-resolution rate:
- **citation density** (resolvable citations per fact), **labeled-claim rate**,
  **malformed-citation rate** (comma-disjoint line lists), **section completeness**,
  **trace presence**, and a documented composite **quality score**;
- the **7 deterministic checks individually** (not just all-pass).

## Compute quality directly

```python
from reposkillopt_engine.grounding import ground_spec
from reposkillopt_engine.quality import compute_quality
spec = open("spec.md").read()
g = ground_spec("/path/to/repo", spec)
q = compute_quality(spec, g, "/path/to/repo")
print(q.quality_score, q.malformed_citation_rate, q.labeled_claim_rate)
```

## Optional model-scored context (off by default)

```sh
python3 -m reposkillopt_engine benchmark --manifest ... --date YYYY-MM-DD \
    --rubric --rollout-provider claude-cli
# adds a clearly-labeled "model-scored (non-reproducible)" rubric block; default runs make no model call.
```

## Validate

```sh
cd engine && python3 -m unittest tests.test_quality tests.test_benchmark -v
```

Acceptance signals:
- two specs with identical citation-resolution but different discipline → different quality
  metrics, cleaner spec scores higher composite (SC-001/FR-011).
- two runs identical (SC-002); default run makes no model call (SC-003).
- re-running the click/objectiv A/B: the new metrics differentiate canonical vs optimized on
  objectiv where citation-resolution alone was flat (SC-005).
