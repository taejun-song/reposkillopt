# Quickstart — Section-Scoped Retrieval

## Inspect what one section would retrieve (model-free)

```python
from reposkillopt_engine.retrieval import retrieve_section_evidence
se = retrieve_section_evidence("/path/to/repo", "Data model", char_budget=8000)
print(se.section, len(se.text), se.categories, se.fell_back)
```

## See the peak-vs-total tradeoff before running the model

```python
from reposkillopt_engine.retrieval import build_retrieval_report
r = build_retrieval_report("/path/to/repo", char_budget=8000)
print(f"baseline pack {r.baseline_chars} | peak section {r.peak_section_chars} "
      f"| total {r.total_chars} | fallbacks {r.fallbacks}")
```

## Generate a spec section-by-section (opt-in)

```sh
# lowers PEAK context per call; may raise TOTAL tokens — for tight windows
reposkillopt-engine benchmark --manifest <m.tsv> --mode generate \
    --skill skills/repo-skillopt/SKILL.md --rollout-provider claude-cli \
    --section-scoped --date demo
```

Default (no flag) = single-pack, unchanged.

## Validate (deterministic, no model)

```sh
cd engine && python3 -m unittest tests.test_retrieval -v
```

Expected: mapping correctness, byte-identical re-retrieval, every slice ≤ budget and ≤ full pack,
inventory fallback on unmapped sections.
