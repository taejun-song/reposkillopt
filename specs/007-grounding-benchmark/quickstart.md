# Quickstart — 007 Grounding Benchmark

## Run the seed suite (model-free)

```sh
cd engine
python3 -m reposkillopt_engine benchmark --manifest ../rubric/benchmarks/seed-manifest.tsv \
    --date 2026-06-07
# -> writes ../rubric/benchmarks/2026-06-07-grounding.md
# -> prints: mean rate, median rate, all-checks-pass share, skipped count
```

The report has a per-repo table (name · commit pin · resolved/total · rate · checks), the aggregate,
the exact command to reproduce, and a machine-readable TSV block.

## Score one (repo, spec) pair directly

```python
from reposkillopt_engine.benchmark import run_benchmark
report = run_benchmark("demo\t/path/to/repo\t/path/to/spec.md\n", mode="score", date="2026-06-07")
print(report.aggregate.mean_rate, report.entries[0].rate, report.entries[0].checks_pass)
```

## Benchmark the *current* skill (generate mode, needs a provider)

```sh
python3 -m reposkillopt_engine benchmark --manifest ../rubric/benchmarks/seed-manifest.tsv \
    --mode generate --skill ../skills/repo-skillopt/SKILL.md --rollout-provider claude-cli --date 2026-06-07
```

## Validate the feature

```sh
cd engine && python3 -m unittest tests.test_benchmark -v
```

Acceptance signals:
- per-repo rates match hand-computed values; aggregate = mean/median of them (SC-001).
- two runs of the same manifest+specs give identical numbers (SC-002); score mode makes **no** model calls (SC-003).
- an unavailable repo is reported as an error and does not abort the run (SC-005).
