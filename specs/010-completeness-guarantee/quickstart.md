# Quickstart — 010 Completeness Guarantee

## Guarantee completeness of any spec (deterministic, no model)

```sh
cd engine
python3 -m reposkillopt_engine complete-spec --repo /path/to/repo --spec spec.md --out spec.complete.md
# appends the exhaustive "Symbols not yet analyzed" listing; symbol_coverage now 100%; idempotent.
```

```python
from reposkillopt_engine.completeness import ensure_symbol_completeness
from reposkillopt_engine.structure import extract_symbols
from reposkillopt_engine.quality import compute_structure
complete = ensure_symbol_completeness(open("spec.md").read(), "/path/to/repo")
m = compute_structure(complete, extract_symbols("/path/to/repo"), [])
print(m.symbol_coverage)   # 1.0  (guaranteed); analyzed_fraction unchanged
```

## Engine paths are complete automatically

- `optimize-repo` writes a `best_spec` that already accounts for 100% of symbols.
- `benchmark --mode generate` reports `symbol_coverage = 100%` with the real `analyzed_fraction`.

## Validate

```sh
cd engine && python3 -m unittest tests.test_completeness -v
```

Acceptance signals:
- after the step, `symbol_coverage == 1.0` (SC-001); a 2nd application is byte-identical (SC-002);
- `analyzed_fraction` equals the model's original (SC-003); model-free (SC-006).
- Live: a generate-mode spec on eco-standard-wiki routed through the step reports 100% coverage
  (vs ~10% one-shot), grouped + counted (SC-005).
