# Data Model — 007 Grounding Benchmark

## BenchmarkEntry (one manifest line)
| field | type | notes |
|---|---|---|
| `name` | str | display id for the repo in the report |
| `repo` | str | local path **or** `url@commit` |
| `spec` | str | path to the Repository Specification to score (score mode) |

Manifest grammar: `name<TAB>repo<TAB>spec` per line; `#`/blank lines ignored.

## EntryResult
| field | type | notes |
|---|---|---|
| `name` | str | from the entry |
| `pin` | str | resolved commit (or `local`) — recorded for reproducibility |
| `resolved` | int | resolving citations (from `GroundingResult.resolved`) |
| `total` | int | resolvable citations (`GroundingResult.resolvable_total`) |
| `rate` | float | `GroundingResult.rate` |
| `checks` | dict[str,bool] | the 7 deterministic checks |
| `checks_pass` | bool | all 7 checks true |
| `failures` | list[str] | concrete grounding defects (capped in the report) |
| `error` | str \| None | non-None ⇒ entry skipped (repo unavailable / spec missing) |

## Aggregate
| field | type | notes |
|---|---|---|
| `n` | int | scored (non-error) entries |
| `skipped` | int | error entries |
| `mean_rate` | float | mean resolution rate over scored entries |
| `median_rate` | float | median resolution rate |
| `checks_pass_share` | float | fraction of scored entries with all 7 checks passing |

## BenchmarkReport (artifact)
`rubric/benchmarks/<date>-grounding.md`:
- YAML front matter: `mode`, `date`, `entries`, `mean_rate`, `median_rate`, `checks_pass_share`, `skipped`.
- Human table: name · pin · resolved/total · rate · checks ✓/✗ · (top failure).
- Aggregate block + the reproduce command + manifest path.
- Machine-readable fenced TSV: `name\tpin\tresolved\ttotal\trate\tchecks_pass` (one row per entry).

## Mode
`score` (default, model-free: read `spec` file → ground) · `generate` (opt-in: regenerate via engine for the current canonical skill → ground).
