# Feature Specification: Deterministic Hallucination Catcher (Claim-Support Verifier)

**Feature Branch**: `022-hallucination-gate`
**Created**: 2026-07-03
**Status**: Draft
**Input**: User description: "A model-free lexical claim-support verifier that catches the hallucinations weak/small-context models (e.g. Qwen) produce which citation-resolution alone misses — shipped as an engine module + a zero-install POSIX-sh gate, wired into the refine loop and the commit gate, and measured by a mutation-based benchmark."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Catch a claim the citation does not actually support (Priority: P1)

A weak model produces a Repository Specification claim like "uses Redis for caching" and cites a real line — but that line is about Postgres. Citation resolution passes (the anchor is real), yet the claim is a hallucination. The catcher inspects the *content* at the cited location and flags the claim as unsupported, naming the claim, its location, which check failed, and why. The author (or the loop) fixes it before it lands.

**Why this priority**: This is the single largest gap today. Citation resolution proves a location exists; it does not prove the location *supports the claim*. Weak, small-context models exploit exactly this gap, so closing it is the core value.

**Independent Test**: On a fixture where a claim's cited line contains none of the claim's identifiers, the catcher emits a finding of the "claim↔cited-code mismatch" kind; on a fixture where the cited line does contain them, it emits none.

**Acceptance Scenarios**:

1. **Given** a `[fact]` whose checkable tokens do not appear within the window around its cited line, **When** the catcher runs, **Then** it flags a mismatch finding identifying the claim, location, and the missing tokens.
2. **Given** a `[fact]` whose tokens do appear at/near the cited line, **When** the catcher runs, **Then** it emits no finding for that claim.
3. **Given** the same artifact and repo, **When** the catcher runs twice, **Then** the findings are byte-identical (reproducible).

---

### User Story 2 - Catch invented symbols, dropped labels, and fabricated quantities (Priority: P1)

Small-context models invent APIs they can't see, forget the claim-labeling discipline, and fabricate specifics. The catcher flags: a backticked code identifier that exists nowhere in the repo (fabricated symbol); a sentence that names a real file/symbol but carries no claim label (unlabeled factual claim); and a numeric claim whose number does not appear at the cited span (unsupported quantity).

**Why this priority**: These three are the rest of the deterministically-catchable hallucination surface and, together with US1, are what makes weak-model output trustworthy. They share the same lexical-vs-disk mechanism, so they ship together.

**Independent Test**: Four fixtures (one per check) each produce exactly the expected finding kind; a clean grounded fixture produces none.

**Acceptance Scenarios**:

1. **Given** a backticked identifier absent from the repo's symbols and files, **When** the catcher runs, **Then** it flags a fabricated-symbol finding.
2. **Given** a sentence naming a real file/symbol with no claim label, **When** the catcher runs, **Then** it flags an unlabeled-claim finding.
3. **Given** a numeric claim whose number is absent from the cited span, **When** the catcher runs, **Then** it flags an unsupported-quantity finding.
4. **Given** a genuinely grounded, fully-labeled spec, **When** the catcher runs, **Then** it emits zero findings (no false positives).

---

### User Story 3 - Zero-install gate for CI / pre-commit / a reviewer's box (Priority: P2)

Someone who has not installed the Python engine still wants to catch hallucinations — in CI, in a pre-commit hook, or on a reviewer's laptop. A standalone dependency-free script runs the same checks and agrees with the engine on shared fixtures.

**Why this priority**: The zero-install path is what makes the catcher adoptable everywhere the engine isn't, mirroring the existing coverage verifier. It's a distribution/portability layer over the same checks (P1), hence P2.

**Independent Test**: On a set of shared fixtures, the script and the engine report the same findings (same kinds, same locations); the script passes under two different POSIX shells.

**Acceptance Scenarios**:

1. **Given** a shared fixture set, **When** both the script and the engine run, **Then** they agree on which artifacts are clean vs. flagged and on the finding kinds.
2. **Given** a clean artifact, **When** the script runs, **Then** it exits success; **Given** a flagged artifact, it exits non-zero; **Given** bad arguments, it exits with a usage code.

---

### User Story 4 - The loop and the commit gate target hallucinations (Priority: P2)

The catcher is not just a report — it feeds the improvement machinery. The refinement loop receives the catcher's findings as concrete gaps to fix, so refinement drives a hallucinated spec toward clean; and the commit-time gate treats unsupported claims as a failing gate, so a weak-model commit carrying a hallucination is blocked (or, with a provider, remediated) before it lands.

**Why this priority**: Detection without enforcement leaves the loop optional. Wiring into the existing loop + commit gate is what makes the improvement *systematic*. It depends on the detector (P1) existing first.

