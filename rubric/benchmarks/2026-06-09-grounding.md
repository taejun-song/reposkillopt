---
kind: grounding-benchmark
mode: score
date: 2026-06-09
entries: 1
mean_rate: 0.6089
median_rate: 0.6089
checks_pass_share: 0.0000
skipped: 0
---

# Grounding Benchmark — 2026-06-09

Citation-resolution rate of Repository Specifications against the real repository files (feature-005 grounding; model-free, reproducible).

| Repo | Commit pin | Resolved/Total | Rate | All checks | Top issue |
|------|-----------|----------------|------|-----------|-----------|
| click | `8.1.7` | 109/179 | 61% | ✗ | cited "tox.ini:32" — line 32 out of range (file has 30)… |

**Aggregate** — scored 1 (skipped 0): mean rate **61%**, median **61%**, all-7-checks-pass share **0%**.

## Deterministic quality metrics (model-free)

| Repo | Quality | Cit/fact | Labeled | Malformed | Sections | Traces |
|------|---------|----------|---------|-----------|----------|--------|
| click | **97%** | 4.16 | 84% | 0% | 100% | 100% |

_quality = mean of [labeled-claim rate, 1−malformed rate, section completeness, min(citations/fact, 1), trace presence]; citations/fact dropped when a spec has no `[fact]` claims._

## Deterministic checks (per-repo)

| Repo | cited_paths_exist | cited_symbols_exist | sections_present | unsupported_claims_marked | no_hallucinated_refs | prior_feedback_addressed | adapter_preserves_intent |
|------|---|---|---|---|---|---|---|
| click | ✗ | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ |

Reproduce:

```sh
python3 -m reposkillopt_engine benchmark --manifest ../rubric/benchmarks/seed-manifest.tsv --mode score --date 2026-06-09
```

Machine-readable (`name\tpin\tresolved\ttotal\trate\tchecks_pass\tquality_score\tcitation_density\tlabeled_rate\tmalformed_rate\tsection_completeness`):

```tsv
click	8.1.7	109	179	0.6089	false	0.9674	4.1628	0.8372	0.0000	1.0000
```
