# Feature Specification: Structural Completeness — Symbol Coverage + ER Diagram

**Feature Branch**: `009-structural-coverage`
**Created**: 2026-06-09
**Status**: Draft
**Input**: User description: "The spec must account for every function/class with no silent omission, and include a grounded ER diagram of the database schema — both backed by deterministic, model-free measurement."

## Clarifications

### Session 2026-06-09

- **"Every function/class" = a no-silent-omission guarantee** (decided): every defined symbol is either referenced in the analysis OR explicitly listed under a "Symbols not yet analyzed" enumeration, plus a coverage percentage. Not a prose paragraph per symbol; not a giant generated index.
- **Symbol extraction is deterministic, regex-based, best-effort** (reusing the evidence-pack code-extension set), not a full language-server/AST resolver — documented as a known limitation; "accounted-for" is judged against what the extractor finds.
- **ER diagram = a Mermaid `erDiagram`** in the Data model section when a database schema exists; "Not applicable" when there is none. Entities are real tables/models with key columns and foreign-key relationships, each traceable to the schema file that defines it.
- **New metrics are deterministic and model-free** (extend feature-008 quality), surfaced in the benchmark; the canonical skill edits are vendor/repo-neutral and mirrored into all four adapters.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - No function or class is silently skipped (Priority: P1)

A reader of a Repository Specification can trust that **every** function and class in the repo has been accounted for: each one is either discussed in the analysis or explicitly listed as not-yet-analyzed, with a coverage percentage — so nothing is hidden.

**Why this priority**: This is the core trust property the user asked for; the current spec gives no completeness guarantee. Independently valuable.

**Independent Test**: For a repo with a known set of function/class definitions, confirm every one appears in the spec (either referenced in an analytical claim or listed under "Symbols not yet analyzed"), and the reported coverage counts match the real definition count.

**Acceptance Scenarios**:

1. **Given** a repo with N defined functions/classes, **When** the spec is produced and measured, **Then** all N are accounted for (referenced or explicitly listed); the spec reports N defined, M analyzed, N−M listed.
2. **Given** a symbol that is neither referenced nor listed, **When** the spec is measured, **Then** the symbol-coverage metric is below 100% and the missing symbol is identifiable.

### User Story 2 - The data model is drawn, grounded in the real schema (Priority: P1)

A reader sees an entity-relationship **diagram** of the database — real tables, their key columns, and the foreign-key relationships — that renders inline and is traceable to the schema files, instead of only prose.

**Why this priority**: Visualizing the schema is the second explicit ask and a large usability gain for data-heavy repos. Depends on the deterministic schema extraction.

**Independent Test**: For a repo with a real DB schema, confirm the Data model section contains an ER diagram whose entities are the actual tables/models and whose relationships match the foreign keys, and that each entity resolves to a real schema definition.

**Acceptance Scenarios**:

1. **Given** a repo with a database schema, **When** the spec is produced, **Then** the Data model section contains an ER diagram of the real tables with key columns and foreign-key relationships.
2. **Given** a repo with no database, **When** the spec is produced, **Then** the Data model section states the diagram is Not applicable (no fabricated schema).
3. **Given** an ER diagram, **When** it is measured, **Then** the fraction of its entities that resolve to a real schema definition (diagram-grounding) is reported.

### User Story 3 - The completeness is measured and reproducible (Priority: P1)

The benchmark reports, deterministically and reproducibly, the new structural metrics — symbol coverage, analyzed fraction, and ER-diagram grounding — alongside the existing grounding/quality metrics, so improvements are measurable.

**Why this priority**: Consistent with the project's "measured, not asserted" discipline; turns the completeness claims into numbers. Depends on US1/US2's extraction.

**Independent Test**: Run the benchmark on a fixture twice; confirm the new metrics appear in the report and machine-readable summary and are byte-identical across runs.

**Acceptance Scenarios**:

1. **Given** a scored spec, **When** the benchmark runs, **Then** the report shows symbol_coverage, analyzed_fraction, and diagram_grounding with no language model involved.
2. **Given** the same inputs run twice, **When** the new metrics are compared, **Then** they are identical.

### Edge Cases

