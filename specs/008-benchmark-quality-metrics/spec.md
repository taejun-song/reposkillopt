# Feature Specification: Deterministic Quality Metrics for the Benchmark

**Feature Branch**: `008-benchmark-quality-metrics`
**Created**: 2026-06-09
**Status**: Draft
**Input**: User description: "Extend the grounding benchmark with additional deterministic, model-free quality metrics so optimization lift is visible even when citation-resolution is already 100% — surfaced by the objectiv A/B, where grounding was flat but the optimizer still improved spec quality."

## Clarifications

### Session 2026-06-09

Resolved as informed defaults (delegated; recorded for explicitness):

- **Headline stays** the citation-resolution rate; the new quality metrics are reported **alongside** it, never replacing it.
- **All new metrics are deterministic and model-free** (computed from spec text + repo), reproducible like feature-005 grounding. The existing **LLM rubric score is optional, OFF by default, and clearly labeled non-reproducible** — never a deterministic headline.
- **Composite quality score**: a documented, reproducible weighted mean of the deterministic metrics in [0,1], reported for convenience; its formula is recorded in the report.
- **Motivating evidence**: objectiv (TS monorepo) baseline citation-resolution was 100% and stayed 100% after optimization, yet the optimizer accepted 2 edits that improved evidence discipline (citation-audit stage, no comma-line-lists, pinpoint citations for doc-characterization claims). These are exactly the deterministic signals added here.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See optimization lift on already-grounded repos (Priority: P1)

A maintainer benchmarks the canonical vs an optimized skill on a repo whose citation-resolution is already 100%. The report now shows **deterministic quality metrics** (citation density, labeled-claim rate, malformed-citation rate, section completeness) that differ between the two skills — so the optimizer's quality improvement is visible, not hidden behind a flat 100%.

**Why this priority**: This is the core gap the objectiv A/B exposed; without it the benchmark understates optimization on clean repos. Independently valuable.

**Independent Test**: Score two specs for the same repo that have identical citation-resolution but different quality (one with comma-malformed citations and an unlabeled overview, one cleaned up); confirm the quality metrics differ and the cleaner spec scores higher on the composite quality score.

**Acceptance Scenarios**:

1. **Given** two specs with the same citation-resolution rate but different evidence discipline, **When** both are scored, **Then** the deterministic quality metrics (and the composite quality score) are higher for the cleaner spec.
2. **Given** a spec with comma-disjoint line citations (e.g. `:39-40,147`), **When** it is scored, **Then** the malformed-citation-rate metric reflects them.

### User Story 2 - Reproducible, fuller report (Priority: P1)

The benchmark report and its machine-readable summary include the new deterministic metrics and surface the seven existing checks **individually** (not just an all-pass boolean), so per-check differences between skills are visible — and re-running gives identical numbers.

**Why this priority**: A fuller, still-reproducible report is what makes the lift legible and citable; the per-check breakdown shows exactly which discipline improved.

**Independent Test**: Run the benchmark twice on the same manifest+specs; confirm the new metrics and per-check values are byte-identical, and the report contains each metric per entry plus the individual checks.

**Acceptance Scenarios**:

1. **Given** a completed run, **When** the report is opened, **Then** each entry shows citation-resolution, the new quality metrics, the composite quality score, and the 7 checks individually.
2. **Given** the same inputs run twice, **When** the deterministic metrics are compared, **Then** they are identical.

### User Story 3 - Optional model-scored context (Priority: P3)

A maintainer optionally enables the existing LLM rubric score as a **secondary, clearly-labeled, non-reproducible** signal for additional context — never as the deterministic headline.

**Why this priority**: Nice-to-have context for those who want the model's holistic view; must not contaminate the deterministic story. Lowest priority and off by default.

**Independent Test**: With the option off (default), no model is called and the report shows only deterministic metrics; with it on, an LLM rubric score appears under a clearly-labeled "non-reproducible" section.

**Acceptance Scenarios**:

1. **Given** the default configuration, **When** a run completes, **Then** zero model calls were made and only deterministic metrics appear.
2. **Given** the optional rubric is enabled, **When** the report is produced, **Then** the rubric score is shown labeled as model-scored / non-reproducible, separate from the deterministic metrics.

### Edge Cases

