# Contract — Structural Extraction & Metrics (009)

## `engine/reposkillopt_engine/structure.py` (NEW)

```python
@dataclass
class Symbol: name: str; kind: str; file: str; line: int
@dataclass
class SchemaEntity: name: str; columns: list[str]; fks: list[tuple[str,str]]; source: str

def extract_symbols(repo_path: str) -> list[Symbol]
    # regex per language over the evidence-pack code set (same exclusions); deterministic, no LLM.

def extract_schema(repo_path: str) -> list[SchemaEntity]
    # SQL CREATE TABLE + FK, ORM model classes + FK cols, migration create_table; deterministic.

def parse_er_entities(spec_text: str) -> list[str]
    # entity names declared in the spec's mermaid erDiagram block(s); deterministic.
```

- **Pure & deterministic** (model-free, reproducible). Excludes generated/vendored dirs like the evidence pack.

## `engine/reposkillopt_engine/quality.py` (CHANGED — additive helpers)

```python
@dataclass
class StructureMetrics:
    symbol_total: int; symbol_accounted: int; symbol_coverage: float
    analyzed_fraction: float; schema_entities: int
    diagram_entities: int; diagram_grounding: float | None

def compute_structure(spec_text, symbols, schema) -> StructureMetrics
    # symbol_coverage = (names present in spec)/total (1.0 if total 0);
    # analyzed_fraction = (names present OUTSIDE "Symbols not yet analyzed")/total;
    # diagram_grounding = (er entities matching a schema entity)/(er entities); None if no schema/diagram.
```

- `compute_quality` (008) is unchanged; `compute_structure` is a sibling so feature-008 stays intact.

## `engine/reposkillopt_engine/benchmark.py` (CHANGED)

- `EntryResult` gains `structure: StructureMetrics | None`.
- `run_entry`: after grounding/quality, call `extract_symbols`/`extract_schema` (once) + `compute_structure` → `res.structure`. Deterministic; no extra model call.
- `render_report`: add a **Structural coverage** table + append TSV columns.

## `engine/reposkillopt_engine/evidence.py` (CHANGED)

- `build_evidence_pack` appends a `SYMBOLS` inventory and a `DB SCHEMA` block (from `extract_symbols`/`extract_schema`), bounded within `char_budget`; omissions recorded.

## Skill / template / adapters (Markdown, mirrored)

- `skills/repo-skillopt/SKILL.md`: add a vendor-neutral rule — *every function/class must be accounted for (referenced or listed under "Symbols not yet analyzed")* — and *the Data model section must include a grounded `erDiagram` of the schema, or "Not applicable"*. Bump `version`; add CHANGELOG row.
- `templates/repository-specification.md`: Data-model `erDiagram` convention + the "Symbols not yet analyzed" subsection.
- `adapters/{claude-code,codex,opencode,generic}/*`: mirror the edits; bump each `canonical_version` to match (adapter-equivalence).

## Invariants
- All metrics deterministic/reproducible (SC-005). Citation-resolution stays headline; new metrics additive (existing report/TSV columns unchanged). `grounding.py`, the rubric, the optimizer reward unchanged (FR-010). Canonical edits vendor-neutral + mirrored (FR-008/009).
