# Feature Specification: Refactoring Opportunities View

**Feature Branch**: `015-refactoring-opportunities`
**Created**: 2026-06-13
**Status**: Draft
**Input**: Analyze potential repeated structure that can be refactored or abstracted. A derived view over the ontology (012): detect clusters of structurally-near-duplicate functions (same shape, different names/literals), suggest an abstraction, and render an **advisory, `[inference]`-only** section "16a. Refactoring opportunities". Deterministic, low-noise (≥3 instances, ≥8 normalized tokens), `rg`-first for the agent path. Built TDD.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Surface repeated structure (Priority: P1)

An engineer wants to see where the codebase repeats the same structure so it can be abstracted (a shared helper, a base class, a decorator) — grounded to the real instances, not vague advice.

**Independent Test**: On a fixture with 3 functions sharing one shape but different names/literals, assert they cluster, with each instance cited and a suggested abstraction.

**Acceptance Scenarios**:
1. **Given** ≥3 functions with the same normalized structure (≥8 tokens), **When** analyzed, **Then** they form a cluster with each instance's `file:line` and a suggested abstraction.
2. **Given** a unique function, **When** analyzed, **Then** it is not reported (low noise).
3. **Given** two handlers with the same shape but different `except` types, **When** analyzed, **Then** they do NOT cluster (the exception type is part of the signature — avoids false merges).

## Requirements *(mandatory)*

- **FR-001**: `analyze_refactors(repo) -> RefactorReport` — deterministic, model-free: extract function blocks (reuse `extract_symbols` + bounded body reads), normalize structurally (identifiers→`ID`, numbers→`NUM`, strings→`STR`; **keep keywords and the type after `except`/`raise`**), signature = stable hash, cluster identical signatures.
- **FR-002**: Report a cluster only when it has **≥3 members** and the normalized body is **≥8 tokens** (low-noise bias). Severity bands: ≥10 high, 5–9 medium, 3–4 low.
- **FR-003**: Each cluster carries every member's `file:line` (resolvable) and a deterministic suggested abstraction (shared helper / base method / decorator) keyed off the shape.
- **FR-004**: Deterministic & reproducible — same repo ⇒ byte-identical structured output; ordering by (severity desc, signature).
- **FR-005**: `render_refactor_section(report)` emits **"16a. Refactoring opportunities"**, **`[inference]`-only** (advisory; never `[fact]`, so it cannot affect the labeled-claim fact denominator), inserted after §16.
- **FR-006**: Advisory only — MUST NOT enter `REQUIRED_SECTIONS`, the rubric, the reward, or any gated set; section-completeness denominator (19) unchanged.
- **FR-007**: `rg`-first scan-don't-read for the agent path; engine reads bounded windows locally. No grounding/rubric/reward/metric-definition change.
- **FR-008**: Built TDD — tests red before implementation.

### Key Entities
- **Block**: `{file, line, normalized, signature, ntokens}`.
- **Cluster**: `{signature, members:[{file,line}], ntokens, severity, suggestion}`.
- **RefactorReport**: `{clusters, counts}`.

## Success Criteria *(mandatory)*

- **SC-001**: On the engine's own source, `analyze_refactors` finds real repeated structures (e.g. the repeated `try/except → ProviderError`/placeholder handler shape) with ≥3 members each, every member cited.
- **SC-002**: Built twice ⇒ byte-identical; zero model calls.
- **SC-003**: The rendered section is `[inference]`-only and resolves all citations; it does not change section-completeness, labeled-claim rate, or any frozen metric (suite green).

## Assumptions
- Structural near-duplication (same shape) is the v1 target; token-level line duplication (e.g. repeated one-line declarations) is out of scope. Best-effort regex normalization (feature 009 posture); the low-noise thresholds bias toward precision over recall.
