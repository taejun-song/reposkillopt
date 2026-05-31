# Feature Specification: N-Scorers Majority Validation Gate

**Feature Branch**: `004-majority-scoring`
**Created**: 2026-06-01
**Status**: Draft
**Input**: User description: "Spec the N-scorers majority gate variant" — replace the single scorer-of-record (feature 003) with multiple independent scorers whose per-dimension scores are combined by majority rule, so one scorer's bias or error cannot decide whether a skill edit is accepted.

## Clarifications

### Session 2026-06-01

- Q: When scorers reach no strict majority on a dimension, how is the aggregate computed? → A: Use the **median** of the scorers' values and flag the dimension low-agreement (no looping, fully reproducible).
- Q: What composition/independence model should the roster require? → A: **Any independent mix** — all-agent, all-human, or mixed; the only hard requirement is that each scorer applies the rubric blind. (Diversity via humans is encouraged for high-stakes edits but not mandated.)
- Q: If scorers are split (low-agreement) on a dimension at or below its baseline (a possible masked regression), what does PASS require? → A: **Adjudicate before PASS** — a low-agreement dimension whose aggregate is at or below baseline MUST be re-scored to resolution before the gate can PASS. (Refines FR-008: low agreement blocks only when it could mask a regression.)
- Q: What should the default roster size N be? → A: **N = 3** (odd), scaling to 5/7 for higher-stakes edits per the mode-selection rule.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Score a held-out repo with N independent scorers and aggregate by majority (Priority: P1)

A skill maintainer gates a `scope: generic` proposal using **majority mode**: instead of one scorer, **N independent scorers** (N odd, ≥3) each apply the existing rubric to each regenerated held-out specification. For every dimension, the **aggregated score is the majority (modal) value** across scorers (the median if no strict majority exists). The gate verdict then runs on these aggregated per-dimension scores using the same no-regression criterion as feature 003.

**Why this priority**: This is the whole point — making the accept/reject decision robust to a single scorer's mistake or bias. It delivers value on its own: a verdict backed by agreement across scorers rather than one person's judgment.

**Independent Test**: Have 3 scorers score a regenerated held-out spec where 2 agree a dimension is `3` and 1 says `2`; confirm the aggregated dimension score is `3` (the majority) and that the lone dissenter does not change it. Recompute the verdict from the aggregated scores.

**Acceptance Scenarios**:

1. **Given** 3 independent scorers' rubric scores for a held-out spec, **When** the maintainer aggregates, **Then** each dimension's aggregate is the majority value (or the median if all three differ).
2. **Given** the aggregated candidate scores and the aggregated baseline, **When** the verdict runs, **Then** it applies feature 003's no-regression criterion to the aggregated per-dimension values.
3. **Given** one scorer is an outlier on a dimension, **When** the other two agree, **Then** the outlier does not flip that dimension's aggregate or the verdict.

---

### User Story 2 - Record the per-scorer matrix, aggregation, and agreement (Priority: P2)

The gate report records the **full per-scorer score matrix** (scorer × dimension, per held-out repo), the **aggregated row** with the method used (majority or median), and a **per-dimension agreement signal** so a reader can see where scorers disagreed.

**Why this priority**: Robustness is only trustworthy if it is auditable — a reader must be able to see that a passing verdict rests on agreement, and where it does not. Builds directly on US1.

**Independent Test**: Read a majority gate report — it shows each scorer's 0–3 per dimension, the aggregated value, the method, and a flag on any dimension where scorers spanned a range ≥2.

**Acceptance Scenarios**:

1. **Given** a completed majority gate run, **When** the report is written, **Then** it contains the per-scorer matrix, the aggregated row, the aggregation method, and a per-dimension agreement signal.
2. **Given** a dimension where scorers split widely (range ≥2), **When** the report is produced, **Then** that dimension is flagged for attention (re-score / adjudication).

---

### User Story 3 - Enforce scorer independence and roster discipline (Priority: P2)

Scorers score **blind** — without access to one another's scores before submitting — and the report records the **roster** (each scorer's identity/role and whether human or agent) and attests independence. N is odd and ≥3.

**Why this priority**: Majority rule only adds value if the votes are independent; correlated or copied scores defeat it. Secondary to having the mechanic (US1) but essential to its integrity.

**Independent Test**: Inspect a report — the roster lists ≥3 odd scorers with roles and an independence attestation; a scenario where a scorer admits seeing others' scores first results in that scorer's row being excluded or redone.

