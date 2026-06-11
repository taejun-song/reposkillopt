# Phase 0 — Research & Decisions: Section-Scoped Retrieval

## D1. Retrieval mechanism: deterministic structural, not embeddings

**Decision**: Map each section to evidence categories and select files/symbols by deterministic
rule (path/name match, symbol density), reusing the existing evidence selector.
**Rationale**: Embeddings/vector-DB break determinism + reproducibility, add a heavy dependency,
and reintroduce silent-omission risk — all rejected by the constitution and the spec's non-goals.
The project already computes a structural ontology (symbols, schema, FKs); retrieval is a
projection over it.
**Alternatives considered**: Embedding RAG (rejected — non-deterministic, heavy dep, omission risk);
full-AST call-graph retrieval (rejected — no language server, out of scope; regex/grep best-effort).

## D2. Section→evidence mapping (the 19 sections)

**Decision**: A static table mapping each canonical section to evidence categories:

| Section | Evidence categories |
|---|---|
| Repository overview | README + top manifest |
| Technology stack | manifests (pyproject/package.json/go.mod/…) |
| Build and runtime commands | CI configs, Makefile, scripts, manifest scripts |
| Major entrypoints | entrypoint files (`__init__`/`index`/`main`/route registries) |
| Architectural layers | top modules by symbol density (one per dir) |
| Core modules | top modules by symbol density + symbol inventory |
| Domain model | symbol inventory (class names) |
| Data model | schema files + ER entities (extract_schema) |
| External integrations | files importing known client libs / network calls |
| Control-flow traces | entrypoints + files they reference |
| Data-flow traces | entrypoints + schema/IO files |
| Dependency map | manifests + import graph summary |
| Configuration map | config files (`*.env*`, `*.toml`, `*.yaml`, `settings*`) |
| Testing strategy | test dirs + runner config |
| Deployment assumptions | deploy files (Dockerfile, compose, systemd, CI deploy) |
| Change-impact map | symbol inventory (file→symbol counts) |
| Known risks | structure inventory (fallback) |
| Unknowns and unresolved questions | structure inventory (fallback) |
| Evidence index | structure inventory (fallback) |

**Rationale**: Each category is computable deterministically from existing extractors / filename
rules. Sections with no specific category fall back to the shared structure inventory (FR-005).
**Alternatives considered**: per-section embedding similarity (rejected, D1); one giant pack
(status quo — high peak context).

## D3. Bounding & determinism

**Decision**: Reuse `evidence`'s line-numbered selection and char budgeting to build each slice;
sort inputs deterministically (lexicographic path, then by symbol density desc with path tiebreak)
so the same (repo, section, budget) yields byte-identical output. Record omissions when truncated.
**Rationale**: FR-003/FR-004; matches the existing pack's bounding so behavior is consistent.

## D4. Generation loop & disk-not-context composition

**Decision**: `--section-scoped` loops the 19 sections in template order; for each it calls the
model with only that section's slice + a minimal spec header (title + the section heading), appends
the returned section to the on-disk spec, and discards it from working memory. After all sections,
run `ensure_symbol_completeness` once.
**Rationale**: Composes with the v0.6.0 disk-not-context rule; keeps peak context = one slice;
preserves the 100% coverage guarantee (010).
**Alternatives considered**: section *groups* (e.g. traces together) — deferred; single-section
keeps peak minimal and the loop simple for the prototype.

## D5. Honest instrumentation (peak vs total)

**Decision**: Build the full single-pack once (cheap, deterministic) to get the baseline size; the
run reports peak per-section slice, baseline pack size, and total evidence across sections, and logs
inventory fallbacks.
**Rationale**: FR-008/SC-005 — the total-token increase must be visible, not hidden.
