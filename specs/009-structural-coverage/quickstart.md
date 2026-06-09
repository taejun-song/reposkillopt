# Quickstart — 009 Structural Completeness

## Extract structure (deterministic, no model)

```python
from reposkillopt_engine.structure import extract_symbols, extract_schema
syms = extract_symbols("/path/to/repo")     # every function/class: name, kind, file:line
schema = extract_schema("/path/to/repo")    # tables/models + columns + foreign keys
print(len(syms), "symbols;", len(schema), "schema entities")
```

## Benchmark now reports structural coverage

```sh
cd engine
python3 -m reposkillopt_engine benchmark --manifest ../rubric/benchmarks/seed-manifest.tsv --date YYYY-MM-DD
# report adds a "Structural coverage" table: symbol coverage, analyzed fraction,
# schema entities, ER-diagram grounding — alongside grounding + quality. Model-free, reproducible.
```

## What a conforming spec now contains

- a `## Data model` with a fenced ```mermaid``` `erDiagram` of the real tables (or "Not applicable"),
- a **Symbols not yet analyzed** subsection so 100% of functions/classes are accounted for.

## Validate

```sh
cd engine && python3 -m unittest tests.test_structure tests.test_benchmark -v
```

Acceptance signals:
- exact symbol set + schema entities/FKs on fixtures (SC-001); an omitted symbol → coverage < 100% (SC-002).
- a fabricated ER entity lowers `diagram_grounding` (SC-003); no-DB repo → "Not applicable" (SC-004).
- two runs identical, zero model calls (SC-005).
- Live (generate mode) on a DB repo: the spec shows the real ER diagram + 100% symbol accounting (SC-007).
