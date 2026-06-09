# Tasks: Structural Completeness — Symbol Coverage + ER Diagram

**Feature**: `009-structural-coverage` | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Paths relative to repo root. `[P]` = parallelizable.

## Phase 1: Setup

- [x] T001 Baseline: `cd engine && python3 -m unittest discover -s tests -t .` + `python3 -m pyflakes reposkillopt_engine/*.py` (record the pass count as the regression floor).

## Phase 2: Foundational (the extractor)

- [x] T002 Create `engine/reposkillopt_engine/structure.py`: `Symbol`/`SchemaEntity` dataclasses; `extract_symbols(repo)` (per-language regex over the evidence-pack code set + exclusions); `extract_schema(repo)` (SQL CREATE TABLE + FK, ORM model classes + FK columns, migration create_table); `parse_er_entities(spec_text)` (names from mermaid `erDiagram` blocks). Deterministic, no LLM. Export from `__init__.py`.

## Phase 3: User Story 1 — No symbol silently skipped (P1)

**Goal**: deterministic symbol coverage of the spec.
**Independent test**: known symbol set → exact coverage; omitted symbol → <100%.

- [x] T003 [US1] In `engine/reposkillopt_engine/quality.py`: add `StructureMetrics` + `compute_structure(spec_text, symbols, schema)` — `symbol_coverage` (names present anywhere / total; 1.0 if 0), `analyzed_fraction` (names outside the "Symbols not yet analyzed" section / total), `schema_entities`, `diagram_entities`, `diagram_grounding` (er entities matching a schema entity / er entities; None if n/a). `compute_quality` untouched.
- [x] T004 [P] [US1] `engine/tests/test_structure.py`: fixtures — a repo with N known func/class defs across Python + TS, and a tiny SQL schema with an FK. Assert the exact symbol set (names/kinds/lines), schema entities + FK, and `parse_er_entities`; assert `symbol_coverage` 100% when all names present, <100% when one omitted (SC-002); `diagram_grounding` lower for a fabricated entity (SC-003); determinism (two runs identical, SC-005).

## Phase 4: User Story 2 — Schema drawn, grounded (P1)

**Goal**: the evidence pack carries the schema/symbol inventory so the agent can draw a grounded ER.

- [x] T005 [US2] In `engine/reposkillopt_engine/evidence.py`: `build_evidence_pack` appends a `=== SYMBOLS (deterministic inventory) ===` block and a `=== DB SCHEMA (deterministic) ===` block (from `extract_symbols`/`extract_schema`), bounded within `char_budget`, omissions recorded.
- [x] T006 [P] [US2] `engine/tests/test_evidence.py` (extend): assert the SYMBOLS + DB SCHEMA blocks appear for a fixture with code + a schema; bounded; omissions recorded.

## Phase 5: User Story 3 — Measured & surfaced (P1)

**Goal**: the structural metrics appear in the benchmark, reproducibly.

- [x] T007 [US3] In `engine/reposkillopt_engine/benchmark.py`: add `structure: StructureMetrics|None` to `EntryResult`; in `run_entry`, call `extract_symbols`/`extract_schema` + `compute_structure` → `res.structure`. `render_report`: add a **Structural coverage** table and append TSV columns after the feature-008 ones (existing columns/positions unchanged).
- [x] T008 [P] [US3] Extend `engine/tests/test_benchmark.py`: assert `EntryResult.structure` populated; the report contains the structural table; appended TSV columns round-trip; determinism.

## Phase 6: Canonical skill + adapters (the spec-output rules)

- [x] T009 Edit `skills/repo-skillopt/SKILL.md` (vendor-neutral): require (a) every function/class accounted for — referenced or under "Symbols not yet analyzed"; (b) the Data model section include a grounded Mermaid `erDiagram` of the schema (or "Not applicable"). Bump `version` (minor); add a `skills/repo-skillopt/CHANGELOG.md` row.
- [x] T010 Edit `templates/repository-specification.md`: Data-model `erDiagram` convention + the "Symbols not yet analyzed" subsection convention.
- [x] T011 Mirror the T009 edits into all four adapters (`adapters/{claude-code,codex,opencode,generic}/*`), bumping each `canonical_version` to match; verify adapter-equivalence (installer `test_integrity` still green).

## Phase 7: Polish & validation

- [x] T012 Full engine suite + pyflakes green (no regression vs T001); `grounding.py` byte-unchanged; installer suite green (adapter-equivalence).
- [ ] T013 Live (generate mode) on a DB repo (eco-standard-wiki): confirm the produced spec's Data model has an `erDiagram` of the real tables (nodes/edges/evidence/jobs) with FKs, and symbol coverage accounts for ~100% of symbols (SC-007). Record the result.

## Dependencies

- T002 blocks T003–T008.
- Engine (T002–T008) is independent of the Markdown edits (T009–T011); both before T012.
- T013 (live) after everything.

## MVP

T002 + US1 (T003–T004): deterministic extraction + symbol-coverage metric. US2/US3 feed and surface it; the canonical edits (T009–T011) make the skill actually produce the coverage + diagram; T013 is the proof.
