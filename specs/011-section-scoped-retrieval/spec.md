# Feature Specification: Deterministic Section-Scoped Evidence Retrieval

**Feature Branch**: `011-section-scoped-retrieval`  
**Created**: 2026-06-11  
**Status**: Draft  
**Input**: User description: "Deterministic section-scoped evidence retrieval — feed each spec section only its relevant evidence to lower peak context. Reuse the structural ontology the project already computes (symbols, schema/FKs, manifests, entrypoints). NO embeddings, NO vector DB. Opt-in `--section-scoped` generation mode; single-pack stays the default. Honest peak-vs-total tradeoff."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate a spec within a small context window (Priority: P1)

An engineer running the optional engine against a large repository (e.g. ~1,600 symbols, 79 tables) needs the per-call context to fit a small model window. Instead of one whole evidence pack (~14k tokens) feeding all 19 sections at once, each section is generated from only the evidence that section needs, retrieved deterministically from the structure the project already computes, and written to the spec file as it completes.

**Why this priority**: This is the core capability — without per-section retrieval there is nothing to test. It directly delivers the peak-context reduction that motivates the feature.

**Independent Test**: Run section-scoped generation on a real repository; confirm the peak per-section evidence slice is a small fraction of the full-pack size, and the produced spec still has all 19 sections, 100% symbol coverage, and resolvable citations.

**Acceptance Scenarios**:

1. **Given** a repository and the section-scoped mode, **When** the spec is generated, **Then** each of the 19 sections is produced from an evidence slice no larger than the configured per-section budget and no larger than the full single-pack evidence.
2. **Given** the same repository, **When** retrieval is run twice for the same section, **Then** the returned evidence slice is byte-identical (deterministic, model-free).
3. **Given** section-scoped generation completes, **When** the spec is scored by the existing deterministic metrics, **Then** symbol coverage is 100%, all 19 sections are present, and the ER diagram (if a schema exists) is grounded — identical guarantees to the default mode.

---

### User Story 2 - See the peak-vs-total tradeoff honestly (Priority: P2)

The same engineer must be able to see that section-scoping lowers *peak* context but may raise *total* tokens, so they can choose it only when the window is the binding constraint.

**Why this priority**: The feature is only trustworthy if its real cost is surfaced; hiding the total-token increase would be dishonest and lead to misuse.

**Independent Test**: Run the mode and confirm the run reports both the peak per-section evidence size (vs the full-pack baseline) and the total evidence sent across all sections.

**Acceptance Scenarios**:

1. **Given** a section-scoped run, **When** it finishes, **Then** it reports peak per-section evidence size, the full-pack baseline size, and total evidence sent across sections.
2. **Given** a section whose mapping yields no specific evidence, **When** it is generated, **Then** the run logs that the section fell back to the shared structure inventory.

---

### User Story 3 - Default behavior is unchanged (Priority: P3)

An engineer who does not opt in must see exactly today's behavior: one cached evidence pack, one generation, same outputs and metrics.

**Why this priority**: Protects existing users and reproducibility; section-scoping is an addition, not a replacement.

**Independent Test**: Run generation without the flag; confirm the evidence pack is built once and the spec/metrics match the pre-feature behavior.

**Acceptance Scenarios**:

1. **Given** no opt-in flag, **When** a spec is generated, **Then** the single-pack path runs exactly as before (no behavior or metric change).

---

### Edge Cases

