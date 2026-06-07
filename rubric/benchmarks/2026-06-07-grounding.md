---
kind: grounding-benchmark
mode: score
date: 2026-06-07
entries: 1
mean_rate: 0.6089
median_rate: 0.6089
checks_pass_share: 0.0000
skipped: 0
---

# Grounding Benchmark — 2026-06-07

Citation-resolution rate of Repository Specifications against the real repository files (feature-005 grounding; model-free, reproducible).

| Repo | Commit pin | Resolved/Total | Rate | All checks | Top issue |
|------|-----------|----------------|------|-----------|-----------|
| click | `8.1.7` | 109/179 | 61% | ✗ | cited "tox.ini:32" — line 32 out of range (file has 30)… |

**Aggregate** — scored 1 (skipped 0): mean rate **61%**, median **61%**, all-7-checks-pass share **0%**.

Reproduce:

```sh
python3 -m reposkillopt_engine benchmark --manifest ../rubric/benchmarks/seed-manifest.tsv --mode score --date 2026-06-07
```

Machine-readable (`name\tpin\tresolved\ttotal\trate\tchecks_pass`):

```tsv
click	8.1.7	109	179	0.6089	false
```
