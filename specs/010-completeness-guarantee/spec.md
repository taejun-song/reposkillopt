# Feature Specification: Deterministic Completeness Guarantee

**Feature Branch**: `010-completeness-guarantee`
**Created**: 2026-06-10
**Status**: Draft
**Input**: User description: "A deterministic step that appends the exhaustive unanalyzed-symbol list to a spec, so every function/class is accounted for — 100%, every time — regardless of what the model managed to write."

## Clarifications

### Session 2026-06-10

- **Guarantee vs analysis (decided)**: the deterministic step guarantees **accounting** (every symbol referenced or listed) = 100%; it does **not** force the model to *analyze* every symbol in prose — that stays best-effort and is honestly reported by `analyzed_fraction` (feature 008/009). No metric definitions change.
- **Why deterministic**: three live runs on a 1,617-symbol repo accounted for only ~8–15% one-shot; a model cannot reliably transcribe every symbol, so the guarantee must be model-free.
- **Idempotent**: running the step on an already-complete spec changes nothing.
- **Two paths**: engine-produced specs (generate/optimize/benchmark) call the step automatically; the agent path uses an optional helper that the skill's final workflow stage instructs the agent to run (never hand-transcribe). Skill edit mirrored to the four adapters; canonical version bumped.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Every symbol is guaranteed accounted for (Priority: P1)

After a Repository Specification is produced, a deterministic step appends a complete "Symbols not yet analyzed" listing of every function/class the spec didn't already mention — so a reader is **guaranteed** nothing was silently skipped, regardless of how much the model wrote.

**Why this priority**: This is the whole point — turning "deal with every function/class" from a hope into a guarantee. Independently valuable.

**Independent Test**: Take a spec that mentions only a few of a repo's symbols; run the completeness step; confirm symbol-coverage is exactly 100% and every previously-missing symbol now appears, grouped by file, with the counts line.

**Acceptance Scenarios**:

1. **Given** a spec mentioning M of N defined symbols, **When** the completeness step runs, **Then** the result accounts for all N (symbol-coverage = 100%) by appending the N−M missing ones, grouped by file, with "N defined, M analyzed, N−M listed".
2. **Given** the step has run, **When** it runs again on the same spec, **Then** the spec is unchanged (idempotent).

### User Story 2 - Honest split of guaranteed vs analyzed (Priority: P1)

The guarantee never inflates how much was actually *analyzed*: after the step, accounting is 100% but the analyzed fraction still reflects only what the model genuinely discussed.

**Why this priority**: The guarantee must not become a way to fake depth; the honesty (analyzed vs merely listed) is what makes it trustworthy.

**Independent Test**: Run the step on a spec that analyzed a small subset; confirm symbol-coverage = 100% while analyzed-fraction equals the originally-analyzed subset (unchanged by the appended listing).

**Acceptance Scenarios**:

1. **Given** a spec that analyzed M symbols, **When** the completeness step appends the rest, **Then** coverage = 100% and analyzed-fraction = M/N (the appended listing does not count as analysis).

### User Story 3 - Works in both the engine and the agent path (Priority: P2)

Engine-produced specs (generation, per-repo optimization, benchmark generate-mode) are always complete automatically; an agent using the skill in its own harness can run the same deterministic step as the final action, instructed by the skill — never transcribing the list by hand.

**Why this priority**: The guarantee must hold wherever specs are produced, not only inside the engine.

**Independent Test**: Confirm an engine-generated spec is complete without extra steps; and that the optional helper produces the same completion from a spec + repo as the engine does.

**Acceptance Scenarios**:

1. **Given** the engine generates a spec, **When** it returns, **Then** the spec already accounts for 100% of symbols.
2. **Given** an agent-produced spec + the repo, **When** the optional helper runs, **Then** it yields the same complete spec the engine would, deterministically.

### Edge Cases

