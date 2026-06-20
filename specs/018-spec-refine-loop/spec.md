# Feature Specification: Continuous Spec Refinement Loop

**Feature Branch**: `018-spec-refine-loop`
**Created**: 2026-06-21
**Status**: Draft
**Input**: When the system evolves automatically it should carry the spec.md generated right before forward and continuously improve THAT document — not regenerate from scratch. Each round: take the current spec, compute its concrete deterministic gaps (unresolved citations, missing sections, uncovered symbols, malformed citations), have the model revise the same document to fix exactly those, re-score, and keep it only if it improved (monotonic). Built TDD.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Carry the prior spec forward and fix its gaps (Priority: P1)

A spec exists for a repo. The loop feeds that exact spec back in with its measured gaps and asks the model to revise it; the document improves round over round instead of being re-written from scratch.

**Acceptance Scenarios**:
1. **Given** a spec with a fabricated/unresolved citation, **When** one refine round runs, **Then** the revise prompt carries the prior spec text + the concrete gaps, and the returned spec replaces the prior one only if its score is higher.
2. **Given** a candidate that scores worse, **When** evaluated, **Then** it is rejected and the prior spec is retained (monotonic — never regress).
3. **Given** N rounds, **Then** the final spec's score is ≥ the initial spec's score, and the loop stops early when there are no gaps left.

## Requirements *(mandatory)*

- **FR-001**: `spec_gaps(repo, spec) -> list[str]` — deterministic, model-free list of concrete gaps from `ground_spec` failures + `compute_structure` coverage + `compute_quality` (missing sections, malformed citations).
- **FR-002**: `score_spec(repo, spec) -> (float, GroundingResult)` — deterministic score combining grounding rate + quality + symbol coverage (reuses frozen metrics; no new metric definitions).
- **FR-003**: `refine_once(provider, skill, repo, prior_spec) -> str` — compute gaps, ask the model (`judge.revise_spec`) to revise the **prior spec** fixing those gaps, then sanitize + `ensure_symbol_completeness`. The revise prompt MUST include the prior spec and the gaps.
- **FR-004**: `refine_loop(provider, skill, repo, *, initial_spec=None, rounds=3) -> RefineResult` — start from `initial_spec` (or generate one), then iterate `refine_once`; accept a candidate **iff its score strictly improves** (monotonic); stop early when `spec_gaps` is empty. Returns the best spec + per-round history.
- **FR-005**: Deterministic scoring/gap-extraction (model-free); the only model call is the revise step. Reuses `grounding`/`quality`/`structure`/`completeness`/`sanitize` unchanged — no grounding/rubric/reward/metric-definition change.
- **FR-006**: Built TDD — tests red before implementation.

### Key Entities
- **RefineStep**: `{round, score, citation_rate, accepted, n_gaps}`.
- **RefineResult**: `{spec, history, rounds}`.

## Success Criteria *(mandatory)*

- **SC-001**: With a stub model that fixes one gap per round, the loop's score is monotonically non-decreasing and the final spec scores higher than the initial.
- **SC-002**: A worse candidate is never accepted (the prior spec is retained).
- **SC-003**: `spec_gaps`/`score_spec` are deterministic (byte-identical across runs) and make zero model calls. Full engine suite green.

## Assumptions
- This refines the SPEC document; it is complementary to `optimize-repo` (which optimizes the SKILL). They can be chained (optimize the skill, then refine the spec). The revise step's quality depends on the model, but the monotonic gate guarantees the document never regresses.
