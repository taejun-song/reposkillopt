# Phase 0 — Research & Decisions

(Decisions D1–D4 are stated inline in plan.md; expanded rationale here.)

## D1. Map completeness via the existing deterministic file set
**Decision**: enumerate with `evidence._list_code_files` (git ls-files + frozen exclusions); write a
summary for EVERY file. If the model fails/returns junk, fall back to a deterministic **skeleton**
(the file's symbols + lines from `structure.extract_symbols`). **Rationale**: 100% file coverage by
construction — directly fixes the demo's `__init__.py` omission. **Alternatives**: model-driven file
selection (rejected — non-deterministic, can skip).

## D2. Repo-relative citation enforcement
**Decision**: `normalize_repo_relative(text, repo)` strips an absolute repo prefix from any citation
and (optionally) flags unresolved ones; applied to every summary and to the from-summaries spec.
**Rationale**: fixes the demo's absolute-path pitfall so the output passes grounding/`check-artifact`
by construction. **Alternatives**: trust the model (rejected — the demo proved it emits absolute paths).

## D3. Reduce assembly bounded but honest
**Decision**: `assemble_from_summaries` concatenates the summary set as evidence; summaries are ~10×
smaller than file contents so far more fits than the file-content pack. Bounded by a budget; on
overflow, **list the dropped summaries** (no silent omission) and rely on the completeness step for
100% symbol accounting. **Rationale**: tractable first milestone; honest. **Alternatives**:
section-scoped-from-summaries (noted future enhancement — keeps peak bounded AND covers all summaries).

## D4. Peak-vs-total reporting
**Decision**: report peak (largest single-call context) + total (sum). summarize: total ≈ Σ files,
peak ≈ one file; reduce: peak ≈ assembled summaries. **Rationale**: the tradeoff must be visible (FR-007).