- **Already-complete spec**: the step is a no-op (idempotent).
- **Repo with no extractable symbols**: the step adds nothing; coverage is defined (100% / not-applicable).
- **Huge repo (thousands of symbols)**: the appended listing is grouped by file with per-file counts; its size is bounded with a recorded note, while still accounting for 100% via per-file listing.
- **Spec already has a "Symbols not yet analyzed" section**: the step updates/extends it rather than duplicating it.
- **A symbol both analyzed and in an existing list**: counted once; not double-listed.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a deterministic, model-free completeness step that, given a Repository Specification and its repository, returns the spec augmented so that **every** defined function/class is accounted for (referenced in the analysis or present in a "Symbols not yet analyzed" listing).
- **FR-002**: The appended listing MUST include every symbol not already accounted for, grouped by file, and MUST include the counts line "N defined, M analyzed, N−M listed".
- **FR-003**: After the step, the deterministic symbol-coverage metric MUST be exactly 100% for the repository.
- **FR-004**: The step MUST be **idempotent**: applying it to an already-complete spec produces an identical spec.
- **FR-005**: The step MUST NOT change the analyzed-fraction beyond what the model actually wrote — appended/listed symbols count as *accounted for*, not *analyzed*.
- **FR-006**: Engine paths that produce specs (spec generation, per-repo optimization, benchmark generate-mode) MUST apply the completeness step so engine-produced specs are always complete.
- **FR-007**: The system MUST provide an optional helper usable in the agent path that produces the same completion from (spec, repo); the canonical skill's final workflow stage MUST instruct the agent to run it (or append the deterministically-computed listing) as the last action and to never hand-transcribe the list.
- **FR-008**: The canonical skill edit MUST be vendor/repo-neutral and mirrored into all four adapters with the canonical version bumped (adapter-equivalence).
- **FR-009**: The appended listing MUST be bounded on large repositories (per-file grouping/counts) with any truncation recorded, while still accounting for 100%.
- **FR-010**: The step MUST be reproducible and add no heavyweight dependency, reusing feature-009 symbol extraction and the feature-008/009 accounting; it MUST NOT change grounding behavior, the rubric, the optimizer reward, or the metric definitions.

### Key Entities *(include if feature involves data)*

- **Completeness step**: the deterministic transform `(spec, repo) → spec'` that guarantees 100% symbol accounting; idempotent.
- **Unanalyzed-symbol listing**: the appended/updated "Symbols not yet analyzed" section — every not-yet-referenced symbol, grouped by file, with counts.
- **Accounting vs analysis**: accounted = referenced or listed (guaranteed 100%); analyzed = genuinely discussed (best-effort, measured by analyzed-fraction).
- **Optional helper**: the agent-path entry point producing the same completion as the engine.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For any spec + repo, after the completeness step the symbol-coverage metric is exactly 100%.
- **SC-002**: Applying the step twice yields a byte-identical spec the second time (idempotent).
- **SC-003**: The analyzed-fraction after the step equals the fraction the model originally analyzed (the appended listing adds accounting, not analysis).
- **SC-004**: An engine-generated spec for a repository accounts for 100% of symbols with no extra manual step.
- **SC-005**: On the validation repository (≈1,600 symbols), a generate-mode spec routed through the step reports symbol-coverage = 100% (vs ~10% one-shot), with the appended section grouped and counted.
- **SC-006**: The step is model-free and reproducible (identical output for identical inputs); grounding behavior, rubric, optimizer reward, and metric definitions are unchanged.

## Assumptions

- Reuses feature-009 `extract_symbols` (regex best-effort, documented) and the feature-008/009 accounting; "accounted-for" remains: name present, or file listed under the unanalyzed section.
- The model's analysis remains best-effort; this feature guarantees only *accounting*, with `analyzed_fraction` keeping the split honest.
- The optional helper follows the project's optional-helper stance (small, deterministic, no new dependency); the canonical skill edit follows the convergence-loop discipline (vendor-neutral, adapter-mirrored, version-bumped, validation-gate referenced).
- "Bounded on huge repos" means per-file counts when full enumeration would exceed a recorded size cap, still accounting for 100%.
- The ER-diagram behavior from feature 009 is unchanged.