- A repository with **no schema** → schema-dependent sections (Data model) fall back to the structure inventory and state "Not applicable" per existing rules; no fabricated evidence.
- A repository with **no recognizable entrypoints/manifests** → entrypoint/dependency sections fall back to the inventory; fallback is logged.
- A **per-section budget smaller than a single file** → the slice is truncated and the omission is recorded (consistent with the existing evidence-pack bounding), never silently dropped.
- A section's mapped evidence **exceeds** the budget → bounded deterministically the same way the evidence pack bounds itself.
- The **completeness step** still runs once after all sections, so symbol coverage is 100% regardless of which slices were shown.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a deterministic, model-free mapping from each of the 19 specification sections to the kinds of repository evidence that section needs (e.g. manifests for Technology stack / Dependency map; schema files + ER entities for Data model; entrypoints and traced files for Control-/Data-flow traces; config files for Configuration map; top modules by symbol density for Core modules).
- **FR-002**: The system MUST provide a retrieval function that, given a repository, a section name, and a character budget, returns a bounded, line-numbered evidence slice for that section, reusing the existing evidence-selection and structure/schema extraction (no new extraction engine, no embeddings, no vector store).
- **FR-003**: Retrieval MUST be deterministic and reproducible: the same (repository, section, budget) MUST yield a byte-identical slice across runs.
- **FR-004**: Each returned slice MUST be no larger than its configured budget and MUST be no larger than the full single-pack evidence for the same repository.
- **FR-005**: For any section whose mapping yields no specific evidence, retrieval MUST fall back to the shared deterministic structure inventory (symbols + schema), and the fallback MUST be recorded/logged.
- **FR-006**: The system MUST provide an opt-in generation mode that produces the spec section-by-section — each model call seeing only that section's slice — appending each completed section to the spec file on disk (composing with the v0.6.0 disk-not-context discipline), then applying the deterministic completeness step once at the end.
- **FR-007**: The single-pack generation path MUST remain the default; section-scoped mode MUST be explicitly opted into and MUST NOT change default behavior or outputs.
- **FR-008**: A section-scoped run MUST report the peak per-section evidence size, the full-pack baseline size, and the total evidence sent across all sections, so the peak-vs-total tradeoff is visible.
- **FR-009**: A spec produced by section-scoped mode MUST satisfy the existing guarantees unchanged — all 19 sections present, 100% symbol coverage (via the completeness step), citations resolvable, ER diagram grounded when a schema exists — measured by the existing deterministic metrics with no metric-definition changes.
- **FR-010**: The feature MUST NOT alter grounding behavior, the rubric, the optimizer reward, or any metric definition; it only ADDS retrieval + an opt-in mode.
- **FR-011**: The feature MUST use only the standard library and the project's existing modules (no embeddings, no vector database, no heavyweight dependency).
- **FR-012**: If the agent-facing skill gains an optional "retrieve per section" note, it MUST be mirrored into all four adapters and the canonical version bumped (adapter-equivalence); the canonical skill stays vendor/repo-neutral. *(Optional — the milestone may be engine-only.)*

### Key Entities *(include if feature involves data)*

- **Section→evidence mapping**: a static, deterministic association from each of the 19 canonical section names to the evidence categories it requires (manifests, schema files, entrypoints, config files, traced files, top modules, or inventory fallback).
- **Evidence slice**: a bounded, line-numbered block of repository material for one section, plus metadata (size, whether it fell back to the inventory).
- **Retrieval report**: per-run instrumentation capturing peak slice size, full-pack baseline size, total evidence across sections, and which sections fell back.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On a large real repository, the peak per-section evidence slice is at most **half** the full single-pack evidence size (target: a small fraction), demonstrating reduced peak context.
- **SC-002**: A spec produced by section-scoped mode scores **100% symbol coverage** and **all 19 sections present**, identical to the default mode's guarantees.
- **SC-003**: Re-running retrieval for any section produces a **byte-identical** slice (100% reproducible), with **zero** model calls in the retrieval step.
- **SC-004**: With the mode off, generated spec and all deterministic metrics are **unchanged** from pre-feature behavior.
- **SC-005**: Every section-scoped run surfaces the **peak, baseline, and total** evidence figures so a user can see the peak-vs-total tradeoff before choosing the mode.

## Assumptions

- "Users" are engineers running the optional Python engine; the canonical Markdown skill, adapters, templates, and installer are unaffected unless the optional FR-012 note is added.
- The existing structural extraction (symbols, schema/FKs) and evidence-selection are sufficient signal for section mapping; no language server or full AST is introduced (regex/grep best-effort, consistent with feature 009).
- Section-scoped mode is for tight context windows; minimizing *total* token spend remains the single-pack default's job. This tradeoff is accepted and documented, not hidden.
- The deterministic completeness step (feature 010) runs once after all sections, so symbol coverage is guaranteed regardless of per-section slicing.
- Reproducibility is preserved: all retrieval is model-free and deterministic; only the per-section generation calls involve a model, exactly as the single-pack mode's one call does.
