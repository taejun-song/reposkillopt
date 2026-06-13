# Feature Specification: Codebase Ontology Substrate

**Feature Branch**: `012-codebase-ontology`
**Created**: 2026-06-13
**Status**: Draft
**Input**: A deterministic, model-free knowledge graph of the whole codebase — entities (modules, classes, functions, data entities, routes, jobs, abstractions) + relations (imports, inherits, foreign-key, registers-route, schedules) — built by reusing `extract_symbols`/`extract_schema` + `rg` passes. It is the **substrate** that business-workflow (013) and refactor (014) views derive from. Enriches Domain model (§7) with an entity map + relationship graph and Data model (§8) with the erDiagram. `rg`-first, frozen metrics.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - An ontology view of the whole codebase (Priority: P1)

An engineer wants a single deterministic map of *what is in the repo and how it connects* — modules, classes, functions, data entities, routes, jobs, and their relationships — grounded to `file:line`, not a hand-wavy diagram.

**Independent Test**: Run `build_ontology(repo)` on a real repo; confirm it returns entities of fixed kinds and relations, every entity pinned to a real `file:line`, byte-identical across runs.

**Acceptance Scenarios**:
1. **Given** a repo, **When** the ontology is built, **Then** it contains entities of the fixed kinds and relations of the fixed kinds, each carrying a resolvable `file:line`.
2. **Given** the same repo, **When** built twice, **Then** the structured output is byte-identical (deterministic, model-free).
3. **Given** a relation whose target cannot be resolved to a known entity, **When** built, **Then** it is recorded under `unresolved` (an `[inference]`/`[unknown]` frontier), never drawn as a hard edge.

### User Story 2 - Ontology renders into the spec (Priority: P2)

The ontology populates the spec: an entity-map table + a relationship `graph` in Domain model, and an `erDiagram` in Data model that round-trips through the existing parser.

**Independent Test**: Render the ontology; confirm the erDiagram is parsed back by `parse_er_entities` to the same data entities (diagram grounding preserved).

**Acceptance Scenarios**:
1. **Given** an ontology with data entities + foreign keys, **When** `render_er_diagram` runs, **Then** `parse_er_entities` returns exactly those entity names (round-trip).
2. **Given** a large repo, **When** the relationship graph renders, **Then** edges are deterministically capped (top-N by sorted key + an "… N more" note), never unbounded.

## Requirements *(mandatory)*

- **FR-001**: Provide `build_ontology(repo_path) -> Ontology` — deterministic, model-free, reusing `extract_symbols` + `extract_schema` and `rg` (via `evidence._run`, grep fallback). Zero model calls.
- **FR-002**: Entities have a fixed kind set (`module`, `class`, `function`, `data_entity`, `route`, `job`, `abstraction`); each carries `name`, `file`, `line`.
- **FR-003**: Relations have a fixed kind set (`imports`, `inherits`, `foreign_key`, `registers_route`, `schedules`); each carries `kind`, `src`, `dst`, `file`, `line`. A relation whose `dst` does not bind to a known entity goes to `Ontology.unresolved` (never a rendered hard edge).
- **FR-004**: Deterministic & reproducible — same `(repo_path)` ⇒ byte-identical `to_structured(ontology)`; ordering rests on the file manifest + explicit sorting, not on which locator tool ran.
- **FR-005**: `abstraction` entities are detected **structurally** (base-class fan-in: a class inherited by ≥2 others), NOT via a repo-specific allowlist (vendor-neutrality).
- **FR-006**: Pure renderers: `render_entity_map` (table), `render_relationship_graph` (mermaid `graph`, deterministically edge-capped), `render_er_diagram` (matches the existing erDiagram convention so `parse_er_entities`/`diagram_grounding` keep working unchanged).
- **FR-007**: `rg`-first scan-don't-read — detect with `rg` (fallback `grep`/`git ls-files`/`find`); read only matched lines / bounded windows; never slurp whole files.
- **FR-008**: MUST NOT change grounding, rubric, reward, or any metric definition. Enriches Domain model (§7) and Data model (§8); adds no required section.
- **FR-009**: Canonical skill gains vendor-neutral "build the ontology first" guidance for §7/§8, mirrored to all four adapters; canonical version bumped.

### Key Entities

- **Entity**: `{kind, name, file, line}` — a node.
- **Relation**: `{kind, src, dst, file, line}` — a resolved edge.
- **Ontology**: `{entities, relations, unresolved}` — the graph + the unresolved frontier.

## Success Criteria *(mandatory)*

- **SC-001**: On `eco-standard-wiki`, `build_ontology` recovers the real entities (≈58 routes, 13 CLI, schema tables) and relations, each grounded; built twice ⇒ byte-identical.
- **SC-002**: `render_er_diagram` output round-trips: `parse_er_entities(render_er_diagram(onto))` equals the data-entity set; `compute_structure.diagram_grounding` is unchanged in definition and computes on it.
- **SC-003**: Zero model calls in ontology construction/rendering; deterministic across reruns.
- **SC-004**: Section-completeness and all frozen metrics are unchanged (verified by the existing suite staying green).

## Assumptions

- Engineers run the optional Python engine; regex/grep best-effort (feature 009 posture), no language server. Under-resolvable relations (calls, dynamic dispatch) are out of scope for v1 and recorded as `unresolved`.
- The ontology is the substrate; business-workflow (013) and refactor (014) are separate follow-on features that read it.
