# Data Model — 009 Structural Completeness

## Symbol (extracted)
| field | type | notes |
|---|---|---|
| `name` | str | identifier |
| `kind` | str | `func` \| `class` |
| `file` | str | repo-relative path |
| `line` | int | 1-based |

## SchemaEntity (extracted)
| field | type | notes |
|---|---|---|
| `name` | str | table/model name |
| `columns` | list[str] | key/declared columns (best-effort) |
| `fks` | list[tuple[str,str]] | (column, target-entity) foreign keys |
| `source` | str | `file:line` of the definition |

## StructureMetrics (added to the benchmark entry, deterministic)
| field | type | notes |
|---|---|---|
| `symbol_total` | int | extracted function/class definitions |
| `symbol_accounted` | int | whose name appears anywhere in the spec |
| `symbol_coverage` | float | accounted / total (1.0 if total == 0) |
| `analyzed_fraction` | float | named outside "Symbols not yet analyzed" / total |
| `schema_entities` | int | extracted tables/models |
| `diagram_entities` | int | entities named in the spec's `erDiagram` |
| `diagram_grounding` | float \| None | erDiagram entities matching a real schema entity / diagram entities; `None` if n/a (no schema or no diagram) |

## Skill / template conventions (output)
- **Symbols not yet analyzed**: a subsection (e.g. under *Core modules*) listing, grouped by file, every defined symbol not referenced elsewhere — so accounted-for = 100%. May summarize per-file counts on huge repos.
- **Data model erDiagram**: a fenced ```mermaid``` `erDiagram` of real tables/models (key columns + FK relationships), each entity traceable to its schema file — or "Not applicable" when no database.

## Evidence-pack additions
- `=== SYMBOLS (deterministic inventory) ===` — `file: name(kind), …`
- `=== DB SCHEMA (deterministic) ===` — `Table(cols…) FK col→Target …`

## Report / TSV (extended additively)
- Human report: a **Structural coverage** table (symbol coverage, analyzed fraction, schema entities, diagram grounding) per entry.
- TSV: append `symbol_coverage	analyzed_fraction	schema_entities	diagram_grounding` after the feature-008 columns.
