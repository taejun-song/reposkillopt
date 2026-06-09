# Implementation Plan: Structural Completeness — Symbol Coverage + ER Diagram

**Branch**: `009-structural-coverage` | **Date**: 2026-06-09 | **Spec**: [spec.md](./spec.md)

## Summary

Add a deterministic structural layer: a regex-based extractor of every function/class definition and of DB schema entities (tables, columns, FKs); deterministic benchmark metrics (symbol_coverage, analyzed_fraction, diagram_grounding); the evidence pack carries the symbol+schema inventory; and the canonical skill (mirrored to all four adapters + the template) requires (a) no-silent-omission symbol accounting and (b) a grounded Mermaid `erDiagram` in the Data model section. All metrics are model-free and reproducible, extending features 005/007/008. `grounding.py` and the optimizer reward are unchanged.

## Technical Context

**Language/Version**: Python ≥ 3.10 (engine) + Markdown (skill/adapters/template). No new language.
**Primary Dependencies**: none new — reuses `evidence` (code-ext set + exclusions), `grounding`, `quality`, `benchmark`; stdlib `re`. Extraction is regex/grep, **not** a language server (documented limitation).
**Storage**: filesystem; benchmark reports under `rubric/benchmarks/` (extended additively).
**Testing**: `python -m unittest` with fixtures (known symbol set + a tiny schema) asserting exact extraction + metric values; live generate-mode run for the ER diagram + 100% symbol accounting.
**Target Platform**: local CLI + the Markdown skill.
**Project Type**: single (engine package) + the skill/adapters/template Markdown.
**Performance**: extraction is a single pass over the already-selected code files; negligible.
**Constraints**: deterministic/reproducible (SC-005); canonical edits vendor/repo-neutral + adapter-mirrored (FR-008/009); grounding behavior + optimizer reward unchanged (FR-010).
**Scale/Scope**: a new extractor module + metric surfacing + evidence-pack lines + skill/adapter/template edits + tests.

## Constitution Check

Unfilled constitution template — no ratified gates. Project non-negotiables (CLAUDE.md):
- **Vendor neutrality (FR-002 of 001)** — the new skill text must name no runtime; the ER-diagram + symbol-coverage rules are generic. ✅ (enforced in implementation)
- **Adapter-equivalence (FR-024/025)** — edits mirrored to all four adapters with `canonical_version` bumped. ✅ (a task)
- **No new heavyweight dependency** — regex/stdlib only. ✅
- **Canonical change → validation gate** — the established acceptance path for canonical edits; referenced, with a live regeneration as evidence.

No violations; Complexity Tracking empty.

## Project Structure

### Documentation (this feature)

```text
specs/009-structural-coverage/
├── spec.md ├── plan.md ├── research.md
├── data-model.md ├── contracts/structure.md ├── quickstart.md
└── checklists/requirements.md
```

### Source Code (repository root)

```text
engine/reposkillopt_engine/
├── structure.py        # NEW: extract_symbols(repo) + extract_schema(repo) (regex, deterministic)
├── quality.py          # CHANGED: symbol_coverage / analyzed_fraction / diagram_grounding helpers
├── benchmark.py        # CHANGED: surface the structural metrics in EntryResult + report + TSV
├── evidence.py         # CHANGED: append the symbol + schema inventory to the pack
├── grounding.py        # unchanged
└── cli.py              # unchanged (benchmark already wired)

engine/tests/
├── test_structure.py   # NEW: symbol/schema extraction on fixtures; metric math; determinism
└── test_benchmark.py   # CHANGED: assert the new metrics surface in report/TSV

skills/repo-skillopt/SKILL.md        # CHANGED: no-omission rule + erDiagram requirement (+ CHANGELOG, version bump)
templates/repository-specification.md# CHANGED: "Symbols not yet analyzed" + Data-model erDiagram conventions
adapters/{claude-code,codex,opencode,generic}/*  # CHANGED: mirror the canonical edits (+ canonical_version)
```

**Structure Decision**: a dedicated `structure.py` isolates the deterministic extraction; `quality.py`/`benchmark.py` surface it; the Markdown edits are the skill side, mirrored by the adapter-equivalence task.

## Phase 0 / 1 outputs

- `research.md` — per-language symbol regexes, schema-extraction forms, metric formulas, the erDiagram convention, determinism.
- `data-model.md` — Symbol, SchemaEntity, SymbolCoverage, the extended metrics.
- `contracts/structure.md` — `extract_symbols`/`extract_schema`/coverage signatures + the skill/template conventions.
- `quickstart.md` — run + read the new columns + the live ER-diagram demo.

## Complexity Tracking

None — additive deterministic extractor + metric surfacing + Markdown skill edits; no new dependency; grounding/reward unchanged.