**Acceptance Scenarios**:

1. **Given** a gate run, **When** the report is produced, **Then** it lists an odd roster of ≥3 scorers with roles and an independence attestation.
2. **Given** a scorer scored after seeing another's scores, **When** this is discovered, **Then** that scorer's row is excluded (or redone blind) and the report notes it.

---

### User Story 4 - Choose between single-scorer and majority mode (Priority: P3)

The gate supports **both** the single scorer-of-record mode (feature 003) and majority mode (this feature). The project documents **when majority mode is required** (e.g., edits to Operating Principles, a proposal that previously failed, or low single-scorer confidence) versus when single-scorer suffices (low-risk clarifying edits). Each report states which mode it used.

**Why this priority**: Majority mode is N× the effort; spending it everywhere is wasteful. A documented mode-selection rule keeps cost proportional to stakes. Useful but not required for the core mechanic.

**Independent Test**: Read the mode-selection rule; confirm a sample high-stakes edit (touches Operating Principles) is marked majority-required and a low-risk clarifying edit is marked single-scorer-eligible; each report's front matter names its mode.

**Acceptance Scenarios**:

1. **Given** the mode-selection rule, **When** a high-stakes edit is gated, **Then** majority mode is required.
2. **Given** any gate report, **When** it is read, **Then** it states whether single-scorer or majority mode was used.

---

### Edge Cases

- **No strict majority** (e.g., scorers give 1/2/3 on a 0–3 dimension): the aggregate is the **median** and the dimension is flagged low-agreement; recorded as method `median`.
- **Even roster** (a scorer drops out leaving an even count): the run notes it and falls back to the no-majority→median rule; the roster SHOULD be restored to odd before relying on the verdict.
- **Independence breach**: a scorer who saw others' scores has their row excluded or redone blind; a verdict MUST NOT rest on a non-independent row.
- **Aggregated tie at a dimension** (candidate aggregate == baseline aggregate): that is **no regression** — the dimension passes, *unless* it is also low-agreement, in which case the next rule applies.
- **Contested potential regression** (a dimension is low-agreement AND its aggregate is at or below baseline): the gate cannot PASS on it as-is; it is adjudicated (re-scored to resolution) and only then re-evaluated. An unresolved such dimension yields `HELD` (FR-008).
- **Inconsistent N across held-out repos**: N SHOULD be constant within a gate run; if it varies, the report records the N used per repo.
- **All scorers agree everywhere**: agreement signal is "unanimous"; the verdict reduces to the same shape as single-scorer but with higher confidence.
- **Cross-scorer aggregation vs cross-dimension aggregation**: combining scorers *within one dimension* is permitted and is the point of this feature; it is **not** the cross-dimension aggregate that the rubric forbids from replacing per-dimension comparison.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The validation gate MUST support a **majority mode** in which **N independent scorers** (N odd, ≥3) each score every regenerated held-out specification with the existing rubric.
- **FR-002**: Each scorer MUST apply the rubric **independently** — without access to other scorers' scores before submitting their own.
- **FR-003**: For each dimension, the **aggregated score** MUST be the majority (modal) value across scorers; if no strict majority exists, the **median**, with the chosen value and method recorded.
- **FR-004**: The gate verdict MUST apply feature 003's no-regression criterion to the **aggregated** per-dimension candidate scores versus the **aggregated** baseline (baseline aggregated by the same N-scorer method).
- **FR-005**: Deterministic checks MUST aggregate by majority pass/fail per check per held-out repo.
- **FR-006**: The gate report MUST record the full **per-scorer score matrix** (scorer × dimension, per repo), the aggregated row, the aggregation method per dimension, and a **per-dimension agreement signal**.
- **FR-007**: The report MUST record the **scorer roster** — each scorer's identity/role and whether human or agent — and the roster MUST be odd and ≥3.
- **FR-008**: A **low-agreement** dimension (scorers span a range ≥2) MUST be flagged. A low-agreement flag on a dimension whose aggregate is **above** baseline does not block the gate. A low-agreement flag on a dimension whose aggregate is **at or below** baseline (a possible masked regression) MUST be **adjudicated** — re-scored to resolution — before the gate may PASS; an unresolved at-or-below low-agreement dimension yields `HELD` (not PASS).
- **FR-009**: The verdict MUST be reproducible from the recorded per-scorer matrix plus the aggregation rule (anyone re-aggregating the matrix reaches the same verdict).
- **FR-010**: Majority mode MUST coexist with the single scorer-of-record mode (feature 003); every report MUST state which **mode** it used.
- **FR-011**: The project MUST document **when majority mode is required** (at minimum: edits to Operating Principles, a proposal that previously failed a gate, or low single-scorer confidence) versus when single-scorer mode is sufficient.
- **FR-012**: The aggregation MUST be a documented, reproducible rule (an optional helper MAY compute it); the feature introduces no service, database, model fine-tuning, or automated training loop, and stays vendor-neutral and skill-first.
- **FR-013**: The specification and report MUST make explicit that combining scorers **within a single dimension** is distinct from — and does not violate — the rule that a cross-dimension aggregate must not replace per-dimension comparison.
- **FR-014**: Independence MUST be **auditable** — the report attests that scores were submitted blind, and a breached row is excluded or redone.
- **FR-015**: When majority mode is used, the held-out **baseline** for each member MUST be an N-scorer aggregated baseline produced by the same method, so candidate and baseline are compared on equal footing.

