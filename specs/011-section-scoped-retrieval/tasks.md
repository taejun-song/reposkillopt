# Tasks: Deterministic Section-Scoped Evidence Retrieval

**Feature**: `011-section-scoped-retrieval` | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Tests are deterministic stdlib `unittest` (model-free). Single-pack default must stay byte-for-byte unchanged.

## Phase 1: Setup

- [x] T001 Confirm reuse surface exists: `evidence` selection/`_numbered`, `structure.extract_symbols`/`extract_schema`, `completeness.ensure_symbol_completeness`, `grounding`/`quality` metrics — no new deps (engine/reposkillopt_engine/).

## Phase 2: Foundational — retrieval module (blocks everything)

- [x] T002 [US1] Create `engine/reposkillopt_engine/retrieval.py` with `SECTION_EVIDENCE` static map (19 sections → categories, per research D2) and `SectionEvidence` dataclass (data-model.md).
- [x] T003 [US1] Implement category resolvers in retrieval.py (model-free, deterministic): `readme`, `manifests`, `ci`, `entrypoints`, `top_modules`, `symbols`, `schema`, `er_entities`, `config`, `tests`, `deploy`, `imports`, `inventory` — each returns repo-relative paths/text via filename rules + `structure`/`evidence`.
- [x] T004 [US1] Implement `retrieve_section_evidence(repo_path, section, *, char_budget=8000) -> SectionEvidence`: resolve categories → bounded, line-numbered slice (reuse evidence numbering/budget), deterministic ordering, fallback to `inventory` with `fell_back=True`, record `omitted`. Raise `ValueError` on unknown section.

## Phase 3: User Story 1 — generate within a small window (P1)

- [x] T005 [US1] Add a per-section generate helper in `engine/reposkillopt_engine/judge.py` (e.g. `generate_section`) that prompts the model with only the section slice + minimal spec header; returns the section markdown.
- [x] T006 [US1] Add section-scoped generation in `benchmark.py` generate-mode path: loop the 19 sections in template order, generate each from its slice, append to the on-disk spec, then `ensure_symbol_completeness` once (compose with v0.6.0 disk-not-context).
- [x] T007 [US1] Wire `--section-scoped` flag onto `benchmark` (and `optimize-repo` if low-cost) in `engine/reposkillopt_engine/cli.py`; default off = unchanged single-pack path.
- [x] T008 [US1] Unit tests `engine/tests/test_retrieval.py`: SECTION_EVIDENCE covers all 19 sections; `retrieve_section_evidence` deterministic (byte-identical re-run); slice ≤ budget AND ≤ full pack; unmapped/empty → fallback with `fell_back=True`; unknown section → ValueError.

## Phase 4: User Story 2 — honest peak-vs-total (P2)

- [x] T009 [US2] Implement `build_retrieval_report(repo_path, *, char_budget) -> RetrievalReport` in retrieval.py: baseline (full pack), peak section, total, fallbacks, per-section sizes.
- [x] T010 [US2] Section-scoped run prints peak/baseline/total + logs inventory fallbacks (cli.py / benchmark.py).
- [x] T011 [US2] Unit tests: report fields correct on a fixture; `total ≥ peak`; `peak ≤ baseline`; `peak_reduction` computed.

## Phase 5: User Story 3 — default unchanged (P3)

- [x] T012 [US3] Test: with `--section-scoped` absent, the single-pack generate path and `_pack_opts`/metrics are unchanged (no regression); full suite green.

## Phase 6: Polish & validation

- [x] T013 Live validation on `eco-standard-wiki`: section-scoped generate; confirm peak per-section ≤ ½ full pack (SC-001), spec scores 100% symbol coverage + 19 sections + grounded ER (SC-002); record figures.
- [x] T014 Docs: engine README "section-scoped" subsection (peak-vs-total tradeoff stated honestly); reference rubric/benchmarks record.
- [~] T015 [optional, FR-012] If a skill "retrieve per section" note is added, mirror to all 4 adapters + bump canonical version; else explicitly defer in the PR.

## Dependencies

- T002–T004 (retrieval) block T005–T012.
- US1 (T002–T008) is the MVP; US2 (T009–T011) and US3 (T012) build on it.
- T013 requires a model (live); T001–T012 are deterministic/model-free.
