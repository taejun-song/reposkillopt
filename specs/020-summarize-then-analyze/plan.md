# Implementation Plan: Summarize-Then-Analyze (Map-Reduce Evidence)

**Branch**: `020-summarize-then-analyze` | **Date**: 2026-06-24 | **Spec**: [spec.md](./spec.md)

## Summary

Two opt-in engine capabilities forming a map-reduce evidence pipeline, keyless via existing providers:

- **`summarize`** (map) — deterministically enumerate **every** source file (reusing
  `evidence._list_code_files`) and write one grounded per-file summary under
  `.reposkillopt/summaries/<path>.md`; the file set is complete + reproducible (no silent omission),
  citations are normalized **repo-relative** (fix-by-construction for the demo's pitfalls). A
  deterministic skeleton from `structure.extract_symbols` is always written even if the model is weak.
- **`generate-spec --from-summaries`** (reduce) — assemble the generation evidence from the complete
  summary set (small) instead of file excerpts, generate the Repository Specification, run the existing
  completeness step (100% symbol coverage), and report **peak vs total** context.

New module `summarize.py` + two CLI subcommands. Reuses `structure`/`evidence`/`grounding`/
`completeness`/`judge`/providers — no new deps, stdlib only, frozen metrics untouched. TDD on the
deterministic parts; live model run validates generation.

## Technical Context

**Language/Version**: Python ≥ 3.10, stdlib only.
**Primary Dependencies**: none new — `structure.extract_symbols`, `evidence._list_code_files`/`_read`,
`grounding` (citation forms), `completeness.ensure_symbol_completeness`, `judge.generate_spec`,
`sanitize`, the providers.
**Storage**: filesystem — summaries under the target repo's `.reposkillopt/summaries/`.
**Testing**: stdlib `unittest`; deterministic parts (enumeration completeness, summary-file accounting,
repo-relative citation normalization, from-summaries assembly) with a fake provider; live generation on a small repo.
**Project Type**: optional Python engine (existing layout).
**Constraints**: deterministic, reproducible file enumeration; repo-relative citations enforced;
opt-in (defaults unchanged); honest peak-vs-total reporting; no grounding/rubric/reward/metric change.
**Scale/Scope**: 1 module + 2 CLI commands + tests; validated on the engine (30 files); composes with
`coverage-gate.sh`, `render`, `refine-spec`.

## Constitution Check

Gated against `.specify/memory/constitution.md` (populated in feature 019):
- **I. Evidence-Grounded** — PASS: summaries + spec carry resolvable repo-relative `file:line`; the
  normalization step enforces it; completeness guarantees symbol accounting.
- **IV. Deterministic & stdlib-only** — PASS: file enumeration is deterministic/reproducible; only the
  summary/spec *prose* is model-generated; no new deps.
- **Reuse, don't fork** — PASS: reuses structure/evidence/grounding/completeness/judge/providers.
- **VI. Test-First for engine code** — PASS: deterministic parts built TDD.
- **Scope boundary** — PASS: opt-in engine mode; default paths unchanged; no skill/adapter change.
No violations.

## Project Structure

```text
specs/020-summarize-then-analyze/
├── plan.md · research.md · data-model.md · quickstart.md
├── contracts/summarize.contract.md
└── tasks.md

engine/reposkillopt_engine/
└── summarize.py        # NEW — enumerate_source_files, summarize_file (skeleton+model),
                        #   summarize_repo, normalize_repo_relative, assemble_from_summaries,
                        #   generate_spec_from_summaries
engine/reposkillopt_engine/cli.py   # + `summarize` and `generate-spec` subcommands
engine/tests/test_summarize.py      # NEW — TDD
```

**Structure Decision**: one new module; CLI gains `summarize` (map) and `generate-spec` (which gets a
`--from-summaries` flag for the reduce, alongside default single-pack/`--section-scoped`).

## Phase 0 decisions (research)

- **D1 Map completeness**: enumerate via `evidence._list_code_files` (the existing deterministic set);
  write a summary for *every* file — even a model failure falls back to the deterministic skeleton
  (symbols+lines), so coverage is 100% by construction (fixes the demo's `__init__` omission).
- **D2 Repo-relative citations**: `normalize_repo_relative(text, repo)` strips any absolute repo prefix
  and rejects unresolved paths; applied to every summary and to the from-summaries spec (fixes the
  demo's absolute-path pitfall). Verified with `grounding`.
- **D3 Reduce assembly**: `assemble_from_summaries` concatenates the summary set as the evidence
  (summaries are ~10× smaller than file contents, so far more fits than the file-content pack);
  bounded by a budget — if it overflows, **dropped summaries are listed, not silently omitted**, and
  the completeness step still backstops 100% symbol coverage. Section-scoped-from-summaries is a noted
  future enhancement.
- **D4 Peak vs total**: report the largest single-call context (peak) and the sum (total); summarize =
  one call per file (high total, tiny peak); reduce peak = the assembled summaries.

## Complexity Tracking
> No violations — omitted.