- **Repo with no extractable symbols** (e.g. only data/markdown): coverage is defined (1.0 over zero / "no symbols"), not a divide-by-zero.
- **Repo with no database**: ER diagram is "Not applicable"; diagram-grounding is reported as not-applicable rather than 0.
- **Regex misses a construct**: documented limitation — accounted-for is judged against the extractor's findings; the extractor's coverage of language constructs is stated.
- **Generated/vendored code** (e.g. build output, `node_modules`, migrations dirs): excluded from the symbol set the same way the evidence pack excludes them, to avoid drowning the coverage signal.
- **Huge repo** (thousands of symbols): the "Symbols not yet analyzed" listing groups by file and may summarize counts per file rather than listing every name inline, while still accounting for 100%.
- **A fabricated table in the ER diagram**: lowers diagram-grounding (entity does not resolve to a real schema definition).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST deterministically extract, with no language model, the function and class definitions of the repository (name, kind, file, line), reusing the evidence-pack's code-file selection and exclusions; the extraction approach and its best-effort/regex limitation MUST be documented.
- **FR-002**: The system MUST deterministically extract the database schema entities (tables/models), their key columns, and foreign-key relationships from schema artifacts (schema definitions, migrations, ORM models) when present.
- **FR-003**: The Repository Specification MUST account for **every** extracted function/class with **no silent omission**: each is either referenced in an analytical claim/citation or listed under an explicit "Symbols not yet analyzed" subsection; the spec MUST report counts (defined N, analyzed M, listed N−M).
- **FR-004**: The Repository Specification's Data model section MUST include a Mermaid `erDiagram` of the database when a schema exists — real tables/models, key columns, foreign-key relationships, each traceable to the defining schema file — or state "Not applicable" when no database is present (never a fabricated schema).
- **FR-005**: The benchmark MUST compute and report, deterministically and reproducibly (no model), **symbol_coverage** (fraction of extracted symbols accounted for in the spec), **analyzed_fraction** (fraction referenced in analysis vs merely listed), and **diagram_grounding** (fraction of ER-diagram entities resolving to a real schema definition).
- **FR-006**: The new metrics MUST appear in both the human benchmark report and the machine-readable summary, alongside the existing grounding/quality metrics; citation-resolution remains the headline.
- **FR-007**: The evidence pack handed to spec generation MUST include the deterministic symbol inventory and schema inventory, so the generating agent can account for all symbols and build the ER diagram from real tables.
- **FR-008**: The canonical skill MUST be updated, in vendor/repo-neutral language, to require (a) the no-silent-omission symbol accounting and (b) the grounded ER diagram; the spec template MUST gain the "Symbols not yet analyzed" convention and the Data-model `erDiagram` convention.
- **FR-009**: The canonical skill edits MUST be mirrored into all four adapters (claude-code, codex, opencode, generic), preserving adapter-equivalence and each adapter's `canonical_version`.
- **FR-010**: All new extraction and metrics MUST be model-free and reproducible (same repo + spec ⇒ identical numbers), add no heavyweight dependency, and leave feature-005 grounding behavior and the optimizer reward unchanged.
- **FR-011**: Generated/vendored/excluded directories MUST be omitted from the symbol set, consistent with the evidence pack, so coverage reflects authored code.

### Key Entities *(include if feature involves data)*

- **Symbol**: a function or class definition — {name, kind, file, line} — extracted deterministically.
- **Schema entity**: a table/model — {name, key columns, foreign keys} — extracted from schema artifacts.
- **Symbol-coverage result**: per spec — defined count, analyzed count, listed count, accounted-for fraction, analyzed fraction.
- **ER diagram**: the Mermaid `erDiagram` in the Data model section; its entities are checked against schema entities for grounding.
- **Structural metrics**: the deterministic symbol_coverage / analyzed_fraction / diagram_grounding added to the benchmark.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For a repo with a known symbol set, a conforming spec accounts for 100% of functions/classes (referenced or explicitly listed), and the reported defined/analyzed/listed counts match the real definitions.
- **SC-002**: A spec that omits a defined symbol (neither referenced nor listed) scores symbol_coverage < 100%, and the omitted symbol is identifiable.
- **SC-003**: For a repo with a database, a conforming spec's Data model section contains an ER diagram whose entities are the real tables and whose relationships match the foreign keys; diagram_grounding ≥ a high threshold; a fabricated entity lowers it.
- **SC-004**: For a repo with no database, the spec states the ER diagram is Not applicable (no fabricated schema).
- **SC-005**: All new metrics are computed with zero model calls and are byte-identical across two runs on the same inputs.
- **SC-006**: The canonical skill and all four adapters carry the new requirements with preserved adapter-equivalence; feature-005 grounding behavior and the optimizer reward are unchanged.
- **SC-007**: A live generate-mode run on a repo with a real DB produces an ER diagram of the real tables + foreign keys and a symbol-coverage report accounting for 100% of symbols.

## Assumptions

- Symbol extraction is regex/grep best-effort across the languages the evidence pack already recognizes; it is deterministic and documented as not a full AST resolver. "Accounted-for" is judged against the extractor's findings, not a perfect symbol set.
- "Accounted for" means the symbol's name appears in the spec — either inside an analytical claim/citation, or within the "Symbols not yet analyzed" listing.
- Schema extraction targets common forms (SQL `CREATE TABLE`, ORM model classes, migration definitions); repos using exotic schema definitions may be partially covered, documented as a limitation.
- The Mermaid `erDiagram` is text that renders on GitHub and similar viewers; no image rendering is in scope.
- The deterministic metrics extend the feature-008 quality layer and the feature-007 benchmark; the canonical skill edits follow the convergence-loop discipline (vendor-neutral, adapter-mirrored), and a full held-out validation-gate run is the established acceptance path for canonical changes (referenced, not re-implemented here).
- Reuses grounding/quality/benchmark/evidence modules; no new heavyweight dependency.