### Key Entities *(include if feature involves data)*

- **Scorer**: An independent rater (human or agent) who scores a regenerated held-out spec with the rubric. Identified by role; never shares scores pre-submission.
- **Scorer Roster**: The odd, ≥3 set of scorers for a gate run, with roles and the independence attestation.
- **Per-scorer Score Matrix**: For each held-out repo, a scorer × dimension grid of 0–3 scores plus per-scorer deterministic-check results.
- **Aggregated Dimension Score**: The majority (or median) value per dimension, with the method and an agreement signal (e.g., unanimous / majority / split).
- **Majority Gate Report**: An extension of feature 003's Validation Gate Report that adds the per-scorer matrix, roster, aggregation method, agreement signals, `mode: majority`, and — for any adjudicated dimension — the adjudication record (who, resolved value); its verdict may be `PASS`, `FAIL`, or `HELD` (unresolved contested potential-regression).
- **N-scorer Baseline**: The aggregated baseline scoring for a held-out member under the current released version, produced with the same N-scorer method.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A held-out specification can be scored by N≥3 independent scorers and aggregated to a per-dimension verdict within a single working session.
- **SC-002**: A single dissenting scorer (1 of 3) cannot change a dimension's aggregated score when the other two agree (majority holds) in 100% of cases.
- **SC-003**: Every majority gate report records the complete per-scorer matrix and the aggregation method, and the verdict is reproducible from them.
- **SC-004**: Every dimension where scorers span a range ≥2 is flagged in the report (100% of low-agreement cases surfaced).
- **SC-005**: Scorer independence is attested in every majority gate report and any breached scorer row is excluded or redone.
- **SC-006**: Re-aggregating the recorded per-scorer matrix reproduces the same verdict every time.
- **SC-007**: The documentation states unambiguously when majority mode is required versus optional, and a reviewer can classify a given edit accordingly without further guidance.
- **SC-008**: Introducing majority mode adds no hosted service, database, or model fine-tuning; it runs locally using the existing rubric.
- **SC-009**: A dimension that is low-agreement and at or below baseline never yields a PASS without recorded adjudication — in 100% of such cases the report shows either a resolved (re-scored) dimension or a `HELD` verdict.

## Assumptions

- Default roster size is **N = 3** (odd), configurable upward (5, 7) for higher-stakes edits; the requirement is odd and ≥3.
- Aggregation: **majority/mode**; when no strict majority exists, the **median**, with the method recorded per dimension (settled in Clarifications). A low-agreement dimension at or below baseline is adjudicated before PASS (FR-008); otherwise low agreement is recorded but non-blocking.
- Scorers may be human and/or agent, but MUST be independent (blind) at scoring time; an agent scorer is one rubric application, not a consensus model.
- This feature **builds on feature 003**: the held-out reference set, regenerate-then-score, the no-regression criterion, disjointness, re-baseline, and report-referenced-by-proposal all carry over unchanged; **only the scoring step changes** from one scorer to N + aggregation.
- "Aggregation" in this feature means **across scorers within one dimension** — orthogonal to, and not in conflict with, the existing rule that a cross-dimension aggregate must not replace per-dimension comparison.
- Majority mode is **opt-in by stakes**: required for high-impact edits, optional for low-risk clarifying edits, so the N× scoring cost is spent only where it matters.
- The single scorer-of-record mode from feature 003 remains valid and is the `mode: single` case; majority mode is `mode: majority`.