**Independent Test**: A hallucinated spec fed to the refinement loop has strictly fewer catcher findings after refinement; the commit gate returns a failing result for an artifact with an unsupported claim and a passing result once it is clean.

**Acceptance Scenarios**:

1. **Given** the catcher reports findings on a spec, **When** the refinement loop runs, **Then** those findings appear among the gaps it is asked to fix and the post-loop finding count does not increase.
2. **Given** an artifact carrying an unsupported claim, **When** the commit gate runs, **Then** the hallucination gate fails (blocking, or triggering remediation with a provider); once the claim is supported, the gate passes.

---

### User Story 5 - Measure and tune the catcher per model (mutation benchmark) (Priority: P3)

To *improve* the catcher (not just run it), a benchmark takes a known-clean grounded spec, injects each hallucination type on purpose, and measures how many injections the catcher catches (recall, per class) and whether it ever flags the clean original (precision). Running it against outputs from different models produces a calibration report showing each model's failure mix.

**Why this priority**: This is the meta-loop that lets the catcher be systematically improved and its weak-model benefit proven with real numbers. It's valuable but sits on top of a working detector, so it is the last increment.

**Independent Test**: Given a clean spec, the benchmark injects known hallucinations, and the reported recall equals the fraction of injections flagged and the reported precision reflects whether the clean spec was flagged — verifiable by construction against the known injection set.

**Acceptance Scenarios**:

1. **Given** a clean grounded spec, **When** the benchmark injects N hallucinations of a class and the catcher flags M of them, **Then** the reported per-class recall is M/N.
2. **Given** a clean grounded spec that the catcher does not flag, **When** the benchmark runs, **Then** the reported precision reflects zero false positives on that input.
3. **When** the benchmark runs over a model's outputs, **Then** it writes a calibration report recording per-class recall and overall precision.

---

### Edge Cases

- **A claim with no checkable tokens** (pure prose, no identifiers/numbers/paths) → not subject to the token-match or quantity checks (nothing lexical to verify); it is not falsely flagged.
- **A backticked span that is prose, not code** (e.g. `` `TODO` `` or an English word in backticks) → the fabricated-symbol check must not flag ordinary words; only code-like identifiers are candidates, and a documented rule decides what "code-like" means.
- **A cited symbol that legitimately appears far from the cited line** (defined at line 10, claim cites a usage at line 400) → the window is around the *cited* line; if the token is genuinely absent from that window the finding is honest, and the fix is to cite the right line. The window size is documented and tunable.
- **An artifact that is not a Repository-Specification-style claim document** (a feedback note, a raw table) → checks that don't apply (e.g. label discipline on a non-claim doc) are scoped so the catcher does not produce noise on non-claim content.
- **A quantity that is a version number or a citation line number** (`v2`, `:42`) → the quantity check must not treat structural numbers (citation anchors, code fences) as factual quantities; a documented rule excludes them.
- **A genuinely correct claim the lexical check cannot verify** (a fluent paraphrase sharing no tokens with the code) → **not caught** — this is the documented semantic blind spot; the catcher neither flags it nor claims to have verified it.
- **A repo with no extractable symbols** → the symbol-existence check has an empty symbol set; it degrades to a file-tree lexical check rather than flagging everything.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a deterministic, model-free catcher that, given an artifact and its repo, returns structured findings; the same artifact + repo MUST yield byte-identical findings on every run.
- **FR-002**: The catcher MUST implement a **claim↔cited-code** check: for each labeled claim-of-fact, its checkable tokens (backticked spans, code-like identifiers, string literals, file paths) MUST appear in the cited file within a documented window around the cited line, else the claim is flagged as unsupported.
- **FR-003**: The catcher MUST implement a **fabricated-symbol** check: every backticked code-like identifier in the artifact MUST exist in the repo's symbol set or file tree, else it is flagged; ordinary (non-code-like) backticked words MUST NOT be flagged.
- **FR-004**: The catcher MUST implement an **unlabeled-claim** check: a sentence that names a real repo file or symbol but carries no claim label MUST be flagged.
- **FR-005**: The catcher MUST implement an **unsupported-quantity** check: a numeric factual quantity in a claim MUST match a number at/near its cited span, else it is flagged; structural numbers (citation line anchors, version tokens) MUST be excluded.
- **FR-006**: Every finding MUST identify the claim text, its location in the artifact, the check that failed, and a human-readable reason.
- **FR-007**: The catcher MUST NOT modify the frozen citation-resolution component or any existing metric, rubric, or reward definition; it is a NEW capability that composes existing citation-parsing and symbol-extraction.
- **FR-008**: The system MUST provide a **zero-install** standalone gate (no engine, no language runtime beyond a POSIX shell and standard text utilities) that runs the same checks and, on a shared fixture set, agrees with the engine catcher on clean-vs-flagged and on finding kinds.
- **FR-009**: The standalone gate MUST exit with distinct codes for clean (success), findings present (failure), and bad usage, and MUST run under at least two different POSIX shells.
- **FR-010**: The catcher's findings MUST be consumable by the refinement loop as concrete gaps, so refinement is driven to fix flagged claims; after a refinement pass the number of catcher findings MUST NOT increase.
- **FR-011**: The commit-time gate MUST treat unsupported/hallucinated claims as a failing gate for claim-bearing artifacts, so an artifact carrying such a claim is blocked (or remediated when a provider is available) and passes only once the claim is supported.
- **FR-012**: The system MUST provide a **mutation benchmark** that injects each hallucination class into a known-clean grounded spec and measures per-class **recall** (fraction of injections flagged) and overall **precision** (whether the clean input is flagged), writing a calibration report.
- **FR-013**: The benchmark MUST support comparing multiple models' outputs and record each model's failure mix in the calibration report.
- **FR-014**: The system MUST document plainly the **blind spot**: purely semantic paraphrase hallucinations that share no lexical tokens with the code are NOT caught; the catcher must neither flag them nor imply it verified them.
- **FR-015**: The window size for the claim↔cited-code and quantity checks, and the rule for what counts as a "code-like" identifier, MUST be documented and adjustable without changing any other component.

