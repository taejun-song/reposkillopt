# Implementation Plan: Deterministic Section-Scoped Evidence Retrieval

**Branch**: `011-section-scoped-retrieval` | **Date**: 2026-06-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/011-section-scoped-retrieval/spec.md`

## Summary

Add a deterministic, model-free `retrieve_section_evidence(repo, section, *, char_budget)` that
returns a bounded, line-numbered evidence slice for a single spec section, plus an opt-in
`--section-scoped` generation mode that produces the 19-section spec one section at a time (each
model call seeing only its slice), writes incrementally to disk, and runs the completeness step
once at the end. Reuses feature-005 evidence selection and feature-009 structure/schema. No
embeddings, no vector DB. Single-pack mode stays the default; the run reports peak/baseline/total
evidence so the peak-vs-total tradeoff is visible.

## Technical Context

**Language/Version**: Python ≥ 3.10 (engine); stdlib only  
**Primary Dependencies**: none new — reuses `evidence` (005), `structure` (009), `completeness` (010), `grounding`/`quality` for scoring. NO embeddings, NO vector store.  
**Storage**: filesystem only — spec written incrementally under the target repo's `.reposkillopt/specs/`; retrieval is in-memory per section.  
**Testing**: stdlib `unittest` (deterministic, no network, no model)  
**Target Platform**: Linux/CLI (the optional engine)  
**Project Type**: single project (Python engine under `engine/`)  
**Performance Goals**: retrieval is grep/regex over the repo — sub-second per section; goal is *peak context* reduction, not throughput  
**Constraints**: deterministic & reproducible (same input ⇒ byte-identical slice); model-free retrieval (0 model calls); each slice ≤ budget and ≤ full pack; no metric-definition changes  
**Scale/Scope**: repos up to ~1,600 symbols / ~80 schema entities (eco-standard-wiki) validated; 19 fixed sections

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Skill-first / no SaaS, no DB, no heavy deps** — PASS: engine-only, stdlib-only, no embeddings/vector DB (explicit non-goal).
- **Determinism & reproducibility** — PASS: retrieval is model-free and byte-identical per (repo, section, budget); only per-section *generation* uses a model, exactly as the single-pack mode's one call does.
- **No silent omission** — PASS: the completeness step (010) still runs once after all sections, guaranteeing 100% symbol coverage; truncated slices record omissions; inventory fallback is logged.
- **Do not change grounding/rubric/reward/metrics** — PASS: additive only; existing metrics score the produced spec unchanged.
- **Vendor neutrality / adapter-equivalence** — PASS: engine-only milestone; the optional skill note (FR-012) would mirror to all four adapters + bump version if added.

No violations → Complexity Tracking not required.

## Project Structure

### Documentation (this feature)

```text
specs/011-section-scoped-retrieval/
├── plan.md              # this file
├── research.md          # Phase 0 — section→evidence mapping decisions
├── data-model.md        # Phase 1 — SectionEvidence / RetrievalReport shapes
├── quickstart.md        # Phase 1 — how to run --section-scoped
├── contracts/
│   └── retrieval.contract.md   # retrieve_section_evidence + mode contract
└── tasks.md             # Phase 2 (/speckit.tasks)
```

### Source Code (repository root)

```text
engine/reposkillopt_engine/
├── retrieval.py         # NEW — SECTION_EVIDENCE map + retrieve_section_evidence() + RetrievalReport
├── evidence.py          # reused (file selection, _numbered, char budgeting)
├── structure.py         # reused (extract_symbols, extract_schema)
├── completeness.py      # reused (ensure_symbol_completeness — run once at end)
├── judge.py             # generate_spec — add a per-section generate helper
├── benchmark.py         # generate-mode: thread section-scoped path
└── cli.py               # NEW flag --section-scoped on optimize-repo / benchmark

engine/tests/
└── test_retrieval.py    # NEW — mapping, determinism, budget bound, fallback
```

**Structure Decision**: Single Python package (`engine/reposkillopt_engine/`). One new module
`retrieval.py` keeps the section→evidence map and the bounded slicer; the generation mode is a
thin loop wired into the existing `judge`/`benchmark`/`cli` paths. No new top-level dirs.

## Complexity Tracking

> No constitution violations — section omitted.
