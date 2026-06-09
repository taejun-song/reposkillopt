# Research & Decisions — 009 Structural Completeness

## R1. Symbol extraction (deterministic, regex, best-effort)
- **Decision**: per-file regex over the evidence-pack code set (same exclusions). Patterns:
  - Python: `^\s*(?:async\s+)?def\s+(\w+)`, `^\s*class\s+(\w+)`.
  - JS/TS/TSX/JSX: `^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)`, `^\s*(?:export\s+)?(?:abstract\s+)?class\s+(\w+)`, `^\s*export\s+(?:const|let)\s+(\w+)\s*=\s*(?:async\s*)?\(` (exported arrow fns), method-ish `^\s*(?:public|private|protected|static|async|\s)*([A-Za-z_]\w*)\s*\([^)]*\)\s*\{` (best-effort, may over/under-match).
  - Go: `^\s*func\s+(?:\([^)]*\)\s*)?(\w+)`.
  - Rust: `^\s*(?:pub\s+)?fn\s+(\w+)`, `^\s*(?:pub\s+)?struct\s+(\w+)`.
  - Java/Kotlin/etc.: class/interface + method best-effort.
- Yields `Symbol{name, kind ∈ {func,class}, file, line}`. **Documented as best-effort, not an AST resolver** (R-limitation); coverage is judged against these findings.
- **Rationale**: deterministic, language-agnostic-ish, no dependency; good enough to give a real completeness signal.

## R2. Schema extraction
- **Decision**: detect entities from:
  - SQL: `CREATE TABLE [IF NOT EXISTS] <name> (...)` → table + column names; `FOREIGN KEY ... REFERENCES <table>` and `<col> ... REFERENCES <table>` → FK edges.
  - ORM models: a class extending a known base (`Base`, `Model`, `models.Model`, `BaseModel`) → entity; FK-ish columns (`ForeignKey(`, `references=`) → edges (best-effort).
  - Migrations: `create_table`/`createTable` calls → entity (best-effort).
- Yields `SchemaEntity{name, columns[], fks[(col,target)]}` + source file:line. None found ⇒ "no database".
- **Rationale**: covers the common cases (SQL DDL, SQLAlchemy/Django/Sequelize-style) deterministically.

## R3. Symbol-coverage metric
- **Decision**: `symbol_coverage` = accounted / total, where a symbol is **accounted** if its name appears in the spec text (anywhere — analytical claim or the "Symbols not yet analyzed" listing). `analyzed_fraction` = (symbols whose name appears OUTSIDE the "Symbols not yet analyzed" section) / total. Both deterministic. total==0 ⇒ coverage 1.0 (n/a).
- **Rationale**: "no silent omission" = name present somewhere; "analyzed" = discussed, not merely listed.

## R4. ER-diagram convention + grounding metric
- **Decision (skill/template)**: the Data model section contains a fenced ```mermaid``` block with an `erDiagram`; entities are real table/model names with key columns; relationships use Mermaid FK syntax. "Not applicable" line when no schema.
- **Decision (metric)**: `diagram_grounding` = fraction of `erDiagram` entity names that match an extracted `SchemaEntity` name (case-insensitive). No diagram + no schema ⇒ n/a; diagram present but entity not in schema ⇒ lowers the score (catches fabricated tables). Entity names parsed from the mermaid block deterministically.
- **Rationale**: grounds the picture the same way citations are grounded.

## R5. Evidence-pack extension
- **Decision**: append two compact sections to the pack: `=== SYMBOLS (deterministic inventory) ===` (file → symbol names) and `=== DB SCHEMA (deterministic) ===` (tables, columns, FKs), bounded within the existing char budget (truncate + record omission). This lets the generating agent account for every symbol and draw the ER from real tables.
- **Rationale**: the model can only cover/draw what it's shown; giving it the deterministic inventory is the lever.

## R6. Surfacing & back-compat
- **Decision**: extend `EntryResult.quality` (or a parallel `structure` block) with the three metrics; `render_report` adds a structural table + appends TSV columns after the feature-008 ones (existing positions unchanged). Additive.

## R7. Canonical skill + adapter mirroring
- **Decision**: add two short, vendor-neutral rules to `SKILL.md` Output/Workflow + the Data-model section guidance; update the template's Data model + add the "Symbols not yet analyzed" convention; mirror verbatim-equivalent text into the 4 adapters; bump canonical `version` + each adapter `canonical_version`; CHANGELOG row. Run a live regeneration as evidence (held-out gate is the established path, referenced).
- **Rationale**: the skill is what produces the spec; the edit must reach every adapter (adapter-equivalence).

## R8. Determinism & tests
- **Decision**: fixtures — a repo with N known defs across 2 languages + a tiny SQL schema with an FK; assert exact symbol set, schema entities/FKs, and the three metrics (covered vs omitted spec; grounded vs fabricated erDiagram). Two runs identical.