### Key Entities *(include if feature involves data)*

- **Claim**: A labeled statement-of-fact in an artifact, with its text, location (line), and citation(s). The unit the catcher inspects.
- **Checkable token**: A lexical fragment of a claim that can be verified against the repo — a backticked span, a code-like identifier, a string literal, a file path, or a number.
- **Finding**: A single detected hallucination — {claim text, artifact location, check kind (mismatch / fabricated-symbol / unlabeled / unsupported-quantity), reason}. The catcher's output unit.
- **Hallucination class**: One of the four detectable kinds; the axis along which recall is measured.
- **Mutation**: A programmatic injection of one hallucination of a given class into a clean spec (flip a citation line, rename a cited symbol, invent an API, strip a label, alter a quantity), with a known ground-truth location — the benchmark's input.
- **Calibration report**: Per-class recall + overall precision for a given set of specs/model, recording the model's failure mix.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On a labeled fixture set containing one planted instance of each of the four hallucination classes plus clean claims, the catcher flags **100% of the planted instances** (recall = 1.0 on the fixtures) — the definition-of-done for detection.
- **SC-002**: On a genuinely grounded, fully-labeled reference spec, the catcher produces **zero findings** (precision = 1.0; no false positives) — no honest spec is blocked.
- **SC-003**: The catcher's findings are **reproducible**: repeated runs on the same artifact + repo produce byte-identical output.
- **SC-004**: The standalone gate and the engine catcher **agree on 100% of shared fixtures** (same clean-vs-flagged verdict and finding kinds), and the gate passes under two different POSIX shells.
- **SC-005**: A hallucinated spec run through the refinement loop has **strictly fewer** catcher findings afterward (and never more); the commit gate returns a failing result for an unsupported-claim artifact and a passing result once it is clean.
- **SC-006**: The mutation benchmark reports **per-class recall and overall precision**, and the reported numbers equal the values computed by construction from the known injection set (the measurement is itself verifiable).
- **SC-007**: No existing metric/rubric/reward changes and the frozen citation-resolution component is untouched; the full existing test suite stays green.

## Assumptions

- **Lexical, not semantic**: The catcher is a *lexical* claim-support verifier. It catches hallucinations that contradict or fail to match the tokens present in the cited code; it does not perform natural-language entailment. Semantic paraphrase hallucinations are out of scope (FR-014).
- **Reuse over re-implementation**: Citation parsing/resolution, symbol extraction, the label-rate notion, the refinement loop, the commit gate, and the benchmark harness already exist; this feature composes them and introduces no fork and no new heavyweight dependency.
- **Scope is `.reposkillopt/` artifacts**: The catcher inspects the project's produced artifacts (specifications and related claim documents), not arbitrary source prose.
- **Deterministic floor, optional judge deferred**: This is the reproducible, model-free floor. An optional model-judge second tier for semantic hallucinations is explicitly deferred to a later feature.
- **Window default**: A small default line window around the cited line is used for token/quantity matching; the exact default is a planning decision and is documented + adjustable (FR-015).
- **Stacking**: This feature extends the commit gate delivered in feature 021 and is developed on top of that work.
