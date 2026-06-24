# Feature Specification: Summarize-Then-Analyze (Map-Reduce Evidence)

**Feature Branch**: `020-summarize-then-analyze`
**Created**: 2026-06-24
**Status**: Draft
**Input**: A map-reduce evidence pipeline — summarize **every** source file first (grounded, repo-relative), then generate the Repository Specification from the complete set of summaries. Bounds peak context and guarantees complete file coverage on large repos. A validated subagent demo proved the approach and surfaced two pitfalls (silently-skipped files; non-resolving absolute-path citations) that this feature fixes by construction.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Summarize every source file (Priority: P1)

An engineer on a large repo that overflows the single evidence pack wants every file accounted for with a small, grounded summary — none silently skipped.

**Why this priority**: It is the *map* phase the reduce step consumes, and it is independently valuable (a per-file index of the repo). Independently testable: the file set is deterministic, so coverage is checkable without a model.

**Independent Test**: Run `summarize` on a repo; confirm a summary exists for **every** enumerated source file (the `coverage-gate.sh --files` reports 100%, including `__init__`-style files), and each summary's citations are repo-relative and resolve.

**Acceptance Scenarios**:
1. **Given** a repo, **When** `summarize` runs, **Then** it writes one summary per enumerated source file under `.reposkillopt/summaries/`, with **no file silently skipped** (the enumerated set is deterministic and complete).
2. **Given** a written summary, **When** its citations are checked, **Then** every citation is a **repo-relative** `file:line` that resolves against the real repo (no absolute paths).
3. **Given** an unreadable/binary or vendored/generated file, **When** enumerating, **Then** it is excluded by the same rules `structure`/`evidence` already use (not a silent omission of a *source* file).

### User Story 2 - Generate the spec from the summaries (Priority: P1)

The same engineer wants the Repository Specification built from the complete set of summaries — so each model call sees small summaries (bounded peak context) instead of the truncated whole repo.

**Why this priority**: It is the *reduce* payoff — complete coverage at bounded peak context. Independently testable given a set of summaries.

**Independent Test**: With summaries present, `generate-spec --from-summaries` builds a spec whose evidence is the summaries; the per-call context is bounded by the summaries (not the full repo), symbol coverage is 100% (completeness step), and citations resolve.

**Acceptance Scenarios**:
1. **Given** a complete summary set, **When** `generate-spec --from-summaries` runs, **Then** the evidence assembled for generation is the summaries (not raw file excerpts), and the produced spec reaches **100% symbol coverage** via the completeness step.
2. **Given** the produced spec, **When** grounded, **Then** its `[fact]` citations resolve as repo-relative `file:line`.
3. **Given** the run, **When** it finishes, **Then** it **reports the peak-vs-total figures** (peak per-call context vs total across the run) so the tradeoff is visible.

### Edge Cases

- **A file the model can't summarize well** → the deterministic skeleton (its real symbols/lines from `structure`) is still recorded; the file is never dropped.
- **Absolute or non-resolving citation from the model** → normalized to repo-relative / flagged, so the artifact passes grounding by construction (the demo's pitfall #2).
- **Summaries missing for some files** (interrupted run) → `generate-spec --from-summaries` reports the gap rather than silently proceeding on partial coverage.
- **Very large repo** → peak stays bounded (one file per summary; the reduce sees summaries), but total model calls grow ~linearly — reported, not hidden.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `summarize <repo>` MUST deterministically enumerate **every** source file (the same set `structure`/`evidence` use; only vendored/generated dirs excluded) and write one summary per file under `<repo>/.reposkillopt/summaries/`, mirroring the source path. The enumerated set MUST be reproducible (same repo ⇒ same set).
- **FR-002**: Each summary MUST contain the file's role, its key functions/classes with a real `file:line` (reusing `structure.extract_symbols` for the deterministic skeleton), its in-repo dependencies, and notes. The summary *content* is model-generated; the *file set* is deterministic.
- **FR-003**: All citations in summaries MUST be **repo-relative** `file:line` that resolve against the repo (no absolute paths) — enforced so the output passes grounding/`check-artifact` by construction.
- **FR-004**: No source file may be **silently skipped**; `summarize` MUST report coverage (files summarized / files enumerated) and the deterministic enumeration MUST cover 100%.
- **FR-005**: `generate-spec --from-summaries` MUST assemble the generation evidence from the **complete set of summaries** (not raw file excerpts), so peak per-call context is bounded by the summaries.
- **FR-006**: The produced spec MUST still reach **100% symbol coverage** (the existing completeness step runs unchanged) and its citations MUST resolve repo-relative.
- **FR-007**: A `--from-summaries` run MUST report **peak per-call context** and **total context** so the peak-vs-total tradeoff is visible; it MUST detect and report missing summaries rather than proceed on partial coverage.
- **FR-008**: Both capabilities MUST be **opt-in** (the default single-pack and section-scoped paths are unchanged), keyless via the existing providers, stdlib-only (no new heavyweight dependency), and MUST NOT change grounding, the rubric, the reward, or any metric definition.
- **FR-009**: The deterministic parts MUST be built test-first (enumeration completeness, summary-file accounting, the from-summaries evidence assembly, repo-relative-citation enforcement); the live model generation is validated by a run on a small repo. Composes with `coverage-gate.sh`, `render`, and `refine-spec`.

### Key Entities

- **File summary**: `{file (repo-relative), role, key_symbols:[{name, line, what}], depends_on:[…], notes}` — one per source file.
- **Summary set**: the complete, deterministically-enumerated collection under `.reposkillopt/summaries/`.
- **From-summaries evidence**: the assembled generation input built from the summary set (bounded, complete).

## Success Criteria *(mandatory)*

- **SC-001**: On a repo, `summarize` produces a summary for **100%** of enumerated source files (no `__init__`-style omission), verifiable by `coverage-gate.sh --files`.
- **SC-002**: **100%** of summary citations are repo-relative and resolve against the repo.
- **SC-003**: `generate-spec --from-summaries` yields a spec with **100% symbol coverage** and **all citations resolving**, where the per-call generation context is bounded by the summaries (measurably smaller peak than the full single pack on a large repo).
- **SC-004**: The run reports peak and total context figures (the tradeoff is visible, not hidden).
- **SC-005**: With the mode off, the default generation paths and all frozen metrics are **unchanged** (full engine suite stays green).

## Assumptions

- "Source file" = the code-file set `evidence._list_code_files` already enumerates (extensions + vendored/generated exclusions); non-source assets are out of scope.
- Summaries are **file-level** (one per file); per-symbol summaries are a non-goal.
- The engine drives its provider sequentially or with bounded concurrency; orchestrating *external* subagents from inside the engine is a non-goal (the standalone subagent workflow demo is separate).
- This is an **opt-in mode for big repos**; it does not replace the single-pack or section-scoped generation paths.
- Reuses `structure`, `evidence`, `grounding`, `completeness`, and the providers; no new heavyweight dependency; deterministic enumeration + repo-relative citations are the guarantees, summary prose is best-effort.