- **Spec with zero `[fact]` claims**: citation-density and labeled-claim-rate are defined (e.g. reported as not-applicable / 1.0 over zero), not a divide-by-zero.
- **Spec with zero citations**: malformed-citation-rate is defined (0 of 0 → 0), section-completeness still computed.
- **Empty/garbage spec**: metrics computed without crashing; composite score reflects the poverty.
- **Already-perfect spec**: all quality metrics at their ceiling; composite = 1.0; identical across re-runs.
- **Backward compatibility**: existing benchmark runs and the existing report fields still work; new fields are additive.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The benchmark MUST compute, with **no language model**, these deterministic quality metrics per scored spec: citation density (resolvable citations per `[fact]` claim, plus the `[fact]` count), labeled-claim rate (fraction of `[fact]` claims immediately followed by a citation), malformed-citation rate (fraction of citations in an invalid form such as comma-disjoint line lists), and section completeness (fraction of the 19 required sections present and non-empty).
- **FR-002**: The benchmark MAY compute a deterministic **trace-presence** metric (whether the Control-flow and Data-flow trace sections each contain ≥1 resolving citation).
- **FR-003**: The benchmark MUST surface the existing seven deterministic checks **individually** in the report (not only the all-pass boolean).
- **FR-004**: The benchmark MAY report a **composite quality score** in [0,1] — a documented, reproducible weighted mean of the deterministic metrics; its formula MUST appear in the report.
- **FR-005**: All metrics in FR-001–FR-004 MUST be reproducible: the same spec + repo MUST yield identical values on every run (no model, no randomness).
- **FR-006**: The citation-resolution rate MUST remain the **primary/headline** metric; the new metrics are reported alongside it, not in place of it.
- **FR-007**: The benchmark MAY, when explicitly enabled (OFF by default), report the existing **LLM rubric score** as a **secondary, clearly-labeled, non-reproducible** signal; it MUST be visually separated from the deterministic metrics and excluded from the deterministic acceptance.
- **FR-008**: The new metrics MUST appear in both the human report and the machine-readable summary.
- **FR-009**: The feature MUST NOT change the canonical skill, the feature-005 grounding behavior (it may only ADD surfaced metrics), the rubric definitions, or the optimizer's reward formula.
- **FR-010**: The feature MUST add no heavyweight runtime dependency and stay within the existing engine.
- **FR-011**: The new metrics MUST distinguish two specs that have identical citation-resolution but different evidence discipline (the objectiv case): the cleaner spec MUST score strictly higher on at least one deterministic quality metric (and on the composite score).

### Key Entities *(include if feature involves data)*

- **Quality metrics**: the per-spec deterministic measures (citation density, labeled-claim rate, malformed-citation rate, section completeness, optional trace presence) added to each benchmark entry result.
- **Composite quality score**: the documented, reproducible [0,1] weighted mean of the deterministic metrics.
- **Per-check breakdown**: the seven existing deterministic checks reported individually.
- **Optional rubric signal**: the model-scored, non-reproducible secondary number, off by default and clearly labeled.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For two specs of one repo with identical citation-resolution but different evidence discipline, the deterministic quality metrics differ and the composite quality score is strictly higher for the cleaner spec (the objectiv-class case is no longer flat).
- **SC-002**: All deterministic metrics are reproducible — two runs on the same inputs yield identical values.
- **SC-003**: With the default configuration, a run makes **zero** model calls and reports only deterministic metrics.
- **SC-004**: The report and machine-readable summary include the new metrics, the composite score, and the seven checks individually, per entry.
- **SC-005**: Re-running the optimization-lift A/B (e.g. click + objectiv) shows the new metrics differentiating canonical vs optimized on the objectiv case where citation-resolution alone was flat.
- **SC-006**: The canonical skill, feature-005 grounding behavior, rubric definitions, and optimizer reward are unchanged.

## Assumptions

- Feature-005 grounding already parses citations and computes the citation-bearing checks; the new metrics reuse that parsing/resolution (e.g. malformed forms are already recognized) and add counts/rates on top — no separate parser.
- The 19 required sections and the four claim labels are those defined by feature-005 grounding; "non-empty section" means it contains content beyond its heading.
- A documented, simple weighting for the composite score (e.g. equal weight of the deterministic metrics) is acceptable as a default; the exact weights are an implementation detail recorded in the report.
- The optional LLM rubric uses the existing scorer and the existing provider layer; it is excluded from deterministic acceptance and off by default.
- The benchmark report layout (feature 007) is extended additively; existing consumers of the report/TSV keep working.
